from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud
from models import User
import schemas
from auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user, verify_password

router = APIRouter()

@router.post("/contacts/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = user.id
    new_contact = crud.create_contact(db, contact, user_id)
    contacts = crud.get_contacts(db)
    
    return new_contact



@router.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(skip: int = Query(0, alias="page", ge=0), limit: int = Query(10, le=100), 
                   db: Session = Depends(get_db)):
    contacts = crud.get_contacts(db, skip, limit)
    return contacts

@router.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    contact = crud.get_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    if contact.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return contact

@router.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    updated_contact = crud.update_contact(db, contact_id, contact)
    if updated_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact

@router.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    contact = crud.get_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    if contact.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    deleted_contact = crud.delete_contact(db, contact_id)
    if deleted_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return deleted_contact

@router.get("/contacts/search/", response_model=List[schemas.Contact])
def search_contacts(query: str, db: Session = Depends(get_db)):
    contacts = crud.search_contacts(db, query)
    return contacts

@router.get("/contacts/birthdays/", response_model=List[schemas.Contact])
def upcoming_birthdays(db: Session = Depends(get_db)):
    contacts = crud.get_upcoming_birthdays(db)
    return contacts


from fastapi import HTTPException

@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    
    new_user = crud.create_user(db, user)
    users = crud.get_users(db)
    users.append(new_user)
    
    return new_user


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/", response_model=List[schemas.User])
def get_all_users(skip: int = Query(0), limit: int = Query(100), 
                   db: Session = Depends(get_db)):
    users = crud.get_users(db, skip, limit)
    return users



