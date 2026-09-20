import asyncio

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

_password_hasher = PasswordHash((BcryptHasher(),))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _password_hasher.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return _password_hasher.hash(password)


# bcrypt 是 CPU 密集操作（单次约 100-300ms），异步路径必须下线程池避免阻塞事件循环
async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    return await asyncio.to_thread(verify_password, plain_password, hashed_password)


async def get_password_hash_async(password: str) -> str:
    return await asyncio.to_thread(get_password_hash, password)
