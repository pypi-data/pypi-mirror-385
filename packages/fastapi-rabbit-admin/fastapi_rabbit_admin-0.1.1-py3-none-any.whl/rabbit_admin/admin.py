from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, create_model
# Correctly import the specific field instance types
from tortoise.fields.relational import ForeignKeyFieldInstance, ManyToManyFieldInstance
from typing import List, Type, Dict, Any, Optional

# Define a consistent schema for representing related objects in API responses
class RelatedFieldSchema(BaseModel):
    id: int
    title: str

class AdminRegistry:
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = {}
        self.router = APIRouter(prefix="/api/admin")

    async def _tortoise_to_dict(self, instance: Type[BaseModel], model_name: str) -> Dict[str, Any]:
        """
        Converts a Tortoise ORM instance to a dictionary that matches our custom schema,
        handling FK and M2M relationships.
        """
        model_config = self.models[model_name]
        model_cls = model_config["model"]
        result = {}

        # Ensure M2M fields are fetched
        await instance.fetch_related(*model_config["m2m_fields"])

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

    def register(self, model: Type[BaseModel]):
        """
        Registers a Tortoise ORM model with the admin interface.
        This method creates custom Pydantic schemas and generates CRUD API routes.
        """
        model_name = model.__name__.lower()
        
        # --- Custom Schema Generation ---
        output_fields: Dict[str, Any] = {}
        input_fields: Dict[str, Any] = {}
        relation_fields: Dict[str, Any] = {}
        m2m_fields: List[str] = []

        for name, field_obj in model._meta.fields_map.items():
            # Use the correct type for the isinstance check
            if isinstance(field_obj, ForeignKeyFieldInstance):
                output_fields[name] = (Optional[RelatedFieldSchema], None)
                input_fields[f"{name}_id"] = (Optional[int], None)
                # FIX: Use related_model_name string to avoid initialization errors
                related_model_name = field_obj.model_name.split('.')[-1].lower()
                relation_fields[name] = {"type": "fk", "related_model": related_model_name}
            # Use the correct type for the isinstance check
            elif isinstance(field_obj, ManyToManyFieldInstance):
                m2m_fields.append(name)
                output_fields[name] = (List[RelatedFieldSchema], [])
                input_fields[f"{name}_ids"] = (List[int], [])
                # FIX: Use related_model_name string to avoid initialization errors
                related_model_name = field_obj.model_name.split('.')[-1].lower()
                relation_fields[name] = {"type": "m2m", "related_model": related_model_name}
            else:
                is_pk = name == model._meta.pk_attr
                python_type = field_obj.field_type
                # Don't include auto-incrementing integer PKs in the input schema
                if not (is_pk and python_type is int):
                    input_fields[name] = (python_type, ... if not field_obj.null else None)
                output_fields[name] = (python_type, ...)

        pydantic_schema = create_model(f"{model.__name__}SchemaOut", **output_fields)
        pydantic_schema_in = create_model(f"{model.__name__}SchemaIn", **input_fields)

        self.models[model_name] = {
            "model": model,
            "schema": pydantic_schema,
            "schema_in": pydantic_schema_in,
            "relation_fields": relation_fields,
            "m2m_fields": m2m_fields,
        }

        # --- Dynamically create API routes for the model ---
        
        @self.router.get(f"/{model_name}", response_model=List[pydantic_schema], tags=[model.__name__])
       
        async def get_all_items():
            items = await model.all()
            return [await self._tortoise_to_dict(item, model_name) for item in items]

        @self.router.post(f"/{model_name}", response_model=pydantic_schema, tags=[model.__name__])
        async def create_item(item: pydantic_schema_in):
            item_dict = item.dict(exclude_unset=True)
            relation_data = {k: v for k, v in item_dict.items() if k.endswith("_ids")}
            regular_data = {k: v for k, v in item_dict.items() if not k.endswith("_ids")}  
            obj = await model.create(**regular_data)

            for key, ids in relation_data.items():
                m2m_field_name = key.replace("_ids", "")
                related_model = model._meta.fields_map[m2m_field_name].related_model
                related_objs = await related_model.filter(id__in=ids)
                await getattr(obj, m2m_field_name).add(*related_objs)        
            return await self._tortoise_to_dict(obj, model_name)

        @self.router.get(f"/{model_name}/{{item_id}}", response_model=pydantic_schema, tags=[model.__name__])
        async def get_item(item_id: int):
            instance = await model.get(id=item_id)
            return await self._tortoise_to_dict(instance, model_name)

        @self.router.put(f"/{model_name}/{{item_id}}", response_model=pydantic_schema, tags=[model.__name__])
        async def update_item(item_id: int, item: pydantic_schema_in):
            item_dict = item.dict(exclude_unset=True)
            relation_data = {k: v for k, v in item_dict.items() if k.endswith("_ids")}
            regular_data = {k: v for k, v in item_dict.items() if not k.endswith("_ids")}

            await model.filter(id=item_id).update(**regular_data)
            obj = await model.get(id=item_id)

            for key, ids in relation_data.items():
                m2m_field_name = key.replace("_ids", "")
                m2m_manager = getattr(obj, m2m_field_name)
                await m2m_manager.clear()
                related_model = model._meta.fields_map[m2m_field_name].related_model
                related_objs = await related_model.filter(id__in=ids)
                await m2m_manager.add(*related_objs)

            return await self._tortoise_to_dict(obj, model_name)

        @self.router.delete(f"/{model_name}/{{item_id}}", response_model=dict, tags=[model.__name__])
        async def delete_item(item_id: int):
            deleted_count = await model.filter(id=item_id).delete()
            if not deleted_count:
                raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
            return {"message": f"Deleted item {item_id}"}





    def get_registered_models_info(self):
        """
        Provides detailed schema information about registered models for the frontend.
        """
        model_info = {}
        for name, data in self.models.items():
            fields_details = {}
            for field_name, field_obj in data["model"]._meta.fields_map.items():
                field_type_name = field_obj.__class__.__name__
                details = {"type": field_type_name}
                if field_name in data["relation_fields"]:
                    details.update(data["relation_fields"][field_name])
                fields_details[field_name] = details

            model_info[name] = {
                "name": data["model"].__name__,
                "fields": fields_details
            }
        return model_info

# Create a global admin instance
admin_app = AdminRegistry()

# Add routes for admin metadata
@admin_app.router.get("/_models", tags=["Admin"])
async def get_registered_models():
    """
    Endpoint to provide the frontend with a detailed schema of all registered models.
    """
    return admin_app.get_registered_models_info()

