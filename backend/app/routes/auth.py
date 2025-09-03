
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from .. import schemas, models
# from ..auth import get_db, get_password_hash, verify_password, create_access_token
# from fastapi.security import OAuth2PasswordRequestForm

# router = APIRouter(prefix="/auth", tags=["auth"])


# @router.post("/register", response_model=schemas.UserOut, status_code=201)
# def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     # Check if email already exists
#     db_user = db.query(models.User).filter(models.User.email == user.email).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Hash the password
#     hashed_pw = get_password_hash(user.password)
    
#     # Create new user
#     new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_pw)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user



# @router.post("/login", response_model=schemas.Token)
# def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     # form_data.username = email in this case
#     user = db.query(models.User).filter(models.User.email == form_data.username).first()
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     access_token = create_access_token(data={"sub": str(user.id)})
#     return {"access_token": access_token, "token_type": "bearer"}






from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
import random, string, smtplib
from email.mime.text import MIMEText
from passlib.context import CryptContext
from fastapi import status
from ..auth import get_current_user  # if you already have auth dependency

from .. import schemas, models
from ..auth import get_db, get_password_hash, verify_password, create_access_token
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- Register ----------------
@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(user.password)
    new_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ---------------- Login ----------------
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------- Forgot Password ----------------
class ForgotPasswordRequest(BaseModel):
    email: str


def generate_temp_password(length: int = 10) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))


def send_email(to_email: str, new_password: str):
    subject = "Your New Temporary Password"
    body = f"Your temporary password is: {new_password}\n\nPlease log in and change it immediately."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USERNAME
    msg["To"] = to_email

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USERNAME, to_email, msg.as_string())


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    temp_password = generate_temp_password()
    hashed_password = pwd_context.hash(temp_password)

    user.hashed_password = hashed_password
    db.commit()

    try:
        send_email(request.email, temp_password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

    return {"message": "Temporary password sent to your email"}


# ---------------- Change Password ----------------
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # requires user to be logged in
):
    # 1. Validate old password
    if not pwd_context.verify(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    # 2. Validate new/confirm password match
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirm password do not match")

    # 3. Hash new password
    hashed_password = pwd_context.hash(request.new_password)

    # 4. Update in DB
    current_user.hashed_password = hashed_password
    db.commit()

    return {"message": "Password updated successfully"}