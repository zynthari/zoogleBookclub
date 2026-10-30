from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


class MinimalFileValidator(FileExtensionValidator):
    """Проверяет наличие файла, его размер и разрешённое расширение."""

    def validate_file_size(self, file_size):
        if file_size > settings.MAX_FILE_SIZE:
            raise ValidationError("Файл слишком большой!")

    def __call__(self, value):
        if value is None:
            raise ValidationError("Файл не был предоставлен ?_?")
        self.validate_file_size(value.size)
        super().__call__(value)
