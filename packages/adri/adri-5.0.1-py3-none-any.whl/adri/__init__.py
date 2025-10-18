"""
ADRI - Agent Data Readiness Index

The missing data layer for AI agents. Auto-validates data quality with one decorator.

AI agents break on bad data. ADRI fixes that by:
- Auto-validating data quality across 5 dimensions
- Auto-generating quality standards from your data
- Blocking or warning on quality failures
- Working with any framework (LangChain, CrewAI, AutoGen, LlamaIndex, etc.)

Quick Start:
    from adri import adri_protected

    @adri_protected(standard="customer_data", data_param="data")
    def my_agent_function(data):
        # Your agent logic here - now protected!
        return process_data(data)

What happens:
- First run with good data → ADRI generates quality standard
- Future runs → ADRI validates against that standard
- Bad data → Blocked with quality report

CLI Tools:
    adri setup --guide                     # Initialize ADRI
    adri generate-standard data.csv        # Generate standard
    adri assess data.csv --standard std    # Check quality

Five Quality Dimensions:
1. Validity - Data types and formats
2. Completeness - Required fields present
3. Consistency - Cross-field relationships
4. Accuracy - Value ranges and patterns
5. Timeliness - Data freshness

Framework Agnostic:
Works seamlessly with LangChain, CrewAI, AutoGen, LlamaIndex, Haystack,
Semantic Kernel, and any Python function.

Learn more: https://github.com/adri-standard/adri
"""

from .analysis import DataProfiler, StandardGenerator, TypeInference
from .config.loader import ConfigurationLoader

# Core public API imports
from .decorator import adri_protected
from .guard.modes import DataProtectionEngine
from .logging.enterprise import send_to_verodat
from .logging.local import LocalLogger

# Core component imports
from .validator.engine import DataQualityAssessor, ValidationEngine

# Version information - updated import for src/ layout
from .version import __version__, get_version_info

# Public API exports
__all__ = [
    "__version__",
    "get_version_info",
    "adri_protected",
    "DataQualityAssessor",
    "ValidationEngine",
    "DataProtectionEngine",
    "LocalLogger",
    "send_to_verodat",
    "ConfigurationLoader",
    "DataProfiler",
    "StandardGenerator",
    "TypeInference",
]

# Package metadata
__author__ = "Thomas"
__email__ = "thomas@adri.dev"
__license__ = "MIT"
__description__ = (
    "Stop Your AI Agents Breaking on Bad Data - Data Quality Assessment Framework"
)
__url__ = "https://github.com/adri-framework/adri"
# ADRI v5.0.0 - Open-source split release
