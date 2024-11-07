from pymongo import MongoClient

import cfg
from train import transform_to_vectors


def seed_mongo():
    article_vectors, articles = transform_to_vectors()

    client = MongoClient(cfg.mongo_cfg['host'], cfg.mongo_cfg['port'])
    db = client[cfg.mongo_cfg['db']]
    collection = db[cfg.mongo_cfg['collection']]

    for article, vector in zip(articles, article_vectors):
        collection.insert_one({'article': article, 'vector': vector.tolist()})

    print('数据导入成功')
