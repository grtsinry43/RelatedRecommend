from pydantic import BaseModel
from typing import Dict


class ArticleForm(BaseModel):
    id: int
    title: str
    content: str


class ApiResponse(BaseModel):
    code: int
    message: str
    data: Dict

    @staticmethod
    def success(data: Dict):
        response = ApiResponse(code=0, message="", data=data)
        return response

    @staticmethod
    def error(code: int, message: str):
        response = ApiResponse(code=code, message=message, data={})
        return response
