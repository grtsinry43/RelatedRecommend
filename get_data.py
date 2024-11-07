import pymysql
import cfg as cfg

# 从数据库读取所有文章数据
def get_articles():
    connect = pymysql.connect(**cfg.cfg)
    cursor = connect.cursor()
    cursor.execute("SELECT id, title, content FROM article")
    rows = cursor.fetchall()
    print(f"共读取到 {len(rows)} 条数据")
    print(rows)
    cursor.close()
    connect.close()
    return rows

get_articles()
