from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import auth, models

users_db = {
    "John Doe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": auth.get_password_hash("secret"),
        "disabled": False,
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def root():
    return {"message": "Hello World"}


def get_user(username: str):
    user = users_db.get(username)
    if user:
        return models.UserInDB(**user)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return None
    return user


@router.post("/token", response_model=models.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = auth.decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    username: str = payload.get("sub")
    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
