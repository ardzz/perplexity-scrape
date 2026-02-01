"""
Programming Research Prompt Templates

This module contains all research prompt templates organized by domain.
Each template is optimized for specific research contexts.

Template files export a single TEMPLATE constant string.
This __init__.py aggregates all templates into PROGRAMMING_RESEARCH_PROMPTS.
"""

from .api import TEMPLATE as api_template
from .library import TEMPLATE as library_template
from .implementation import TEMPLATE as implementation_template
from .debugging import TEMPLATE as debugging_template
from .comparison import TEMPLATE as comparison_template
from .general import TEMPLATE as general_template
from .ml_architecture import TEMPLATE as ml_architecture_template
from .ml_training import TEMPLATE as ml_training_template
from .ml_concepts import TEMPLATE as ml_concepts_template
from .ml_frameworks import TEMPLATE as ml_frameworks_template
from .ml_math import TEMPLATE as ml_math_template
from .ml_paper import TEMPLATE as ml_paper_template
from .ml_debugging import TEMPLATE as ml_debugging_template
from .ml_dataset_tabular import TEMPLATE as ml_dataset_tabular_template
from .ml_dataset_image import TEMPLATE as ml_dataset_image_template
from .ml_dataset_text import TEMPLATE as ml_dataset_text_template
from .ml_dataset_timeseries import TEMPLATE as ml_dataset_timeseries_template
from .ml_dataset_audio import TEMPLATE as ml_dataset_audio_template
from .ml_dataset_graph import TEMPLATE as ml_dataset_graph_template
from .ml_dataset_multimodal import TEMPLATE as ml_dataset_multimodal_template

PROGRAMMING_RESEARCH_PROMPTS = {
    "api": api_template,
    "library": library_template,
    "implementation": implementation_template,
    "debugging": debugging_template,
    "comparison": comparison_template,
    "general": general_template,
    "ml_architecture": ml_architecture_template,
    "ml_training": ml_training_template,
    "ml_concepts": ml_concepts_template,
    "ml_frameworks": ml_frameworks_template,
    "ml_math": ml_math_template,
    "ml_paper": ml_paper_template,
    "ml_debugging": ml_debugging_template,
    "ml_dataset_tabular": ml_dataset_tabular_template,
    "ml_dataset_image": ml_dataset_image_template,
    "ml_dataset_text": ml_dataset_text_template,
    "ml_dataset_timeseries": ml_dataset_timeseries_template,
    "ml_dataset_audio": ml_dataset_audio_template,
    "ml_dataset_graph": ml_dataset_graph_template,
    "ml_dataset_multimodal": ml_dataset_multimodal_template,
}

VALID_CATEGORIES = set(PROGRAMMING_RESEARCH_PROMPTS.keys())

__all__ = ["PROGRAMMING_RESEARCH_PROMPTS", "VALID_CATEGORIES"]
