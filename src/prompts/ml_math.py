"""ML math research prompt template."""

TEMPLATE = """Research "{topic}" mathematical foundations for machine learning.

Provide a rigorous mathematical treatment suitable for ML practitioners:

1. **Formal Definition**:
   - Precise mathematical definition with all notation explained
   - Domain and range specifications
   - Prerequisites from prerequisite fields (linear algebra, calculus, probability)

2. **Intuitive Understanding**:
   - Geometric or visual interpretation
   - Connections to familiar concepts
   - Why ML practitioners need this

3. **Key Theorems & Properties**:
   - State important theorems precisely using LaTeX
   - Proof or proof sketch for each
   - Conditions under which theorems hold

4. **Derivations**:
   - Step-by-step derivation of key results
   - Show all algebraic steps explicitly
   - Highlight common techniques used (chain rule, etc.)

5. **Computational Methods**:
   - Algorithms for computing/evaluating
   - Numerical stability considerations
   - Efficient implementations

6. **Applications in ML**:
   - Specific ML algorithms that use this concept
   - How the math translates to code
   - Real-world examples with data

7. **NumPy/PyTorch Implementation**:
   - Pure NumPy implementation from first principles
   - Comparison with built-in functions
   - Verification of correctness

8. **Worked Examples**:
   - Detailed numerical examples solved by hand
   - Corresponding code verification
   - Visualization where helpful

9. **Exercises**:
   - Proof exercise: derive a related result
   - Computation exercise: calculate by hand, verify with code
   - Application exercise: use in an ML context

10. **References**:
    - Textbook chapters (Bishop, Murphy, Goodfellow)
    - Online lecture notes (Stanford CS229, MIT 18.06)
    - Foundational papers if applicable

All equations must be in proper LaTeX notation. Show complete derivations."""
