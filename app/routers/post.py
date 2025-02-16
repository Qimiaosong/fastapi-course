from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models, oauth2
from ..database import get_db
from sqlalchemy import func


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# @router.get("/")
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), get_current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = None):
    # post_query = db.query(models.Post)
    # posts = post_query.limit(limit).offset(skip).all()

    # results = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
    #     models.Vote, models.Post.id == models.Vote.post_id, isouter=True
    # ).group_by(models.Post.id).all()
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit).offset(skip)
        .all()
    )
    # response = [{"post": post, "votes": votes} for post, votes in results]

    # if search:
    #     posts = post_query.filter(models.Post.title.contains(search))
       
    print("c"*20, get_current_user.email)
    return posts

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id:int, db:Session = (Depends(get_db)), get_current_user: int = Depends(oauth2.get_current_user)):
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id).filter(models.Post.id == id).first()
    )
    print(post)
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} was not found")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db:Session=Depends(get_db), 
                get_current_user: int = Depends(oauth2.get_current_user)):
    # new_post = models.Post(
    #     title=post.title, content=post.content, published=post.published
    # )
    print("g"*20, get_current_user)
    new_post = models.Post(owner_id=get_current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db:Session = (Depends(get_db)),
                get_current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post with id: {id} does not exist")
    if post.owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to delete this post")
    post_query.delete(synchronize_session=False)
    db.commit()

@router.put("/{id}", response_model=schemas.Post)
def update_post(id:int, updated_post: schemas.PostCreate, db: Session = Depends(get_db),
                get_current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    if post.owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to update this post")
    
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()

