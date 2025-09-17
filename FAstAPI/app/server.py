from fastapi import FastAPI, HTTPException, Depends, status, Request
from typing import List, Iterator
import fastapi
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt

#ЗАЩИТА
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.pydant import User as DbUser, UserCreate, PostResponse, PostCreate, Token, Name_JWT
from app.db.models import User, Post
from app.db.database import engine, sesion_local, Base
from app.auth import get_password_hash, verify_password, create_acces_token
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

from sqlalchemy.sql import text

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#ЗАЩИТА
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


Base.metadata.create_all(bind=engine)

#DataBase
def get_db() -> Iterator[Session]:
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()


#верификация
def verify_token(token: str = Depends(oauth2_scheme)):
    credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email: str = payload.get("sub")

        if email is None:
            raise credentials
        
        return Name_JWT(email=email)
    
    except JWTError:
        raise credentials

#РЕГИСТРАЦИЯ
@app.post("/register/", response_model=DbUser, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_user(user: UserCreate, db: Session = Depends(get_db), request: Request = None) -> User:
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is not None:
        raise HTTPException(status_code=409, detail="Email already registered!")
    
    hash_user_pass = get_password_hash(user.password)

    db_user = User(
        name=user.name, age=user.age, town=user.town, email=user.email, hash_password=hash_user_pass
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


#ВХОД
@app.post("/token/", response_model=Token)
@limiter.limit("10/minute")
async def login_users(
    form_data: fastapi.security.OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None) -> dict:
    db_user = db.query(User).filter(User.email == form_data.username).first()
    
    if db_user is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not verify_password(form_data.password, db_user.hash_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_acces_token(
        data={"sub": db_user.email},
        expires_delta= timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/posts/", response_model=PostResponse)
@limiter.limit("5/minute")
async def create_post(
    post: PostCreate,
    current_user: Name_JWT = Depends(verify_token),
    db: Session = Depends(get_db),
    request: Request = None) -> Post:
    db_user = db.query(User).filter(User.email == current_user.email).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_post = Post(title=post.title, body=post.body, author_id=db_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@app.get("/posts/", response_model=List[PostResponse])
@limiter.limit("20/minute")
async def posts(
    current_user: Name_JWT = Depends(verify_token),
    db: Session=Depends(get_db),
    request: Request = None) -> List[Post]:
    return db.query(Post).all()

@app.get("/users/me/", response_model=DbUser)
@limiter.limit("10/minute")
async def users(
    current_user: Name_JWT = Depends(verify_token),
    db: Session=Depends(get_db),
    request: Request = None):
    
    db_user = db.query(User).filter(User.email == current_user.email).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user



#УЯЗВИМЫЙ ЭНДПОИНТ
@app.get("/vulnerable_search/")
async def vulnerable_search(query: str, db: Session = Depends(get_db)):
    raw_query = f"SELECT * FROM users WHERE email = '{query}'"
    try:
        result = db.execute(text(raw_query)).fetchall()
        return {"results": [dict(row) for row in result]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))