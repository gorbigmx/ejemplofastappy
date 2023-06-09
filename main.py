from typing_extensions import deprecated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Union
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError

fake_users_db = {
    "juan":{
        "username": "juan",
        "full_name": "Juan",
        "email": "juanito@correo.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disdable": False        
    },
     "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "$2b$12$gSvqqUPvlXP2tfVFaWK1Be7DlH.PKZbv5H8KnzzVgXXbVxpva.pFm",
        "disabled": False,
    },
      "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}
app = FastAPI()

oauth2_sheme = OAuth2PasswordBearer("/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "9843afe0afea1fc1ff49e193b4fc58f2d3db93f8766e672b7cf305b8b28d36a7"
ALGORITHM = "HS256"

class User(BaseModel):
    username: str
    full_name: Union[str, None]= None
    email:Union[str, None]= None
    disdable:Union[bool, None]= None

class UserInDB(User):
    hashed_password: str

def get_user(db, username):
    if username in db:
        user_data = db[username]
        return UserInDB(**user_data)
    return []

def verify_password(plane_password, hashed_password):
    return pwd_context.verify(plane_password, hashed_password)

def authenticate_user(db, username, password):
    user = get_user(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="Error de Usuario", headers={"WWW-authenticate": "Bearer"})
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Error de Password", headers={"WWW-authenticate": "Bearer"})
    return user

def create_token(data: dict, time_expire: Union[datetime, None]=None):
    data_copy = data.copy()
    if time_expire is None:
        expires = datetime.utcnow() + timedelta(minutes=15)
    else:
        expires = datetime.utcnow() + time_expire
    data_copy.update({"exp": expires})
    token_jwt = jwt.encode(data_copy, key=SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

def get_user_current(token: str = Depends(oauth2_sheme)):
    try:
        token_decode = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username = token_decode.get("sub")
        if username == None:
            raise HTTPException(status_code=401, detail="Error de Usuario", headers={"WWW-authenticate": "Bearer"})
    
    except JWTError:
            raise HTTPException(status_code=401, detail="Error de Usuario", headers={"WWW-authenticate": "Bearer"})
    user = get_user(fake_users_db, username)
    if not user:
        raise HTTPException(status_code=401, detail="Error de Usuario", headers={"WWW-authenticate": "Bearer"})
    return user

def get_user_disabled_current(user: User = Depends(get_user_current)):
    if user.disdable:
        raise HTTPException(status_code=400, detail="Inactive User")
    return user

@app.get("/")
def root():
    return "Hola fastMedia"

@app.get("/users/me")
def user(user: User = Depends(get_user_disabled_current)):
    return user

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    access_token_expired = timedelta(minutes=30)
    access_token_jwe = create_token({"sub": user.username}, access_token_expired)
    return {
        "access_token": access_token_jwe,
        "token_type": "bearer"
    }

#@app.post("/token")
#def 