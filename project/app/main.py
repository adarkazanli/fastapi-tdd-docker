# # from fastapi import FastAPI, Depends

# # from app.config import get_settings, Settings
# # from fastapi import FastAPI
# # from tortoise.contrib.fastapi import register_tortoise
# # from config.db import DB_CONFIG
# # from config.settings import Settings
# # import uvicorn
# # settings = Settings()

# # app = FastAPI()

# # register_tortoise(
# #     app,
# #     config=DB_CONFIG,
# #     generate_schemas=False,
# # )
# # @app.get("/ping")
# # async def ping(settings:Settings = Depends(get_settings)):
# #     return {
# #             "ping":"pong! (ammar)",
# #             "environment": settings.environment,
# #             "testing": settings.testing
# #             }


# # example.py

# import uvicorn as uvicorn
# from fastapi import FastAPI
# from fastapi_crudrouter.core.tortoise import TortoiseCRUDRouter
# from tortoise.contrib.fastapi import register_tortoise
# from tortoise.contrib.pydantic import pydantic_model_creator
# from tortoise.models import Model
# from tortoise import fields, Tortoise

# TORTOISE_ORM = {
#     "connections": {"default": 'postgres://postgres:postgres@172.22.0.2:5432/postgres'},
#     "apps": {
#         "models": {
#             "models": [],
#             "default_connection": "default",
#         },
#     },
# }

# # Create Database Tables
# async def init():
#     await Tortoise.init(config=TORTOISE_ORM)
#     await Tortoise.generate_schemas()

# app = FastAPI()
# register_tortoise(app, config=TORTOISE_ORM)


# # Tortoise ORM Model
# class TestModel(Model):
#     test = fields.IntField(null=False, description=f"Test value")
#     ts = fields.IntField(null=False, description=f"Epoch time")


# # Pydantic schema
# TestSchema = pydantic_model_creator(TestModel, name=f"{TestModel.__name__}Schema")
# TestSchemaCreate = pydantic_model_creator(TestModel, name=f"{TestModel.__name__}SchemaCreate", exclude_readonly=True)

# # Make your FastAPI Router from your Pydantic schema and Tortoise Model
# router = TortoiseCRUDRouter(
#     schema=TestSchema,
#     create_schema=TestSchemaCreate,
#     db_model=TestModel,
#     prefix="test"
# )

# # Add it to your app
# app.include_router(router)

# if __name__ == "__main__":
#     uvicorn.run("example:app", host="127.0.0.1", port=5000, log_level="info")



from typing import List

from fastapi import FastAPI, HTTPException
from models import User_Pydantic, UserIn_Pydantic, Users
from pydantic import BaseModel

from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise

app = FastAPI(title="Tortoise ORM FastAPI example")


class Status(BaseModel):
    message: str


@app.get("/users", response_model=List[User_Pydantic])
async def get_users():
    return await User_Pydantic.from_queryset(Users.all())


@app.post("/users", response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    user_obj = await Users.create(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_tortoise_orm(user_obj)


@app.get(
    "/user/{user_id}", response_model=User_Pydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def get_user(user_id: int):
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@app.put(
    "/user/{user_id}", response_model=User_Pydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def update_user(user_id: int, user: UserIn_Pydantic):
    await Users.filter(id=user_id).update(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@app.delete("/user/{user_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_user(user_id: int):
    deleted_count = await Users.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return Status(message=f"Deleted user {user_id}")


register_tortoise(
    app,
    db_url='postgres://postgres:postgres@172.22.0.2:5432/postgres',
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)