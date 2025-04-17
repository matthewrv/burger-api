from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

from db.user import User
from tests.conftest import SampleUser


def test_register(client: TestClient, session: Session, test_user: SampleUser):
    with session.begin():
        session.exec(delete(User))
        result = session.exec(select(User)).all()
        assert len(result) == 0, f"Expected no users in db, but got {len(result)}"

    response = client.post('/api/auth/register', json={
        'name': test_user.name,
        'email': test_user.email,
        'password': test_user.password,
    })
    assert response.status_code == 200

    with session.begin():
        users = session.exec(select(User)).all()
        
        assert len(users) == 1

        user = users[0]
        assert user.email == test_user.email
        assert user.name == test_user.name

    # assert user can login after registration
    response = client.post('/api/auth/login', json={'email': test_user.email, 'password': test_user.password})
    assert response.status_code == 200
    response_body = response.json()
    assert 'user' in response_body
    assert response_body['user'] == {
        'email': test_user.email,
        'name': test_user.name,
    }
