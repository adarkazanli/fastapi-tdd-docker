import os

from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .my_models import User_Pydantic, UserIn_Pydantic, Users
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise

from .managers.query_manager import QueryManager, queryManager

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
        raise HTTPException(
            status_code=404, detail=f"User {user_id} not found")
    return Status(message=f"Deleted user {user_id}")


# Direct

@app.get("/users_direct")
async def get_direct_users():
    return queryManager.get_users()


@app.get("/users_by_id_direct/{user_id}")
async def get_direct_users(user_id: int):
    return queryManager.get_users_by_id(user_id)


register_tortoise(
    app,
    db_url=os.environ.get("DATABASE_URL"),
    modules={"models": ["app.my_models"]},
    generate_schemas=False,
    add_exception_handlers=True,
)
