from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, create_model, Field, computed_field, validator
# Correctly import the specific field instance types
import tortoise
from tortoise.fields.relational import ForeignKeyFieldInstance, ManyToManyFieldInstance
from typing import List, Type, Dict, Any, Optional, Union
# NOTE: This file is kept for backward compatibility
# The main package is in rabbit_admin/ directory
# Import models are removed - users should register their own models
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .decor import log_decor
import asyncio


BASE_ADMIN_URL = "/api/admin"


class FieldSchema(BaseModel):
    name: str
    type: str

class ForeignFieldSchema(FieldSchema):
    fk: str
    model: Optional[Type[tortoise.Model]] = Field(default=None, exclude=True)





class ModelSchema(BaseModel):
    name: str
    fields: List[FieldSchema|ForeignFieldSchema]
    model:Optional[Type[tortoise.Model]] = Field(default=None, exclude=True)
    total_entries: int = 0

    @computed_field
    def relations(self) -> List[str]:
        return [field.name for field in self.fields if field.type in ["fk","m2m"]]

    @classmethod
    @log_decor
    async def create(cls, model: Type[BaseModel]):
        self = cls(name=model.__name__, fields=[], model=model)
        for field_name, obj in model._meta.fields_map.items():
            if not isinstance(obj, ManyToManyFieldInstance) and not isinstance(obj, ForeignKeyFieldInstance):
                self.fields.append(FieldSchema(name=field_name, type=obj.field_type.__name__))
            else:
                fk_model_name = obj.model_name.split('.')[-1]
                self.fields.append(ForeignFieldSchema(name=field_name, type="fk" if isinstance(obj, ForeignKeyFieldInstance) else "m2m", fk=fk_model_name, model=obj.related_model))
        
        # Set total_entries synchronously
        self.total_entries = await model.all().count()
        return self



class RelatedFieldSchema(BaseModel):
    id: int
    title: str

class ForeignFieldSchemaForm(ForeignFieldSchema):
    choices : Optional[list[RelatedFieldSchema]] 
    selected : Optional[list[RelatedFieldSchema]|RelatedFieldSchema] 
    class Config:
        exclude_fields = ["type","fk","model","choices","selected"]


class FieldSchemaForm(FieldSchema):
    data:Optional[Any] = None


class FieldSchemaFormIn(FieldSchemaForm):
    data:Any
    class Config:
        exclude_fields = ["type"]


class ForeignFieldSchemaFormIn(ForeignFieldSchemaForm):
    selected : Optional[list[int]|int] = Field(default=None)

    class Config:
        exclude_fields = ["type","fk","model","choices"]


# Custom field type that can handle both regular and foreign fields
class DynamicFieldSchemaFormIn(BaseModel):
    name: str
    data: Optional[Any] = None
    selected: Optional[Union[list[int], int]] = None


class ModelSchemaForm(BaseModel):
    name: str
    fields: List[FieldSchemaForm|ForeignFieldSchemaForm]
    model:Optional[Type[tortoise.Model]] = Field(default=None, exclude=True)
    class Config:
        exclude_fields = ["model"]

    @classmethod
    @log_decor
    async def create(cls, model: Type[BaseModel]):
        self = cls(name=model.__name__, fields=[], model=model)
        for field_name, obj in model._meta.fields_map.items():
            if not isinstance(obj, ManyToManyFieldInstance) and not isinstance(obj, ForeignKeyFieldInstance):
                self.fields.append(FieldSchemaForm(name=field_name, type=obj.field_type.__name__))
            else:
                fk_model_name = obj.model_name.split('.')[-1]
                try:
                    # Check if related_model exists and is accessible
                    if hasattr(obj, 'related_model') and obj.related_model is not None:
                        data = await obj.related_model.all()
                        self.fields.append(ForeignFieldSchemaForm(
                            name=field_name, 
                            type="fk" if isinstance(obj, ForeignKeyFieldInstance) else "m2m", 
                            fk=fk_model_name, 
                            choices=[RelatedFieldSchema(id=item.id, title=str(item)) for item in data], 
                            selected=None
                        ))
                    else:
                        # If related_model is not accessible, create an empty choices list
                        self.fields.append(ForeignFieldSchemaForm(
                            name=field_name, 
                            type="fk" if isinstance(obj, ForeignKeyFieldInstance) else "m2m", 
                            fk=fk_model_name, 
                            choices=[], 
                            selected=None
                        ))
                except Exception as e:
                    print(f"Error processing field {field_name}: {e}")
                    # Create field with empty choices if there's an error
                    self.fields.append(ForeignFieldSchemaForm(
                        name=field_name, 
                        type="fk" if isinstance(obj, ForeignKeyFieldInstance) else "m2m", 
                        fk=fk_model_name, 
                        choices=[], 
                        selected=None
                    ))
        return self




    @classmethod
    @log_decor
    async def get_item(cls, schema_obj: ModelSchema, pk: int):
        item = await schema_obj.model.get(id=pk).prefetch_related(*set(schema_obj.relations))
        self = cls(name=schema_obj.name, fields=[], model=schema_obj.model)
        return await self.load_item(item, schema_obj.fields)

    
    @log_decor
    async def load_item(self, item: tortoise.Model, field_schemas: List[FieldSchema|ForeignFieldSchema]):
        fields = []
        for field_schema in field_schemas:
            match(field_schema.type):
                case "fk":
                    related_obj = getattr(item, field_schema.name)
                    field_obj = self.model._meta.fields_map.get(field_schema.name)
                    all_choices = await field_obj.related_model.all()
                    choices = [RelatedFieldSchema(id=obj.id, title=str(obj)) for obj in all_choices]
                    if isinstance(field_obj, ForeignKeyFieldInstance):
                        field = ForeignFieldSchemaForm(
                            name=field_schema.name, 
                            type="fk", 
                            fk=field_schema.fk,
                            choices = choices,
                            selected=[RelatedFieldSchema(id=related_obj.id, title=str(related_obj))] if related_obj else None
                        )
                case "m2m":
                    related_objs = getattr(item, field_schema.name)
                    selection = [RelatedFieldSchema(id=obj.id, title=str(obj)) for obj in related_objs]
                    field_obj = self.model._meta.fields_map.get(field_schema.name)
                    if isinstance(field_obj, ManyToManyFieldInstance):
                        all_choices = await field_obj.related_model.all()
                        choices = [RelatedFieldSchema(id=obj.id, title=str(obj)) for obj in all_choices]
                        field = ForeignFieldSchemaForm(
                            name=field_schema.name, 
                            type="m2m", 
                            fk=field_schema.fk,
                            choices=choices,
                            selected=selection
                        )
                case _:
                    field = FieldSchemaForm(
                        name=field_schema.name,
                        type=field_schema.type,
                        data=getattr(item, field_schema.name, None)
                    )
            fields.append(field)
        self.fields = fields
        return self


    @classmethod
    @log_decor
    async def get_items(cls, schema_obj: ModelSchema, item_pks :list[int] | None = None):
        if item_pks is None:
            items = await schema_obj.model.all()
        else:
            items = await schema_obj.model.filter(id__in=item_pks).all()
        res = []
        for item in items:
            # Fetch related data for each item
            await item.prefetch_related(*set(schema_obj.relations))
            self = cls(name=schema_obj.name, fields=[], model=schema_obj.model)
            res.append(await self.load_item(item, schema_obj.fields))
        return res
        



class ModelSchemaFormIn(BaseModel):
    name: str
    fields: List[DynamicFieldSchemaFormIn]
    model:Optional[Type[tortoise.Model]] = None
    class Config:
        exclude_fields = ["model"]

    @log_decor
    async def create_model(self):
        new_obj = self.model()
        m2m_fields, non_m2m_fields = [], []
        
        # Properly identify m2m fields by checking the model's field type
        for field in self.fields:
            model_field = self.model._meta.fields_map.get(field.name)
            if model_field and isinstance(model_field, ManyToManyFieldInstance):
                m2m_fields.append(field)
            else:
                non_m2m_fields.append(field)
        
        # First, set non-m2m fields and save the object
        for field in non_m2m_fields:
            await self._add_field(field, new_obj)
        await new_obj.save()
        
        # Then, handle m2m fields (which require the object to be saved first)
        for field in m2m_fields:
            await self._add_field(field, new_obj)
        await new_obj.save()
        return new_obj

    @log_decor
    async def update_model(self, pk: int):
        obj = await self.model.get(id=pk)
        await self._update_model(obj)
        return obj
    
    @log_decor
    async def _update_model(self, obj: tortoise.Model):
        m2m_fields, non_m2m_fields = [], []
        
        # Properly identify m2m fields by checking the model's field type
        for field in self.fields:
            model_field = self.model._meta.fields_map.get(field.name)
            if model_field and isinstance(model_field, ManyToManyFieldInstance):
                m2m_fields.append(field)
            else:
                non_m2m_fields.append(field)
        
        # First, update non-m2m fields and save the object
        for field in non_m2m_fields:
            await self._add_field(field, obj)
        await obj.save()
        
        # Then, handle m2m fields
        for field in m2m_fields:
            await self._add_field(field, obj)
        await obj.save()
        return obj

    
    @staticmethod
    @log_decor
    async def _add_field(field: DynamicFieldSchemaFormIn, model_obj: tortoise.Model):
        try:
            # Skip the id field as it's auto-generated
            if field.name == 'id':
                return
                
            # Check if this is a foreign key or many-to-many field by looking at the model's field definition
            model_field = model_obj._meta.fields_map.get(field.name)
            
            if model_field and (isinstance(model_field, ForeignKeyFieldInstance) or isinstance(model_field, ManyToManyFieldInstance)):
                # This is a foreign field
                if isinstance(model_field, ForeignKeyFieldInstance):
                    # Foreign key field
                    if field.selected is not None:
                        related_obj = await model_field.related_model.get(id=field.selected)
                        setattr(model_obj, field.name, related_obj)
                elif isinstance(model_field, ManyToManyFieldInstance):
                    # Many-to-many field
                    if field.selected is not None:
                        if isinstance(field.selected, list):
                            related_objs = await model_field.related_model.filter(id__in=field.selected)
                        else:
                            related_objs = await model_field.related_model.filter(id=field.selected)
                        m2m_manager = getattr(model_obj, field.name)
                        await m2m_manager.clear()
                        for related_obj in related_objs:
                            await m2m_manager.add(related_obj)
            else:
                # Regular field
                if field.data is not None:
                    setattr(model_obj, field.name, field.data)
        except Exception as e:
            print(f"Error in _add_field for field {field.name}: {e}")
            raise e





    # async def _get_add_form_data(self, model_schema:ModelSchema):
        



class ModelManager:
    def __init__(self, model: Type[tortoise.Model]):
        self.model = model
        self.name = None
        self.schema = None
        self.schema_form = None
        
    
    async def load(self, full=False):
        await self.get_schema()
        if full:
            await self.get_schema_form()
        
    @log_decor
    async def get_schema(self):
        self.schema = await ModelSchema.create(self.model)
        self.name = self.schema.name
        return self.schema

    @log_decor
    async def get_schema_form(self):
        self.schema_form = await ModelSchemaForm.create(self.model)
        return self.schema_form

    @log_decor
    async def get_item(self, pk: int):
        return await ModelSchemaForm.get_item(self.schema, pk)
    

    @log_decor
    async def get_items(self, item_pks: list[int] | None = None):
        return await ModelSchemaForm.get_items(self.schema, item_pks)


    @log_decor
    async def create_item(self, item: ModelSchemaFormIn):
        item.model = self.model
        created_obj = await item.create_model()
        # Convert the created object back to a ModelSchemaForm
        return await self.get_item(created_obj.id)
    
    @log_decor
    async def update_item(self, pk: int, item: ModelSchemaFormIn):
        item.model = self.model
        updated_obj = await item.update_model(pk)
        # Convert the updated object back to a ModelSchemaForm
        return await self.get_item(updated_obj.id)
    

    @log_decor
    async def delete_items(self, item_ids: list[int]) -> list[dict]:
        deletion_statuses = await asyncio.gather(*[self.delete_item(item_id) for item_id in item_ids])
        return deletion_statuses


    @log_decor    
    async def delete_item(self, pk: int):
        try:
            obj = await self.model.get(id=pk)
            await obj.delete()
            return {"id": pk, "status": "success"}
        except Exception as e:
            return {"id": pk, "status": "error", "error": str(e)}



class ModelSummary(BaseModel):
    schemas: List[ModelSchema]

    @computed_field
    def endpoints(self) -> dict:
        return {
            "list": f"{BASE_ADMIN_URL}/(model_name)/list",
            "create": f"{BASE_ADMIN_URL}/(model_name)",
            "get": f"{BASE_ADMIN_URL}/(model_name)/{{item_id}}",
            "update": f"{BASE_ADMIN_URL}/(model_name)/{{item_id}}",
            "delete": f"{BASE_ADMIN_URL}/(model_name)",
            "form": f"{BASE_ADMIN_URL}/(model_name)/form"
        }
    
    @computed_field
    def total_entries(self) -> int:
        return len(self.schemas)

class AdminRegistry:
    def __init__(self,base_url=BASE_ADMIN_URL):
        self.models: Dict[str, Dict[str, Any]] = {}
        self.router = APIRouter(prefix=base_url)

    async def _tortoise_to_dict(self, instance: Type[BaseModel], model_name: str) -> Dict[str, Any]:
        """
        Converts a Tortoise ORM instance to a dictionary that matches our custom schema,
        handling FK and M2M relationships.
        """
        model_config = self.models[model_name]
        model_cls = model_config["model"]
        result = {}

        # Ensure M2M fields are fetched
        await instance.prefetch_related(*model_config["m2m_fields"])

        for field_name in model_config["schema"].__fields__.keys():
            field_obj = model_cls._meta.fields_map.get(field_name)
            
            # Use the correct type for the isinstance check
            if isinstance(field_obj, ForeignKeyFieldInstance):
                related_obj = getattr(instance, field_name)
                # Ensure the related object is fetched
                if related_obj and not getattr(related_obj, '_fetched', True):
                    await related_obj.fetch()
                
                if related_obj:
                    result[field_name] = {"id": related_obj.id, "title": str(related_obj)}
                else:
                    result[field_name] = None
            # Use the correct type for the isinstance check
            elif isinstance(field_obj, ManyToManyFieldInstance):
                related_manager = getattr(instance, field_name)
                result[field_name] = [
                    {"id": obj.id, "title": str(obj)} for obj in related_manager
                ]
            else:
                result[field_name] = getattr(instance, field_name)
        return result

    @log_decor
    async def register(self, model: Type[BaseModel]):
        """
        Registers a Tortoise ORM model with the admin interface.
        This method creates custom Pydantic schemas and generates CRUD API routes.
        """
        model_manager = ModelManager(model)
        await model_manager.load(full=True)
        model_name = model_manager.name
        self.models[model_name] = model_manager

        # --- Dynamically create API routes for the model ---
        




        # async def 

        # Define the route handler
        # s
        @log_decor
        async def get_all_items():
            items = await model.all()
            return [await model_manager.get_item(item.id) for item in items]
        
        @log_decor
        async def create_item(item: ModelSchemaFormIn):
            return await model_manager.create_item(item)

        @log_decor
        async def get_item(item_id: int):
            return await model_manager.get_item(item_id)

        @log_decor
        async def update_item(item_id: int, item: ModelSchemaFormIn):
            return await model_manager.update_item(item_id, item)

        @log_decor
        async def delete_items(item_ids: list[int]) -> list[dict]:
            deletion_statuses = await model_manager.delete_items(item_ids)
            return deletion_statuses


        @log_decor
        async def get_schema_form():
            return await model_manager.get_schema_form()

        # Add routes to the router using add_api_route
        # IMPORTANT: Order matters! More specific routes must come before more general ones
        self.router.add_api_route(
            f"/{model_name}/list",
            get_all_items,
            methods=["GET"],
            response_model=List[ModelSchemaForm],
            tags=[model.__name__]
        )
        
        self.router.add_api_route(
            f"/{model_name}/form",
            get_schema_form,
            methods=["GET"],
            response_model=ModelSchemaForm,
            tags=[model.__name__]
        )
        
        self.router.add_api_route(
            f"/{model_name}",
            create_item,
            methods=["POST"],
            response_model=ModelSchemaForm,
            tags=[model.__name__]
        )

        self.router.add_api_route(
            f"/{model_name}/{{item_id}}",
            get_item,
            methods=["GET"],
            response_model=ModelSchemaForm,
            tags=[model.__name__]
        )

        self.router.add_api_route(
            f"/{model_name}/{{item_id}}",
            update_item,
            methods=["PUT"],
            response_model=ModelSchemaForm,
            tags=[model.__name__]
        )

        self.router.add_api_route(
            f"/{model_name}",
            delete_items,
            methods=["DELETE"],
            response_model=List[dict],
            tags=[model.__name__]
        )






    @log_decor
    async def get_registered_models_info(self):
        """
        Provides detailed schema information about registered models for the frontend.
        """
        schemas = []
        for model_name, model_manager in self.models.items():
            schema = await model_manager.get_schema()
            schemas.append(schema)
        summary = ModelSummary(schemas=schemas)
        return summary  
# Create a global admin instance
admin_app = AdminRegistry(base_url=BASE_ADMIN_URL)

# Add routes for admin metadata
@admin_app.router.get("/_models", tags=["Admin"])
async def get_registered_models():
    """
    Endpoint to provide the frontend with a detailed schema of all registered models.
    """
    return await admin_app.get_registered_models_info()


# Get the absolute path to the static directory within the package
static_dir = Path(__file__).parent / "static"
admin_app.router.mount("/dash", StaticFiles(directory=str(static_dir), html=True), name="static")
