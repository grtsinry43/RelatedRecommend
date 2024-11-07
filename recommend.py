import faiss
import numpy as np

from save import get_article_vectors


def recommend_by_article_id(article_id, k=5):
    """
    根据文章ID推荐相似的文章

    :param article_id: 文章ID
    :param k: 推荐的文章数量
    :return: 推荐的文章ID列表
    """

    # 取出所有文章向量
    article_vectors = get_article_vectors()

    # 将向量转换为 numpy 数组
    vectors = np.array([article['vector'] for article in article_vectors]).astype('float32')

    # 确保向量数组不为空
    if vectors.size == 0:
        raise ValueError("Vectors array is empty")

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
        raise ValueError(f"Article ID {article_id} not found")

    # 将目标向量转换为 numpy 数组
    target_vector = np.array([target_vector]).astype('float32')

    # 使用FAISS索引进行搜索
    distances, indices = index.search(target_vector, k + 1)  # 搜索k+1个结果

    # 获取推荐的文章ID，排除自身
    recommended_ids = [article_vectors[i]['id'] for i in indices[0] if article_vectors[i]['id'] != article_id]

    # 返回前k个推荐结果
    return recommended_ids[:k]
