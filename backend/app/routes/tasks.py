# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from .. import schemas, crud
# from ..database import SessionLocal

# router = APIRouter(prefix="/tasks", tags=["tasks"])

# # Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.post("/", response_model=schemas.TaskOut, status_code=201)
# def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
#     return crud.create_task(db, payload)

# @router.get("/", response_model=list[schemas.TaskOut])
# def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return crud.list_tasks(db, skip=skip, limit=limit)

# @router.get("/{task_id}", response_model=schemas.TaskOut)
# def get_task(task_id: int, db: Session = Depends(get_db)):
#     task = crud.get_task(db, task_id)
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")
#     return task

# @router.patch("/{task_id}", response_model=schemas.TaskOut)
# def patch_task_status(task_id: int, payload: schemas.TaskUpdateStatus, db: Session = Depends(get_db)):
#     task, err = crud.update_task_status(db, task_id, payload.new_status)
#     if err == "not_found":
#         raise HTTPException(status_code=404, detail="Task not found")
#     if err and err.startswith("invalid_status"):
#         raise HTTPException(status_code=400, detail="Invalid status value")
#     if err:
#         raise HTTPException(status_code=400, detail=err)
#     return task

# @router.delete("/{task_id}", status_code=204)
# def delete_task(task_id: int, db: Session = Depends(get_db)):
#     ok = crud.delete_task(db, task_id)
#     if not ok:
#         raise HTTPException(status_code=404, detail="Task not found")
#     return

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, crud
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

# ------------------- CREATE TASK -------------------
@router.post("/", response_model=schemas.TaskOut, status_code=201)
def create_task_route(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_task(db, payload, current_user.id)

# ------------------- LIST TASKS -------------------
@router.get("/", response_model=List[schemas.TaskOut])
def get_tasks_route(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.list_tasks(db, current_user.id)

# ------------------- GET SINGLE TASK -------------------
@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_task_route(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task = crud.get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# ------------------- UPDATE TASK STATUS -------------------
@router.patch("/{task_id}", response_model=schemas.TaskOut)
def patch_task_status_route(
    task_id: int,
    payload: schemas.TaskUpdateStatus,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task, err = crud.update_task_status(db, task_id, payload.new_status, current_user.id)
    if err == "not_found":
        raise HTTPException(status_code=404, detail="Task not found")
    if err and err.startswith("invalid_status"):
        raise HTTPException(status_code=400, detail="Invalid status value")
    if err:
        raise HTTPException(status_code=400, detail=err)
    return task

# ------------------- DELETE TASK -------------------
@router.delete("/{task_id}", status_code=204)
def delete_task_route(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    ok = crud.delete_task(db, task_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return
