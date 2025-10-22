from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from .models import UserModel


class AuthService(SQLAlchemyAsyncRepositoryService):
    class Repository(SQLAlchemyAsyncRepository[UserModel]):
        model_type = UserModel

    repository_type = Repository


def provide_auth_service(db_session) -> AuthService:
    return AuthService(session=db_session)
