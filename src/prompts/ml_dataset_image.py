"""Image/computer vision dataset research prompt template."""

TEMPLATE = """Research "{topic}" image dataset for computer vision machine learning.

Provide comprehensive guidance for working with this image data:

1. **Dataset Characterization**: Analyze image dimensions including height, width, and aspect ratio distributions. Identify color channels (RGB three-channel, grayscale single-channel, RGBA with transparency). Examine class distribution for classification tasks and annotation quality for detection and segmentation. Note file formats (JPEG, PNG) and storage requirements.

2. **Data Quality Assessment**: Implement detection for corrupted or unreadable image files using integrity checks. Identify systematic labeling errors through visual inspection and statistical analysis. Assess class imbalance severity and impact on model training. Check for duplicate images that could cause data leakage between train and test splits.

3. **Preprocessing Pipeline**: Apply resizing strategies maintaining aspect ratio using padding or center cropping. Normalize pixel values using ImageNet statistics or dataset-specific values. Handle color space conversions between RGB, BGR, and grayscale when required. Address variable input sizes through consistent resizing or adaptive pooling mechanisms.

4. **Data Augmentation**: Apply geometric transforms including horizontal flips, rotations, and affine transformations for perspective changes. Use color augmentations like brightness, contrast, saturation, and hue jittering. Implement advanced techniques including mixup, cutout, CutMix, and RandAugment policies. Leverage albumentations library for efficient GPU-accelerated augmentation.

5. **Model Selection Framework**: For classification, use CNN backbones like ResNet, EfficientNet, and ConvNeXt. For detection, consider YOLO family or Faster R-CNN. For segmentation, use U-Net or DeepLabV3+. Consider Vision Transformers for large datasets with sufficient samples.

6. **Supervised Learning Approaches**: Fine-tune pretrained ImageNet models using transfer learning for faster convergence. Implement CNNs including ResNet, EfficientNet, and ConvNeXt variants. Apply Vision Transformers and hybrid architectures. Use learning rate scheduling with warmup and cosine decay.

7. **Unsupervised Learning Approaches**: Train autoencoders and variational autoencoders for feature learning and reconstruction. Apply clustering on extracted embeddings from pretrained models for visual pattern discovery. Use pretrained encoders as feature extractors for downstream unsupervised analysis.

8. **Self-Supervised and Semi-Supervised Methods**: Implement contrastive learning approaches including SimCLR, MoCo, and DINO for representation learning. Apply semi-supervised techniques like FixMatch combining consistency regularization with pseudo-labeling. Use knowledge distillation for model compression.

9. **Code Implementation**: Use torchvision for data loading with ImageFolder, transforms, and pretrained weights. Implement custom Dataset classes with proper augmentation integration. Set up mixed precision training for efficiency. Leverage timm library for pretrained model access. Structure code for reproducibility.

10. **Evaluation Strategy**: Calculate accuracy, precision, recall, and F1-score for classification. Use mAP at various IoU thresholds for detection. Apply IoU and Dice coefficient for segmentation. Implement stratified splits maintaining distributions. Visualize predictions and analyze failure cases.

Include code examples using PyTorch, torchvision, albumentations, and timm with proper data validation."""
