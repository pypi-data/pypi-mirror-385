#!/usr/bin/env python3
"""
Power System Data Analysis Command Line Tool

Author: Sustainable Power Systems Lab (SPSL)
Web: https://sps-lab.org
Contact: info@sps-lab.org

This tool performs comprehensive analysis of power system operational data from multiple Excel files.
It provides a complete command-line interface with enhanced configuration management and clean output formatting.

CONFIGURATION-DRIVEN ARCHITECTURE:
==================================
The tool follows a centralized configuration approach where all parameters, file mappings,
and utility functions are managed in config.py. This design ensures:
- Consistent parameter values across all analysis workflows
- Easy customization without modifying core analysis code
- Maintainable codebase with single source of truth for configuration
- Clean, readable output files using shared utility functions

The tool supports month-based filtering to analyze specific time periods, which significantly
reduces memory usage and processing time for large datasets.

Features:
- Load analysis (Total Load, Net Load) with comprehensive statistics
- Generator categorization (Voltage Control vs PQ Control)
- Wind power analysis with generation statistics
- Reactive power analysis with proper sign conventions
- Representative day extraction from load patterns
- Extreme day identification (minimum and maximum net load)
- Clean column naming for improved output readability (via config.clean_column_name)
- Comprehensive logging and validation

Data File Structure:
The tool expects Excel files with the following structure:

* Substation active power data (MW) - timestamps in column C (row 6+), 
  substation names in row 2 (columns G, I, K, M, etc.), data in row 6+ (columns G, I, K, M, etc.)
* Substation reactive power data (MVAR) - same structure as active power data
* Generator voltage setpoints data (KV) - timestamps in column C (row 6+),
  generator names in row 3 (columns G, I, K, M, etc.), data in row 6+ (columns G, I, K, M, etc.)
* Wind farm active power data (MW) - timestamps in column C (row 6+),
  wind farm names in row 3 (columns G, I, K, M, O, etc.), data in row 6+ (columns G, I, K, M, O, etc.)
* Shunt element reactive power data (MVAR) - timestamps in column C (row 6+),
  shunt element names in row 3 (columns G, I, K, M, etc.), data in row 6+ (columns G, I, K, M, etc.)
* Generator reactive power data (MVAR) - timestamps in column C (row 6+),
  generator names in row 3 (columns G, I, K, M, etc.), data in row 6+ (columns G, I, K, M, etc.)

Usage:

Command Line Interface:
    python power_analysis_cli.py [OPTIONS] [MONTH]

Python Module Import:
    from power_analysis_cli import execute
    success = execute(month="2024-01", save_csv=True, save_plots=True)

Arguments:
    MONTH                  Month to filter data for (format: "YYYY-MM") or None for all data

Command Line Examples:

    # Run full analysis with all outputs for January 2024
    python power_analysis_cli.py 2024-01 --output-dir results --data-dir "raw_data" --save-plots --save-csv --verbose
    
    # Run analysis with specific data directory for March 2024
    python power_analysis_cli.py 2024-03 --data-dir "raw_data" --verbose
    
    # Run analysis and save only summary report for December 2024
    python power_analysis_cli.py 2024-12 --output-dir results --summary-only
    
    # Run analysis for all data (no month filter)
    python power_analysis_cli.py --output-dir results --save-plots --save-csv
    
    # Quick analysis for a specific month with summary only
    python power_analysis_cli.py 2024-06 --summary-only

Python Script Examples:

    # Basic analysis for all data
    from power_analysis_cli import execute
    success, df = execute()
    if success:
        print(f"Analysis completed with {len(df)} time points")
    
    # Analysis for specific month with all outputs
    success, df = execute(
        month="2024-01", 
        data_dir="raw_data", 
        output_dir="results", 
        save_csv=True, 
        save_plots=True, 
        verbose=True
    )
    if success:
        # Use the dataframe for further analysis
        from operating_point_extractor import extract_representative_ops
        rep_df, diag = extract_representative_ops(df, max_power=850, MAPGL=200)
    
    # Summary only analysis
    success, df = execute(month="2024-12", summary_only=True, output_dir="results_dec")
    
    # Custom configuration
    success, df = execute(
        data_dir="my_data_folder",
        output_dir="my_results",
        save_csv=True,
        verbose=True
    )
"""

import argparse
import sys
import os

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for CLI
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import datetime
from pathlib import Path

# Import our custom modules

from .power_system_analytics import calculate_total_load, calculate_net_load, get_load_statistics, categorize_generators, calculate_total_wind, calculate_total_reactive_power
from .power_system_visualizer import plot_load_timeseries, plot_monthly_profile, plot_total_load_daily_profile, plot_net_load_daily_profile, create_comprehensive_plots
from .power_data_validator import DataValidator
from .system_configuration import (
    FILES, COLUMN_PREFIXES, DEFAULT_OUTPUT_DIR, DEFAULT_VERBOSE,
    DATA_DIR, PLOT_STYLE, PLOT_PALETTE,
    FIGURE_SIZES, FONT_SIZES, MIN_YEAR, MAX_YEAR, MIN_MONTH, MAX_MONTH,
    clean_column_name
)

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

class PowerAnalysisCLI:
    """Command line interface for power system data analysis."""
    
    def __init__(self, data_dir=DATA_DIR, output_dir=DEFAULT_OUTPUT_DIR, verbose=DEFAULT_VERBOSE, month=None):
        """
        Initialize the CLI tool.
        
        Args:
            data_dir (str): Directory containing the Excel data files
            output_dir (str): Directory to save output files
            verbose (bool): Whether to print detailed progress information
            month (str): Month to filter data for (format: 'YYYY-MM' or None for all data)
        """
        self.data_dir = data_dir
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.month = month
        self.merged_df = None
        self.total_load = None
        self.net_load = None
        self.total_wind = None
        self.total_reactive_power = None
        self.load_stats = None
        self.generator_categories = None
        self.validation_summary = None
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        # Create logs subdirectory
        self.logs_dir = self.output_dir / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        
        # Set up logging
        if self.month:
            self.log_file = self.logs_dir / f'analysis_{self.month}.log'
        else:
            self.log_file = self.logs_dir / 'analysis.log'
        
    def log(self, message, level='INFO'):
        """Log a message to both console and file."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {level}: {message}"
        
        if self.verbose or level in ['ERROR', 'WARNING']:
            print(log_message)
        
        # Always write to log file
        try:
            # Ensure the logs directory exists
            self.logs_dir.mkdir(exist_ok=True)
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            # If logging fails, just print to console
            print(f"Logging error: {e}")
            print(log_message)
    
    def filter_data_by_month(self, df):
        """Filter DataFrame to include only data for the specified month."""
        if self.month is None:
            return df
        
        try:
            # Convert month string to datetime for comparison
            month_start = pd.to_datetime(f"{self.month}-01")
            # Get the last day of the month and set it to 23:59:59 to include the full day
            month_end = (month_start + pd.offsets.MonthEnd(1)).replace(hour=23, minute=59, second=59)
            
            # Filter data for the specified month
            filtered_df = df[(df.index >= month_start) & (df.index <= month_end)]
            
            self.log(f"Filtered data for {self.month}: {len(filtered_df)} records out of {len(df)} total")
            self.log(f"Date range: {filtered_df.index.min()} to {filtered_df.index.max()}")
            
            return filtered_df
            
        except Exception as e:
            self.log(f"Error filtering data by month: {str(e)}", 'ERROR')
            return df
    
    def load_data(self):
        """Load and merge all data files."""
        try:
            self.log("Starting data loading process...")
            self.log(f"Data directory: {self.data_dir}")
            if self.month:
                self.log(f"Filtering data for month: {self.month}")
            else:
                self.log("Processing all available data (no month filter)")
            
            # Step 1: Load all Excel files individually with debugging
            self.log("Step 1: Loading individual Excel files...")
            dataframes = {}
            
            # Use centralized file mapping from config
            files_dict = FILES
            
            for data_type, filename in files_dict.items():
                try:
                    self.log(f"Loading {data_type}: {filename}")
                    file_path = os.path.join(self.data_dir, filename)
                    
                    if not os.path.exists(file_path):
                        self.log(f"Warning: File not found: {file_path}", 'WARNING')
                        continue
                    
                    # Load the Excel file with proper structure handling
                    df_raw = pd.read_excel(file_path, header=None)
                    
                    # Extract timestamps from column C (index 2), starting from row 6 (index 5)
                    timestamps = df_raw.iloc[5:, 2]  # Column C, starting from row 6
                    
                    # Convert timestamps to datetime
                    timestamps = pd.to_datetime(timestamps)
                    
                    # Get column names based on data type
                    if data_type == 'substation_mw':
                        # Substation names are in row 2 (index 1), columns G, I, K, M, etc.
                        col_names = []
                        for col_idx in range(6, df_raw.shape[1], 2):  # Start from G (index 6), skip every other column
                            if col_idx < df_raw.shape[1]:
                                station_name = df_raw.iloc[1, col_idx]  # Row 2 (index 1)
                                if pd.notna(station_name):
                                    col_names.append(f"ss_mw_{station_name}")
                                else:
                                    col_names.append(f"ss_mw_col_{col_idx}")
                    
                    elif data_type == 'substation_mvar':
                        # Substation names are in row 2 (index 1), columns G, I, K, M, etc.
                        col_names = []
                        for col_idx in range(6, df_raw.shape[1], 2):  # Start from G (index 6), skip every other column
                            if col_idx < df_raw.shape[1]:
                                station_name = df_raw.iloc[1, col_idx]  # Row 2 (index 1)
                                if pd.notna(station_name):
                                    col_names.append(f"ss_mvar_{station_name}")
                                else:
                                    col_names.append(f"ss_mvar_col_{col_idx}")
                    
                    elif data_type == 'gen_voltage':
                        # Generator names are in row 3 (index 2), columns G, I, K, M, etc.
                        col_names = []
                        for col_idx in range(6, df_raw.shape[1], 2):  # Start from G (index 6), skip every other column
                            if col_idx < df_raw.shape[1]:
                                gen_name = df_raw.iloc[2, col_idx]  # Row 3 (index 2)
                                if pd.notna(gen_name):
                                    col_names.append(f"gen_v_{gen_name}")
                                else:
                                    col_names.append(f"gen_v_col_{col_idx}")
                    
                    elif data_type == 'wind_power':
                        # Wind farm names are in row 3 (index 2), columns G, I, K, M, O, etc.
                        col_names = []
                        for col_idx in range(6, df_raw.shape[1], 2):  # Start from G (index 6), skip every other column
                            if col_idx < df_raw.shape[1]:
                                wind_name = df_raw.iloc[2, col_idx]  # Row 3 (index 2)
                                if pd.notna(wind_name):
                                    col_names.append(f"wind_mw_{wind_name}")
                                else:
                                    col_names.append(f"wind_mw_col_{col_idx}")
                    
                    elif data_type == 'shunt_elements':
                        # Shunt element names are in row 3 (index 2)
                        # shunt_mvar_* columns: G3, K3, O3, S3, W3 (names) with data at G6+, K6+, O6+, S6+, W6+
                        # shunt_tap_* columns: I3, M3, Q3, U3, Y3 (names) with data at I6+, M6+, Q6+, U6+, Y6+
                        col_names = []
                        
                        # Define the specific column indices for mvar and tap data
                        mvar_cols = [6, 10, 14, 18, 22]  # G, K, O, S, W
                        tap_cols = [8, 12, 16, 20, 24]   # I, M, Q, U, Y
                        
                        # Process mvar columns
                        for col_idx in mvar_cols:
                            if col_idx < df_raw.shape[1]:
                                shunt_name = df_raw.iloc[2, col_idx]  # Row 3 (index 2)
                                if pd.notna(shunt_name):
                                    col_names.append(f"shunt_mvar_{shunt_name}")
                                else:
                                    col_names.append(f"shunt_mvar_col_{col_idx}")
                        
                        # Process tap columns
                        for col_idx in tap_cols:
                            if col_idx < df_raw.shape[1]:
                                shunt_name = df_raw.iloc[2, col_idx]  # Row 3 (index 2)
                                if pd.notna(shunt_name):
                                    col_names.append(f"shunt_tap_{shunt_name}")
                                else:
                                    col_names.append(f"shunt_tap_col_{col_idx}")
                        
                        # Log the generated column names for debugging
                        self.log(f"Generated shunt column names: {col_names}")
                    
                    elif data_type == 'gen_mvar':
                        # Generator names are in row 3 (index 2), columns G, I, K, M, etc.
                        col_names = []
                        for col_idx in range(6, df_raw.shape[1], 2):  # Start from G (index 6), skip every other column
                            if col_idx < df_raw.shape[1]:
                                gen_name = df_raw.iloc[2, col_idx]  # Row 3 (index 2)
                                if pd.notna(gen_name):
                                    col_names.append(f"gen_mvar_{gen_name}")
                                else:
                                    col_names.append(f"gen_mvar_col_{col_idx}")
                    
                    else:
                        # Default column naming
                        col_names = [f"{data_type}_col_{i}" for i in range(df_raw.shape[1] - 6)]
                    
                    # Get the data starting from row 6 (index 5)
                    data_dict = {}
                    if data_type == 'shunt_elements':
                        # For shunt elements, process only the specific columns for mvar and tap
                        # shunt_mvar_*: G(6), K(10), O(14), S(18), W(22)
                        # shunt_tap_*: I(8), M(12), Q(16), U(20), Y(24)
                        mvar_cols = [6, 10, 14, 18, 22]  # G, K, O, S, W
                        tap_cols = [8, 12, 16, 20, 24]   # I, M, Q, U, Y
                        
                        # Process mvar columns
                        mvar_names = [name for name in col_names if name.startswith('shunt_mvar_')]
                        for i, col_idx in enumerate(mvar_cols):
                            if col_idx < df_raw.shape[1] and i < len(mvar_names):
                                col_name = mvar_names[i]
                                col_data = df_raw.iloc[5:, col_idx].values  # Row 6 (index 5) onwards
                                data_dict[col_name] = col_data
                        
                        # Process tap columns
                        tap_names = [name for name in col_names if name.startswith('shunt_tap_')]
                        for i, col_idx in enumerate(tap_cols):
                            if col_idx < df_raw.shape[1] and i < len(tap_names):
                                col_name = tap_names[i]
                                col_data = df_raw.iloc[5:, col_idx].values  # Row 6 (index 5) onwards
                                data_dict[col_name] = col_data
                    else:
                        # For other data types, process every other column (G, I, K, M, etc.)
                        for i, col_idx in enumerate(range(6, df_raw.shape[1], 2)):
                            if col_idx < df_raw.shape[1] and i < len(col_names):
                                col_name = col_names[i]
                                col_data = df_raw.iloc[5:, col_idx].values  # Row 6 (index 5) onwards
                                data_dict[col_name] = col_data
                    
                    # Create DataFrame with proper structure
                    if data_dict:
                        try:
                            data = pd.DataFrame(data_dict, index=timestamps)
                            self.log(f"Created DataFrame with shape: {data.shape}")
                            
                            # Clean up the data by removing rows with NaT timestamps
                            # Check if index has any NaT values and remove them
                            valid_mask = pd.notna(data.index)
                            data = data[valid_mask]
                            self.log(f"After removing NaT timestamps: {data.shape}")
                            
                            # Convert index to datetime and sort
                            data.index = pd.to_datetime(data.index)
                            data = data.sort_index()
                            self.log(f"After datetime conversion: {data.shape}")
                            
                            # Filter by month if specified
                            data = self.filter_data_by_month(data)
                            self.log(f"After month filtering: {data.shape}")
                            
                            # Skip if no data remains after filtering
                            if len(data) == 0:
                                self.log(f"No data found for {self.month} in {filename}, skipping...", 'WARNING')
                                continue
                            
                            # Data validation will be applied to the final merged dataframe
                            df = data
                        except Exception as e:
                            self.log(f"Error creating DataFrame: {str(e)}", 'ERROR')
                            import traceback
                            self.log(f"Traceback: {traceback.format_exc()}", 'ERROR')
                            raise
                    else:
                        self.log(f"No data columns found in {filename}, skipping...", 'WARNING')
                        continue
                    
                    self.log(f"DataFrame shape: {df.shape}")
                    
                    dataframes[data_type] = df
                    self.log(f"Successfully loaded {data_type}")
                    
                except Exception as e:
                    self.log(f"Error loading {data_type}: {str(e)}", 'ERROR')
                    return False
            
            self.log(f"Successfully loaded {len(dataframes)} data files")
            
            # Step 2: Clean and prepare individual dataframes
            self.log("Step 2: Cleaning and preparing individual dataframes...")
            cleaned_dataframes = {}
            keys_to_delete = []  # Track keys to delete after iteration
            
            for data_type, df in dataframes.items():
                try:
                    self.log(f"Cleaning {data_type}...")
                    
                    # Clean column names
                    df_clean = df.copy()
                    cleaned_columns = []
                    for col in df_clean.columns:
                        col_str = str(col)
                        col_clean = col_str.strip()
                        col_clean = ''.join(c for c in col_clean if c.isalnum() or c in ' _')
                        col_clean = ' '.join(col_clean.split())
                        col_clean = col_clean.replace(' ', '_')
                        col_clean = col_clean.strip('_')
                        cleaned_columns.append(col_clean)
                    
                    df_clean.columns = cleaned_columns
                    
                    # Use centralized column prefixes from config
                    column_prefixes = COLUMN_PREFIXES
                    
                    prefix = column_prefixes.get(data_type, f"{data_type}_")
                    df_prefixed = df_clean.copy()
                    df_prefixed.columns = [
                        col if col.startswith(prefix) else f"{prefix}{col}"
                        for col in df_prefixed.columns
                    ]
                    
                    cleaned_dataframes[data_type] = df_prefixed
                    self.log(f"Successfully cleaned {data_type} - shape: {df_prefixed.shape}")
                    
                    # Track this key for deletion after iteration
                    keys_to_delete.append(data_type)
                    
                except Exception as e:
                    self.log(f"Error cleaning {data_type}: {str(e)}", 'ERROR')
                    return False
            
            # Free original dataframes after iteration to save memory
            for key in keys_to_delete:
                del dataframes[key]
            
            # Step 3: Merge dataframes incrementally with conservative approach
            self.log("Step 3: Merging dataframes incrementally...")
            self.merged_df = None
            cleaned_keys_to_delete = []  # Track keys to delete after iteration
            
            for i, (data_type, df) in enumerate(cleaned_dataframes.items()):
                try:
                    self.log(f"Merging dataframe {i+1}/{len(cleaned_dataframes)}: {data_type}")
                    
                    if self.merged_df is None:
                        self.merged_df = df.copy()
                        self.log(f"Initial dataframe created with shape: {self.merged_df.shape}")
                    else:
                        # Perform outer merge
                        self.log(f"Merging {data_type} (shape: {df.shape}) with existing dataframe (shape: {self.merged_df.shape})")
                        
                        # Check for common timestamps
                        common_timestamps = self.merged_df.index.intersection(df.index)
                        self.log(f"Common timestamps: {len(common_timestamps)}")
                        
                        try:
                            # Perform merge with error handling
                            self.log("Starting merge operation...")
                            
                            # Check if this merge would be too large
                            estimated_size = len(self.merged_df) * (len(self.merged_df.columns) + len(df.columns))
                            self.log(f"Estimated merge size: {estimated_size:,} cells")
                            
                            # Use a more conservative threshold
                            if estimated_size > 5000000:  # 5M cells threshold (much lower)
                                self.log("Large merge detected, using concat approach...")
                                # Use concat instead of merge for very large datasets
                                self.merged_df = pd.concat([self.merged_df, df], axis=1, join='outer')
                            else:
                                # Use regular merge for smaller datasets
                                self.merged_df = self.merged_df.merge(df, left_index=True, right_index=True, how='outer')
                            
                            self.log(f"Merge completed. New shape: {self.merged_df.shape}")
                            
                        except Exception as merge_error:
                            self.log(f"Error during merge operation: {str(merge_error)}", 'ERROR')
                            self.log("Attempting to continue with existing dataframe...")
                            # Continue with the existing merged_df instead of failing completely
                    
                    # Track this key for deletion after iteration
                    cleaned_keys_to_delete.append(data_type)
                    
                except Exception as e:
                    self.log(f"Error merging {data_type}: {str(e)}", 'ERROR')
                    return False
            
            # Free the individual dataframes after iteration to save memory
            for key in cleaned_keys_to_delete:
                del cleaned_dataframes[key]
            
            # Step 4: Apply final validation to merged dataframe
            if self.merged_df is not None:
                self.log("Step 4: Applying final validation to merged dataframe...")
                try:
                    # Apply comprehensive validation to the merged dataframe
                    validator = DataValidator(self)
                    self.merged_df = validator.validate_dataframe(self.merged_df)
                    self.validation_summary = validator.get_validation_summary()
                    
                    self.log("Final validation completed successfully")
                    
                except Exception as e:
                    self.log(f"Error during final validation: {str(e)}", 'ERROR')
                    return False
            
            self.log(f"Final merged DataFrame shape: {self.merged_df.shape}")
            self.log(f"Time range: {self.merged_df.index.min()} to {self.merged_df.index.max()}")
            self.log(f"Number of columns: {len(self.merged_df.columns)}")
            
            return True
            
        except Exception as e:
            self.log(f"Error loading data: {str(e)}", 'ERROR')
            return False
    
    def perform_analysis(self):
        """Perform the main analysis calculations."""
        try:
            self.log("Starting analysis calculations...")
            
            # Calculate total load
            self.log("Calculating total load...")
            self.total_load = calculate_total_load(self.merged_df)
            self.log(f"Total load calculated for {len(self.total_load)} time points")
            
            # Calculate net load
            self.log("Calculating net load...")
            self.net_load = calculate_net_load(self.merged_df, self.total_load)
            self.log(f"Net load calculated for {len(self.net_load)} time points")
            
            # Calculate total wind generation
            self.log("Calculating total wind generation...")
            self.total_wind = calculate_total_wind(self.merged_df)
            self.log(f"Total wind generation calculated for {len(self.total_wind)} time points")
            
            # Calculate total reactive power
            self.log("Calculating total reactive power...")
            self.total_reactive_power = calculate_total_reactive_power(self.merged_df)
            self.log(f"Total reactive power calculated for {len(self.total_reactive_power)} time points")
            
            # Get load statistics
            self.log("Calculating load statistics...")
            self.load_stats = get_load_statistics(self.total_load)
            self.log("Load statistics calculated successfully")
            
            # Categorize generators
            self.log("Categorizing generators...")
            self.generator_categories = categorize_generators(self.merged_df)
            self.log(f"Voltage Control Generators: {len(self.generator_categories['voltage_control'])}")
            self.log(f"PQ Control Generators: {len(self.generator_categories['pq_control'])}")
            
            return True
            
        except Exception as e:
            self.log(f"Error during analysis: {str(e)}", 'ERROR')
            return False
    
    def save_csv_data(self):
        """Save analysis results to CSV files."""
        try:
            self.log("Saving CSV data...")
            
            # Create month-specific filenames if month is specified
            if self.month:
                total_load_file = f'total_load_{self.month}.csv'
                net_load_file = f'net_load_{self.month}.csv'
                stats_file = f'load_statistics_{self.month}.csv'
                gen_categories_file = f'generator_categories_{self.month}.csv'
                all_power_data_file = f'all_power_data_{self.month}.csv'
            else:
                total_load_file = 'total_load.csv'
                net_load_file = 'net_load.csv'
                stats_file = 'load_statistics.csv'
                gen_categories_file = 'generator_categories.csv'
                all_power_data_file = 'all_power_data.csv'
            
            # Save total load
            total_load_df = pd.DataFrame({
                'timestamp': self.total_load.index,
                'total_load_mw': self.total_load.values
            })
            total_load_df.to_csv(self.output_dir / total_load_file, index=False)
            
            # Save net load
            net_load_df = pd.DataFrame({
                'timestamp': self.net_load.index,
                'net_load_mw': self.net_load.values
            })
            net_load_df.to_csv(self.output_dir / net_load_file, index=False)
            
            # Save load statistics
            stats_df = pd.DataFrame([self.load_stats])
            stats_df.to_csv(self.output_dir / stats_file, index=False)
            
            # Save generator categories
            gen_categories = {
                'voltage_control': self.generator_categories['voltage_control'],
                'pq_control': self.generator_categories['pq_control']
            }
            
            # Convert to DataFrame for easier CSV export
            max_len = max(len(gen_categories['voltage_control']), len(gen_categories['pq_control']))
            gen_df = pd.DataFrame({
                'voltage_control': gen_categories['voltage_control'] + [''] * (max_len - len(gen_categories['voltage_control'])),
                'pq_control': gen_categories['pq_control'] + [''] * (max_len - len(gen_categories['pq_control']))
            })
            gen_df.to_csv(self.output_dir / gen_categories_file, index=False)
            
            # Save comprehensive power data CSV with all individual columns
            self.log("Creating comprehensive power data CSV...")
            
            # Start with timestamp column
            power_data_df = pd.DataFrame({'timestamp': self.merged_df.index})
            
            # Add all substation active power columns (ss_mw_*)
            ss_mw_columns = [col for col in self.merged_df.columns if col.startswith('ss_mw_')]
            if ss_mw_columns:
                for col in ss_mw_columns:
                    clean_col_name = clean_column_name(col)
                    power_data_df[clean_col_name] = self.merged_df[col].values
                self.log(f"Added {len(ss_mw_columns)} substation active power columns")
            
            # Add all substation reactive power columns (ss_mvar_*)
            ss_mvar_columns = [col for col in self.merged_df.columns if col.startswith('ss_mvar_')]
            if ss_mvar_columns:
                for col in ss_mvar_columns:
                    clean_col_name = clean_column_name(col)
                    power_data_df[clean_col_name] = self.merged_df[col].values
                self.log(f"Added {len(ss_mvar_columns)} substation reactive power columns")
            
            # Add all shunt element reactive power columns (shunt_mvar_*)
            shunt_mvar_columns = [col for col in self.merged_df.columns if col.startswith('shunt_mvar_')]
            if shunt_mvar_columns:
                for col in shunt_mvar_columns:
                    clean_col_name = clean_column_name(col)
                    power_data_df[clean_col_name] = self.merged_df[col].values
                self.log(f"Added {len(shunt_mvar_columns)} shunt element reactive power (mvar) columns")
            
            # Add all shunt element tap position columns (shunt_tap_*)
            shunt_tap_columns = [col for col in self.merged_df.columns if col.startswith('shunt_tap_')]
            if shunt_tap_columns:
                for col in shunt_tap_columns:
                    clean_col_name = clean_column_name(col)
                    power_data_df[clean_col_name] = self.merged_df[col].values
                self.log(f"Added {len(shunt_tap_columns)} shunt element tap position columns")
            
            # Add all generator reactive power columns (gen_mvar_*)
            gen_mvar_columns = [col for col in self.merged_df.columns if col.startswith('gen_mvar_')]
            if gen_mvar_columns:
                for col in gen_mvar_columns:
                    clean_col_name = clean_column_name(col)
                    power_data_df[clean_col_name] = self.merged_df[col].values
                self.log(f"Added {len(gen_mvar_columns)} generator reactive power columns")
            
            # Add all wind power columns (wind_mw_*)
            wind_columns = [col for col in self.merged_df.columns if col.startswith('wind_mw_')]
            if wind_columns:
                for col in wind_columns:
                    clean_col_name = clean_column_name(col)
                    power_data_df[clean_col_name] = self.merged_df[col].values
                self.log(f"Added {len(wind_columns)} wind power columns")
            
            # Add total load, net load, total wind, and total reactive power
            power_data_df['tot_load'] = self.total_load.values
            power_data_df['net_load'] = self.net_load.values
            power_data_df['tot_wind'] = self.total_wind.values
            power_data_df['tot_reactive'] = self.total_reactive_power.values
            
            # Add attribution comment at the top of the CSV
            attribution_comment = "# Power System Data Analysis Tool - Sustainable Power Systems Lab (SPSL) - https://sps-lab.org\n"
            
            # Save the comprehensive CSV with attribution
            csv_path = self.output_dir / all_power_data_file
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                f.write(attribution_comment)
                power_data_df.to_csv(f, index=False)
            
            self.log(f"Comprehensive power data CSV saved: {csv_path}")
            self.log(f"CSV contains {len(power_data_df.columns)} columns and {len(power_data_df)} rows")
            
            self.log("CSV data saved successfully")
            return True
            
        except Exception as e:
            self.log(f"Error saving CSV data: {str(e)}", 'ERROR')
            return False
    
    def save_plots(self):
        """Generate and save plots."""
        try:
            self.log("Generating plots...")
            
            # Set style for better-looking plots
            plt.style.use(PLOT_STYLE)
            sns.set_palette(PLOT_PALETTE)
            
            # Create month-specific filenames if month is specified
            if self.month:
                comprehensive_file = f'comprehensive_analysis_{self.month}.png'
                timeseries_file = f'load_timeseries_{self.month}.png'
                total_daily_file = f'total_load_daily_profile_{self.month}.png'
                net_daily_file = f'net_load_daily_profile_{self.month}.png'
                monthly_file = f'monthly_profile_{self.month}.png'
            else:
                comprehensive_file = 'comprehensive_analysis.png'
                timeseries_file = 'load_timeseries.png'
                total_daily_file = 'total_load_daily_profile.png'
                net_daily_file = 'net_load_daily_profile.png'
                monthly_file = 'monthly_profile.png'
            
            # Create comprehensive plots (skip monthly analysis if analyzing single month)
            if self.month:
                # For single month analysis, create a simplified comprehensive plot without monthly analysis
                fig, axes = plt.subplots(2, 2, figsize=FIGURE_SIZES['comprehensive'])
                
                # Plot 1: Time series (top left)
                plot_load_timeseries(self.total_load, self.net_load, ax=axes[0, 0])
                
                # Plot 2: Total Load Daily Profile (top right)
                plot_total_load_daily_profile(self.total_load, ax=axes[0, 1])
                
                # Plot 3: Net Load Daily Profile (bottom left)
                plot_net_load_daily_profile(self.net_load, ax=axes[1, 0])
                
                # Plot 4: Statistics summary (bottom right)
                stats = {
                    'Max Load': self.total_load.max(),
                    'Min Load': self.total_load.min(),
                    'Mean Load': self.total_load.mean(),
                    'Max Net Load': self.net_load.max(),
                    'Min Net Load': self.net_load.min(),
                    'Mean Net Load': self.net_load.mean()
                }
                
                axes[1, 1].bar(range(len(stats)), list(stats.values()))
                axes[1, 1].set_title('Load Statistics Summary', fontsize=14, fontweight='bold')
                axes[1, 1].set_xlabel('Statistics', fontsize=12)
                axes[1, 1].set_ylabel('Load (MW)', fontsize=12)
                axes[1, 1].set_xticks(range(len(stats)))
                axes[1, 1].set_xticklabels(list(stats.keys()), rotation=45, ha='right')
                axes[1, 1].grid(True, alpha=0.3)
                
                plt.tight_layout()
                fig.savefig(self.output_dir / comprehensive_file, dpi=300, bbox_inches='tight')
                plt.close(fig)
            else:
                # For full analysis, use the original comprehensive plots with monthly analysis
                fig = create_comprehensive_plots(self.total_load, self.net_load)
                fig.savefig(self.output_dir / comprehensive_file, dpi=300, bbox_inches='tight')
                plt.close(fig)
            
            # Create individual plots
            # Time series plot
            fig, ax = plt.subplots(figsize=FIGURE_SIZES['timeseries'])
            plot_load_timeseries(self.total_load, self.net_load, ax=ax)
            fig.savefig(self.output_dir / timeseries_file, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            # Total Load Daily profile plot
            fig, ax = plt.subplots(figsize=FIGURE_SIZES['daily_profile'])
            plot_total_load_daily_profile(self.total_load, ax=ax)
            fig.savefig(self.output_dir / total_daily_file, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            # Net Load Daily profile plot
            fig, ax = plt.subplots(figsize=FIGURE_SIZES['daily_profile'])
            plot_net_load_daily_profile(self.net_load, ax=ax)
            fig.savefig(self.output_dir / net_daily_file, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            # Monthly profile plot (only create when not analyzing a single month)
            if not self.month:
                fig, ax = plt.subplots(figsize=FIGURE_SIZES['monthly_profile'])
                plot_monthly_profile(self.total_load, self.net_load, ax=ax)
                fig.savefig(self.output_dir / monthly_file, dpi=300, bbox_inches='tight')
                plt.close(fig)
            
            self.log("Plots saved successfully")
            return True
            
        except Exception as e:
            self.log(f"Error saving plots: {str(e)}", 'ERROR')
            return False
    
    def _convert_to_json_serializable(self, obj):
        """
        Convert numpy/pandas types to JSON serializable Python types.
        
        Args:
            obj: Object to convert
            
        Returns:
            JSON serializable object
        """
        import numpy as np
        
        if isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        try:
            self.log("Generating summary report...")
            
            # Generate detailed validation summary report first
            self.generate_validation_summary_report()
            
            # Create month-specific filename if month is specified
            if self.month:
                txt_file = f'analysis_summary_{self.month}.txt'
            else:
                txt_file = 'analysis_summary.txt'
            
            # Find timestamps for min/max values
            max_load_idx = self.total_load.idxmax()
            min_load_idx = self.total_load.idxmin()
            max_net_load_idx = self.net_load.idxmax()
            min_net_load_idx = self.net_load.idxmin()
            max_wind_idx = self.total_wind.idxmax()
            min_wind_idx = self.total_wind.idxmin()
            max_reactive_idx = self.total_reactive_power.idxmax()
            min_reactive_idx = self.total_reactive_power.idxmin()
            
            report = {
                'analysis_timestamp': datetime.now().isoformat(),
                'month_filter': self.month,
                'data_overview': {
                    'total_time_points': len(self.merged_df),
                    'time_range_start': self.merged_df.index.min().isoformat(),
                    'time_range_end': self.merged_df.index.max().isoformat(),
                    'total_variables': len(self.merged_df.columns)
                },
                'load_analysis': {
                    'max_total_load_mw': float(self.load_stats['max_load']),
                    'max_total_load_timestamp': max_load_idx.isoformat(),
                    'min_total_load_mw': float(self.load_stats['min_load']),
                    'min_total_load_timestamp': min_load_idx.isoformat(),
                    'mean_total_load_mw': float(self.load_stats['mean_load']),
                    'std_total_load_mw': float(self.load_stats['std_load'])
                },
                'generator_analysis': {
                    'voltage_control_generators': self.generator_categories['voltage_control'],
                    'pq_control_generators': self.generator_categories['pq_control'],
                    'total_voltage_control': len(self.generator_categories['voltage_control']),
                    'total_pq_control': len(self.generator_categories['pq_control'])
                },
                'net_load_analysis': {
                    'max_net_load_mw': float(self.net_load.max()),
                    'max_net_load_timestamp': max_net_load_idx.isoformat(),
                    'min_net_load_mw': float(self.net_load.min()),
                    'min_net_load_timestamp': min_net_load_idx.isoformat(),
                    'mean_net_load_mw': float(self.net_load.mean()),
                    'std_net_load_mw': float(self.net_load.std())
                },
                'wind_analysis': {
                    'max_total_wind_mw': float(self.total_wind.max()),
                    'max_total_wind_timestamp': max_wind_idx.isoformat(),
                    'min_total_wind_mw': float(self.total_wind.min()),
                    'min_total_wind_timestamp': min_wind_idx.isoformat(),
                    'mean_total_wind_mw': float(self.total_wind.mean()),
                    'std_total_wind_mw': float(self.total_wind.std())
                },
                'reactive_power_analysis': {
                    'max_total_reactive_mvar': float(self.total_reactive_power.max()),
                    'max_total_reactive_timestamp': max_reactive_idx.isoformat(),
                    'min_total_reactive_mvar': float(self.total_reactive_power.min()),
                    'min_total_reactive_timestamp': min_reactive_idx.isoformat(),
                    'mean_total_reactive_mvar': float(self.total_reactive_power.mean()),
                    'std_total_reactive_mvar': float(self.total_reactive_power.std())
                },
                'data_validation': self.validation_summary if self.validation_summary else {}
            }
            
            # Save as text report
            with open(self.output_dir / txt_file, 'w', encoding='utf-8') as f:
                f.write("=== POWER SYSTEM ANALYSIS SUMMARY ===\n\n")
                f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if self.month:
                    f.write(f"Month Filter: {self.month}\n")
                f.write("\n")
                
                f.write("DATA OVERVIEW:\n")
                f.write(f"  Total time points: {report['data_overview']['total_time_points']}\n")
                f.write(f"  Time range: {report['data_overview']['time_range_start'][:10]} to {report['data_overview']['time_range_end'][:10]}\n")
                f.write(f"  Total variables: {report['data_overview']['total_variables']}\n\n")
                
                f.write("LOAD ANALYSIS:\n")
                f.write(f"  Maximum Total Load: {report['load_analysis']['max_total_load_mw']:.2f} MW (at {report['load_analysis']['max_total_load_timestamp']})\n")
                f.write(f"  Minimum Total Load: {report['load_analysis']['min_total_load_mw']:.2f} MW (at {report['load_analysis']['min_total_load_timestamp']})\n")
                f.write(f"  Average Total Load: {report['load_analysis']['mean_total_load_mw']:.2f} MW\n")
                f.write(f"  Load Standard Deviation: {report['load_analysis']['std_total_load_mw']:.2f} MW\n\n")
                
                f.write("NET LOAD ANALYSIS:\n")
                f.write(f"  Maximum Net Load: {report['net_load_analysis']['max_net_load_mw']:.2f} MW (at {report['net_load_analysis']['max_net_load_timestamp']})\n")
                f.write(f"  Minimum Net Load: {report['net_load_analysis']['min_net_load_mw']:.2f} MW (at {report['net_load_analysis']['min_net_load_timestamp']})\n")
                f.write(f"  Average Net Load: {report['net_load_analysis']['mean_net_load_mw']:.2f} MW\n")
                f.write(f"  Net Load Standard Deviation: {report['net_load_analysis']['std_net_load_mw']:.2f} MW\n\n")
                
                f.write("WIND GENERATION ANALYSIS:\n")
                f.write(f"  Maximum Total Wind: {report['wind_analysis']['max_total_wind_mw']:.2f} MW (at {report['wind_analysis']['max_total_wind_timestamp']})\n")
                f.write(f"  Minimum Total Wind: {report['wind_analysis']['min_total_wind_mw']:.2f} MW (at {report['wind_analysis']['min_total_wind_timestamp']})\n")
                f.write(f"  Average Total Wind: {report['wind_analysis']['mean_total_wind_mw']:.2f} MW\n")
                f.write(f"  Wind Generation Standard Deviation: {report['wind_analysis']['std_total_wind_mw']:.2f} MW\n\n")
                
                f.write("REACTIVE POWER ANALYSIS:\n")
                f.write(f"  Maximum Total Reactive Power: {report['reactive_power_analysis']['max_total_reactive_mvar']:.2f} MVAR (at {report['reactive_power_analysis']['max_total_reactive_timestamp']})\n")
                f.write(f"  Minimum Total Reactive Power: {report['reactive_power_analysis']['min_total_reactive_mvar']:.2f} MVAR (at {report['reactive_power_analysis']['min_total_reactive_timestamp']})\n")
                f.write(f"  Average Total Reactive Power: {report['reactive_power_analysis']['mean_total_reactive_mvar']:.2f} MVAR\n")
                f.write(f"  Reactive Power Standard Deviation: {report['reactive_power_analysis']['std_total_reactive_mvar']:.2f} MVAR\n\n")
                
                f.write("GENERATOR ANALYSIS:\n")
                f.write(f"  Voltage Control Generators: {report['generator_analysis']['total_voltage_control']}\n")
                f.write(f"  PQ Control Generators: {report['generator_analysis']['total_pq_control']}\n")
                f.write(f"  Voltage Control List: {', '.join(report['generator_analysis']['voltage_control_generators'])}\n")
                f.write(f"  PQ Control List: {', '.join(report['generator_analysis']['pq_control_generators'])}\n\n")
                
                # Add validation summary
                if self.validation_summary:
                    f.write("DATA VALIDATION SUMMARY:\n")
                    f.write(f"  Type Errors: {self.validation_summary['type_errors_count']}\n")
                    f.write(f"  Limit Errors: {self.validation_summary['limit_errors_count']}\n")
                    f.write(f"  Gaps Filled: {self.validation_summary['gaps_filled']}\n")
                    f.write(f"  Gaps Too Large: {self.validation_summary['gaps_too_large']}\n")
                    f.write(f"  Values Rounded: {self.validation_summary['values_rounded']}\n")
                    f.write(f"  Rows Removed Due to Gaps: {self.validation_summary['rows_removed_due_to_gaps']}\n")
                    f.write(f"  Total Records Processed: {self.validation_summary['total_records_processed']:,}\n")
                    f.write(f"  Records with Errors: {self.validation_summary['records_with_errors']}\n\n")
                    
                    # Add detailed error information
                    if self.validation_summary['type_errors']:
                        f.write("TYPE ERRORS:\n")
                        for error in self.validation_summary['type_errors'][:10]:  # Show first 10 errors
                            f.write(f"  - {error}\n")
                        if len(self.validation_summary['type_errors']) > 10:
                            f.write(f"  ... and {len(self.validation_summary['type_errors']) - 10} more\n")
                        f.write("\n")
                    
                    if self.validation_summary['limit_errors']:
                        f.write("LIMIT ERRORS:\n")
                        for error in self.validation_summary['limit_errors'][:10]:  # Show first 10 errors
                            f.write(f"  - {error}\n")
                        if len(self.validation_summary['limit_errors']) > 10:
                            f.write(f"  ... and {len(self.validation_summary['limit_errors']) - 10} more\n")
                        f.write("\n")
                
                f.write("Analysis completed successfully!\n")
            
            self.log("Summary report generated successfully")
            return True
            
        except Exception as e:
            self.log(f"Error generating summary report: {str(e)}", 'ERROR')
            return False
    
    def generate_validation_summary_report(self):
        """Generate a detailed validation summary report as a separate file."""
        if not self.validation_summary:
            self.log("No validation summary available to generate report", 'WARNING')
            return
            
        try:
            self.log("Generating detailed validation summary report...")
            
            # Create month-specific filename if month is specified
            if self.month:
                validation_file = f'validation_summary_{self.month}.txt'
            else:
                validation_file = 'validation_summary.txt'
            
            validation_path = self.output_dir / validation_file
            
            with open(validation_path, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("POWER SYSTEM DATA VALIDATION SUMMARY REPORT\n")
                f.write("="*80 + "\n\n")
                
                f.write("Author: Sustainable Power Systems Lab (SPSL)\n")
                f.write("Web: https://sps-lab.org\n")
                f.write("Contact: info@sps-lab.org\n\n")
                
                f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if self.month:
                    f.write(f"Data Period: {self.month}\n")
                else:
                    f.write("Data Period: All available data\n")
                f.write(f"Total Time Points Processed: {len(self.merged_df):,}\n")
                f.write(f"Total Variables Processed: {len(self.merged_df.columns)}\n")
                f.write(f"Data Range: {self.merged_df.index.min().strftime('%Y-%m-%d %H:%M:%S')} to {self.merged_df.index.max().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # === VALIDATION OVERVIEW ===
                f.write("="*50 + "\n")
                f.write("VALIDATION PROCESS OVERVIEW\n")
                f.write("="*50 + "\n\n")
                
                f.write(f"Total Records Processed: {self.validation_summary['total_records_processed']:,}\n")
                f.write(f"Records with Validation Issues: {self.validation_summary['records_with_errors']:,}\n")
                f.write(f"Data Type Violations: {self.validation_summary['type_errors_count']:,}\n")
                f.write(f"Limit Violations: {self.validation_summary['limit_errors_count']:,}\n")
                f.write(f"Gaps Successfully Filled: {self.validation_summary['gaps_filled']:,}\n")
                f.write(f"Gaps Too Large to Fill: {self.validation_summary['gaps_too_large']:,}\n")
                f.write(f"Values Rounded: {self.validation_summary['values_rounded']:,}\n")
                f.write(f"Rows Removed Due to Excessive Gaps: {self.validation_summary['rows_removed_due_to_gaps']:,}\n\n")
                
                # === DATA TYPE VIOLATIONS ===
                if self.validation_summary['type_errors']:
                    f.write("="*50 + "\n")
                    f.write("DATA TYPE VIOLATIONS\n")
                    f.write("="*50 + "\n\n")
                    
                    f.write(f"Total Type Violations: {len(self.validation_summary['type_errors'])}\n\n")
                    f.write("Description: These violations occur when data cannot be converted to the expected\n")
                    f.write("numeric format. Common causes include text values in numeric columns or\n") 
                    f.write("missing data represented as text.\n\n")
                    
                    f.write("Treatment: Non-numeric values are converted to NaN (Not a Number) to maintain\n")
                    f.write("data integrity while allowing the analysis to continue.\n\n")
                    
                    # Group violations by column for better organization
                    column_violations = {}
                    for error in self.validation_summary['type_errors']:
                        # Extract column name from error message
                        if 'Column ' in error and ':' in error:
                            column = error.split('Column ')[1].split(':')[0]
                            if column not in column_violations:
                                column_violations[column] = []
                            column_violations[column].append(error)
                    
                    f.write("DETAILED TYPE VIOLATIONS BY COLUMN:\n")
                    f.write("-" * 40 + "\n")
                    for column, violations in column_violations.items():
                        f.write(f"\nColumn: {column}\n")
                        if column.startswith('ss_mw_'):
                            f.write("  Type: Substation Active Power (MW)\n")
                        elif column.startswith('ss_mvar_'):
                            f.write("  Type: Substation Reactive Power (MVAR)\n")
                        elif column.startswith('wind_mw_'):
                            f.write("  Type: Wind Farm Active Power (MW)\n")
                        elif column.startswith('gen_v_'):
                            f.write("  Type: Generator Voltage Setpoint (KV)\n")
                        elif column.startswith('gen_mvar_'):
                            f.write("  Type: Generator Reactive Power (MVAR)\n")
                        elif column.startswith('shunt_mvar_'):
                            f.write("  Type: Shunt Element Reactive Power (MVAR)\n")
                        elif column.startswith('shunt_tap_'):
                            f.write("  Type: Shunt Element Tap Position (Integer)\n")
                        else:
                            f.write("  Type: Unknown/Other\n")
                        
                        f.write(f"  Violations: {len(violations)}\n")
                        for violation in violations[:5]:  # Show first 5 per column
                            f.write(f"    • {violation}\n")
                        if len(violations) > 5:
                            f.write(f"    • ... and {len(violations) - 5} more violations\n")
                    
                    # Add detailed timestamp information for type violations
                    if ('detailed_violations' in self.validation_summary and 
                        'type_violations' in self.validation_summary['detailed_violations'] and
                        self.validation_summary['detailed_violations']['type_violations']):
                        f.write("\nSPECIFIC TYPE VIOLATION TIMESTAMPS:\n")
                        f.write("-" * 40 + "\n")
                        for violation in self.validation_summary['detailed_violations']['type_violations'][:15]:
                            f.write(f"• {violation['timestamp']} - {violation['column']}: ")
                            f.write(f"{violation['description']}\n")
                        if len(self.validation_summary['detailed_violations']['type_violations']) > 15:
                            remaining = len(self.validation_summary['detailed_violations']['type_violations']) - 15
                            f.write(f"  ... and {remaining} more type violations\n")
                    
                    f.write(f"\nNote: Only the first 5 violations per column are shown above.\n")
                    f.write(f"Total violations: {len(self.validation_summary['type_errors'])}\n\n")
                
                # === LIMIT VIOLATIONS ===
                if self.validation_summary['limit_errors']:
                    f.write("="*50 + "\n")
                    f.write("LIMIT VIOLATIONS AND CORRECTIONS\n")
                    f.write("="*50 + "\n\n")
                    
                    f.write(f"Total Limit Violations: {len(self.validation_summary['limit_errors'])}\n\n")
                    f.write("Description: These violations occur when values fall outside the expected\n")
                    f.write("operational ranges for power system equipment. Limits are defined based on\n")
                    f.write("engineering constraints and typical operational parameters.\n\n")
                    
                    f.write("Treatment: Values exceeding limits are either corrected (clamped to valid\n")
                    f.write("ranges) or flagged for further investigation depending on the severity.\n\n")
                    
                    # Group limit violations by column
                    limit_violations = {}
                    for error in self.validation_summary['limit_errors']:
                        # Extract column name from error message
                        if 'Column ' in error and ':' in error:
                            column = error.split('Column ')[1].split(':')[0]
                            if column not in limit_violations:
                                limit_violations[column] = []
                            limit_violations[column].append(error)
                    
                    f.write("DETAILED LIMIT VIOLATIONS BY COLUMN:\n")
                    f.write("-" * 40 + "\n")
                    for column, violations in limit_violations.items():
                        f.write(f"\nColumn: {column}\n")
                        if column.startswith('ss_mw_'):
                            f.write("  Type: Substation Active Power (MW)\n")
                            f.write("  Expected Range: 0 to 1000 MW\n")
                        elif column.startswith('ss_mvar_'):
                            f.write("  Type: Substation Reactive Power (MVAR)\n")
                            f.write("  Expected Range: -500 to 500 MVAR\n")
                        elif column.startswith('wind_mw_'):
                            f.write("  Type: Wind Farm Active Power (MW)\n")
                            f.write("  Expected Range: 0 to 500 MW\n")
                        elif column.startswith('gen_v_'):
                            f.write("  Type: Generator Voltage Setpoint (KV)\n")
                            f.write("  Expected Range: 0.9 to 1.1 KV\n")
                        elif column.startswith('gen_mvar_'):
                            f.write("  Type: Generator Reactive Power (MVAR)\n")
                            f.write("  Expected Range: -300 to 300 MVAR\n")
                        elif column.startswith('shunt_mvar_'):
                            f.write("  Type: Shunt Element Reactive Power (MVAR)\n")
                            f.write("  Expected Range: -100 to 100 MVAR\n")
                        elif column.startswith('shunt_tap_'):
                            f.write("  Type: Shunt Element Tap Position\n")
                            f.write("  Expected Range: 1 to 32 (Integer)\n")
                        else:
                            f.write("  Type: Unknown/Other\n")
                        
                        f.write(f"  Violations: {len(violations)}\n")
                        for violation in violations[:5]:  # Show first 5 per column
                            f.write(f"    • {violation}\n")
                        if len(violations) > 5:
                            f.write(f"    • ... and {len(violations) - 5} more violations\n")
                    
                    # Add detailed timestamp information for limit violations
                    if ('detailed_violations' in self.validation_summary and 
                        'limit_violations' in self.validation_summary['detailed_violations'] and
                        self.validation_summary['detailed_violations']['limit_violations']):
                        f.write("\nSPECIFIC LIMIT VIOLATION TIMESTAMPS:\n")
                        f.write("-" * 40 + "\n")
                        for violation in self.validation_summary['detailed_violations']['limit_violations'][:15]:
                            f.write(f"• {violation['timestamp']} - {violation['column']}: ")
                            f.write(f"{violation['description']}\n")
                        if len(self.validation_summary['detailed_violations']['limit_violations']) > 15:
                            remaining = len(self.validation_summary['detailed_violations']['limit_violations']) - 15
                            f.write(f"  ... and {remaining} more limit violations\n")
                    
                    f.write(f"\nNote: Only the first 5 violations per column are shown above.\n")
                    f.write(f"Total violations: {len(self.validation_summary['limit_errors'])}\n\n")
                
                # === GAP FILLING SUMMARY ===
                f.write("="*50 + "\n")
                f.write("GAP FILLING PROCESS SUMMARY\n")
                f.write("="*50 + "\n\n")
                
                f.write("Description: Missing data points (gaps) in time series are identified and\n")
                f.write("filled using appropriate interpolation methods to maintain data continuity.\n\n")
                
                f.write("Gap Filling Methods:\n")
                f.write("• Small gaps (≤3 time steps): Linear interpolation\n")
                f.write("• Medium gaps (4-6 steps): Cubic spline interpolation (if enhanced validation enabled)\n")
                f.write("• Large gaps (≥24 steps): Marked for removal to maintain data integrity\n\n")
                
                f.write(f"Gap Filling Results:\n")
                f.write(f"• Successfully filled gaps: {self.validation_summary['gaps_filled']:,}\n")
                f.write(f"• Gaps too large to fill: {self.validation_summary['gaps_too_large']:,}\n")
                f.write(f"• Rows removed due to excessive gaps: {self.validation_summary['rows_removed_due_to_gaps']:,}\n\n")
                
                # Add detailed gap filling timestamps
                if ('detailed_violations' in self.validation_summary and 
                    'gap_filling_events' in self.validation_summary['detailed_violations'] and
                    self.validation_summary['detailed_violations']['gap_filling_events']):
                    f.write("SPECIFIC GAP FILLING EVENTS:\n")
                    f.write("-" * 40 + "\n")
                    gap_events = self.validation_summary['detailed_violations']['gap_filling_events']
                    filled_events = [e for e in gap_events if e['method'] == 'linear_interpolation']
                    too_large_events = [e for e in gap_events if e['method'] == 'not_filled_too_large']
                    
                    if filled_events:
                        f.write(f"\nGaps Successfully Filled ({len(filled_events)} events):\n")
                        for event in filled_events[:10]:  # Show first 10
                            f.write(f"• {event['start_timestamp']} to {event['end_timestamp']} - ")
                            f.write(f"{event['column']}: {event['description']}\n")
                        if len(filled_events) > 10:
                            f.write(f"  ... and {len(filled_events) - 10} more gap fills\n")
                    
                    if too_large_events:
                        f.write(f"\nGaps Too Large to Fill ({len(too_large_events)} events):\n")
                        for event in too_large_events[:10]:  # Show first 10
                            f.write(f"• {event['start_timestamp']} to {event['end_timestamp']} - ")
                            f.write(f"{event['column']}: {event['description']}\n")
                        if len(too_large_events) > 10:
                            f.write(f"  ... and {len(too_large_events) - 10} more large gaps\n")
                    f.write("\n")
                
                if self.validation_summary['gaps_filled'] > 0:
                    f.write("Treatment Applied: Linear interpolation was used to estimate missing values\n")
                    f.write("based on surrounding data points. This method preserves trends while\n")
                    f.write("maintaining reasonable estimates for short-term missing data.\n\n")
                
                if self.validation_summary['gaps_too_large'] > 0:
                    f.write("Large Gap Handling: Gaps exceeding the maximum threshold were left as NaN\n")
                    f.write("to avoid introducing unreliable interpolated values over extended periods.\n")
                    f.write("These may require special attention in subsequent analysis.\n\n")
                
                if self.validation_summary['rows_removed_due_to_gaps'] > 0:
                    f.write("Row Removal: Time points with excessive missing data across multiple\n")
                    f.write("variables were removed to maintain overall data quality.\n\n")
                
                # === VALUE ROUNDING SUMMARY ===
                if self.validation_summary['values_rounded'] > 0:
                    f.write("="*50 + "\n")
                    f.write("VALUE ROUNDING SUMMARY\n")
                    f.write("="*50 + "\n\n")
                    
                    f.write(f"Values Rounded: {self.validation_summary['values_rounded']:,}\n\n")
                    f.write("Description: Certain columns require integer values (e.g., shunt tap positions)\n")
                    f.write("but may contain fractional values due to data collection or processing.\n\n")
                    
                    f.write("Treatment: Fractional values in integer columns (primarily shunt_tap_*)\n")
                    f.write("are rounded to the nearest integer to maintain data type consistency\n")
                    f.write("while preserving the closest valid operational state.\n\n")
                    
                    # Add detailed rounding timestamps
                    if ('detailed_violations' in self.validation_summary and 
                        'rounding_events' in self.validation_summary['detailed_violations'] and
                        self.validation_summary['detailed_violations']['rounding_events']):
                        f.write("SPECIFIC ROUNDING EVENTS:\n")
                        f.write("-" * 40 + "\n")
                        rounding_events = self.validation_summary['detailed_violations']['rounding_events']
                        for event in rounding_events[:15]:  # Show first 15
                            f.write(f"• {event['timestamp']} - {event['column']}: ")
                            f.write(f"Rounded {event['original_value']:.3f} to {event['rounded_value']}\n")
                        if len(rounding_events) > 15:
                            remaining = len(rounding_events) - 15
                            f.write(f"  ... and {remaining} more rounding events\n")
                        f.write("\n")
                
                # === ENHANCED VALIDATION SUMMARY (if available) ===
                if ('statistical_outliers_count' in self.validation_summary or 
                    'rate_violations_count' in self.validation_summary):
                    f.write("="*50 + "\n")
                    f.write("ENHANCED VALIDATION SUMMARY\n")
                    f.write("="*50 + "\n\n")
                    
                    f.write("Description: Advanced validation techniques were applied to detect\n")
                    f.write("anomalous patterns and operational inconsistencies.\n\n")
                    
                    if 'statistical_outliers_count' in self.validation_summary:
                        f.write(f"Statistical Outliers Detected: {self.validation_summary.get('statistical_outliers_count', 0):,}\n")
                    if 'rate_violations_count' in self.validation_summary:
                        f.write(f"Rate of Change Violations: {self.validation_summary.get('rate_violations_count', 0):,}\n")
                    if 'correlation_anomalies_count' in self.validation_summary:
                        f.write(f"Correlation Anomalies: {self.validation_summary.get('correlation_anomalies_count', 0):,}\n")
                    if 'power_balance_violations_count' in self.validation_summary:
                        f.write(f"Power Balance Violations: {self.validation_summary.get('power_balance_violations_count', 0):,}\n")
                    f.write("\n")
                
                # === SUMMARY AND RECOMMENDATIONS ===
                f.write("="*50 + "\n")
                f.write("VALIDATION SUMMARY AND RECOMMENDATIONS\n")
                f.write("="*50 + "\n\n")
                
                total_issues = (self.validation_summary['type_errors_count'] + 
                              self.validation_summary['limit_errors_count'] + 
                              self.validation_summary['gaps_too_large'])
                
                if total_issues == 0:
                    f.write("✓ EXCELLENT: No significant validation issues detected.\n")
                    f.write("  The dataset appears to be of high quality with minimal problems.\n\n")
                elif total_issues < 10:
                    f.write("✓ GOOD: Minor validation issues detected but overall data quality is acceptable.\n")
                    f.write("  The issues found are typical for real-world power system data.\n\n")
                elif total_issues < 100:
                    f.write("⚠ MODERATE: Some validation issues detected that may affect analysis quality.\n")
                    f.write("  Review the detailed violations above for specific concerns.\n\n")
                else:
                    f.write("⚠ SIGNIFICANT: Multiple validation issues detected.\n")
                    f.write("  Consider reviewing data collection and processing procedures.\n\n")
                
                f.write("Data Quality Assessment:\n")
                data_quality_score = max(0, 100 - (total_issues / len(self.merged_df) * 100))
                f.write(f"• Overall Data Quality Score: {data_quality_score:.1f}%\n")
                f.write(f"• Time Coverage: {len(self.merged_df):,} time points\n")
                f.write(f"• Variable Coverage: {len(self.merged_df.columns)} variables\n")
                f.write(f"• Successful Gap Fills: {self.validation_summary['gaps_filled']:,}\n\n")
                
                f.write("Recommendations:\n")
                if self.validation_summary['type_errors_count'] > 0:
                    f.write("• Review data collection procedures to minimize non-numeric entries\n")
                if self.validation_summary['limit_errors_count'] > 0:
                    f.write("• Investigate equipment operating outside normal parameters\n")
                if self.validation_summary['gaps_too_large'] > 0:
                    f.write("• Consider improving data acquisition systems to reduce large gaps\n")
                if self.validation_summary['rows_removed_due_to_gaps'] > 0:
                    f.write("• Review periods with excessive missing data for potential system issues\n")
                
                f.write("\nNext Steps:\n")
                f.write("• Proceed with power system analysis using the validated dataset\n")
                f.write("• Monitor validation reports for trends in data quality over time\n")
                f.write("• Consider implementing enhanced validation for critical analysis periods\n\n")
                
                f.write("="*80 + "\n")
                f.write("END OF VALIDATION SUMMARY REPORT\n")
                f.write("="*80 + "\n")
            
            self.log(f"Detailed validation summary saved to: {validation_path}")
            
        except Exception as e:
            self.log(f"Error generating validation summary report: {str(e)}", 'ERROR')
    
    def print_summary(self):
        """Print a summary to the console."""
        print("\n" + "="*50)
        print("POWER SYSTEM ANALYSIS SUMMARY")
        print("="*50)
        
        if self.month:
            print(f"\nMonth Filter: {self.month}")
        
        print(f"\nData Overview:")
        print(f"  Total time points: {len(self.merged_df)}")
        print(f"  Time range: {self.merged_df.index.min().strftime('%Y-%m-%d')} to {self.merged_df.index.max().strftime('%Y-%m-%d')}")
        print(f"  Total variables: {len(self.merged_df.columns)}")
        
        # Find timestamps for min/max values for console output
        max_load_idx = self.total_load.idxmax()
        min_load_idx = self.total_load.idxmin()
        max_net_load_idx = self.net_load.idxmax()
        min_net_load_idx = self.net_load.idxmin()
        max_wind_idx = self.total_wind.idxmax()
        min_wind_idx = self.total_wind.idxmin()
        max_reactive_idx = self.total_reactive_power.idxmax()
        min_reactive_idx = self.total_reactive_power.idxmin()
        
        print(f"\nLoad Analysis:")
        print(f"  Maximum Total Load: {self.load_stats['max_load']:.2f} MW (at {max_load_idx.strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"  Minimum Total Load: {self.load_stats['min_load']:.2f} MW (at {min_load_idx.strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"  Average Total Load: {self.load_stats['mean_load']:.2f} MW")
        print(f"  Load Standard Deviation: {self.load_stats['std_load']:.2f} MW")
        
        print(f"\nNet Load Analysis:")
        print(f"  Maximum Net Load: {self.net_load.max():.2f} MW (at {max_net_load_idx.strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"  Minimum Net Load: {self.net_load.min():.2f} MW (at {min_net_load_idx.strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"  Average Net Load: {self.net_load.mean():.2f} MW")
        print(f"  Net Load Standard Deviation: {self.net_load.std():.2f} MW")
        
        print(f"\nWind Generation Analysis:")
        print(f"  Maximum Total Wind: {self.total_wind.max():.2f} MW (at {max_wind_idx.strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"  Minimum Total Wind: {self.total_wind.min():.2f} MW (at {min_wind_idx.strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"  Average Total Wind: {self.total_wind.mean():.2f} MW")
        print(f"  Wind Generation Standard Deviation: {self.total_wind.std():.2f} MW")
        
        print(f"\nReactive Power Analysis:")
        print(f"  Maximum Total Reactive Power: {self.total_reactive_power.max():.2f} MVAR (at {max_reactive_idx.strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"  Minimum Total Reactive Power: {self.total_reactive_power.min():.2f} MVAR (at {min_reactive_idx.strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"  Average Total Reactive Power: {self.total_reactive_power.mean():.2f} MVAR")
        print(f"  Reactive Power Standard Deviation: {self.total_reactive_power.std():.2f} MVAR")
        
        print(f"\nGenerator Analysis:")
        print(f"  Voltage Control Generators: {len(self.generator_categories['voltage_control'])}")
        print(f"  PQ Control Generators: {len(self.generator_categories['pq_control'])}")
        
        # Add validation summary to console output
        if self.validation_summary:
            print(f"\nData Validation Summary:")
            print(f"  Type Errors: {self.validation_summary['type_errors_count']}")
            print(f"  Limit Errors: {self.validation_summary['limit_errors_count']}")
            print(f"  Gaps Filled: {self.validation_summary['gaps_filled']}")
            print(f"  Gaps Too Large: {self.validation_summary['gaps_too_large']}")
            print(f"  Values Rounded: {self.validation_summary['values_rounded']}")
            print(f"  Rows Removed Due to Gaps: {self.validation_summary['rows_removed_due_to_gaps']}")
            print(f"  Total Records Processed: {self.validation_summary['total_records_processed']:,}")
            print(f"  Records with Errors: {self.validation_summary['records_with_errors']}")
        
        print(f"\nOutput files saved to: {self.output_dir}")
        print("="*50)
    
    def run_analysis(self, save_csv=False, save_plots=False, summary_only=False):
        """Run the complete analysis pipeline."""
        self.log("Starting power system analysis...")
        
        # Load data
        if not self.load_data():
            return False
        
        # Perform analysis
        if not self.perform_analysis():
            return False
        
        # Generate summary report
        if not self.generate_summary_report():
            return False
        
        # Print summary to console
        self.print_summary()
        
        # Save additional outputs if requested
        if save_csv and not summary_only:
            if not self.save_csv_data():
                return False
        
        if save_plots and not summary_only:
            if not self.save_plots():
                return False
        
        self.log("Analysis completed successfully!")
        return True


def execute(month=None, data_dir=DATA_DIR, output_dir=DEFAULT_OUTPUT_DIR, 
           save_csv=False, save_plots=False, summary_only=False, verbose=DEFAULT_VERBOSE):
    """
    Execute the power system analysis with specified parameters.
    
    This function can be called directly from other Python scripts to perform
    power system data analysis without using the command line interface. It follows
    a configuration-driven approach for consistent, maintainable analysis.

    CONFIGURATION INTEGRATION:
    ==========================
    - Uses centralized file mappings from config.FILES
    - Applies column prefixes from config.COLUMN_PREFIXES  
    - Leverages data validation settings from config.DATA_VALIDATION
    - Generates clean column names using config.clean_column_name()
    - Creates outputs with standardized naming conventions

    OUTPUT FEATURES:
    ===============
    - CSV files with clean, readable column names (removes verbose suffixes)
    - Comprehensive power data CSV with all variables and calculated metrics
    - JSON and text summary reports with detailed analysis results
    - PNG plots with professional styling and clear visualizations
    - Detailed validation reports with data quality assessment
    
    Args:
        month (str, optional): Month to filter data for (format: "YYYY-MM") or None for all data.
                              Examples: "2024-01", "2024-12", None
        data_dir (str): Directory containing the Excel data files (default: from config.DATA_DIR)
        output_dir (str): Directory to save output files (default: from config.DEFAULT_OUTPUT_DIR)
        save_csv (bool): Save analysis results to CSV files with clean column names (default: False)
        save_plots (bool): Generate and save plots as PNG files (default: False)
        summary_only (bool): Generate only summary report, no CSV or plots (default: False)
        verbose (bool): Print detailed progress information (default: from config.DEFAULT_VERBOSE)
        
    Returns:
        tuple: (success, all_power_df) where:
            - success (bool): True if analysis completed successfully, False otherwise
            - all_power_df (pandas.DataFrame or None): The merged power system dataframe 
              containing all loaded and processed data with original column names.
              None if analysis failed. This dataframe can be used for further analysis
              such as calling extract_representative_ops().
        
    Raises:
        ValueError: If month format is invalid or data directory doesn't exist
        
    Examples:

        # Basic analysis for all data
        success, df = execute()
        if success:
            print(f"Analysis completed with {len(df)} time points")
        
        # Analysis for specific month with plots and CSV
        success, df = execute(month="2024-01", save_csv=True, save_plots=True, verbose=True)
        if success:
            # Use dataframe for representative operations analysis
            from operating_point_extractor import extract_representative_ops
            rep_df, diag = extract_representative_ops(df, max_power=850, MAPGL=200)
        
        # Summary only for a specific month
        success, df = execute(month="2024-12", summary_only=True, output_dir="results_dec")
        
        # Custom data directory
        success, df = execute(data_dir="my_data", output_dir="my_results", save_csv=True)
    """
    # Validate data directory
    if not os.path.exists(data_dir):
        raise ValueError(f"Data directory '{data_dir}' does not exist.")
    
    # Validate month format if provided
    if month:
        try:
            # Validate month format (YYYY-MM)
            if not (len(month) == 7 and month[4] == '-'):
                raise ValueError("Invalid format")
            
            year, month_part = month.split('-')
            year_int = int(year)
            month_int = int(month_part)
            
            if not (MIN_YEAR <= year_int <= MAX_YEAR and MIN_MONTH <= month_int <= MAX_MONTH):
                raise ValueError("Invalid year or month")
                
        except (ValueError, IndexError):
            raise ValueError(f"Invalid month format '{month}'. Expected format: YYYY-MM (e.g., 2024-01)")
    
    # Create CLI instance
    cli = PowerAnalysisCLI(
        data_dir=data_dir,
        output_dir=output_dir,
        verbose=verbose,
        month=month
    )
    
    # Run analysis
    success = cli.run_analysis(
        save_csv=save_csv,
        save_plots=save_plots,
        summary_only=summary_only
    )
    
    # Return both success status and the merged dataframe
    if success:
        return success, cli.merged_df
    else:
        return False, None


def main():
    """Main function to handle command line arguments and run analysis."""
    parser = argparse.ArgumentParser(
        description='Power System Data Analysis Command Line Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python power_analysis_cli.py --output-dir results --save-plots --save-csv
  python power_analysis_cli.py --data-dir "raw_data" --verbose
  python power_analysis_cli.py --output-dir results --summary-only
  
  # Month-specific analysis
  python power_analysis_cli.py 2024-01 --output-dir results --save-plots --save-csv
  python power_analysis_cli.py 2024-03 --data-dir "raw_data" --verbose
  python power_analysis_cli.py 2024-12 --output-dir results --summary-only
        """
    )
    
    parser.add_argument(
        'month',
        nargs='?',
        help='Month to filter data for (format: "YYYY-MM") or None for all data'
    )
    
    parser.add_argument(
        '--data-dir',
        default=DATA_DIR,
        help=f'Directory containing the Excel data files (default: "{DATA_DIR}")'
    )
    
    parser.add_argument(
        '--output-dir',
        default=DEFAULT_OUTPUT_DIR,
        help=f'Directory to save output files (default: "{DEFAULT_OUTPUT_DIR}")'
    )
    
    parser.add_argument(
        '--save-csv',
        action='store_true',
        help='Save analysis results to CSV files'
    )
    
    parser.add_argument(
        '--save-plots',
        action='store_true',
        help='Generate and save plots as PNG files'
    )
    
    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Generate only summary report (no CSV or plots)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed progress information'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Power System Analysis CLI v1.0'
    )
    
    args = parser.parse_args()
    
    try:
        # Call the execute function with parsed arguments
        success, all_power_df = execute(
            month=args.month,
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            save_csv=args.save_csv,
            save_plots=args.save_plots,
            summary_only=args.summary_only,
            verbose=args.verbose
        )
        
        if not success:
            print("Analysis failed. Check the log file for details.")
            sys.exit(1)
        
        print("\nAnalysis completed successfully!")
        print(f"Processed {len(all_power_df)} time points with {len(all_power_df.columns)} variables.")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 