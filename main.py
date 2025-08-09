import asyncio

from fastapi import FastAPI
import uvicorn

from cfg import app_port
from get_data import get_article_by_id
from model import ArticleForm, ApiResponse
from pre_process import pre_process_single_article
from recommend import recommend_by_article_id, recommend_by_user_id
from save import seed_mongo, get_processed_article_by_id, add_article_vector, update_article_vector, \
    process_and_save_all_user_interest_vector, get_user_behavior_by_user_id, process_and_save_user_interest_vector, \
    get_user_interest_vector, delete_article_vector, get_article_vectors
from train import transform_single_article_to_vector, get_model_status

app = FastAPI()


@app.get("/")
async def root():
    return ApiResponse.success(get_model_status())


@app.get("/health")
async def health_check():
    """健康检查接口，检查数据库连接和数据状态"""
    try:
        from save import db, collection_behavior, collection_user_vectors
        
        # 检查文章向量数据
        article_vectors = get_article_vectors()
        article_count = len(article_vectors) if article_vectors else 0
        
        # 检查用户行为数据
        user_behavior_count = collection_behavior.count_documents({})
        
        # 检查用户向量数据
        user_vector_count = collection_user_vectors.count_documents({})
        
        return ApiResponse.success({
            'status': 'healthy',
            'article_vectors_count': article_count,
            'user_behavior_count': user_behavior_count,
            'user_vector_count': user_vector_count,
            'database_connected': True
        })
    except Exception as e:
        return ApiResponse.error(500, f"健康检查失败: {str(e)}")


@app.post("/article/{article_id}")
async def add_or_update_article(article_id: int, article_form: ArticleForm):
    # 首先检查文章是否在mysql中，防止返回给Spring的数据出现问题
    article = get_article_by_id(article_id)
    if article is None:
        return ApiResponse.error(404, "文章" + str(article_id) + "不存在")
    # 然后看看这个文章是否在mongodb中（是否有计算好的向量）
    processed_article_cursor = get_processed_article_by_id(article_id)
    processed_article = list(processed_article_cursor)
    # 无论是否存在，都说明需要进行处理
    # 先对内容进行预处理，然后转换成向量
    vector = transform_single_article_to_vector(article_form.content)
    # 如果列表为空，说明没有这个文章的向量数据，需要添加
    if not processed_article:
        print("文章不存在，添加新文章" + str(article_id))
        add_article_vector(article_id, vector)
        return ApiResponse.success({
            'article_id': str(article_id),
            'status': 'added',
        })
    else:
        print("文章已存在，更新文章" + str(article_id))
        update_article_vector(article_id, vector)
        return ApiResponse.success({
            'article_id': str(article_id),
            'status': 'updated',
        })


@app.delete("/article/{article_id}")
async def delete_article(article_id: int):
    # 首先检查文章是否在mysql中，防止返回给Spring的数据出现问题
    article = get_article_by_id(article_id)
    if article is None:
        return ApiResponse.error(404, "文章" + str(article_id) + "不存在")
    # 然后看看这个文章是否在mongodb中（是否有计算好的向量）
    processed_article_cursor = get_processed_article_by_id(article_id)
    processed_article = list(processed_article_cursor)
    # 如果列表为空，说明没有这个文章的向量数据，不需要删除
    if not processed_article:
        return ApiResponse.error(404, "文章" + str(article_id) + "不存在")
    else:
        print("文章已存在，删除文章" + str(article_id))
        delete_article_vector(article_id)
        return ApiResponse.success({
            'article_id': str(article_id),
            'status': 'deleted',
        })


@app.get("/article/{article_id}")
async def get_recommendation(article_id: int, count: int = 5):
    # 检查一下有没有这个文章的向量数据
    article_cursor = get_processed_article_by_id(article_id)
    article_list = list(article_cursor)
    if not article_list:
        return ApiResponse.error(404, "文章" + str(article_id) + "不存在")
    
    # 获取推荐结果
    recommendation = recommend_by_article_id(article_id, count)
    
    # 检查推荐结果是否为空
    if not recommendation:
        return ApiResponse.error(503, "暂时无法为文章" + str(article_id) + "生成推荐，请稍后再试")
    
    # 这里得到的是一个列表，是所有的文章id
    return ApiResponse.success({
        'article_id': str(article_id),
        'recommendation': recommendation,
    })


@app.get("/user/{user_id}")
async def get_user_recommendation(user_id: str, count: int = 5):
    # 检查一下有没有这个用户的行为数据
    user_behavior = get_user_interest_vector(user_id)
    if user_behavior is None:
        process_and_save_user_interest_vector(user_id)
        return ApiResponse.error(404, "用户" + str(user_id) + "不存在")
    # 更新一下用户的兴趣向量
    process_and_save_user_interest_vector(user_id)

    # 获取推荐结果
    recommendation = recommend_by_user_id(user_id, count)
    
    # 检查推荐结果是否为空
    if not recommendation:
        return ApiResponse.error(503, "暂时无法为用户" + str(user_id) + "生成推荐，请稍后再试")

    # 这里得到的是一个列表，是所有的文章id
    return ApiResponse.success({
        'user_id': str(user_id),
        'recommendation': recommendation,
    })


async def main():
    # 这里首先调用 seed_mongo 函数，将数据导入到 MongoDB 中，完成之后才能启用 FastAPI 服务
    await seed_mongo()
    # 读取用户行为数据，并将其转换为用户向量
    await process_and_save_all_user_interest_vector()


if __name__ == '__main__':
    asyncio.run(main())
    print("> 启动 FastAPI 服务")
    uvicorn.run(app, host="0.0.0.0", port=app_port if app_port else 8000)
