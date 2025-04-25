from fastapi import HTTPException, status


class CarCreationError(HTTPException):
    def __init__(self, detail: str = "Failed to create car"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class CarNotFoundError(Exception):
    def __init__(self, detail: str = "Car not found"):
        self.detail = detail
        super().__init__(self.detail)


class CarUpdateError(Exception):
    def __init__(self, detail: str = "Failed to update car"):
        self.detail = detail
        super().__init__(self.detail)


class CarDeletionError(Exception):
    def __init__(self, detail: str = "Failed to delete car"):
        self.detail = detail
        super().__init__(self.detail)