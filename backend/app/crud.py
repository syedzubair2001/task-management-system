from sqlalchemy.orm import Session
from . import models, schemas

# Allowed statuses
ALLOWED_STATUSES = ["pending", "in-progress", "completed", "archived"]

# Define the allowed transitions (the "trick requirement")
ALLOWED_TRANSITIONS = {
    "pending": ["in-progress"],
    "in-progress": ["completed"],
    "completed": ["archived"],
    "archived": []
}

def create_task(db: Session, payload: schemas.TaskCreate, user_id: int) -> models.Task:
    task = models.Task(
        title=payload.title,
        description=payload.description,
        owner_id=user_id  # Ensure this field exists in models.Task
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# def get_task(db: Session, task_id: int):
#     return db.query(models.Task).filter(models.Task.id == task_id, models.Task.is_deleted == False).first()

# def get_task(db: Session, task_id: int, user_id: int):
#     return db.query(models.Task)\
#         .filter(
#             models.Task.id == task_id,
#             models.Task.owner_id == user_id,  # check ownership
#             models.Task.is_deleted == False
#         ).first()

# def get_task(db: Session, task_id: int, user_id: int):
#     return db.query(models.Task)\
#         .filter(
#             models.Task.id == task_id,
#             models.Task.owner_id == user_id,
#             models.Task.is_deleted == False
#         ).first()


def get_task(db: Session, task_id: int, user_id: int):
    return db.query(models.Task)\
        .filter(
            models.Task.id == task_id,
            models.Task.owner_id == user_id,
            models.Task.is_deleted == False
        ).first()



def list_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.is_deleted == False).offset(skip).limit(limit).all()

# def update_task_status(db: Session, task_id: int, new_status: str):
#     task = get_task(db, task_id)
#     if not task:
#         return None, "not_found"
#     if new_status not in ALLOWED_STATUSES:
#         return None, "invalid_status"
#     allowed = ALLOWED_TRANSITIONS.get(task.status, [])
#     if new_status not in allowed:
#         return None, f"invalid_transition: allowed from {task.status} -> {allowed}"
#     task.status = new_status
#     db.commit()
#     db.refresh(task)
#     return task, None

def update_task_status(db: Session, task_id: int, new_status: str, user_id: int):
    task = get_task(db, task_id, user_id)  # pass user_id to ensure task belongs to user
    if not task:
        return None, "not_found"
    ALLOWED_STATUSES = ["pending", "in_progress", "completed"]
    if new_status not in ALLOWED_STATUSES:
        return None, "invalid_status"

    ALLOWED_TRANSITIONS = {
        "pending": ["in_progress", "completed"],
        "in_progress": ["completed"],
        "completed": [],
    }
    allowed = ALLOWED_TRANSITIONS.get(task.status, [])
    if new_status not in allowed:
        return None, f"invalid_transition: allowed from {task.status} -> {allowed}"

    task.status = new_status
    db.commit()
    db.refresh(task)
    return task, None


# def delete_task(db: Session, task_id: int):
#     task = get_task(db, task_id)
#     if not task:
#         return False
#     task.is_deleted = True
#     db.commit()
#     return True


def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    task = get_task(db, task_id, user_id)
    if not task:
        return False
    task.is_deleted = True
    db.commit()
    return True
