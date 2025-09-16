"""
Database utility functions for better transaction management and error handling
"""

import logging
import time
from functools import wraps

from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm.exc import StaleDataError

logger = logging.getLogger(__name__)

def with_transaction(retries=3, delay=0.5):
    """
    Decorator for database operations with automatic transaction management.
    Provides retry logic for transient failures and proper rollback on errors.

    Args:
        retries: Number of retry attempts for transient failures
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from app import db

            last_error = None
            for attempt in range(retries):
                try:
                    # Start a new transaction if not already in one
                    if not db.session.is_active:
                        db.session.begin()

                    # Execute the function
                    result = func(*args, **kwargs)

                    # Commit the transaction
                    db.session.commit()
                    return result

                except IntegrityError as e:
                    # Integrity errors should not be retried
                    db.session.rollback()
                    logger.error(f"Database integrity error in {func.__name__}: {str(e)}")
                    raise

                except OperationalError as e:
                    # Operational errors might be transient (deadlocks, timeouts)
                    db.session.rollback()
                    last_error = e
                    logger.warning(f"Database operational error in {func.__name__} (attempt {attempt + 1}/{retries}): {str(e)}")

                    if attempt < retries - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        raise

                except StaleDataError as e:
                    # Stale data errors indicate concurrent modifications
                    db.session.rollback()
                    last_error = e
                    logger.warning(f"Stale data error in {func.__name__}: {str(e)}")

                    if attempt < retries - 1:
                        time.sleep(delay)
                        continue
                    else:
                        raise

                except SQLAlchemyError as e:
                    # Generic SQLAlchemy errors
                    db.session.rollback()
                    logger.error(f"Database error in {func.__name__}: {str(e)}")
                    raise

                except Exception as e:
                    # Non-database errors should still trigger rollback
                    db.session.rollback()
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                    raise

            # If we get here, all retries failed
            if last_error:
                raise last_error

        return wrapper
    return decorator


def safe_commit():
    """
    Safely commit the current transaction with error handling.
    Returns True if successful, False otherwise.
    """
    from app import db

    try:
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Failed to commit transaction: {str(e)}")
        return False


def safe_bulk_insert(objects, batch_size=100):
    """
    Safely insert multiple objects in batches with error handling.

    Args:
        objects: List of SQLAlchemy model instances to insert
        batch_size: Number of objects to insert per batch

    Returns:
        Tuple of (successful_count, failed_count)
    """
    from app import db

    successful = 0
    failed = 0

    for i in range(0, len(objects), batch_size):
        batch = objects[i:i + batch_size]
        try:
            db.session.bulk_save_objects(batch)
            db.session.commit()
            successful += len(batch)
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Failed to insert batch {i//batch_size + 1}: {str(e)}")
            failed += len(batch)

    return successful, failed


def cleanup_old_records(model_class, date_field, days_to_keep=30, batch_size=1000):
    """
    Clean up old records from a table in batches.

    Args:
        model_class: SQLAlchemy model class
        date_field: Name of the date field to filter on
        days_to_keep: Number of days of records to keep
        batch_size: Number of records to delete per batch

    Returns:
        Total number of records deleted
    """
    from datetime import datetime, timedelta

    from app import db

    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    total_deleted = 0

    while True:
        try:
            # Find old records
            old_records = model_class.query.filter(
                getattr(model_class, date_field) < cutoff_date
            ).limit(batch_size).all()

            if not old_records:
                break

            # Delete in batch
            for record in old_records:
                db.session.delete(record)

            db.session.commit()
            total_deleted += len(old_records)

            logger.info(f"Deleted {len(old_records)} old records from {model_class.__tablename__}")

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error cleaning up old records: {str(e)}")
            break

    return total_deleted


def get_or_create(model_class, defaults=None, **kwargs):
    """
    Get an existing record or create a new one.

    Args:
        model_class: SQLAlchemy model class
        defaults: Dictionary of default values for creation
        **kwargs: Fields to filter by

    Returns:
        Tuple of (instance, created) where created is True if a new record was created
    """
    from app import db

    instance = model_class.query.filter_by(**kwargs).first()
    if instance:
        return instance, False

    # Create new instance
    params = dict((k, v) for k, v in kwargs.items())
    if defaults:
        params.update(defaults)

    instance = model_class(**params)
    db.session.add(instance)

    try:
        db.session.commit()
        return instance, True
    except IntegrityError:
        # Another process may have created the record
        db.session.rollback()
        instance = model_class.query.filter_by(**kwargs).first()
        return instance, False


def update_or_create(model_class, defaults=None, **kwargs):
    """
    Update an existing record or create a new one.

    Args:
        model_class: SQLAlchemy model class
        defaults: Dictionary of values to update/create with
        **kwargs: Fields to filter by

    Returns:
        Tuple of (instance, created) where created is True if a new record was created
    """
    from app import db

    instance = model_class.query.filter_by(**kwargs).first()
    if instance:
        # Update existing
        if defaults:
            for key, value in defaults.items():
                setattr(instance, key, value)
        try:
            db.session.commit()
            return instance, False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise
    else:
        # Create new
        return get_or_create(model_class, defaults, **kwargs)
