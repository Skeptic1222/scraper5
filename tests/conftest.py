"""
Shared pytest fixtures for bulk download tests
Provides reusable test setup and teardown
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Asset, MediaBlob, Role, User, UserRole, db


@pytest.fixture(scope="session")
def app():
    """
    Create and configure Flask application for testing
    Uses in-memory SQLite database for speed
    """
    # Import here to avoid circular imports
    from app import create_app

    # Create app with test configuration
    app = create_app()

    # Override configuration for testing
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key-for-testing-only",
        "SERVER_NAME": "localhost",
        "APPLICATION_ROOT": "/scraper",
        "PREFERRED_URL_SCHEME": "http",
    })

    # Setup app context
    with app.app_context():
        # Create all tables
        db.create_all()

        # Initialize with default roles
        _create_default_roles()

        yield app

        # Cleanup
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def test_client(app):
    """
    Create Flask test client for making requests
    Function scope ensures fresh client for each test
    """
    return app.test_client()


@pytest.fixture(scope="function")
def test_user(app):
    """
    Create a test user for authentication
    Cleaned up after each test
    """
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(email="test@example.com").first()

        if not user:
            user = User(
                google_id="test_user_12345",
                email="test@example.com",
                name="Test User",
                credits=1000,
                subscription_plan="pro",
                subscription_status="active"
            )
            db.session.add(user)

            # Assign user role
            user_role = Role.query.filter_by(name="user").first()
            if user_role:
                db.session.add(UserRole(user_id=user.id, role_id=user_role.id))

            db.session.commit()

        yield user

        # Cleanup is handled by transaction rollback


@pytest.fixture(scope="function")
def admin_user(app):
    """
    Create an admin user for permission testing
    """
    with app.app_context():
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        user = User.query.filter_by(email=admin_email).first()

        if not user:
            user = User(
                google_id="admin_user_12345",
                email=admin_email,
                name="Admin User",
                credits=9999,
                subscription_plan="ultra",
                subscription_status="active"
            )
            db.session.add(user)

            # Assign admin role
            admin_role = Role.query.filter_by(name="admin").first()
            if admin_role:
                db.session.add(UserRole(user_id=user.id, role_id=admin_role.id))

            db.session.commit()

        yield user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """
    Create authentication headers for API requests
    """
    return {
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="function")
def authenticated_client(test_client, test_user):
    """
    Create authenticated test client with session
    """
    with test_client.session_transaction() as sess:
        sess['user_id'] = test_user.id
        sess['_fresh'] = True

    return test_client


@pytest.fixture
def tmp_path():
    """
    Create temporary directory for file operations
    Cleaned up automatically after test
    """
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir

    # Cleanup
    for file in temp_dir.glob("*"):
        try:
            file.unlink()
        except:
            pass

    try:
        temp_dir.rmdir()
    except:
        pass


@pytest.fixture(scope="function")
def sample_asset(test_user, app):
    """
    Create a single sample asset with MediaBlob
    """
    with app.app_context():
        asset = Asset(
            user_id=test_user.id,
            filename="sample_asset.jpg",
            file_path="/fake/path/sample_asset.jpg",
            file_type="image",
            file_size=1024 * 50,  # 50 KB
            file_extension=".jpg",
            source_name="test_source",
            source_url="https://example.com/sample.jpg",
            width=1024,
            height=768,
            stored_in_db=True
        )
        db.session.add(asset)
        db.session.flush()

        # Create MediaBlob
        fake_data = b"FAKE_IMAGE_DATA" * 100
        blob = MediaBlob(
            asset_id=asset.id,
            user_id=test_user.id,
            media_data=fake_data,
            mime_type="image/jpeg",
            file_hash="sample_hash_123"
        )
        db.session.add(blob)
        db.session.commit()

        yield asset

        # Cleanup handled by transaction


def _create_default_roles():
    """
    Create default roles for testing
    Internal helper function
    """
    import json

    roles_data = [
        {
            "name": "admin",
            "description": "Administrator",
            "permissions": ["admin_access", "manage_users", "delete_assets", "view_all_assets"]
        },
        {
            "name": "user",
            "description": "Standard User",
            "permissions": ["delete_own_assets", "view_own_assets"]
        },
        {
            "name": "guest",
            "description": "Guest User",
            "permissions": ["view_public_assets"]
        }
    ]

    for role_data in roles_data:
        existing = Role.query.filter_by(name=role_data["name"]).first()
        if not existing:
            role = Role(
                name=role_data["name"],
                description=role_data["description"],
                permissions=json.dumps(role_data["permissions"])
            )
            db.session.add(role)

    db.session.commit()


# Pytest configuration
def pytest_configure(config):
    """
    Configure pytest with custom markers
    """
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end browser test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


# Async fixtures for Playwright tests
@pytest.fixture(scope="session")
def browser_context_args():
    """
    Configure browser context for Playwright
    """
    return {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "locale": "en-US",
        "timezone_id": "America/New_York",
    }


@pytest.fixture(scope="function")
async def playwright_page(playwright):
    """
    Create Playwright page for E2E tests
    """
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        accept_downloads=True
    )
    page = await context.new_page()

    yield page

    await page.close()
    await context.close()
    await browser.close()
