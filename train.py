from gensim.models import Word2Vec
from pre_process import pre_process, pre_process_single_article
import numpy as np
import os

MODEL_PATH = 'word2vec.model'
MIN_ARTICLE_COUNT = 20


# 在所有文章上训练Word2Vec模型并保存
def train_and_save_model():
    # 读取文章数据并进行分词
    sentences, articles = pre_process()

    # 训练模型
    model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)
    model.save(MODEL_PATH)
    return model, articles


# 加载已训练的Word2Vec模型
def load_model():
    if os.path.exists(MODEL_PATH):
        model = Word2Vec.load(MODEL_PATH)
        _, articles = pre_process()
        return model, articles
    else:
        return train_and_save_model()


# 根据文章数量决定是否每次训练模型（这里的逻辑是：如果文章数量小于20，则重新训练模型，防止模型过拟合）
def get_model_and_articles():
    sentences, articles = pre_process()
    if len(articles) < MIN_ARTICLE_COUNT:
        model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)
        return model, articles
    else:
        return load_model()


# 将所有文章转换为向量
def transform_to_vectors():
    model, articles = get_model_and_articles()

    # 获取每篇文章的平均词向量
    def get_article_vector(article_tokens):
        vectors = [model.wv[word] for word in article_tokens if word in model.wv]
        if vectors:
            return sum(vectors) / len(vectors)
        else:
            return np.zeros(model.vector_size)

    # 生成每篇文章的向量
    sentences, _ = pre_process()
    article_vectors = [get_article_vector(article) for article in sentences]
    return article_vectors, articles


# 使用训练好的模型将单篇文章转换为向量
def transform_single_article_to_vector(article):
    model, _ = get_model_and_articles()

    # 预处理单篇文章
    article_tokens = pre_process_single_article(article)

    # 获取文章的平均词向量
    vectors = [model.wv[word] for word in article_tokens if word in model.wv]
    if vectors:
        return sum(vectors) / len(vectors)
    else:
        return np.zeros(model.vector_size)

# 获取模型状态是否正常，文章是否小于5篇
def get_model_status():
    # 检查模型文件是否存在
    model_exists = os.path.exists(MODEL_PATH)

    # 读取文章数据
    sentences, articles = pre_process()

    # 检查文章数量是否小于5篇
    article_count = len(articles)
    articles_less_than_min = article_count < MIN_ARTICLE_COUNT

    return {
        'full_trained_model_exists': model_exists,
        'article_count': article_count,
        'articles_less_than_min': articles_less_than_min
    }