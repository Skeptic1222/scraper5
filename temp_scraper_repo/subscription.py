"""
Subscription Management Module
Handles PayPal Advanced Checkout integration and subscription logic
"""

import os
from datetime import datetime, timedelta
from functools import wraps

import paypalrestsdk
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required

from models import User, db


# Initialize PayPal SDK
def init_paypal():
    """Initialize PayPal SDK with credentials from environment"""
    # Clean the mode value to remove any comments
    paypal_mode = os.environ.get('PAYPAL_MODE', 'sandbox').strip().split('#')[0].strip()

    # Validate mode
    if paypal_mode not in ['sandbox', 'live']:
        paypal_mode = 'sandbox'  # Default to sandbox for safety

    paypalrestsdk.configure({
        "mode": paypal_mode,
        "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
        "client_secret": os.environ.get('PAYPAL_SECRET')
    })

# Subscription Plans Configuration
SUBSCRIPTION_PLANS = {
    'basic': {
        'name': 'Basic',
        'monthly_price': 4.99,
        'yearly_price': 41.90,
        'features': [
            '2TB storage',
            'All basic sources unlocked',
            'No watermarks',
            'Priority support'
        ],
        'sources': ['reddit', 'imgur', 'wikimedia', 'deviantart', 'pixabay', 'unsplash', 'pexels'],
        'storage_gb': 2048
    },
    'pro': {
        'name': 'Pro',
        'monthly_price': 14.99,
        'yearly_price': 125.90,
        'features': [
            '10TB storage',
            'All sources unlocked except NSFW',
            'No watermarks',
            'API access',
            'Bulk download',
            'Priority support'
        ],
        'sources': ['reddit', 'imgur', 'wikimedia', 'deviantart', 'pixabay', 'unsplash', 'pexels',
                   'facebook', 'instagram', 'twitter', 'tiktok', 'youtube', 'vimeo'],
        'storage_gb': 10240
    },
    'ultra': {
        'name': 'Ultra',
        'monthly_price': 29.99,
        'yearly_price': 215.90,
        'features': [
            'Unlimited storage',
            'All sources unlocked',
            'NSFW content access',
            'Safe Search toggle',
            'No watermarks',
            'API access',
            'Bulk download',
            'Custom integrations',
            'Dedicated support'
        ],
        'sources': 'all',  # Special case for all sources
        'storage_gb': -1,  # Unlimited
        'nsfw_enabled': True
    }
}

# All available sources
ALL_SOURCES = [
    'reddit', 'imgur', 'wikimedia', 'deviantart', 'pixabay', 'unsplash', 'pexels',
    'facebook', 'instagram', 'twitter', 'tiktok', 'youtube', 'vimeo', 'pinterest',
    'tumblr', 'flickr', '500px', 'giphy', 'tenor'
]

# Free trial sources
TRIAL_SOURCES = [
    'reddit', 'imgur', 'wikimedia', 'deviantart', 'pixabay', 'unsplash', 'pexels',
    'google_images', 'bing_images', 'youtube', 'vimeo', 'facebook', 'instagram',
    'twitter', 'tiktok', 'pinterest', 'tumblr', 'flickr'
]

# Create subscription blueprint
subscription_bp = Blueprint('subscription', __name__, url_prefix='/subscription')

def subscription_required(f):
    """Decorator to check if user has active subscription"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_subscribed():
            flash('This feature requires an active subscription.', 'warning')
            return redirect(url_for('subscription.plans'))
        return f(*args, **kwargs)
    return decorated_function

def credits_required(f):
    """Decorator to check if user has credits or subscription"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.has_credits():
            flash('You have no credits remaining. Please upgrade to continue.', 'warning')
            return redirect(url_for('subscription.plans'))
        return f(*args, **kwargs)
    return decorated_function

@subscription_bp.route('/plans')
@login_required
def plans():
    """Display subscription plans"""
    return render_template('subscription/plans.html',
                         plans=SUBSCRIPTION_PLANS,
                         current_plan=current_user.subscription_plan,
                         credits=current_user.credits)

@subscription_bp.route('/subscribe/<plan_id>/<billing_cycle>')
@login_required
def subscribe(plan_id, billing_cycle):
    """Initialize PayPal subscription"""
    if plan_id not in SUBSCRIPTION_PLANS:
        flash('Invalid subscription plan.', 'error')
        return redirect(url_for('subscription.plans'))

    if billing_cycle not in ['monthly', 'yearly']:
        flash('Invalid billing cycle.', 'error')
        return redirect(url_for('subscription.plans'))

    plan = SUBSCRIPTION_PLANS[plan_id]
    price = plan['monthly_price'] if billing_cycle == 'monthly' else plan['yearly_price']

    # Initialize PayPal
    init_paypal()

    # Create PayPal payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('subscription.payment_success', _external=True),
            "cancel_url": url_for('subscription.payment_cancel', _external=True)
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": f"{plan['name']} Subscription ({billing_cycle})",
                    "sku": f"{plan_id}_{billing_cycle}",
                    "price": str(price),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(price),
                "currency": "USD"
            },
            "description": f"{plan['name']} subscription - {billing_cycle} billing"
        }]
    })

    if payment.create():
        # Store payment details in session
        session['payment_id'] = payment.id
        session['plan_id'] = plan_id
        session['billing_cycle'] = billing_cycle

        # Redirect to PayPal
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
    else:
        flash(f'Error creating payment: {payment.error}', 'error')
        return redirect(url_for('subscription.plans'))

@subscription_bp.route('/payment/success')
@login_required
def payment_success():
    """Handle successful PayPal payment"""
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    if not payment_id or not payer_id:
        flash('Invalid payment details.', 'error')
        return redirect(url_for('subscription.plans'))

    # Initialize PayPal
    init_paypal()

    # Execute payment
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Get plan details from session
        plan_id = session.get('plan_id')
        billing_cycle = session.get('billing_cycle')

        # Update user subscription
        current_user.subscription_plan = plan_id
        current_user.subscription_status = 'active'
        current_user.paypal_subscription_id = payment_id
        current_user.subscription_start_date = datetime.utcnow()

        # Set end date based on billing cycle
        if billing_cycle == 'monthly':
            current_user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
        else:
            current_user.subscription_end_date = datetime.utcnow() + timedelta(days=365)

        # Update enabled sources
        plan = SUBSCRIPTION_PLANS[plan_id]
        if plan['sources'] == 'all':
            current_user.set_enabled_sources(ALL_SOURCES)
        else:
            current_user.set_enabled_sources(plan['sources'])

        # Enable NSFW for Ultra plan
        if plan_id == 'ultra':
            current_user.is_nsfw_enabled = True

        # Clear session data
        session.pop('payment_id', None)
        session.pop('plan_id', None)
        session.pop('billing_cycle', None)

        db.session.commit()

        flash(f'✅ Thanks for subscribing! Your {plan["name"]} account is now active. Enjoy full access.', 'success')
        return redirect(url_for('index'))
    else:
        flash(f'Payment execution failed: {payment.error}', 'error')
        return redirect(url_for('subscription.plans'))

@subscription_bp.route('/payment/cancel')
@login_required
def payment_cancel():
    """Handle cancelled PayPal payment"""
    flash('Payment cancelled. You can try again anytime.', 'info')
    return redirect(url_for('subscription.plans'))

@subscription_bp.route('/cancel')
@login_required
@subscription_required
def cancel_subscription():
    """Cancel user subscription"""
    current_user.subscription_status = 'cancelled'
    db.session.commit()

    flash('Your subscription has been cancelled. You will retain access until the end of your billing period.', 'info')
    return redirect(url_for('subscription.account'))

@subscription_bp.route('/account')
@login_required
def account():
    """Display user account and subscription details"""
    return render_template('subscription/account.html',
                         user=current_user,
                         plan=SUBSCRIPTION_PLANS.get(current_user.subscription_plan),
                         all_sources=ALL_SOURCES,
                         trial_sources=TRIAL_SOURCES)

@subscription_bp.route('/webhook', methods=['POST'])
def paypal_webhook():
    """Handle PayPal webhooks for subscription events"""
    # Verify webhook signature (implement based on PayPal docs)
    webhook_data = request.get_json()

    event_type = webhook_data.get('event_type')
    resource = webhook_data.get('resource', {})

    if event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
        # Handle subscription cancellation
        subscription_id = resource.get('id')
        user = User.query.filter_by(paypal_subscription_id=subscription_id).first()
        if user:
            user.subscription_status = 'cancelled'
            db.session.commit()

    elif event_type == 'PAYMENT.SALE.COMPLETED':
        # Handle successful payment
        pass

    elif event_type == 'BILLING.SUBSCRIPTION.EXPIRED':
        # Handle subscription expiration
        subscription_id = resource.get('id')
        user = User.query.filter_by(paypal_subscription_id=subscription_id).first()
        if user:
            user.subscription_status = 'expired'
            user.subscription_plan = 'trial'
            user.set_enabled_sources(TRIAL_SOURCES)
            db.session.commit()

    return jsonify({'status': 'ok'}), 200

def check_subscription_status(user):
    """Check and update user subscription status"""
    if user.subscription_end_date and user.subscription_end_date < datetime.utcnow():
        user.subscription_status = 'expired'
        user.subscription_plan = 'trial'
        user.set_enabled_sources(TRIAL_SOURCES)
        db.session.commit()
        return False
    return user.subscription_status == 'active'

def get_user_sources(user):
    """Get sources available to user based on subscription"""
    if user.subscription_plan == 'ultra' and user.subscription_status == 'active':
        return ALL_SOURCES
    elif user.is_subscribed():
        plan = SUBSCRIPTION_PLANS.get(user.subscription_plan)
        if plan and plan['sources'] != 'all':
            return plan['sources']
    return user.get_enabled_sources()

def can_use_source(user, source):
    """Check if user can use a specific source"""
    allowed_sources = get_user_sources(user)
    return source in allowed_sources

# Export the blueprint and utility functions
__all__ = ['subscription_bp', 'subscription_required', 'credits_required',
           'check_subscription_status', 'get_user_sources', 'can_use_source',
           'SUBSCRIPTION_PLANS', 'ALL_SOURCES', 'TRIAL_SOURCES']
