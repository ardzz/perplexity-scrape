"""Audio dataset research prompt template."""

TEMPLATE = """Research "{topic}" audio dataset for audio machine learning.

Provide comprehensive guidance for working with this audio data:

1. **Dataset Characterization**: Analyze sample rates (8kHz for telephony, 16kHz for speech, 44.1kHz for music) and duration distributions across the dataset. Identify channel configuration (mono single-channel vs stereo dual-channel). Examine file formats (WAV, MP3, FLAC, OGG) and encoding quality specifications. Assess class distribution for classification tasks. Note total duration in hours and storage requirements.

2. **Data Quality Assessment**: Detect clipping and distortion artifacts where signal exceeds maximum amplitude. Identify silence segments and low-energy regions that may need trimming. Measure background noise levels and estimate Signal-to-Noise Ratio across recordings. Examine recording quality consistency across the dataset. Check for potential labeling errors and timestamp alignment issues.

3. **Preprocessing Pipeline**: Apply resampling to standardize all audio to a consistent sample rate using high-quality interpolation. Implement amplitude normalization and DC offset removal for consistent levels. Apply noise reduction using spectral gating when appropriate for the task. Segment long recordings into fixed-length chunks. Handle variable lengths with padding or truncation using appropriate masking.

4. **Feature Extraction**: Compute time-frequency representations including Short-Time Fourier Transform spectrograms, mel-scaled spectrograms, and log-mel spectrograms. Extract MFCCs for speech and speaker recognition tasks. Calculate additional spectral features like chromagram, spectral centroid, bandwidth, and zero-crossing rate. Apply delta and delta-delta coefficients for temporal dynamics. Consider raw waveform input for end-to-end models.

5. **Model Selection Framework**: For audio classification, use CNNs on spectrogram representations or pretrained audio models. For automatic speech recognition, consider transformer architectures like Whisper and Conformer. For audio generation, apply neural vocoder and diffusion-based models. Balance model complexity with inference speed requirements.

6. **Supervised Learning Approaches**: Train CNN architectures like VGGish and ResNet on mel-spectrogram representations. Fine-tune pretrained self-supervised models like wav2vec 2.0 and HuBERT for downstream tasks. Apply Audio Spectrogram Transformer for classification. Use CTC loss for speech recognition and sequence-to-sequence tasks. Implement learning rate scheduling with warmup.

7. **Unsupervised Learning Approaches**: Apply clustering algorithms on audio embeddings from pretrained models for organizing sound collections. Train variational autoencoders for generative audio representations. Use PANNs for unsupervised feature extraction. Implement anomaly detection for audio quality monitoring and outlier identification.

8. **Self-Supervised and Semi-Supervised Methods**: Leverage contrastive pretraining on large unlabeled audio corpora for robust representations. Apply wav2vec-style masked prediction pretraining. Implement pseudo-labeling for semi-supervised classification. Use self-training with confident predictions iteratively.

9. **Code Implementation**: Use librosa for comprehensive feature extraction and audio analysis functions. Implement data loading with torchaudio transforms for preprocessing and augmentation. Apply audio augmentations using audiomentations including time stretch, pitch shift, and noise injection. Set up training pipelines with proper variable-length batching. Structure code for reproducibility.

10. **Evaluation Strategy**: Calculate accuracy, precision, recall, and F1-score for classification tasks. Use WER and CER for ASR evaluation. Apply MOS estimation and objective metrics like PESQ and STOI for generation quality. Maintain speaker or recording separation in splits to prevent leakage. Analyze errors by audio characteristics.

Include code examples using librosa, torchaudio, soundfile, and audiomentations with proper audio validation."""
