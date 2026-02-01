"""ML frameworks research prompt template."""

TEMPLATE = """Research "{topic}" in the context of ML/DL frameworks (PyTorch, TensorFlow, JAX, etc.).

Provide framework-specific guidance with implementation details:

1. **Concept Overview**:
   - What this feature/API does and why it's important
   - Which frameworks support it and naming differences
   - When to use this vs alternatives

2. **API Reference**:
   - Function/class signature with all parameters
   - Parameter types and default values
   - Return types and shapes

3. **Under the Hood**:
   - How the framework implements this internally
   - Computational graph implications
   - Memory and performance characteristics

4. **Basic Usage**:
   - Minimal working example with imports
   - Step-by-step explanation of the code
   - Expected output with tensor shapes

5. **Advanced Patterns**:
   - Custom implementations and extensions
   - Integration with training loops
   - Multi-GPU/distributed considerations

6. **Framework Comparison**:
   - PyTorch implementation
   - TensorFlow/Keras equivalent
   - JAX/Flax approach if applicable
   - Highlight API differences and gotchas

7. **Performance Optimization**:
   - Efficient usage patterns
   - Common performance pitfalls
   - Profiling and benchmarking approach

8. **Debugging Guide**:
   - Common errors and their solutions
   - Shape mismatch debugging
   - Gradient flow verification

9. **Complete Example**:
   - Full working code integrating with a training pipeline
   - Include data loading, model definition, training loop
   - Show checkpointing and inference

10. **Best Practices**:
    - Official recommendations from framework documentation
    - Community conventions and patterns
    - Version compatibility notes

All code should be complete, runnable, and follow framework conventions."""
