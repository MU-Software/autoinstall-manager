from __future__ import annotations

from contextlib import suppress
from email.utils import parseaddr
from re import sub
from string import ascii_letters, digits, punctuation
from typing import LiteralString
from unicodedata import normalize

# ---------- Check and Normalize strings ----------
char_printable: LiteralString = ascii_letters + digits + punctuation
char_urlsafe: LiteralString = ascii_letters + digits + "-_"


def is_printable(s: str) -> bool:
    return all(c in char_printable for c in s)


def is_urlsafe(s: str) -> bool:
    return all(c in char_urlsafe for c in s)


def is_email(s: str) -> bool:
    with suppress(BaseException):
        if parsed_email := parseaddr(normalize("NFC", s))[1]:
            splited_mail_address: list[str] = parsed_email.split("@")
            splited_domain: list[str] = splited_mail_address[1].split(".")
            return len(splited_mail_address) == 2 and all(splited_mail_address) and len(splited_domain) >= 2 and all(splited_domain)
    return False


# ---------- Case modifier ----------
def camel_to_snake_case(camel: str) -> str:
    camel = sub("(.)([A-Z][a-z]+)", r"\1_\2", camel)
    return sub("([a-z0-9])([A-Z])", r"\1_\2", camel).lower()


def snake_to_camel_case(snake: str) -> str:
    return "".join(word.title() for word in snake.split("_"))


def snake_to_train_case(snake: str) -> str:
    """
    Convert a snake_case string to Train-Case.
    Args: snake: The string to convert.
    Returns: The Train-Case string.
    """
    return snake.title().replace("_", "-")
