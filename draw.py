import matplotlib.pyplot as plt
import numpy as np
from save import get_article_vectors, get_all_user_vectors

# 获取所有文章向量
article_vectors = get_article_vectors()

# # 获取所有用户向量
# user_vectors = get_all_user_vectors()

# 将向量转换为 numpy 数组
article_vectors_np = np.array([article['vector'] for article in article_vectors]).astype('float32')
# user_vectors_np = np.array([user['vector'] for user in user_vectors]).astype('float32')

# 确保向量数组不为空
if article_vectors_np.size == 0:
    raise ValueError("Article vectors array is empty")
# if user_vectors_np.size == 0:
#     raise ValueError("User vectors array is empty")

# 绘制散点图
plt.figure(figsize=(10, 8))
plt.scatter(article_vectors_np[:, 0], article_vectors_np[:, 1], alpha=0.5, label='Articles')
# plt.scatter(user_vectors_np[:, 0], user_vectors_np[:, 1], alpha=0.5, label='Users', color='red')

# 标注文章ID
for article in article_vectors:
    plt.annotate(article['id'], (article['vector'][0], article['vector'][1]))

# # 标注用户ID
# for user in user_vectors:
#     plt.annotate(user['user_id'], (user['vector'][0], user['vector'][1]), color='red')

plt.title('Article and User Vectors Distribution')
plt.xlabel('Dimension 1')
plt.ylabel('Dimension 2')
plt.legend()
plt.show()
