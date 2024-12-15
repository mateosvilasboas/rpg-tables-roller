#write get and post router for models.py
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .models import Example as ExampleModel
from .schemas import (ExampleBaseSchema,
                      ExampleGetSchema)

router = APIRouter(
    prefix="/example",
    tags=["example"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[ExampleGetSchema])
async def get_examples(db: AsyncSession = Depends(get_db)):
    print (await db.scalars(select(ExampleModel)))
    return await db.scalars(select(ExampleModel))

@router.post("/", response_model=ExampleGetSchema)
async def create_example(example: ExampleBaseSchema, db: AsyncSession = Depends(get_db)):
    db_example = ExampleModel(name=example.name)
    db.add(db_example)
    await db.commit()
    await db.refresh(db_example)
    return db_example