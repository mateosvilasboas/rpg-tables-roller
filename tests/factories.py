import factory

from project.models import Framework, User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    name = factory.Sequence(lambda n: f'teste{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.name}@teste.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.name}@example.com')


class FrameworkFactory(factory.Factory):
    class Meta:
        model = Framework

    name = factory.Faker('text')
    user_id = None
