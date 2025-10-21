from typing import List

import numpy as np


def mmr_reranking_optimized(
    query_embedding: List[float],
    search_results: List[List[float]],
    lambda_param: float = 0.5,
    top_k: int = 10,
) -> List[int]:
    """
    | 场景描述 | 推荐 `lambda_param` | 解释与示例 |
    | :--- | :--- | :--- |
    | **传统搜索引擎** | **0.6 ~ 0.8** | 用户希望最相关的结果排在前面。可以接受一定程度重复，但第一页结果必须高度相关。 |
    | **推荐系统 / 探索发现** | **0.3 ~ 0.5** | 目标是展示多样化的内容，避免给用户推荐相同的东西。例如：新闻推荐、商品推荐、内容发现平台。 |
    | **学术检索、法律案例检索** | **0.5 ~ 0.7** | 需要平衡：既要找到最相关的文献/案例，又要覆盖问题的不同方面或不同学派的观点。 |
    | **去除重复/近乎重复的文档** | **0.1 ~ 0.3** | 主要目的是过滤掉内容几乎相同的冗余文档。 |
    """
    if not search_results:
        return []

    n_docs = len(search_results)
    top_k = min(top_k, n_docs)

    doc_embeddings_np = np.array(search_results)
    query_embedding_np = np.array(query_embedding)

    query_norm = np.linalg.norm(query_embedding_np)
    doc_norms = np.linalg.norm(doc_embeddings_np, axis=1)
    relevance_scores = np.dot(doc_embeddings_np, query_embedding_np) / (
        doc_norms * query_norm + 1e-9
    )

    doc_doc_similarities = np.dot(doc_embeddings_np, doc_embeddings_np.T) / (
        np.outer(doc_norms, doc_norms) + 1e-9
    )

    selected_indices = []
    remaining_indices = list(range(n_docs))

    first_selected = np.argmax(relevance_scores)
    selected_indices.append(first_selected)
    remaining_indices.remove(first_selected)

    while len(selected_indices) < top_k and remaining_indices:
        rel_scores = relevance_scores[remaining_indices]
        max_sim_to_selected = np.max(
            doc_doc_similarities[np.ix_(remaining_indices, selected_indices)], axis=1
        )
        mmr_scores = (
            lambda_param * rel_scores - (1 - lambda_param) * max_sim_to_selected
        )

        best_idx_in_remaining = np.argmax(mmr_scores)
        best_idx = remaining_indices[best_idx_in_remaining]

        selected_indices.append(best_idx)
        del remaining_indices[best_idx_in_remaining]

    return selected_indices
