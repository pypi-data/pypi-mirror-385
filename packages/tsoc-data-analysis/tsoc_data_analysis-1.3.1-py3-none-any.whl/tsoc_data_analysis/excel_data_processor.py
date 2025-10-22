"""
Data Loading Module for Power System Analysis

Author: Sustainable Power Systems Lab (SPSL)
Web: https://sps-lab.org
Contact: info@sps-lab.org

This module provides utility functions for processing power system operational data from Excel files.
It includes basic functions for loading individual Excel files, cleaning column names, and 
converting indices to datetime format.

Note: This module provides basic data loading utilities. For comprehensive analysis,
the power_analysis_cli.py script implements a complete data loading and processing pipeline
that handles the complex Excel structure and data validation more efficiently.

Functions:
- load_excel_file(): Load a single Excel file with proper headers and indexing
- clean_column_names(): Clean and standardize DataFrame column names
- convert_index_to_datetime(): Convert DataFrame index to datetime format
"""

import pandas as pd
import os
from .system_configuration import DATA_DIR

# Task 1.2: Function to load a single Excel file
def load_excel_file(filename, data_dir=DATA_DIR):
    """
    Load a single Excel file using the second row as header and first column as index.
    
    Args:
        filename (str): Name of the Excel file to load
        data_dir (str): Directory containing the Excel files
        
    Returns:
        pandas.DataFrame: Loaded data with second row as headers and first column as index
        
    Raises:
        FileNotFoundError: If the specified file is not found
        ValueError: If the file cannot be read or processed
    """
    file_path = os.path.join(data_dir, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Load Excel file with second row (index 1) as header and first column as index
        df = pd.read_excel(file_path, header=1, index_col=0)
        return df
    except Exception as e:
        raise ValueError(f"Error loading file {filename}: {str(e)}")



# Task 2.1: Function to clean column names
def clean_column_names(df):
    """
    Clean column names by stripping whitespace and removing special characters.
    
    Args:
        df (pandas.DataFrame): DataFrame whose column names need to be cleaned
        
    Returns:
        pandas.DataFrame: DataFrame with cleaned column names
    """
    # Create a copy to avoid modifying the original DataFrame
    df_clean = df.copy()
    
    # Clean column names
    cleaned_columns = []
    for col in df_clean.columns:
        # Convert to string if not already
        col_str = str(col)
        # Strip whitespace
        col_clean = col_str.strip()
        # Remove special characters (keep alphanumeric, spaces, and underscores)
        col_clean = ''.join(c for c in col_clean if c.isalnum() or c in ' _')
        # Replace multiple spaces with single space
        col_clean = ' '.join(col_clean.split())
        # Replace spaces with underscores
        col_clean = col_clean.replace(' ', '_')
        # Remove leading/trailing underscores
        col_clean = col_clean.strip('_')
        
        cleaned_columns.append(col_clean)
    
    df_clean.columns = cleaned_columns
    return df_clean

# Task 2.2: Function to convert index to datetime and ensure consistency
def convert_index_to_datetime(df):
    """
    Convert the index of a DataFrame to datetime objects and ensure consistency.
    
    Args:
        df (pandas.DataFrame): DataFrame whose index needs to be converted
        
    Returns:
        pandas.DataFrame: DataFrame with datetime index
    """
    df_dt = df.copy()
    
    try:
        # Convert index to datetime
        df_dt.index = pd.to_datetime(df_dt.index)
        
        # Sort by datetime to ensure chronological order
        df_dt = df_dt.sort_index()
        
        return df_dt
    except Exception as e:
        raise ValueError(f"Error converting index to datetime: {str(e)}") 