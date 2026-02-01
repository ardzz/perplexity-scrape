"""ML concepts research prompt template."""

TEMPLATE = """Research "{topic}" concept in machine learning/deep learning.

Provide a comprehensive explanation with theoretical foundations:

1. **Formal Definition**:
   - Rigorous mathematical definition using proper notation
   - LaTeX equations for all formulas
   - Clearly define all terms and symbols used

2. **Intuitive Explanation**:
   - Plain-language explanation accessible to beginners
   - Analogies and visual mental models
   - Why this concept matters in practice

3. **Mathematical Framework**:
   - Theoretical foundations and assumptions
   - Key theorems and their implications
   - Proof sketches for important results

4. **Relationship to Other Concepts**:
   - How this connects to related ML concepts
   - Prerequisites for understanding
   - What this concept enables (downstream applications)

5. **Detection & Measurement**:
   - How to identify/measure this concept in practice
   - Metrics and diagnostic tools
   - Visual indicators (learning curves, etc.)

6. **Practical Solutions**:
   - Techniques to address or leverage this concept
   - Code examples showing each technique
   - Trade-offs between different approaches

7. **Code Demonstration**:
   - Complete Python example demonstrating the concept
   - Visualization code (matplotlib/seaborn)
   - Before/after comparison where applicable

8. **Common Misconceptions**:
   - Frequently misunderstood aspects
   - Clarifications with concrete examples
   - Edge cases and exceptions

9. **Exercises**:
   - Theoretical: prove a related result or derive a formula
   - Practical: implement detection/mitigation in code
   - Analysis: interpret given experimental results

10. **Further Reading**:
    - Seminal papers and textbook chapters
    - Online resources and tutorials
    - Research directions and open questions

Emphasize both mathematical rigor and practical applicability."""
