import json


class WrongJSONFormat(ValueError):
    pass

class WrongBookFormat(ValueError):
    pass


def validate_json(templates):
    match templates:
        case {"books": [*books]}:
            for number, book in enumerate(books, start=1):
                try:
                    validate_book(book)
                except WrongBookFormat as exc:
                    raise WrongBookFormat(f"Книга №{number}: {exc}") from exc
            return books
        case _:
            raise WrongJSONFormat(
                "JSON должен быть объектом с полем 'books', содержащим список книг"
            )


def validate_book(book):
    if not isinstance(book, dict):
        raise WrongBookFormat("Запись должна быть объектом")

    for field in ("title", "description"):
        if field not in book:
            raise WrongBookFormat(f"Отсутствует обязательное поле '{field}'")
        value = book[field]
        if not isinstance(value, str) or not value.strip():
            raise WrongBookFormat(f"Поле '{field}' должно быть непустой строкой")

    # у книги может не быть автора
    if "author" in book and not isinstance(book["author"], str):
        raise WrongBookFormat("Поле 'author' должно быть строкой")
    if "year" in book and type(book["year"]) is not int:
        raise WrongBookFormat("Поле 'year' должно быть целым числом")
    if "category" in book and not isinstance(book["category"], str):
        raise WrongBookFormat("Поле 'category' должно быть строкой")


def validate_json_file(json_file):
    try:
        if hasattr(json_file, "read"):
            templates = json.load(json_file)
        else:
            with open(json_file, encoding="utf-8-sig") as f:
                templates = json.load(f)
    except json.JSONDecodeError as exc:
        raise WrongJSONFormat(
            f"Некорректный JSON: строка {exc.lineno}, столбец {exc.colno}: {exc.msg}"
        ) from exc
    except UnicodeDecodeError as exc:
        raise WrongJSONFormat("Файл должен содержать JSON в кодировке UTF-8") from exc

    return validate_json(templates)
