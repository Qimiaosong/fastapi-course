from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, models, database, oauth2

router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session=Depends(database.get_db),
         get_current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {vote.post_id} not found")
    
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == get_current_user.id)
    found_vote = vote_query.first()

    # 想点赞
    if(vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"user {get_current_user.id} has already vote on post {vote.post_id}")
        new_vote = models.Vote(post_id=vote.post_id, user_id=get_current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "successfully added vote"}
    
    # 想取消点赞
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="vote does not exist")
        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "successfully deleted vote"}
