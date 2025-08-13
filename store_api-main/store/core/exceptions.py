class BaseException(Exception):
    message: str = "Internal Server Error"

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message


class NotFoundException(BaseException):
    message = "Not Found"

class InsertErrorException(Exception):
    def __init__(self, message: str = "Erro ao inserir o registro"):
        self.message = message
        super().__init__(self.message)
