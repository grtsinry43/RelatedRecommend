from pymongo import MongoClient

import cfg
from train import transform_to_vectors

client = MongoClient(cfg.mongo_cfg['host'], cfg.mongo_cfg['port'])
db = client[cfg.mongo_cfg['db']]
collection = db[cfg.mongo_cfg['collection']]


async def seed_mongo():
    article_vectors, articles = transform_to_vectors()

    # 清除原有数据
    collection.drop()

    for article, vector in zip(articles, article_vectors):
        collection.insert_one({'id': article[0], 'article': article, 'vector': vector.tolist()})

    print('数据导入成功')


def get_article_vectors():
    return list(collection.find({}))
