from datetime import datetime

from pymongo import MongoClient

import cfg
import numpy as np

from train import transform_to_vectors

client = MongoClient(cfg.mongo_cfg['host'], cfg.mongo_cfg['port'])
db = client[cfg.mongo_cfg['db']]
collection = db[cfg.mongo_cfg['collection']]
collection_behavior = db[cfg.mongo_cfg['behavior_collection']]
collection_user_vectors = db[cfg.mongo_cfg['user_vector_collection']]


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
    return collection.find({'id': article_id}, {'_id': 0})


def add_article_vector(article_id, vector):
    collection.insert_one({'id': article_id, 'vector': vector.tolist()})


def update_article_vector(article_id, vector):
    collection.update_one({'id': article_id}, {'$set': {'vector': vector.tolist()}})


def delete_article_vector(article_id):
    collection.delete_one({'id': article_id})


# 从mongo数据库根据用户ID读取用户行为数据
def get_user_behavior_by_user_id(user_id):
    user_behavior = collection_behavior.find_one({'userId': user_id}, {'_id': 0})
    return user_behavior


def get_weight_by_type(behavior_type, value=0):
    # 定义初始权重
    base_weights = {
        '1': 0.3,  # 阅读文章
        '2': 1.5,  # 点赞文章
        '3': 1.0,  # 评论文章
        '4': 1.3,  # 分享文章
        '5': 1.2,  # 收藏文章
        '6': min(value / 60.0, 3.0)  # 阅读时间，权重上限为3.0
    }

    # 获取权重，默认返回1.0
    return base_weights.get(behavior_type, 1.0)


def get_user_behaviors(user_id):
    return list(collection_behavior.find({'userId': user_id}, {'_id': 0}))


def calculate_user_interest_vector(user_id):
    user_behaviors = get_user_behaviors(user_id)
    user_behavior_vectors = []
    weights_sum = 0

    for behavior in user_behaviors:
        article_vector_cursor = get_processed_article_by_id(int(behavior['articleId']))
        # 将游标转换为列表并检查是否有数据
        article_vector_list = list(article_vector_cursor)
        if article_vector_list:
            article_vector = article_vector_list[0]
            weight = get_weight_by_type(behavior['type'], behavior.get('value', 0))

            # 添加时间衰减系数
            days_since_behavior = (datetime.now() - behavior['date']).days
            decay_factor = 1 / (1 + days_since_behavior / 30)  # 每月衰减一定比例

            weighted_vector = np.array(article_vector['vector']) * weight * decay_factor
            user_behavior_vectors.append(weighted_vector)
            weights_sum += weight * decay_factor
        else:
            print(f"警告: 用户 {user_id} 的行为数据中引用的文章 {behavior['articleId']} 不存在")

    # 获取所有文章向量
    article_vectors = get_article_vectors()
    
    # 检查是否有文章向量数据
    if not article_vectors:
        print(f"警告: 没有找到任何文章向量数据，无法为用户 {user_id} 计算兴趣向量")
        # 返回一个默认的零向量，维度为768（BERT标准维度）
        return np.zeros(768, dtype='float32')
    
    mean_article_vector = np.mean([article['vector'] for article in article_vectors], axis=0)

    if user_behavior_vectors:
        # 使用加权平均，并与文章均值向量合成计算
        user_interest_vector = (np.sum(user_behavior_vectors, axis=0) + mean_article_vector) / (weights_sum + 1)
    else:
        # 用户没有任何行为，使用文章均值向量
        user_interest_vector = mean_article_vector

    return user_interest_vector.astype('float32')


def save_user_interest_vector(user_id, user_interest_vector):
    collection_user_vectors.update_one(
        {'user_id': user_id},
        {'$set': {'vector': user_interest_vector.tolist()}},
        upsert=True
    )


def process_and_save_user_interest_vector(user_id: int):
    user_interest_vector = calculate_user_interest_vector(user_id)
    save_user_interest_vector(user_id, user_interest_vector)


# 提供一个用于全局初始化的函数，将所有的用户行为数据转换为用户向量并保存
async def process_and_save_all_user_interest_vector():
    user_ids = collection_behavior.distinct('userId')
    for user_id in user_ids:
        process_and_save_user_interest_vector(user_id)
    print('已处理并保存所有用户向量，共计', len(user_ids), '个用户')


def get_user_interest_vector(user_id):
    user_vector = collection_user_vectors.find_one({'user_id': user_id}, {'_id': 0, 'vector': 1})
    if user_vector is None:
        return None
    return np.array(user_vector['vector']).astype('float32')


def get_all_user_vectors():
    return list(collection_user_vectors.find({}, {'_id': 0, 'user_id': 1, 'vector': 1}))
