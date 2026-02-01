"""ML training research prompt template."""

TEMPLATE = """Research "{topic}" training procedure/optimization in machine learning/deep learning.

Provide a mathematically rigorous explanation of the training algorithm:

1. **Formal Definition**:
   - Mathematical formulation of the optimization objective
   - Loss function definition with LaTeX: $\\mathcal{{L}}(\\theta) = ...$
   - Gradient computation: $\\nabla_\\theta \\mathcal{{L}} = ...$

2. **Algorithm Derivation**:
   - Step-by-step derivation from first principles
   - Show how the update rule is obtained
   - For momentum-based methods: derive the exponential moving average

3. **Update Rules**:
   - Parameter update equation: $\\theta_{{t+1}} = \\theta_t - \\alpha \\cdot g_t$
   - Any auxiliary variables (momentum, adaptive learning rates)
   - Bias correction terms if applicable

4. **Convergence Analysis**:
   - Convergence guarantees (convex vs non-convex)
   - Learning rate requirements for convergence
   - Regret bounds if applicable

5. **Pseudocode & Implementation**:
   - Clear pseudocode showing the complete algorithm
   - PyTorch implementation: both using built-in optimizer and from scratch
   - Comparison showing they produce identical results

6. **Hyperparameter Guidance**:
   - Learning rate: typical ranges and scheduling strategies
   - Momentum/beta parameters: default values and when to adjust
   - Batch size effects on training dynamics

7. **Practical Considerations**:
   - Gradient clipping: when and how
   - Learning rate warmup and decay schedules
   - Debugging tips: what gradient magnitudes to expect

8. **Exercises**:
   - Derive the gradient for a simple loss function by hand
   - Implement the optimizer from scratch and verify against PyTorch
   - Visualize the optimization trajectory on a simple 2D function

9. **References**:
   - Original paper introducing the method
   - Key improvements and variants
   - Empirical comparisons on benchmark tasks

All mathematical derivations should be complete and verifiable."""
