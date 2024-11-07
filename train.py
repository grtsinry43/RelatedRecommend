from gensim.models import Word2Vec
from pre_process import pre_process
import numpy as np

def transform_to_vectors():
    # 读取文章数据并进行分词
    sentences, articles = pre_process()

    # 训练模型
    model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

    # 获取每篇文章的平均词向量
    def get_article_vector(article_tokens):
        vectors = [model.wv[word] for word in article_tokens if word in model.wv]
        if vectors:
            return sum(vectors) / len(vectors)
        else:
            return np.zeros(model.vector_size)

    # 生成每篇文章的向量
    article_vectors = [get_article_vector(article) for article in sentences]
    return article_vectors, articles
