import jwt
from jwt import InvalidTokenError, algorithms

from mm_api.settings import settings


# Decode token using JWKS
def decode_token(token: str) -> dict[str, str]:

    public_key = algorithms.RSAAlgorithm.from_jwk(settings.jwks["keys"][0])  # type: ignore

    decoded_token = {}
    try:
        # Decode the token
        decoded_token = jwt.decode(
            token,
            public_key,  # type: ignore
            algorithms=["RS256"],  # Use the appropriate algorithm
        )

        # Print the decoded token
    except jwt.ExpiredSignatureError:
        print("Token has expired")
    except InvalidTokenError as e:
        print(f"Invalid token: {e}")

    return decoded_token
