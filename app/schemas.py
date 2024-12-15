from pydantic import BaseModel, model_serializer

class ExampleBaseSchema(BaseModel):
    name: str

    class Config:
        orm_mode = True

class ExampleGetSchema(ExampleBaseSchema):
    id: int

    @model_serializer(when_used='json')
    def sort_model(self):
        return dict([('id', self.id), 
                     ('name', self.name)])