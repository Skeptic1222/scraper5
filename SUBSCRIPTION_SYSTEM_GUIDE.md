# 🎯 Subscription System Implementation Guide

## Overview

This guide documents the complete PayPal Advanced Checkout subscription system implementation for the Enhanced Media Scraper web application. The system includes free trials, multiple subscription tiers, source restrictions, watermark overlays, and visual upsell mechanics.

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Database Schema](#database-schema)
3. [Subscription Tiers](#subscription-tiers)
4. [Key Features](#key-features)
5. [Setup Instructions](#setup-instructions)
6. [API Endpoints](#api-endpoints)
7. [UI Components](#ui-components)
8. [Testing Guide](#testing-guide)

## 🏗️ System Architecture

### Components

1. **Subscription Module** (`subscription.py`)
   - PayPal integration
   - Plan management
   - Subscription decorators
   - Webhook handling

2. **Watermark Module** (`watermark.py`)
   - Image watermarking
   - Video watermarking
   - CSS/HTML overlays

3. **Database Models** (Updated `models.py`)
   - User subscription fields
   - Credit tracking
   - Source restrictions

4. **Frontend Integration** (Updated `index.html`)
   - Subscription status display
   - Source locking UI
   - Credit tracking

## 💾 Database Schema

### User Table Additions

```sql
-- New columns added to users table
ALTER TABLE users ADD credits INT DEFAULT 50;
ALTER TABLE users ADD subscription_plan VARCHAR(50) DEFAULT 'trial';
ALTER TABLE users ADD subscription_status VARCHAR(50) DEFAULT 'active';
ALTER TABLE users ADD is_nsfw_enabled BIT DEFAULT 0;
ALTER TABLE users ADD paypal_subscription_id VARCHAR(255);
ALTER TABLE users ADD subscription_start_date DATETIME;
ALTER TABLE users ADD subscription_end_date DATETIME;
ALTER TABLE users ADD sources_enabled TEXT;
```

Run the migration script:
```bash
python migrate_subscription_fields.py
```

## 💳 Subscription Tiers

| Plan  | Monthly | Yearly (Discount) | Features |
|-------|---------|-------------------|----------|
| Trial | Free    | -                 | 50 credits, 4 sources, watermarks |
| Basic | $4.99   | $41.90 (30% off)  | 2TB, 7 sources, no watermarks |
| Pro   | $14.99  | $125.90 (30% off) | 10TB, 14 sources, API access |
| Ultra | $29.99  | $215.90 (40% off) | Unlimited, all sources, NSFW |

### Available Sources by Tier

- **Trial**: Reddit, Imgur, Wikimedia, DeviantArt
- **Basic**: Trial + Pixabay, Unsplash, Pexels
- **Pro**: Basic + Facebook, Instagram, Twitter, TikTok, YouTube, Vimeo
- **Ultra**: All sources including NSFW content

## 🌟 Key Features

### 1. Free Trial System
- New users receive 50 free credits
- Credits are consumed per search
- Trial notice displayed in navbar
- Automatic upgrade prompts when credits depleted

### 2. Source Restrictions
- Sources locked based on subscription tier
- Visual lock indicators on disabled sources
- Tooltips explaining upgrade requirements
- Backend enforcement of source access

### 3. Watermark System
- Diagonal watermark overlay on trial content
- CSS-based implementation for web display
- PIL-based implementation for downloaded files
- Automatic removal for subscribed users

### 4. NSFW Toggle
- Restricted to Ultra plan only
- Safe Search forced on for non-Ultra users
- Visual indicator when restricted
- Backend enforcement

### 5. PayPal Integration
- Advanced Checkout implementation
- Webhook support for subscription events
- Automatic plan activation
- Cancellation handling

## 🚀 Setup Instructions

### 1. Environment Configuration

Add to your `.env` file:

```env
# PayPal Configuration (SANDBOX)
PAYPAL_CLIENT_ID=AYmGjmBj0UNF-ddYrTyEjtusaq1I4tgS1WcmTvxyNXrauc3DZJdBGR4P7FcikJu_kDiNpUXEVRaAnKpO
PAYPAL_SECRET=ENab7lt1bLY_-Rentvwa78GM5twu2l3lfTY_zYuYpZ6hIffCsAx7HhhbP6GVHx9pfblK03g_SKJC1GBC
PAYPAL_MODE=sandbox  # Change to 'live' for production

# Subscription Settings
FREE_TRIAL_CREDITS=50
TRIAL_SOURCES=reddit,imgur,wikimedia,deviantart
```

### 2. Install Dependencies

```bash
pip install paypalrestsdk==1.13.1 opencv-python==4.8.1.78
```

### 3. Run Database Migration

```bash
python migrate_subscription_fields.py
```

### 4. Configure PayPal Webhooks

In PayPal Developer Dashboard, set webhook URL to:
```
https://yourdomain.com/subscription/webhook
```

Subscribe to events:
- BILLING.SUBSCRIPTION.CANCELLED
- PAYMENT.SALE.COMPLETED
- BILLING.SUBSCRIPTION.EXPIRED

### 5. Restart Application

```bash
python app.py
```

## 🔌 API Endpoints

### Subscription Management

#### Get Subscription Plans
```
GET /subscription/plans
```
Displays available subscription plans with pricing.

#### Subscribe to Plan
```
GET /subscription/subscribe/<plan_id>/<billing_cycle>
```
Initiates PayPal checkout for selected plan.

#### Account Management
```
GET /subscription/account
```
Shows user's subscription details and management options.

#### Cancel Subscription
```
GET /subscription/cancel
```
Cancels active subscription (retains access until end of period).

### User Information

#### Get User Info
```
GET /api/user-info
```
Returns current user's subscription status and details.

Response:
```json
{
  "authenticated": true,
  "user": { ... },
  "subscription": {
    "plan": "trial",
    "status": "active",
    "credits": 45,
    "is_subscribed": false,
    "can_use_nsfw": false,
    "sources_enabled": ["reddit", "imgur", "wikimedia", "deviantart"]
  }
}
```

#### Update NSFW Setting
```
POST /api/update-nsfw
```
Body:
```json
{
  "enabled": true
}
```

### Source Management

#### Get Available Sources
```
GET /api/sources?safe_search=true
```
Returns sources filtered by user's subscription and safe search setting.

Response includes:
- Source categories
- Locked status per source
- Lock reasons
- Subscription info

## 🎨 UI Components

### 1. Navbar Subscription Status

Shows trial credits or subscription badge:
```html
<div id="subscriptionStatus" class="subscription-status">
    <i class="fas fa-info-circle"></i>
    You're in free trial mode — 45 credits remaining. 
    <a href="/subscription/plans">Upgrade to unlock full access</a>
</div>
```

### 2. Source Lock Indicators

Locked sources show with visual indicators:
```css
.source-item.locked {
    opacity: 0.6;
}

.source-item.locked::after {
    content: '\f023'; /* Lock icon */
    font-family: 'Font Awesome 6 Free';
}
```

### 3. Watermark Overlay

Applied to trial user content:
```css
.watermark-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}
```

### 4. Plan Selection Cards

Beautiful pricing cards with feature lists:
- Monthly/Yearly toggle
- Savings badges
- Feature comparison
- Current plan indicator

## 🧪 Testing Guide

### 1. Test Free Trial Flow

1. Sign in with new Google account
2. Verify 50 credits displayed
3. Check only 4 sources enabled
4. Perform search (verify credit deduction)
5. View media (verify watermark)

### 2. Test Subscription Flow

1. Navigate to `/subscription/plans`
2. Select a plan and billing cycle
3. Complete PayPal sandbox payment
4. Verify plan activation
5. Check source unlocking
6. Verify watermark removal

### 3. Test Source Restrictions

1. As trial user, verify locked sources
2. Upgrade to Basic plan
3. Verify Basic sources unlocked
4. Check Pro/Ultra sources still locked
5. Attempt to use locked source (should fail)

### 4. Test NSFW Toggle

1. As non-Ultra user, verify toggle disabled
2. Upgrade to Ultra plan
3. Verify toggle enabled
4. Toggle NSFW on
5. Verify adult sources appear

### 5. Test Credit System

1. As trial user, use searches
2. Verify credit deduction
3. Use all 50 credits
4. Verify upgrade prompt
5. Check search blocking

## 🔍 Troubleshooting

### Common Issues

1. **PayPal Connection Failed**
   - Verify credentials in `.env`
   - Check PayPal mode (sandbox/live)
   - Ensure PayPal SDK installed

2. **Sources Not Locking**
   - Run database migration
   - Clear browser cache
   - Check user subscription status

3. **Watermarks Not Appearing**
   - Verify PIL/OpenCV installed
   - Check watermark CSS loaded
   - Inspect media serving endpoint

4. **Credits Not Deducting**
   - Check database connection
   - Verify user authentication
   - Review app logs

### Debug Mode

Enable debug logging:
```python
# In app.py
app.config['DEBUG'] = True

# In subscription.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Analytics & Monitoring

Track subscription metrics:

```sql
-- Active subscriptions by plan
SELECT subscription_plan, COUNT(*) as count
FROM users
WHERE subscription_status = 'active'
GROUP BY subscription_plan;

-- Credit usage
SELECT AVG(50 - credits) as avg_credits_used
FROM users
WHERE subscription_plan = 'trial';

-- Conversion rate
SELECT 
  (COUNT(CASE WHEN subscription_plan != 'trial' THEN 1 END) * 100.0 / COUNT(*)) as conversion_rate
FROM users;
```

## 🚨 Production Checklist

- [ ] Switch PayPal to production mode
- [ ] Update PayPal credentials
- [ ] Configure production webhook URL
- [ ] Enable HTTPS
- [ ] Set up payment failure notifications
- [ ] Configure subscription renewal reminders
- [ ] Implement usage analytics
- [ ] Set up customer support workflow
- [ ] Create subscription management dashboard
- [ ] Test payment flows thoroughly

## 📝 License & Support

For support or questions about the subscription system:
1. Check the troubleshooting section
2. Review PayPal documentation
3. Contact system administrator

---

**Last Updated**: December 2024
**Version**: 1.0.0 