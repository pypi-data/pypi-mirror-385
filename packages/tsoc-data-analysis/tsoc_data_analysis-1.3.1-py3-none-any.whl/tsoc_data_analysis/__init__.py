"""
TSOC Data Analysis Package

A comprehensive Python tool for analyzing the TSOC power system operational data from Excel files.
The tool provides a powerful command-line interface (CLI) and modular Python API for load analysis,
generator categorization, wind power analysis, reactive power calculations, and representative 
operating point extraction.

Author: Sustainable Power Systems Lab (SPSL)
Web: https://sps-lab.org
Contact: info@sps-lab.org

Pure Python Implementation: This tool is implemented entirely in Python. It can be used from 
the command line, imported as Python modules, or integrated into automated analysis pipelines.
"""

__version__ = "1.3.1"
__author__ = "Sustainable Power Systems Lab (SPSL)"
__email__ = "info@sps-lab.org"
__url__ = "https://sps-lab.org"

# Import main modules for easy access
from . import system_configuration
from . import power_system_analytics
from . import power_system_visualizer
from . import power_data_validator
from . import operating_point_extractor
from . import excel_data_processor

# Import commonly used functions for convenience
from .power_system_analytics import (
    calculate_total_load,
    calculate_net_load,
    get_load_statistics,
    categorize_generators,
    calculate_total_wind,
    calculate_total_reactive_power
)

from .operating_point_extractor import (
    extract_representative_ops,
    extract_representative_ops_enhanced,
    loadallpowerdf
)

from .power_analysis_cli import execute

from .power_data_validator import DataValidator

from .system_configuration import (
    FILES,
    COLUMN_PREFIXES,
    DATA_VALIDATION,
    REPRESENTATIVE_OPS,
    clean_column_name,
    convert_numpy_types
)

# Package-level exports
__all__ = [
    # Main modules
    'system_configuration',
    'power_system_analytics', 
    'power_system_visualizer',
    'power_data_validator',
    'operating_point_extractor',
    'excel_data_processor',
    
    # Commonly used functions
    'calculate_total_load',
    'calculate_net_load', 
    'get_load_statistics',
    'categorize_generators',
    'calculate_total_wind',
    'calculate_total_reactive_power',
    'extract_representative_ops',
    'extract_representative_ops_enhanced',
    'loadallpowerdf',
    'execute',
    'DataValidator',
    
    # Configuration
    'FILES',
    'COLUMN_PREFIXES', 
    'DATA_VALIDATION',
    'REPRESENTATIVE_OPS',
    'clean_column_name',
    'convert_numpy_types'
] 