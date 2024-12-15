from sqlalchemy.orm import mapped_column, Mapped
from .database import Base

class Example(Base):
    __tablename__ = "example"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
