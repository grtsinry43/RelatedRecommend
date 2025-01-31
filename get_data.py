import pymysql
from pymongo import MongoClient

import cfg as cfg


# 从数据库读取所有文章数据
def get_articles():
    connect = pymysql.connect(**cfg.mysql_cfg)
    cursor = connect.cursor()

    # 定义带有 WHERE 条件的 SQL 查询
    query = """
        SELECT id, title, content 
        FROM article 
        WHERE deleted_at IS NULL AND is_published = 1
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"首次启动提取数据，共计 {len(rows)} 条")

    cursor.close()
    connect.close()
    return rows


def get_article_by_id(article_id):
    connect = pymysql.connect(**cfg.mysql_cfg)
    cursor = connect.cursor()
    cursor.execute("SELECT id, title, content FROM article WHERE id = %s", (article_id,))
    row = cursor.fetchone()
    cursor.close()
    connect.close()
    return row
