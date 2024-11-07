# RelatedRecommendation

## 1. 介绍 / Introduction

这是我博客框架/内容管理系统`grtblog`的一块"拼图"，用于实现相关推荐功能。
目前的实现方式是基于博客文章进行分词和矢量转换，然后计算文章之间的余弦相似度，最后根据相似度进行推荐。
对于这个推荐模块，建议是以微服务整合到Spring Boot进行使用，当然也可以独立作为服务使用。

This is a piece of "jigsaw puzzle" (a part) of my blog framework/content management system `grtblog`, which is used to
implement related recommendation function.
The current implementation method is to segment and vectorize the blog articles, then calculate the cosine similarity
between the articles, and finally recommend them according to the similarity.
For this recommendation module, it is recommended to integrate it into Spring Boot as a microservice, but it can also be
used as a standalone service.

## 2. 使用 / Usage

### 使用前配置 / Configuration before use
请在项目根目录创建`cfg.py`文件，并按照以下格式配置：
Please create a `cfg.py` file in the root directory of the project and configure it in the following format:

```python
mysql_cfg = {
    'host': 'localhost',
    'user': "YOUR_MYSQL_USER",
    'password': "YOUR_MYSQL_PASSWORD",
    'database': "YOUR_MYSQL_DATABASE",
    'port': 3306
}

mongo_cfg = {
    'host': 'localhost',
    'port': 27017,
    'db': "DB_NAME",
    'collection': "COLLECTION_NAME",
    'user': "YOUR_MONGO_USER",
    'password': "YOUR_MONGO_PASSWORD"
}

app_port = 8001
```

### 使用Docker快速部署 / Deploy with Docker

```shell
docker build -t related-recommendation .
docker run -d -p 8001:8001 --name related-recommendation related-recommendation
```


