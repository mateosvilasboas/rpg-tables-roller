from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSON as pgJSON
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

from .utils.mixins import BaseMixins


class Base(DeclarativeBase, MappedAsDataclass, BaseMixins):
    pass


class User(Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]
    password: Mapped[str]
    frameworks: Mapped[list['Framework']] = relationship(
        init=False, lazy='selectin'
    )

    id: Mapped[int] = mapped_column(init=False, primary_key=True, index=True)


class Framework(Base):
    __tablename__ = 'frameworks'

    name: Mapped[str]
    entries: Mapped[dict] = mapped_column(
        pgJSON, init=False, server_default='{}'
    )
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    id: Mapped[int] = mapped_column(init=False, primary_key=True, index=True)
