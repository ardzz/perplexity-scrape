"""Graph/network dataset research prompt template."""

TEMPLATE = """Research "{topic}" graph dataset for graph neural network machine learning.

Provide comprehensive guidance for working with this graph-structured data:

1. **Dataset Characterization**: Analyze graph statistics including node counts, edge counts, and their distributions. Calculate graph density (ratio of actual to possible edges) and average degree distribution shape (power-law, normal). Identify graph types: homogeneous, heterogeneous with multiple node and edge types, bipartite, or hypergraphs. Examine connectivity, diameter, and clustering coefficient. Assess node and edge feature dimensions.

2. **Data Quality Assessment**: Check for missing node attributes and incomplete edge features that may require imputation strategies. Identify isolated nodes with zero degree and disconnected components needing special handling. Detect self-loops and multi-edges and determine if appropriate for the domain. Examine class imbalance for node and graph classification tasks. Verify edge direction consistency for directed graphs.

3. **Preprocessing Pipeline**: Construct efficient graph representations including sparse adjacency matrices, edge index tensors, and adjacency lists. Apply graph normalization (symmetric normalization for GCN, row normalization for attention). Scale node and edge features with proper per-feature normalization. Implement subgraph sampling strategies like neighbor sampling for training on large graphs. Create train/validation/test masks for transductive settings.

4. **Feature Engineering**: Compute structural node features including degree centrality, betweenness centrality, closeness centrality, and PageRank scores. Generate node embeddings using random walk methods like Node2Vec and DeepWalk for local and global structure. Extract ego-network features summarizing neighborhood statistics. Apply graph-level descriptors for classification tasks. Consider Laplacian positional encodings for transformer models.

5. **Model Selection Framework**: For node-level tasks, use message-passing neural networks aggregating neighbor information. For link prediction, apply encoder-decoder architectures with pairwise scoring functions. For graph classification, implement pooling methods or global readout operations. Consider scalability requirements for graphs with millions of nodes.

6. **Supervised Learning Approaches**: Implement Graph Convolutional Networks and GraphSAGE with aggregation functions (mean, max, LSTM). Apply Graph Attention Networks with multi-head attention for learning edge importance. Use Graph Transformers for expressive representations. Train with appropriate loss functions for node, edge, or graph-level tasks.

7. **Unsupervised Learning Approaches**: Apply Node2Vec and DeepWalk for learning node embeddings without supervision. Train Variational Graph Autoencoders for link prediction and graph generation. Implement community detection algorithms for cluster structure discovery. Use graph clustering methods like MinCut pooling.

8. **Self-Supervised and Semi-Supervised Methods**: Apply graph contrastive learning frameworks like GraphCL, GRACE, and GCC for representation learning. Implement label propagation for semi-supervised node classification leveraging graph homophily. Use self-training with pseudo-labels on unlabeled nodes. Leverage masked feature prediction pretraining.

9. **Code Implementation**: Use PyTorch Geometric for efficient graph data handling, batching, and message-passing layers. Implement custom GNN layers using MessagePassing base class. Set up mini-batch training with NeighborLoader for large graphs. Handle both transductive fixed-graph and inductive unseen-graph settings appropriately.

10. **Evaluation Strategy**: Calculate node classification accuracy and macro F1-score accounting for class imbalance. Use AUC-ROC and Average Precision for link prediction evaluation. Apply graph classification with proper cross-validation ensuring no graph leakage. Maintain structural integrity in splits. Analyze predictions by node degree and graph properties.

Include code examples using PyTorch Geometric, DGL, and NetworkX with proper graph validation."""
