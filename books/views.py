from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET, require_POST

from .service import pick_books_for_answer, enrich_book_collection
from django.core.exceptions import ValidationError
from .validations import MinimalFileValidator


def welcome(request):
    return HttpResponse("Welcome to Zoogle Bookclub.")


@require_GET
def csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})


def get_question(request):
    # извлечем запрос из запроса
    question = request.GET.get("question", None)
    if question is None or question == "":
        return HttpResponse("Вопрос не был задан!", status=400)

    # подбор подходящих книг
    result = pick_books_for_answer(question)

    return HttpResponse(result)

@require_POST
def upload_library(request):
    library = request.FILES.get("file")

    validator = MinimalFileValidator(
        allowed_extensions=["json"],
        message="Разрешены только JSON-файлы для пополнения библиотеки!"
    )
    try:
        validator(library)
        renewed_books_count = enrich_book_collection(collection_name="sample_collection", json_file=library)
        if renewed_books_count > 0:
            return HttpResponse(f"В библиотеке обновлено {renewed_books_count} книг!", status=200)
        else:
            return HttpResponse(f"В файле не нашлось новинок =(", status=200)
    except ValidationError as e:
        return HttpResponse("; ".join(e.messages), status=400)
    except Exception as e:
        return HttpResponse(str(e), status=400)

