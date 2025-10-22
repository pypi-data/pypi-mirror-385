from src.auth.factories import UserFactory
from src.auth.services import provide_auth_service


async def test_get_users(db_session, test_client):
    auth_service = provide_auth_service(db_session)
    await auth_service.create_many(
        [UserFactory.build() for _ in range(10)], auto_commit=True
    )

    response_json = (await test_client.get("/api/auth/users")).json()
    assert response_json["total"] == 10
