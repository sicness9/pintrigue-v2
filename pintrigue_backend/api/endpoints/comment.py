# comment endpoints

from fastapi import HTTPException, APIRouter

from pintrigue_backend.database.mongodb.db_comment import create_comment, update_comment, delete_comment
from pintrigue_backend.schemas.schemas import Comment

router = APIRouter(
    prefix="/api/comments",
    tags=["comments"]
)


@router.post("/add_comment")
def api_add_comment(comment: Comment):
    response = create_comment(pin_id=comment.pin_id, posted_by=comment.posted_by, comment=comment.comment)
    print(f"Received response: {response}")
    if response:
        return {"success": True}
    raise HTTPException(400, "Something went wrong")


@router.put("/update_comment/<comment_id>")
def api_update_comment(comment_id: str, comment: str):
    response = update_comment(comment_id=comment_id, comment=comment)
    if response:
        return {"success": True}
    raise HTTPException(400, "Something went wrong")


@router.delete("/delete_comment")
def api_delete_comment(comment_id: str):
    response = delete_comment(comment_id=comment_id)
    if response:
        return {"success": True}
    raise HTTPException(400, "Something went wrong")
