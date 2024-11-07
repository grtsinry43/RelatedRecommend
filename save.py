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
        collection.insert_one({'id': article[0], 'vector': vector.tolist()})

    print('已清除原有数据并导入新数据，共计', len(articles), '条')


def get_article_vectors():
    return list(collection.find({}))


def get_processed_article_by_id(article_id):
    return collection.find({'id': article_id})


def add_article_vector(article_id, vector):
    collection.insert_one({'id': article_id, 'vector': vector.tolist()})


def update_article_vector(article_id, vector):
    collection.update_one({'id': article_id}, {'$set': {'vector': vector.tolist()}})
