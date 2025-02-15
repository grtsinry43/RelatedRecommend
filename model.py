from pydantic import BaseModel
from typing import Dict


class ArticleForm(BaseModel):
    id: str
    title: str
    content: str


class ApiResponse(BaseModel):
    code: int
    msg: str
    data: Dict

    @staticmethod
    def success(data: Dict):
        response = ApiResponse(code=0, msg="", data=data)
        return response

    @staticmethod
    def error(code: int, message: str):
        response = ApiResponse(code=code, msg=message, data={})
        return response
