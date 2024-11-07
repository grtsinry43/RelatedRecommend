import asyncio

from fastapi import FastAPI
import uvicorn

from cfg import app_port
from get_data import get_article_by_id
from model import ArticleForm, ApiResponse
from pre_process import pre_process_single_article
from recommend import recommend_by_article_id
from save import seed_mongo, get_processed_article_by_id, add_article_vector, update_article_vector
from train import transform_single_article_to_vector, get_model_status

app = FastAPI()


@app.get("/")
async def root():
    return ApiResponse.success(get_model_status())


@app.post("/article/{article_id}")
async def add_or_update_article(article_id: int, article_form: ArticleForm):
    # 首先检查文章是否在mysql中，防止返回给Spring的数据出现问题
    article = get_article_by_id(article_id)
    if article is None:
        return ApiResponse.error(404, "文章" + str(article_id) + "不存在")
    # 然后看看这个文章是否在mongodb中（是否有计算好的向量）
    processed_article = get_processed_article_by_id(article_id)
    # 无论是否存在，都说明需要进行处理
    # 先对内容进行预处理
    processed_content = pre_process_single_article(article_form.content)
    # 然后转换成向量
    vector = transform_single_article_to_vector(processed_content)
    if processed_article is None:
        add_article_vector(article_id, vector)
        return ApiResponse.success({
            'article_id': str(article_id),
            'status': 'added',
        })
    else:
        update_article_vector(article_id, vector)
        return ApiResponse.success({
            'article_id': str(article_id),
            'status': 'updated',
        })


@app.get("/article/{article_id}")
async def get_recommendation(article_id: int, count: int = 5):
    # 检查一下有没有这个文章的向量数据
    article = get_processed_article_by_id(article_id)
    if article is None:
        return ApiResponse.error(404, "文章" + str(article_id) + "不存在")
    recommendation = recommend_by_article_id(article_id, count)
    # 这里得到的是一个列表，是所有的文章id
    return ApiResponse.success({
        'article_id': str(article_id),
        'recommendation': recommendation,
    })


async def main():
    # 这里首先调用 seed_mongo 函数，将数据导入到 MongoDB 中，完成之后才能启用 FastAPI 服务
    await seed_mongo()


if __name__ == '__main__':
    asyncio.run(main())
    print("> 启动 FastAPI 服务")
    uvicorn.run(app, host="127.0.0.1", port=app_port if app_port else 8000)
