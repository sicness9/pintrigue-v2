# save endpoints

from fastapi import HTTPException, APIRouter
from fastapi.encoders import jsonable_encoder

from pintrigue_backend.schemas.schemas import Save
from pintrigue_backend.database.mongodb.db_save import add_save, remove_save

router = APIRouter(
    prefix="/api/saves",
    tags=["saves"]
)


@router.post("/create_save")
def api_create_save(save: Save):
    response = add_save(posted_by=save.posted_by, user_id=save.user_id)
    if response:
        return {"success": True}
    raise HTTPException(400, "Something went wrong")


@router.delete("/remove_save")
def api_remove_save(save_id: str):
    response = remove_save(save_id=save_id)
