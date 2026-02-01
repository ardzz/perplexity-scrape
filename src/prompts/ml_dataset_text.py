"""Text/NLP dataset research prompt template."""

TEMPLATE = """Research "{topic}" text dataset for natural language processing machine learning.

Provide comprehensive guidance for working with this text data:

1. **Dataset Characterization**: Analyze text length distributions including token counts, word counts, and character statistics across the corpus. Determine vocabulary size and word frequency distributions following Zipf's law patterns. Identify languages present and detect multilingual or code-switched content. Assess document structure including paragraphs, sentences, and formatting elements.

2. **Data Quality Assessment**: Detect duplicate and near-duplicate texts using fingerprinting methods like MinHash and SimHash. Identify labeling noise, annotation errors, and inter-annotator disagreement. Check class imbalance in classification tasks and analyze label distributions. Examine text encoding issues, malformed characters, and special character handling requirements.

3. **Preprocessing Pipeline**: Implement text cleaning including case normalization, punctuation handling, and special character processing. Apply tokenization using subword methods like BPE, WordPiece, and SentencePiece for effective OOV handling. Handle unknown tokens appropriately. Implement language-specific normalization including stemming and lemmatization when appropriate for the task.

4. **Text Representation**: Generate dense vector embeddings using pretrained models like BERT and sentence-transformers for semantic representations. Implement traditional sparse representations including TF-IDF vectors and bag-of-words when appropriate for simpler tasks. Apply positional encoding schemes for transformer architectures. Handle variable sequence lengths with proper padding and truncation strategies.

5. **Model Selection Framework**: For classification tasks, use BERT-based models like RoBERTa and DeBERTa for highest accuracy. For sequence labeling tasks, apply token classification with CRF layers when helpful. For text generation, use GPT-style autoregressive or encoder-decoder models. Balance model size with inference latency requirements.

6. **Supervised Learning Approaches**: Fine-tune state-of-the-art transformers including BERT, RoBERTa, ALBERT, and DeBERTa for classification and NER. Implement LSTM and GRU with attention mechanisms for sequential processing. Apply TextCNN models for efficient text classification. Use learning rate warmup followed by linear or cosine decay.

7. **Unsupervised Learning Approaches**: Apply topic modeling using Latent Dirichlet Allocation and neural topic models like BERTopic for thematic discovery. Implement text clustering using sentence embeddings from models like all-MiniLM. Use UMAP and t-SNE for dimensionality reduction and visualization. Extract keywords using TextRank and YAKE.

8. **Self-Supervised and Semi-Supervised Methods**: Leverage masked language model pretraining for domain adaptation on unlabeled corpus data. Apply data augmentation including back-translation and synonym replacement using WordNet. Implement pseudo-labeling for semi-supervised learning by training on confident model predictions. Use contrastive methods like SimCSE for sentence embeddings.

9. **Code Implementation**: Use HuggingFace transformers library for tokenization and model fine-tuning workflows. Implement custom datasets with dynamic batching and proper attention mask handling. Use Trainer API for standard workflows or custom training loops for advanced needs. Apply gradient accumulation for effective large batch sizes on limited GPU memory.

10. **Evaluation Strategy**: Calculate precision, recall, and F1-score at micro and macro levels for classification tasks. Use BLEU, ROUGE, and METEOR for text generation evaluation. Apply token-level and entity-level metrics for NER tasks. Implement stratified cross-validation maintaining label distributions. Analyze errors systematically by category and confusion patterns.

Include code examples using transformers, tokenizers, datasets, nltk, and spaCy with proper text validation."""
