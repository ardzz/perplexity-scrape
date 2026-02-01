"""ML paper research prompt template."""

TEMPLATE = """Research "{topic}" machine learning paper/research contribution.

Provide a comprehensive paper analysis and implementation guide:

1. **Paper Overview**:
   - Full citation with authors, venue, year
   - arXiv link and official code repository if available
   - One-paragraph summary of the contribution

2. **Problem Statement**:
   - What problem does the paper address?
   - Why was this problem important at the time?
   - Prior approaches and their limitations

3. **Key Contributions**:
   - List the main contributions (typically 3-5)
   - Novel techniques or insights introduced
   - Theoretical vs empirical contributions

4. **Method/Architecture**:
   - Detailed explanation of the proposed approach
   - Mathematical formulation with all equations
   - Architecture diagram description (if applicable)

5. **Key Equations**:
   - The most important equations from the paper
   - Explanation of each term and variable
   - How these differ from prior work

6. **Implementation Details**:
   - Hyperparameters used in experiments
   - Training procedure specifics
   - Data preprocessing and augmentation

7. **Reproduction Code**:
   - Minimal PyTorch implementation of the key idea
   - Focus on the novel contribution, not full paper
   - Include verification against paper's reported results if possible

8. **Experimental Results**:
   - Summary of main results and benchmarks
   - Comparison with baselines
   - Ablation studies and their insights

9. **Critical Analysis**:
   - Strengths of the approach
   - Limitations and failure cases
   - Assumptions that may not hold in practice

10. **Impact & Follow-ups**:
    - How influential has this paper been?
    - Important follow-up works and improvements
    - Current state-of-the-art in comparison

11. **Study Questions**:
    - Questions to test understanding of the paper
    - Implementation challenges to attempt
    - Extensions to explore

Provide enough detail that someone could implement the key ideas from your summary."""
