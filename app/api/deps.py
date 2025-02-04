from typing import AsyncIterator

import app.crud.user as crud
import app.schemas.user as schemas
from app.core.config import settings
from app.db.database import async_session
from app.schemas.token import TokenData
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            raise e
        finally:
            await session.close()


async def get_current_user(session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)

    except JWTError:
        raise credentials_exception

    user = await crud.user.get_by_username(session, username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


async def get_current_approved_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.permission_level > 0:
        raise HTTPException(status_code=400, detail="Not approved.")

    return current_user
