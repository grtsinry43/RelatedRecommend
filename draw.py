import matplotlib.pyplot as plt
import numpy as np
from save import get_article_vectors

# 获取所有文章向量
article_vectors = get_article_vectors()

# 将向量转换为 numpy 数组
vectors = np.array([article['vector'] for article in article_vectors]).astype('float32')

# 确保向量数组不为空
if vectors.size == 0:
    raise ValueError("Vectors array is empty")

# 绘制散点图
plt.figure(figsize=(10, 8))
plt.scatter(vectors[:, 0], vectors[:, 1], alpha=0.5)

# 标注文章ID
for article in article_vectors:
    plt.annotate(article['id'], (article['vector'][0], article['vector'][1]))

plt.title('Article Vectors Distribution')
plt.xlabel('Dimension 1')
plt.ylabel('Dimension 2')
plt.show()
