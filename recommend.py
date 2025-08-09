from datetime import datetime

import faiss
import numpy as np

from save import get_article_vectors, get_user_interest_vector, get_user_behaviors


def recommend_by_article_id(article_id, k=5):
    """
    根据文章ID推荐相似的文章

    :param article_id: 文章ID
    :param k: 推荐的文章数量
    :return: 推荐的文章ID列表
    """

    # 取出所有文章向量
    article_vectors = get_article_vectors()

    # 检查是否有文章向量数据
    if not article_vectors:
        print(f"警告: 没有找到任何文章向量数据，文章 {article_id} 无法获得推荐")
        return []

    # 检查文章数量是否足够生成推荐
    if len(article_vectors) <= 1:
        print(f"警告: 文章数量不足，无法为文章 {article_id} 生成推荐")
        return []

    # 将向量转换为 numpy 数组
    vectors = np.array([article['vector'] for article in article_vectors]).astype('float32')

    # 确保向量数组不为空
    if vectors.size == 0:
        print(f"警告: 向量数组为空，文章 {article_id} 无法获得推荐")
        return []

    # 构建索引
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

    # 获取目标文章的向量
    target_vector = None
    for article in article_vectors:
        if article['id'] == article_id:
            target_vector = article['vector']
            break

    if target_vector is None:
        print(f"警告: 文章ID {article_id} 未找到")
        return []

    # 将目标向量转换为 numpy 数组
    target_vector = np.array([target_vector]).astype('float32')

    # 使用FAISS索引进行搜索
    distances, indices = index.search(target_vector, k + 1)  # 搜索k+1个结果

    # 获取推荐的文章ID，排除自身
    recommended_ids = [article_vectors[i]['id'] for i in indices[0] if article_vectors[i]['id'] != article_id]

    # 返回前k个推荐结果，并且转换为字符串类型避免 JSON 序列化问题
    return [str(article_id) for article_id in recommended_ids[:k]]


from datetime import datetime, timedelta

import faiss
import numpy as np

from save import get_article_vectors, get_user_interest_vector, get_user_behaviors


def recommend_by_user_id(user_id, k=5):
    """
    根据用户ID推荐文章

    :param user_id: 用户ID
    :param k: 推荐的文章数量
    :return: 推荐的文章ID列表
    """
    # 获取用户兴趣向量
    user_interest_vector = get_user_interest_vector(user_id)

    # 取出所有文章向量
    article_vectors = get_article_vectors()

    # 检查是否有文章向量数据
    if not article_vectors:
        print(f"警告: 没有找到任何文章向量数据，用户 {user_id} 无法获得推荐")
        return []

    # 检查文章数量是否足够生成推荐
    if len(article_vectors) < k:
        print(f"警告: 文章数量不足，无法为用户 {user_id} 生成足够的推荐")
        # 返回所有可用的文章
        return [str(article['id']) for article in article_vectors]

    # 将向量转换为 numpy 数组
    vectors = np.array([article['vector'] for article in article_vectors]).astype('float32')

    # 确保向量数组不为空
    if vectors.size == 0:
        print(f"警告: 向量数组为空，用户 {user_id} 无法获得推荐")
        return []

    # 获取用户已经看过的文章ID列表及其行为时间
    user_behaviors = get_user_behaviors(user_id)
    seen_articles = {behavior['articleId']: behavior['date'] for behavior in user_behaviors}

    # 构建索引
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

    # 使用FAISS索引进行搜索
    user_interest_vector = np.array([user_interest_vector]).astype('float32')
    distances, indices = index.search(user_interest_vector, k + len(seen_articles))  # 搜索k+len(seen_articles)个结果

    # 获取推荐的文章ID及其距离
    recommended_articles = [(article_vectors[i]['id'], distances[0][j]) for j, i in enumerate(indices[0])]

    # 根据时间衰减系数调整推荐分数
    adjusted_recommendations = []
    for article_id, distance in recommended_articles:
        if article_id in seen_articles:
            days_since_behavior = (datetime.now() - seen_articles[article_id]).days
            decay_factor = 1 / (1 + days_since_behavior / 30)  # 每月衰减一定比例
            adjusted_distance = distance * decay_factor
        else:
            adjusted_distance = distance
        adjusted_recommendations.append((article_id, adjusted_distance))

    # 排除用户最近看过的文章（3天内）
    recent_threshold = datetime.now() - timedelta(days=3)
    filtered_recommendations = [rec for rec in adjusted_recommendations if
                                seen_articles.get(rec[0], recent_threshold) < recent_threshold]

    # 如果过滤后不足k个推荐结果，则放宽时间限制
    if len(filtered_recommendations) < k:
        filtered_recommendations = adjusted_recommendations

    # 按照调整后的距离排序
    filtered_recommendations.sort(key=lambda x: x[1])

    # 返回前k个推荐结果，并且转换为字符串类型避免 JSON 序列化问题
    return [str(article_id) for article_id, _ in filtered_recommendations[:k]]
