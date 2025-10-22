"""
Central Configuration Module for Power System Analysis

Author: Sustainable Power Systems Lab (SPSL)
Web: https://sps-lab.org
Contact: info@sps-lab.org

This module serves as the central configuration hub for the entire power system 
analysis toolkit. It provides a single source of truth for all configurable 
parameters, file mappings, validation settings, and shared utilities.

CONFIGURATION AREAS:
==================

1. Data File Mappings (FILES, COLUMN_PREFIXES)
2. Data Validation Settings (DATA_VALIDATION, ENHANCED_DATA_VALIDATION)  
3. Representative Operations Parameters (REPRESENTATIVE_OPS)
4. Plotting and Visualization Settings (PLOT_STYLE, FIGURE_SIZES)
5. Shared Utility Functions (clean_column_name, convert_numpy_types)

USAGE EXAMPLES:
==============

# Basic configuration access
from system_configuration import FILES, REPRESENTATIVE_OPS

# Use default clustering parameters
k_max = REPRESENTATIVE_OPS['defaults']['k_max']
random_state = REPRESENTATIVE_OPS['defaults']['random_state']

# Access validation settings
power_limits = DATA_VALIDATION['limit_checks']['power_limits']

# Use shared utilities
from system_configuration import clean_column_name, convert_numpy_types
clean_name = clean_column_name('ss_mw_STATION1_132REACTOR_REACTIVE_POWER')
# Result: 'ss_mw_STATION1'

# Convert numpy types for JSON serialization
import numpy as np
data = {'value': np.int64(42), 'array': np.array([1, 2, 3])}
json_safe_data = convert_numpy_types(data)
# Result: {'value': 42, 'array': [1, 2, 3]}
"""

# Data directory
DATA_DIR = 'raw_data/'

# File mapping for different data types
# Note: These are the actual Excel file names used in the system
FILES = {
    'substation_mw': 'substation_active_power.xlsx',
    'substation_mvar': 'substation_reactive_power.xlsx', 
    'wind_power': 'wind_farm_active_power.xlsx',
    'shunt_elements': 'shunt_element_reactive_power.xlsx',
    'gen_voltage': 'generator_voltage_setpoints.xlsx',
    'gen_mvar': 'generator_reactive_power.xlsx'
}

# Column prefixes for merging (to avoid name collisions)
COLUMN_PREFIXES = {
    'substation_mw': 'ss_mw_',
    'substation_mvar': 'ss_mvar_',
    'wind_power': 'wind_mw_',
    'shunt_elements': 'shunt_',
    'gen_voltage': 'gen_v_',
    'gen_mvar': 'gen_mvar_'
}

# Data type descriptions for documentation
DATA_TYPE_DESCRIPTIONS = {
    'substation_mw': 'Substation active power data (MW)',
    'substation_mvar': 'Substation reactive power data (MVAR)',
    'wind_power': 'Wind farm active power data (MW)',
    'shunt_elements': 'Shunt element reactive power data (MVAR)',
    'gen_voltage': 'Generator voltage setpoints data (KV)',
    'gen_mvar': 'Generator reactive power data (MVAR)'
}

# Default settings
DEFAULT_OUTPUT_DIR = 'results'

DEFAULT_VERBOSE = False

# Excel file structure constants
TIMESTAMP_COLUMN = 2  # Column C (0-indexed)
DATA_START_ROW = 5    # Row 6 (0-indexed)
SUBSTATION_NAME_ROW = 1  # Row 2 (0-indexed)
GENERATOR_NAME_ROW = 2   # Row 3 (0-indexed)
DATA_COLUMN_START = 6    # Column G (0-indexed)
DATA_COLUMN_STEP = 2     # Skip every other column 



# Plotting settings
PLOT_STYLE = 'seaborn-v0_8'
PLOT_PALETTE = 'husl'

# Figure sizes for different plot types
FIGURE_SIZES = {
    'timeseries': (12, 6),
    'daily_profile': (10, 6),
    'monthly_profile': (10, 6),
    'comprehensive': (15, 12),

}

# Font sizes for plots
FONT_SIZES = {
    'title': 14,
    'axis_label': 12,
    'legend': 10,
    'tick': 10
}

# Date validation settings
MIN_YEAR = 2000
MAX_YEAR = 2100
MIN_MONTH = 1
MAX_MONTH = 12

# Data validation settings
DATA_VALIDATION = {
    # Type checks for different data categories
    'type_checks': {
        'real_numbers': [
            'ss_mw_',      # Substation active power (MW)
            'ss_mvar_',    # Substation reactive power (MVAR)
            'wind_mw_',       # Wind generation (MW)
            'shunt_mvar_', # Shunt element reactive power (MVAR)
            'gen_mvar_',      # Generator reactive power (MVAR)
            'gen_v_'       # Generator voltage setpoints (KV)
        ],
        'integers': [
            'shunt_tap_'   # Shunt element tap positions
        ]
    },
    
    # Limit checks for different data categories
    'limit_checks': {
        'non_negative': [
            'wind_mw_'        # Wind power cannot be negative
        ],
        'voltage_limits': {
            'min': 0.0,    # Minimum voltage in KV
            'max': 20.0     # Maximum voltage in KV
        },
        'power_limits': {
            'wind': {
                'min_mw': 0,      # Wind power cannot be negative
                'max_mw': 100   # Maximum reasonable wind power in MW
            },
            'substation': {
                'min_mw': -100,  # Substation can consume or produce power
                'max_mw': 100,   # Maximum reasonable substation power in MW
                'min_mvar': -100, # Substation can consume or produce reactive power
                'max_mvar': 100   # Maximum reasonable substation reactive power in MVAR
            },
            'shunt': {
                'min_mvar': -100, # Shunt can consume or produce reactive power
                'max_mvar': 100   # Maximum reasonable shunt reactive power in MVAR
            },
            'generator': {
                'min_q': -100,    # Generator can consume or produce reactive power
                'max_q': 100      # Maximum reasonable generator reactive power in MVAR
            }
        },
        'tap_limits': {
            'min': 0,    # Minimum tap position
            'max': 20      # Maximum tap position
        }
    },
    
    # Gap filling settings
    'gap_filling': {
        'max_gap_steps': 3,     # Maximum gap size for interpolation (in time steps)
        'interpolation_method': 'linear',  # Interpolation method to use
        'max_nan_percentage': 50.0,  # Maximum percentage of NaN values allowed in a row before removal
        'enable_advanced_gap_filling': True,  # Enable advanced gap filling methods
        'advanced_max_gap_steps': 12,  # Maximum gap size for advanced methods (larger than basic)
        'remove_large_gaps_threshold': 24  # Remove gaps larger than this completely
    },
    
    # Data quality thresholds
    'quality_thresholds': {
        'max_missing_percentage': 10.0,  # Maximum percentage of missing data allowed
        'min_valid_records': 100         # Minimum number of valid records required
    }
}

# Validation error messages
VALIDATION_MESSAGES = {
    'type_error': {
        'real_number': 'Value must be a real number',
        'integer': 'Value must be an integer',
        'non_negative': 'Value must be non-negative',
        'voltage_range': 'Voltage must be between {min} and {max} KV',
        'power_range': 'Power must be between 0 and {max} {unit}',
        'tap_range': 'Tap position must be between {min} and {max}'
    },
    'gap_filling': {
        'interpolated': 'Applied linear interpolation to fill {count} gaps of size <= {max_steps} steps',
        'gap_too_large': 'Gap of {size} steps exceeds maximum allowed size of {max_steps} steps',
        'no_interpolation': 'No interpolation applied - gap size {size} exceeds limit of {max_steps}'
    }
}

# Enhanced Data Validation Settings
ENHANCED_DATA_VALIDATION = {
    # General settings
    'enable_ml_validation': True,  # Enable machine learning-based validation methods
    'min_data_points': 10,         # Minimum data points required for analysis
    
    # Statistical outlier detection parameters
    'outlier_detection': {
        'default_methods': ['iqr', 'isolation_forest'],  # Default outlier detection methods
        'contamination': 0.1,                            # Expected proportion of outliers for ML methods
        'zscore_threshold': 3.0,                         # Z-score threshold for outlier detection
        'modified_zscore_threshold': 3.5,                # Modified Z-score threshold
        'iqr_multiplier': 1.5,                          # IQR multiplier for outlier detection
        'mad_constant': 0.6745                          # Constant for modified Z-score (MAD-based)
    },
    
    # Rate of change violation detection
    'rate_validation': {
        'enable_rate_check': True,                       # Enable rate of change validation
        'adaptive_threshold_multiplier': 3.0,           # Multiplier for adaptive threshold (n * std)
        'min_points_for_rate_check': 3                  # Minimum points needed for rate calculation
    },
    
    # Correlation anomaly detection
    'correlation_validation': {
        'enable_correlation_check': True,               # Enable correlation anomaly detection
        'correlation_threshold': 0.5,                  # Minimum correlation threshold for related variables
        'window_size_ratio': 0.2,                      # Window size as ratio of total data (max 50 points)
        'min_window_size': 10,                         # Minimum window size for correlation analysis
        'max_window_size': 50,                         # Maximum window size for correlation analysis
        'correlation_break_threshold': 0.5             # Threshold for detecting correlation breaks
    },
    
    # Power balance validation
    'power_balance': {
        'enable_power_balance_check': True,            # Enable power balance validation
        'tolerance': 0.05,                             # Tolerance for power balance violations (5%)
        'epsilon': 1e-6                                # Small value to avoid division by zero
    },
    
    # Clustering-based anomaly detection
    'clustering_validation': {
        'enable_clustering_check': True,               # Enable clustering-based anomaly detection
        'algorithm': 'DBSCAN',                         # Clustering algorithm to use
        'eps': 0.5,                                    # Maximum distance between samples for DBSCAN
        'min_samples': 5,                              # Minimum samples for core point in DBSCAN
        'min_points_multiplier': 2,                    # Minimum data points = min_samples * multiplier
        'power_column_prefixes': [                     # Column prefixes for power data clustering
            'gen_mvar_', 'ss_mw_', 'ss_mvar_', 'wind_mw_', 'shunt_mvar_', 'shunt_tap_'
        ]
    },
    
    # Variable grouping for correlation analysis
    'variable_groups': {
        'generators': ['gen_mvar_'],
        'substations': ['ss_mw_', 'ss_mvar_'],
        'wind': ['wind_mw_'],
        'shunts': ['shunt_mvar_', 'shunt_tap_'],
        'voltages': ['gen_v_']
    },
    
    # Comprehensive anomaly detection settings
    'comprehensive_detection': {
        'enable_all_methods': True,                    # Enable all detection methods by default
        'fill_gaps_after_detection': True             # Fill gaps after anomaly removal
    },
    
    # Advanced gap filling settings
    'advanced_gap_filling': {
        'enable_advanced_gap_filling': True,          # Enable advanced gap filling methods
        'default_method': 'adaptive',                 # Default method: 'adaptive', 'spline', 'polynomial', 'knn', 'ml'
        'context_size_ratio': 0.25,                   # Context size as ratio of total data (max 48 points)
        'min_context_points': 10,                     # Minimum context points needed for advanced methods
        'spline_smoothing': 0.0,                      # Smoothing parameter for spline (0 = interpolating spline)
        'polynomial_max_degree': 3,                   # Maximum polynomial degree
        'knn_neighbors': 5,                           # Number of neighbors for KNN imputation
        'adaptive_thresholds': {
            'variance_trend_ratio': 0.1,              # Threshold for trend vs variance comparison
            'high_variance_multiplier': 0.5,          # Multiplier for high variance detection
            'small_gap_size': 3,                      # Size threshold for small gaps (use linear)
            'medium_gap_size': 6,                     # Size threshold for medium gaps (use spline)
            'large_gap_size': 12                      # Size threshold for large gaps (use KNN)
        }
    }
}

# Enhanced validation error messages
ENHANCED_VALIDATION_MESSAGES = {
    'outlier_detection': {
        'iqr': 'IQR outlier detected: value outside {lower_bound:.2f} to {upper_bound:.2f} range',
        'zscore': 'Z-score outlier detected: |z-score| > {threshold}',
        'modified_zscore': 'Modified Z-score outlier detected: |modified z-score| > {threshold}',
        'isolation_forest': 'Isolation Forest anomaly detected',
        'lof': 'Local Outlier Factor anomaly detected',
        'insufficient_data': 'Insufficient data points ({count}) for {method} analysis (minimum: {min_required})'
    },
    'rate_validation': {
        'violation': 'Rate of change violation: {rate:.2f} exceeds threshold {threshold:.2f}',
        'insufficient_data': 'Insufficient data points for rate of change analysis (minimum: {min_required})'
    },
    'correlation_validation': {
        'anomaly': 'Correlation anomaly detected: {var1} vs {var2} correlation changed from {expected:.2f} to {observed:.2f}',
        'insufficient_data': 'Insufficient data for correlation analysis in window'
    },
    'power_balance': {
        'violation': 'Power balance violation: {imbalance:.2f}% exceeds tolerance {tolerance:.1f}%',
        'insufficient_data': 'Insufficient generation or load data for power balance validation'
    },
    'clustering': {
        'anomaly': 'Clustering anomaly detected using {algorithm}',
        'insufficient_data': 'Insufficient data points ({count}) for clustering analysis (minimum: {min_required})',
        'insufficient_columns': 'Insufficient power columns ({count}) for clustering analysis (minimum: 2)'
    }
}


# Representative Operations Configuration
REPRESENTATIVE_OPS = {
    # Default parameters for representative operations extraction
    'defaults': {
        'k_max': 10,                    # Maximum number of clusters to test
        'random_state': 42,             # Random seed for reproducibility
        'mapgl_belt_multiplier': 1.1,   # MAPGL belt upper limit (MAPGL * multiplier)
        'fallback_clusters': 2          # Fallback number of clusters if none meet quality criteria
    },
    
    # K-means clustering configuration
    'kmeans': {
        'n_init': 'auto',              # Number of initialization runs for K-means
        'algorithm': 'auto'            # K-means algorithm variant
    },
    
    # Clustering quality thresholds
    'quality_thresholds': {
        'min_silhouette': 0.25,        # Minimum silhouette score for acceptable clustering
        'silhouette_excellent': 0.7,   # Silhouette score threshold for excellent clustering
        'silhouette_good': 0.5,        # Silhouette score threshold for good clustering
        'silhouette_acceptable': 0.25  # Silhouette score threshold for acceptable clustering
    },
    
    # Multi-objective ranking weights for cluster selection
    'ranking_weights': {
        'silhouette_weight': 1000,     # Weight for silhouette score in ranking
        'calinski_harabasz_weight': 1, # Weight for Calinski-Harabasz index in ranking
        'davies_bouldin_weight': 10    # Weight for Davies-Bouldin index in ranking (negative)
    },
    
    # Feature selection configuration
    'feature_columns': {
        'clustering_prefixes': ['ss_mw_', 'ss_mvar_', 'wind_mw_'],  # Column prefixes for clustering features
        'power_injection_types': ['substation_active', 'substation_reactive', 'wind_generation']
    },
    
    # Output file naming
    'output_files': {
        'representative_points': 'representative_operating_points.csv',
        'clustering_summary': 'clustering_summary.txt'
    },
    
    # Clustering validation and diagnostics
    'validation': {
        'min_data_points': 10,         # Minimum data points required for clustering
        'max_features_to_display': 10, # Maximum number of features to display in summaries
        'display_clusters_limit': 20   # Maximum number of clusters to display detailed info
    }
}

# Utility functions

def convert_numpy_types(obj):
    """
    Convert numpy types to native Python types for JSON serialization.
    
    This function recursively converts numpy data types to native Python types
    to ensure JSON serialization compatibility.
    
    Parameters
    ----------
    obj : any
        Object to convert (can be numpy types, dict, list, or native Python types)
        
    Returns
    -------
    any
        Object with numpy types converted to native Python types
        
    Examples
    --------
    >>> import numpy as np
    >>> data = {'value': np.int64(42), 'array': np.array([1, 2, 3])}
    >>> converted = convert_numpy_types(data)
    >>> print(converted)
    {'value': 42, 'array': [1, 2, 3]}
    """
    import numpy as np
    
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


def clean_column_name(col_name):
    """
    Remove specific suffixes from column names for cleaner CSV output.
    
    This function standardizes column names by removing verbose suffixes that
    are commonly found in power system data files. The cleaned names are more
    readable and suitable for analysis outputs.
    
    Args:
        col_name (str): Original column name to clean
        
    Returns:
        str: Cleaned column name with suffix removed if found
        
    Examples:
        >>> clean_column_name('ss_mw_STATION1_132REACTOR_REACTIVE_POWER')
        'ss_mw_STATION1'
        >>> clean_column_name('gen_mvar_GEN1_GEN_GENERATED_MVAR')
        'gen_mvar_GEN1'
        >>> clean_column_name('simple_name')
        'simple_name'
    """
    # Remove specific suffixes that make column names verbose
    suffixes_to_remove = [
        '_132REACTOR_REACTIVE_POWER',
        '_GEN_GENERATED_MVAR', 
        '_132REACTOR_TAP_POSITION',
        '_TOTAL_GEN_MW'
    ]
    
    cleaned_name = col_name
    for suffix in suffixes_to_remove:
        if cleaned_name.endswith(suffix):
            cleaned_name = cleaned_name[:-len(suffix)]
            break
    
    return cleaned_name 