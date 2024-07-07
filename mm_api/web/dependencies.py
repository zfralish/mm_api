from typing import Annotated

from fastapi import Header

from mm_api.web.utils.token import decode_token


async def is_authenticated(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    return decode_token(authorization[7:])["sub"]  # type: ignore
