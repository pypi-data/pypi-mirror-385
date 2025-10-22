"""
Analysis Module for Power System Data

Author: Sustainable Power Systems Lab (SPSL)
Web: https://sps-lab.org
Contact: info@sps-lab.org

This module provides functions for analyzing power system operational data, including
load calculations, generator categorization, and statistical analysis.

The module works with merged DataFrames that contain data from multiple Excel files
with standardized column naming conventions:
- ss_mw_*: Substation active power (MW)
- ss_mvar_*: Substation reactive power (MVAR)
- wind_mw_*: Wind farm active power (MW)
- shunt_mvar_*: Shunt element reactive power (MVAR)
- shunt_tap_*: Shunt element tap position
- gen_v_*: Generator voltage setpoints (KV)
- gen_mvar_*: Generator reactive power (MVAR)

Functions:
- calculate_total_load(): Sum all substation active power to get total system load
- calculate_net_load(): Calculate net load by subtracting wind generation from total load
- get_load_statistics(): Compute statistical measures of load (max, min, mean, std)
- categorize_generators(): Categorize generators into Voltage Control and PQ Control types
"""

import pandas as pd
import numpy as np

# Task 3.1: Function to calculate total load
def calculate_total_load(merged_df):
    """
    Calculate total load by summing all substation active power columns.
    
    Args:
        merged_df (pandas.DataFrame): Merged DataFrame containing all data
        
    Returns:
        pandas.Series: Time series of total load values
    """
    # Find all columns that start with 'ss_mw_' (substation active power)
    load_columns = [col for col in merged_df.columns if col.startswith('ss_mw_')]
    
    if not load_columns:
        raise ValueError("No substation active power columns found. Expected columns starting with 'ss_mw_'")
    
    # Sum all substation active power columns
    total_load = merged_df[load_columns].sum(axis=1)
    
    return total_load

# Task 3.2: Function to calculate net load
def calculate_net_load(merged_df, total_load=None):
    """
    Calculate net load by subtracting total wind generation from total load.
    
    Args:
        merged_df (pandas.DataFrame): Merged DataFrame containing all data
        total_load (pandas.Series, optional): Pre-calculated total load. If None, will calculate it.
        
    Returns:
        pandas.Series: Time series of net load values
    """
    # Calculate total load if not provided
    if total_load is None:
        total_load = calculate_total_load(merged_df)
    
    # Find all columns that start with 'wind_mw_' (wind generation)
    wind_columns = [col for col in merged_df.columns if col.startswith('wind_mw_')]
    
    if not wind_columns:
        print("Warning: No wind generation columns found. Net load will equal total load.")
        return total_load
    
    # Sum all wind generation columns
    total_wind = merged_df[wind_columns].sum(axis=1)
    
    # Calculate net load
    net_load = total_load - total_wind
    
    return net_load

# Task 3.3: Function to get load statistics
def get_load_statistics(total_load):
    """
    Compute and return the max, min, and mean of the total load.
    
    Args:
        total_load (pandas.Series): Time series of total load values
        
    Returns:
        dict: Dictionary containing max, min, and mean load values
    """
    stats = {
        'max_load': total_load.max(),
        'min_load': total_load.min(),
        'mean_load': total_load.mean(),
        'std_load': total_load.std()
    }
    
    return stats

# Task 3.4: Function to categorize generators by control type
def categorize_generators(merged_df):
    """
    Categorize generators into "Voltage Control" and "PQ Control" based on the rules in FR7.
    
    Rules:
    - Generators with non-zero voltage setpoints are in 'Voltage Control'
    - Generators in the reactive power dataset are in 'PQ Control'
    
    Args:
        merged_df (pandas.DataFrame): Merged DataFrame containing all data
        
    Returns:
        dict: Dictionary with 'voltage_control' and 'pq_control' lists of generator names
    """
    voltage_control_generators = []
    pq_control_generators = []
    
    # Find voltage control generators (from gen_voltage columns with non-zero values)
    gen_v_columns = [col for col in merged_df.columns if col.startswith('gen_v_')]
    
    for col in gen_v_columns:
        # Check if this generator has any non-zero voltage setpoints
        if merged_df[col].notna().any() and (merged_df[col] != 0).any():
            # Extract generator name from column (remove prefix)
            gen_name = col.replace('gen_v_', '')
            voltage_control_generators.append(gen_name)
    
    # Find PQ control generators (from gen_mvar columns)
    gen_mvar_columns = [col for col in merged_df.columns if col.startswith('gen_mvar_')]
    
    for col in gen_mvar_columns:
        # Extract generator name from column (remove prefix)
        gen_name = col.replace('gen_mvar_', '')
        pq_control_generators.append(gen_name)
    
    return {
        'voltage_control': voltage_control_generators,
        'pq_control': pq_control_generators
    }

# Function to calculate total wind generation
def calculate_total_wind(merged_df):
    """
    Calculate total wind generation by summing all wind farm active power columns.
    
    Args:
        merged_df (pandas.DataFrame): Merged DataFrame containing all data
        
    Returns:
        pandas.Series: Time series of total wind generation values
    """
    # Find all columns that start with 'wind_mw_' (wind farm active power)
    wind_columns = [col for col in merged_df.columns if col.startswith('wind_mw_')]
    
    if not wind_columns:
        print("Warning: No wind generation columns found. Returning zero series.")
        return pd.Series(0, index=merged_df.index)
    
    # Sum all wind generation columns
    total_wind = merged_df[wind_columns].sum(axis=1)
    
    return total_wind

# Function to calculate total reactive power
def calculate_total_reactive_power(merged_df):
    """
    Calculate total reactive power by summing all reactive power components with proper signs.
    
    This includes:
    - Substation reactive power (ss_mvar_*) with positive sign (+)
    - Generator reactive power (gen_mvar_*) with negative sign (-)
    - Shunt element reactive power (shunt_mvar_*) with negative sign (-)
    
    Args:
        merged_df (pandas.DataFrame): Merged DataFrame containing all data
        
    Returns:
        pandas.Series: Time series of total reactive power values
    """
    total_reactive = pd.Series(0, index=merged_df.index)
    
    # Add substation reactive power (positive sign)
    ss_mvar_columns = [col for col in merged_df.columns if col.startswith('ss_mvar_')]
    if ss_mvar_columns:
        total_reactive += merged_df[ss_mvar_columns].sum(axis=1)
    
    # Subtract generator reactive power (negative sign)
    gen_mvar_columns = [col for col in merged_df.columns if col.startswith('gen_mvar_')]
    if gen_mvar_columns:
        total_reactive -= merged_df[gen_mvar_columns].sum(axis=1)
    
    # Subtract shunt element reactive power (positive sign)
    shunt_mvar_columns = [col for col in merged_df.columns if col.startswith('shunt_mvar_')]
    if shunt_mvar_columns:
        total_reactive += merged_df[shunt_mvar_columns].sum(axis=1)
    
    return total_reactive 