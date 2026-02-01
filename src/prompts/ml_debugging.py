"""ML debugging research prompt template."""

TEMPLATE = """Research "{topic}" debugging issue in machine learning/deep learning.

Provide systematic debugging guidance with mathematical insights:

1. **Problem Description**:
   - Clear definition of the issue
   - How it manifests in training (loss curves, metrics, outputs)
   - Mathematical explanation of why this happens

2. **Root Causes**:
   - List all common causes with mathematical reasoning
   - For each cause: why it leads to this symptom
   - Probability/frequency of each cause

3. **Diagnostic Process**:
   - Step-by-step debugging procedure
   - What to check first (most likely causes)
   - Specific values/behaviors to look for

4. **Detection Code**:
   - Python functions to detect the issue
   - Gradient checking utilities
   - Visualization code for diagnosis

5. **Mathematical Analysis**:
   - Formal analysis of when/why the issue occurs
   - Relevant theorems or bounds
   - Conditions that trigger the problem

6. **Solutions & Fixes**:
   - For each root cause: specific solution
   - Code changes required
   - Hyperparameter adjustments

7. **Prevention Strategies**:
   - Best practices to avoid this issue
   - Architectural choices that help
   - Initialization and normalization techniques

8. **Verification**:
   - How to verify the fix worked
   - Expected behavior after resolution
   - Regression testing approach

9. **Complete Example**:
   - Code demonstrating the problem
   - Code showing the diagnosis
   - Code implementing the fix
   - Before/after comparison

10. **Related Issues**:
    - Other problems with similar symptoms
    - How to differentiate between them
    - Issues that often co-occur

11. **Debugging Checklist**:
    - Quick reference checklist for this issue
    - Commands/snippets to run
    - Expected outputs at each step

Include complete, runnable code for all diagnostic and fix examples."""
