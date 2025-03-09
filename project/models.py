from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

class Base(DeclarativeBase):
    pass

class Example(Base):
    __tablename__ = "examples"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    address: Mapped[str]
    email: Mapped[str]
