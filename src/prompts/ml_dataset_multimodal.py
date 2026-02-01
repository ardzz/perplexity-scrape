"""Multimodal dataset research prompt template."""

TEMPLATE = """Research "{topic}" multimodal dataset for multi-modal machine learning.

Provide comprehensive guidance for working with this multimodal data:

1. **Dataset Characterization**: Identify all modality types present including vision (images, video), text (captions, transcripts), audio (speech, music), and structured tabular data. Analyze alignment status: temporally synchronized, semantically paired, or loosely associated. Examine data scale and quality metrics per individual modality. Assess missing modality patterns across samples. Note storage and computational requirements.

2. **Data Quality Assessment**: Detect missing modalities and analyze missing patterns: random, systematic, or modality-specific. Check alignment and synchronization accuracy between audio-visual modalities. Identify quality disparities where one modality may be significantly noisier than others. Examine labeling consistency for cross-modal annotations. Detect potential modality-specific biases affecting model fairness.

3. **Preprocessing Pipeline**: Apply modality-specific preprocessing pipelines tailored to each data type (image resizing, text tokenization, audio features). Implement temporal alignment for video and audio synchronization using timestamps or cross-correlation. Handle missing modalities through masking, zero-padding, or learned imputation. Standardize feature dimensions across modalities for fusion. Create efficient multi-stream data loading.

4. **Feature Engineering**: Extract embeddings using modality-specific pretrained encoders (ViT for images, BERT for text, wav2vec for audio). Create cross-modal features through learned attention mechanisms capturing inter-modal relationships. Implement shared embedding spaces for direct modality comparison. Apply per-modality dimensionality reduction before fusion if needed. Design fusion-aware representations.

5. **Model Selection Framework**: Choose fusion strategy based on task requirements. For early fusion, concatenate features before processing through shared layers. For late fusion, train modality-specific encoders and combine predictions. For hybrid, use cross-attention at intermediate layers. Consider computational constraints and inference latency requirements.

6. **Supervised Learning Approaches**: Implement cross-attention transformer architectures for modality interaction learning. Apply CLIP-style contrastive training for vision-language alignment with dual encoders. Use unified multimodal transformers like ViLT, FLAVA, and OFA. Train modality-specific encoders followed by learned fusion layers with joint decoders.

7. **Unsupervised Learning Approaches**: Apply cross-modal autoencoders for joint representation learning from unlabeled multimodal data. Implement clustering in shared embedding space for discovering multimodal concepts. Use modality translation (image-to-text, text-to-image) for unsupervised alignment discovery. Extract cross-modal correspondences through projection.

8. **Self-Supervised and Semi-Supervised Methods**: Leverage contrastive learning across modalities like CLIP and CLAP for aligned representations. Apply masked prediction objectives across modalities. Implement pseudo-labeling using confident cross-modal predictions. Use self-supervised pretraining per modality before multimodal fusion to initialize strong encoders.

9. **Code Implementation**: Combine frameworks (transformers, torchvision, torchaudio) in unified training pipelines. Implement multi-stream data loading with proper synchronization using custom collate functions. Create modular architecture designs with pluggable encoders for flexibility. Apply gradient balancing using GradNorm across modalities. Structure code for systematic ablation studies.

10. **Evaluation Strategy**: Calculate per-modality and joint performance metrics to understand contributions. Use cross-modal retrieval metrics (Recall@K) for image-text and audio-text tasks. Apply task-specific evaluation (VQA accuracy, captioning BLEU/CIDEr). Analyze modality contribution through ablations. Test with missing modality scenarios simulating real deployment.

Include code examples using transformers, torchvision, and torchaudio with proper multimodal validation."""
