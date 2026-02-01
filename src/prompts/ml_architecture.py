"""ML architecture research prompt template."""

TEMPLATE = """Research "{topic}" neural network architecture in machine learning/deep learning.

Provide a rigorous yet accessible explanation with mathematical foundations:

1. **Formal Definition**: 
   - Precise mathematical definition of the architecture
   - Use LaTeX notation for all equations (e.g., $f(x) = Wx + b$)
   - Define all variables and their dimensions explicitly

2. **Intuition & Motivation**:
   - Why was this architecture developed? What problem does it solve?
   - Visual mental model: describe how data flows through the architecture
   - Historical context and evolution from prior architectures

3. **Mathematical Formulation**:
   - Forward pass equations with full derivation
   - Key operations (convolution, attention, etc.) with tensor dimensions
   - Complexity analysis: time and space complexity in Big-O notation

4. **Architecture Components**:
   - Layer-by-layer breakdown with input/output shapes
   - Activation functions and their mathematical properties
   - Normalization, regularization, and other components

5. **Code Implementation**:
   - Complete, runnable implementation in PyTorch (preferred) or TensorFlow
   - Include all imports, layer definitions, and forward method
   - Show example usage with dummy data and correct tensor shapes

6. **Training Considerations**:
   - Appropriate loss functions and why
   - Initialization strategies (Xavier, He, etc.) with mathematical justification
   - Common hyperparameters and their typical ranges

7. **Practical Exercises**:
   - Exercise 1: Implement a simplified version from scratch (numpy only)
   - Exercise 2: Modify the architecture for a specific use case
   - Include expected outputs to verify correctness

8. **Key Papers & References**:
   - Original paper with arXiv link if available
   - Follow-up improvements and variants
   - Benchmark results on standard datasets

Use proper mathematical notation throughout. All equations should be in LaTeX format."""
