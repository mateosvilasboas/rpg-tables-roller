from pydantic import BaseModel, model_serializer

class ExampleBaseSchema(BaseModel):
    name: str
    address: str
    email: str

    class Config:
        from_attributes = True

class ExampleGetSchema(ExampleBaseSchema):
    id: int 
    
    @model_serializer(when_used='json')
    def sort_model(self):
        return dict([('id', self.id), 
                     ('name', self.name),
                     ('email', self.email),
                     ('address', self.address)])