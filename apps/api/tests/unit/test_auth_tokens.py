from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

settings = get_settings()


def test_token_round_trip_keeps_subject_and_claims() -> None:
    token = create_access_token("user-42", {"role": "candidate"})
    claims = decode_access_token(token)
    assert claims is not None
    assert claims["sub"] == "user-42"
    assert claims["role"] == "candidate"


def test_tampered_token_is_rejected() -> None:
    token = create_access_token("user-42")
    header, payload, signature = token.split(".")
    flipped = ("A" if signature[0] != "A" else "B") + signature[1:]
    assert decode_access_token(f"{header}.{payload}.{flipped}") is None


def test_token_signed_with_another_secret_is_rejected() -> None:
    forged = jwt.encode({"sub": "admin"}, "not-the-server-secret", algorithm=settings.jwt_algorithm)
    assert decode_access_token(forged) is None


def test_expired_token_is_rejected() -> None:
    expired = jwt.encode(
        {"sub": "user-42", "exp": datetime.now(timezone.utc) - timedelta(seconds=5)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    assert decode_access_token(expired) is None


def test_unsigned_token_is_rejected() -> None:
    unsigned = jwt.encode({"sub": "admin"}, key=None, algorithm="none")
    assert decode_access_token(unsigned) is None


def test_garbage_input_is_rejected() -> None:
    assert decode_access_token("not-a-jwt") is None


def test_password_hash_verifies_only_the_original_password() -> None:
    hashed = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", hashed)
    assert not verify_password("wrong password", hashed)
