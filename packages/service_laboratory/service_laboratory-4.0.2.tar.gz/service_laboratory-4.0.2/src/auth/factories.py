from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.fields import Use

from .models import UserModel

faker = Faker()



class UserFactory(SQLAlchemyFactory[UserModel]):
    email = Use(faker.email)
