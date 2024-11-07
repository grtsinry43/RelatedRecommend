import jieba
import re
from get_data import get_articles

# 定义没有意义的语气词连接词作为停用词
stop_words = {'的', '是', '在', '了', '和', '与', '或', '等', '有', '就', '不', '也', '这', '那', '但', '还', '只',
              '或者', '不是', '不会', '不要', '不了', '不会', '不用', '不到', '不了', '不去', '不想', '不让', '不同',
              '不同于', '不同的', '不同意'}

# markdown语法符号作为停用词
stop_words.update(
    {'#', '##', '###', '####', '#####', '######', '*', '**', '***', '~~', '```', '```', '>', '---', '>>', '\n', '\t',
     ' ', '  ', '!', '[', ']', '(', ')', '{', '}', '<', '>', '/', '\\', '|', '&', '^', '%', '$', '@', '`', '~', '_',
     '-', ':', ';', '.', ',', '?', '!', '"', '\'', '=', '，', '。', '？', '！', '“', '”', '‘', '’', '；', '：', '、', '——'})


# 调用结巴分词库进行分词
def cut_words(sentence):
    # 结巴分词
    tokens = jieba.cut(sentence)
    # 去掉停用词
    filter_tokens = [word for word in tokens if word not in stop_words]
    return filter_tokens


def remove_code_blocks(text):
    # 使用正则表达式去掉文章中的代码块
    code_block_pattern = r'```.*?```'
    return re.sub(code_block_pattern, '', text, flags=re.DOTALL)


def pre_process():
    # 读取文章数据并进行分词
    articles = get_articles()
    processed_articles = []
    for item in articles:
        # 去掉代码块
        processed_item = remove_code_blocks(item[2])
        processed_articles.append(cut_words(processed_item))
    # 这里都返回一下，方便id的使用
    return processed_articles, articles
