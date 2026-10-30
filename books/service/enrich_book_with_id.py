import json
import unicodedata
from uuid import UUID, uuid5

BOOK_NAMESPACE_UUID = UUID("b6b581ee-4676-48c2-abeb-9a61bde75fc7")

def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value)
    return " ".join(value.casefold().split())

def enrich_book_with_id(book):
    # непустые - название и описание
    identity = [
        normalize_text(book["title"]),
        normalize_text(book.get("author", "")),
        book.get("year"),
    ]

    composed_identity = json.dumps(
        identity,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return str(uuid5(BOOK_NAMESPACE_UUID, composed_identity))
