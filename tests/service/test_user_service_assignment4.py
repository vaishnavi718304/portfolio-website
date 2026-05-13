import pytest

from app.models import User
from app.service.user_service import (
    UnsupportedUserOperationError,
    create_user,
    delete_user,
    get_all_users,
    get_user_by_username,
    update_user_balance,
)


def test_get_user_by_username_returns_user(db_session):
    user = User(
        username='alice',
        password='secret',
        firstname='Alice',
        lastname='Doe',
        balance=100.0,
    )
    db_session.add(user)
    db_session.commit()

    found = get_user_by_username('alice')

    assert found is not None
    assert found.username == 'alice'


def test_get_user_by_username_raises_for_empty_username(db_session):
    with pytest.raises(UnsupportedUserOperationError) as exc:
        get_user_by_username('')

    assert 'Username cannot be empty' in str(exc.value)


def test_get_all_users_returns_seeded_admin(db_session):
    users = get_all_users()
    usernames = [user.username for user in users]

    assert 'admin' in usernames


def test_create_user_persists_user(db_session):
    create_user(
        username='new_user',
        password='secret',
        firstname='New',
        lastname='User',
        balance=250.0,
    )
    db_session.commit()

    created = db_session.query(User).filter_by(username='new_user').one()
    assert created.firstname == 'New'
    assert created.balance == 250.0


def test_update_user_balance_updates_existing_user(db_session):
    user = User(
        username='balance_user',
        password='secret',
        firstname='Balance',
        lastname='User',
        balance=100.0,
    )
    db_session.add(user)
    db_session.commit()

    update_user_balance('balance_user', 999.0)
    db_session.commit()

    refreshed = db_session.query(User).filter_by(username='balance_user').one()
    assert refreshed.balance == 999.0


def test_update_user_balance_raises_for_missing_user(db_session):
    with pytest.raises(UnsupportedUserOperationError) as exc:
        update_user_balance('missing_user', 500.0)

    assert 'does not exist' in str(exc.value)


def test_delete_user_removes_existing_user(db_session):
    user = User(
        username='delete_me',
        password='secret',
        firstname='Delete',
        lastname='Me',
        balance=100.0,
    )
    db_session.add(user)
    db_session.commit()

    delete_user('delete_me')
    db_session.commit()

    deleted = db_session.query(User).filter_by(username='delete_me').one_or_none()
    assert deleted is None


def test_delete_user_rejects_admin(db_session):
    with pytest.raises(UnsupportedUserOperationError) as exc:
        delete_user('admin')

    assert 'Cannot delete admin user' in str(exc.value)


def test_delete_user_rejects_empty_username(db_session):
    with pytest.raises(UnsupportedUserOperationError) as exc:
        delete_user('')

    assert 'Username cannot be empty' in str(exc.value)


def test_delete_user_raises_for_missing_user(db_session):
    with pytest.raises(UnsupportedUserOperationError) as exc:
        delete_user('ghost')

    assert 'does not exist' in str(exc.value)