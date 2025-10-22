"""
Data Validation Module for Power System Analysis

Author: Sustainable Power Systems Lab (SPSL)
Web: https://sps-lab.org
Contact: info@sps-lab.org

This module provides comprehensive data validation functionality for power system
operational data, including type checks, limit validation, and gap filling.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from .system_configuration import DATA_VALIDATION, VALIDATION_MESSAGES, ENHANCED_DATA_VALIDATION, ENHANCED_VALIDATION_MESSAGES
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.impute import KNNImputer
from scipy import stats
from scipy.interpolate import interp1d, UnivariateSpline
import warnings

class DataValidator:
    """Comprehensive data validator for power system operational data."""
    
    def __init__(self, logger=None):
        """
        Initialize the data validator.
        
        Args:
            logger: Optional logger object for recording validation results
        """
        self.logger = logger
        self.validation_summary = {
            'type_errors': [],
            'limit_errors': [],
            'gaps_filled': 0,
            'gaps_too_large': 0,
            'total_records_processed': 0,
            'records_with_errors': 0,
            'values_rounded': 0,
            'rows_removed_due_to_gaps': 0,
            'detailed_violations': {
                'type_violations': [],  # [{column, timestamp, original_value, description}]
                'limit_violations': [],  # [{column, timestamp, value, violation_type, limit}]
                'rounding_events': [],  # [{column, timestamp, original_value, rounded_value}]
                'gap_filling_events': []  # [{column, start_timestamp, end_timestamp, gap_size, method}]
            }
        }
    
    def log(self, message: str, level: str = 'INFO'):
        """Log a message using the provided logger or print to console."""
        if self.logger:
            self.logger.log(message, level)
        else:
            print(f"[{level}] {message}")
    
    def _handle_dst_duplicate_hours(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle duplicated timestamps caused by DST fall-back (hour repeats).
        
        Rule: If the same hour exists twice, keep only the second pair of
        half-hour inputs (i.e., keep the last occurrence of duplicated
        timestamps and drop the first).
        
        Args:
            df: Input DataFrame, expected to have a DatetimeIndex
        
        Returns:
            DataFrame with first occurrences of duplicated timestamps removed
        """
        try:
            # Ensure datetime index; if not, do nothing
            if not isinstance(df.index, pd.DatetimeIndex):
                return df
            
            # Work on a sorted copy to ensure chronological order
            df_sorted = df.sort_index()
            
            # Identify duplicated timestamps (e.g., 02:00 and 02:30 repeated at DST fall-back)
            dup_any_mask = df_sorted.index.duplicated(keep=False)
            if not dup_any_mask.any():
                return df_sorted
            
            # Count duplicates for logging
            total_dup_labels = int(dup_any_mask.sum())
            to_drop_mask = df_sorted.index.duplicated(keep='last')
            to_drop_count = int(to_drop_mask.sum())
            
            self.log(
                f"Detected {total_dup_labels} duplicated timestamp rows (likely DST fall-back). "
                f"Dropping first occurrences: {to_drop_count}, keeping second half-hour pair(s).",
                'INFO'
            )
            
            # Keep last occurrence of each duplicated timestamp (second pair)
            df_deduped = df_sorted[~to_drop_mask]
            return df_deduped
        except Exception as e:
            # Fail-safe: on any error, return original df
            self.log(f"DST duplicate handling failed: {str(e)}", 'WARNING')
            return df
    
    def validate_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate data types for all columns in the DataFrame.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            DataFrame with validated data types
        """
        self.log("Starting data type validation...")
        
        df_validated = df.copy()
        type_checks = DATA_VALIDATION['type_checks']
        
        for col in df_validated.columns:
            try:
                # Check if column should be real numbers
                if any(prefix in col for prefix in type_checks['real_numbers']):
                    # Convert to numeric, coercing errors to NaN
                    df_validated[col] = pd.to_numeric(df_validated[col], errors='coerce')
                    
                    # Check for non-numeric values
                    non_numeric_mask = pd.isna(df_validated[col]) & ~pd.isna(df[col])
                    if non_numeric_mask.any():
                        non_numeric_count = non_numeric_mask.sum()
                        error_msg = f"Column {col}: {non_numeric_count} non-numeric values found"
                        self.validation_summary['type_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        
                        # Store detailed type violation information with timestamps
                        type_error_indices = df.index[non_numeric_mask]
                        for idx in type_error_indices[:10]:  # Store first 10 type errors for detail
                            original_value = str(df.loc[idx, col])
                            self.validation_summary['detailed_violations']['type_violations'].append({
                                'column': col,
                                'timestamp': idx.strftime('%Y-%m-%d %H:%M:%S'),
                                'original_value': original_value,
                                'description': f'Non-numeric value "{original_value}" found in real number column'
                            })
                
                # Check if column should be integers (shunt tap positions)
                elif any(prefix in col for prefix in type_checks['integers']):
                    # Convert to numeric first, but keep as float64 for now
                    # The rounding to integers will be handled in limit validation
                    df_validated[col] = pd.to_numeric(df_validated[col], errors='coerce')
                    
                    # Check for non-numeric values
                    non_numeric_mask = pd.isna(df_validated[col]) & ~pd.isna(df[col])
                    if non_numeric_mask.any():
                        non_numeric_count = non_numeric_mask.sum()
                        error_msg = f"Column {col}: {non_numeric_count} non-numeric values found"
                        self.validation_summary['type_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        
                        # Store detailed type violation information with timestamps
                        type_error_indices = df.index[non_numeric_mask]
                        for idx in type_error_indices[:10]:  # Store first 10 type errors for detail
                            original_value = str(df.loc[idx, col])
                            self.validation_summary['detailed_violations']['type_violations'].append({
                                'column': col,
                                'timestamp': idx.strftime('%Y-%m-%d %H:%M:%S'),
                                'original_value': original_value,
                                'description': f'Non-numeric value "{original_value}" found in integer column'
                            })
                    
                    # Note: We don't convert to Int64 here because rounding will be handled in limit validation
                    # This prevents the "cannot safely cast" error when there are NaN values
                    
            except Exception as e:
                error_msg = f"Error validating column {col}: {str(e)}"
                self.validation_summary['type_errors'].append(error_msg)
                self.log(error_msg, 'ERROR')
        
        self.log(f"Data type validation completed. {len(self.validation_summary['type_errors'])} type errors found")
        return df_validated
    
    def validate_limits(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate data limits for all columns in the DataFrame.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            DataFrame with validated limits
        """
        self.log("Starting limit validation...")
        
        df_validated = df.copy()
        limit_checks = DATA_VALIDATION['limit_checks']
        
        for col in df_validated.columns:
            try:
                # Check non-negative constraints
                if any(prefix in col for prefix in limit_checks['non_negative']):
                    negative_mask = (df_validated[col] < 0) & ~pd.isna(df_validated[col])
                    if negative_mask.any():
                        negative_count = negative_mask.sum()
                        min_value = df_validated[col][negative_mask].min()
                        error_msg = f"Column {col}: {negative_count} negative values found (min: {min_value})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        
                        # Store detailed violation information with timestamps
                        negative_indices = df_validated.index[negative_mask]
                        for idx in negative_indices[:10]:  # Store first 10 violations for detail
                            self.validation_summary['detailed_violations']['limit_violations'].append({
                                'column': col,
                                'timestamp': idx.strftime('%Y-%m-%d %H:%M:%S'),
                                'value': float(df_validated.loc[idx, col]),
                                'violation_type': 'negative_value',
                                'limit': 'min >= 0',
                                'description': f'Negative value {df_validated.loc[idx, col]:.3f} in non-negative column'
                            })
                        
                        # Set negative values to NaN for later interpolation
                        df_validated.loc[negative_mask, col] = np.nan
                
                # Check voltage limits (min <= value <= max)
                if 'gen_v_' in col:
                    voltage_limits = limit_checks['voltage_limits']
                    low_voltage_mask = (df_validated[col] < voltage_limits['min']) & ~pd.isna(df_validated[col])
                    high_voltage_mask = (df_validated[col] > voltage_limits['max']) & ~pd.isna(df_validated[col])
                    
                    if low_voltage_mask.any():
                        low_count = low_voltage_mask.sum()
                        min_voltage = df_validated[col][low_voltage_mask].min()
                        error_msg = f"Column {col}: {low_count} values below {voltage_limits['min']} KV (min: {min_voltage})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        
                        # Store detailed violation information with timestamps
                        low_indices = df_validated.index[low_voltage_mask]
                        for idx in low_indices[:10]:  # Store first 10 violations for detail
                            self.validation_summary['detailed_violations']['limit_violations'].append({
                                'column': col,
                                'timestamp': idx.strftime('%Y-%m-%d %H:%M:%S'),
                                'value': float(df_validated.loc[idx, col]),
                                'violation_type': 'voltage_too_low',
                                'limit': f'min {voltage_limits["min"]} KV',
                                'description': f'Voltage {df_validated.loc[idx, col]:.3f} KV below minimum {voltage_limits["min"]} KV'
                            })
                        
                        df_validated.loc[low_voltage_mask, col] = np.nan
                    
                    if high_voltage_mask.any():
                        high_count = high_voltage_mask.sum()
                        max_voltage = df_validated[col][high_voltage_mask].max()
                        error_msg = f"Column {col}: {high_count} values above {voltage_limits['max']} KV (max: {max_voltage})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        
                        # Store detailed violation information with timestamps
                        high_indices = df_validated.index[high_voltage_mask]
                        for idx in high_indices[:10]:  # Store first 10 violations for detail
                            self.validation_summary['detailed_violations']['limit_violations'].append({
                                'column': col,
                                'timestamp': idx.strftime('%Y-%m-%d %H:%M:%S'),
                                'value': float(df_validated.loc[idx, col]),
                                'violation_type': 'voltage_too_high',
                                'limit': f'max {voltage_limits["max"]} KV',
                                'description': f'Voltage {df_validated.loc[idx, col]:.3f} KV above maximum {voltage_limits["max"]} KV'
                            })
                        
                        df_validated.loc[high_voltage_mask, col] = np.nan
                
                # Check wind power limits
                if 'wind_mw_' in col:
                    wind_limits = limit_checks['power_limits']['wind']
                    low_power_mask = (df_validated[col] < wind_limits['min_mw']) & ~pd.isna(df_validated[col])
                    high_power_mask = (df_validated[col] > wind_limits['max_mw']) & ~pd.isna(df_validated[col])
                    
                    if low_power_mask.any():
                        low_count = low_power_mask.sum()
                        min_value = df_validated[col][low_power_mask].min()
                        error_msg = f"Column {col}: {low_count} values below {wind_limits['min_mw']} MW (min: {min_value})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        
                        # Store detailed violation information with timestamps
                        low_indices = df_validated.index[low_power_mask]
                        for idx in low_indices[:10]:  # Store first 10 violations for detail
                            self.validation_summary['detailed_violations']['limit_violations'].append({
                                'column': col,
                                'timestamp': idx.strftime('%Y-%m-%d %H:%M:%S'),
                                'value': float(df_validated.loc[idx, col]),
                                'violation_type': 'power_too_low',
                                'limit': f'min {wind_limits["min_mw"]} MW',
                                'description': f'Wind power {df_validated.loc[idx, col]:.3f} MW below minimum {wind_limits["min_mw"]} MW'
                            })
                        
                        df_validated.loc[low_power_mask, col] = np.nan
                    
                    if high_power_mask.any():
                        high_count = high_power_mask.sum()
                        max_value = df_validated[col][high_power_mask].max()
                        error_msg = f"Column {col}: {high_count} values above {wind_limits['max_mw']} MW (max: {max_value})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        
                        # Store detailed violation information with timestamps
                        high_indices = df_validated.index[high_power_mask]
                        for idx in high_indices[:10]:  # Store first 10 violations for detail
                            self.validation_summary['detailed_violations']['limit_violations'].append({
                                'column': col,
                                'timestamp': idx.strftime('%Y-%m-%d %H:%M:%S'),
                                'value': float(df_validated.loc[idx, col]),
                                'violation_type': 'power_too_high',
                                'limit': f'max {wind_limits["max_mw"]} MW',
                                'description': f'Wind power {df_validated.loc[idx, col]:.3f} MW above maximum {wind_limits["max_mw"]} MW'
                            })
                        df_validated.loc[high_power_mask, col] = np.nan

                # Check substation active power limits
                elif 'ss_mw_' in col:
                    ss_limits = limit_checks['power_limits']['substation']
                    low_power_mask = (df_validated[col] < ss_limits['min_mw']) & ~pd.isna(df_validated[col])
                    high_power_mask = (df_validated[col] > ss_limits['max_mw']) & ~pd.isna(df_validated[col])
                    
                    if low_power_mask.any():
                        low_count = low_power_mask.sum()
                        min_value = df_validated[col][low_power_mask].min()
                        error_msg = f"Column {col}: {low_count} values below {ss_limits['min_mw']} MW (min: {min_value})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        df_validated.loc[low_power_mask, col] = np.nan
                    
                    if high_power_mask.any():
                        high_count = high_power_mask.sum()
                        max_value = df_validated[col][high_power_mask].max()
                        error_msg = f"Column {col}: {high_count} values above {ss_limits['max_mw']} MW (max: {max_value})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        df_validated.loc[high_power_mask, col] = np.nan

                # Check substation reactive power limits
                elif 'ss_mvar_' in col:
                    ss_limits = limit_checks['power_limits']['substation']
                    low_power_mask = (df_validated[col] < ss_limits['min_mvar']) & ~pd.isna(df_validated[col])
                    high_power_mask = (df_validated[col] > ss_limits['max_mvar']) & ~pd.isna(df_validated[col])
                    
                    if low_power_mask.any():
                        low_count = low_power_mask.sum()
                        min_value = df_validated[col][low_power_mask].min()
                        error_msg = f"Column {col}: {low_count} values below {ss_limits['min_mvar']} MVAR (min: {min_value})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        df_validated.loc[low_power_mask, col] = np.nan
                    
                    if high_power_mask.any():
                        high_count = high_power_mask.sum()
                        max_value = df_validated[col][high_power_mask].max()
                        error_msg = f"Column {col}: {high_count} values above {ss_limits['max_mvar']} MVAR (max: {max_value})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        df_validated.loc[high_power_mask, col] = np.nan

                # Check shunt reactive power limits
                elif 'shunt_mvar_' in col:
                    shunt_limits = limit_checks['power_limits']['shunt']
                    low_power_mask = (df_validated[col] < shunt_limits['min_mvar']) & ~pd.isna(df_validated[col])
                    high_power_mask = (df_validated[col] > shunt_limits['max_mvar']) & ~pd.isna(df_validated[col])
                    
                    if low_power_mask.any():
                        low_count = low_power_mask.sum()
                        min_value = df_validated[col][low_power_mask].min()
                        error_msg = f"Column {col}: {low_count} values below {shunt_limits['min_mvar']} MVAR (min: {min_value})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        df_validated.loc[low_power_mask, col] = np.nan
                    
                    if high_power_mask.any():
                        high_count = high_power_mask.sum()
                        max_value = df_validated[col][high_power_mask].max()
                        error_msg = f"Column {col}: {high_count} values above {shunt_limits['max_mvar']} MVAR (max: {max_value})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        df_validated.loc[high_power_mask, col] = np.nan

                # Check generator reactive power limits
                elif 'gen_mvar_' in col:
                    gen_limits = limit_checks['power_limits']['generator']
                    low_power_mask = (df_validated[col] < gen_limits['min_q']) & ~pd.isna(df_validated[col])
                    high_power_mask = (df_validated[col] > gen_limits['max_q']) & ~pd.isna(df_validated[col])
                    
                    if low_power_mask.any():
                        low_count = low_power_mask.sum()
                        min_value = df_validated[col][low_power_mask].min()
                        error_msg = f"Column {col}: {low_count} values below {gen_limits['min_q']} MVAR (min: {min_value})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        df_validated.loc[low_power_mask, col] = np.nan
                    
                    if high_power_mask.any():
                        high_count = high_power_mask.sum()
                        max_value = df_validated[col][high_power_mask].max()
                        error_msg = f"Column {col}: {high_count} values above {gen_limits['max_q']} MVAR (max: {max_value})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        df_validated.loc[high_power_mask, col] = np.nan

                # Check tap limits and apply rounding for valid real numbers
                elif 'shunt_tap_' in col:
                    tap_limits = limit_checks['tap_limits']
                    
                    # First, check if values are within limits (before rounding)
                    low_tap_mask = (df_validated[col] < tap_limits['min']) & ~pd.isna(df_validated[col])
                    high_tap_mask = (df_validated[col] > tap_limits['max']) & ~pd.isna(df_validated[col])
                    
                    # Apply rounding to valid real numbers within limits
                    valid_mask = ~pd.isna(df_validated[col]) & ~low_tap_mask & ~high_tap_mask
                    if valid_mask.any():
                        # Store original values to detect which ones were rounded
                        original_values = df_validated[col][valid_mask].copy()
                        
                        # Round valid real numbers to nearest integer
                        rounded_values = np.round(df_validated[col][valid_mask])
                        df_validated.loc[valid_mask, col] = rounded_values
                        
                        # Count how many values were rounded (had fractional parts)
                        non_integer_mask = (original_values != rounded_values)
                        rounded_count = non_integer_mask.sum()
                        if rounded_count > 0:
                            self.validation_summary['values_rounded'] += rounded_count
                            
                            # Store detailed rounding information with timestamps
                            rounding_indices = df_validated.index[valid_mask][non_integer_mask]
                            for idx in rounding_indices[:20]:  # Store first 20 rounding events for detail
                                # Find the position in the original_values array
                                valid_idx_pos = df_validated.index[valid_mask].get_loc(idx)
                                original_value = float(original_values.iloc[valid_idx_pos])
                                rounded_value = float(rounded_values.iloc[valid_idx_pos])
                                self.validation_summary['detailed_violations']['rounding_events'].append({
                                    'column': col,
                                    'timestamp': idx.strftime('%Y-%m-%d %H:%M:%S'),
                                    'original_value': original_value,
                                    'rounded_value': rounded_value,
                                    'description': f'Rounded {original_value:.3f} to {rounded_value} for integer column'
                                })
                            
                            self.log(f"Column {col}: Rounded {rounded_count} valid real numbers to nearest integer", 'INFO')
                    
                    # Now check for values outside limits after rounding
                    low_tap_mask = (df_validated[col] < tap_limits['min']) & ~pd.isna(df_validated[col])
                    high_tap_mask = (df_validated[col] > tap_limits['max']) & ~pd.isna(df_validated[col])
                    
                    if low_tap_mask.any():
                        low_count = low_tap_mask.sum()
                        min_tap = df_validated[col][low_tap_mask].min()
                        error_msg = f"Column {col}: {low_count} values below {tap_limits['min']} (min: {min_tap})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        df_validated.loc[low_tap_mask, col] = np.nan
                    
                    if high_tap_mask.any():
                        high_count = high_tap_mask.sum()
                        max_tap = df_validated[col][high_tap_mask].max()
                        error_msg = f"Column {col}: {high_count} values above {tap_limits['max']} (max: {max_tap})"
                        self.validation_summary['limit_errors'].append(error_msg)
                        self.log(error_msg, 'WARNING')
                        df_validated.loc[high_tap_mask, col] = np.nan
                        
            except Exception as e:
                error_msg = f"Error validating limits for column {col}: {str(e)}"
                self.validation_summary['limit_errors'].append(error_msg)
                self.log(error_msg, 'ERROR')
        
        self.log(f"Limit validation completed. {len(self.validation_summary['limit_errors'])} limit errors found")
        return df_validated
    
    def fill_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill gaps in the data using linear interpolation for short gaps.
        
        Args:
            df: DataFrame to fill gaps in
            
        Returns:
            DataFrame with gaps filled
        """
        self.log("Starting gap filling process...")
        
        df_filled = df.copy()
        gap_settings = DATA_VALIDATION['gap_filling']
        max_gap_steps = gap_settings['max_gap_steps']
        
        # Process each column separately
        for col in df_filled.columns:
            if col == df_filled.index.name:  # Skip index column
                continue
                
            try:
                # Find gaps in the data
                series = df_filled[col]
                gaps = self._find_gaps(series)
                
                for gap_start, gap_end in gaps:
                    gap_size = gap_end - gap_start + 1
                    
                    # Get timestamps for the gap
                    start_timestamp = series.index[gap_start]
                    end_timestamp = series.index[gap_end]
                    
                    if gap_size <= max_gap_steps:
                        # Fill the gap using linear interpolation
                        self._fill_gap_linear(df_filled, col, gap_start, gap_end)
                        self.validation_summary['gaps_filled'] += 1
                        
                        # Store detailed gap filling information
                        self.validation_summary['detailed_violations']['gap_filling_events'].append({
                            'column': col,
                            'start_timestamp': start_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'end_timestamp': end_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'gap_size': gap_size,
                            'method': 'linear_interpolation',
                            'description': f'Filled {gap_size}-step gap using linear interpolation'
                        })
                        
                        self.log(f"Filled gap in {col} from {start_timestamp} to {end_timestamp} (size: {gap_size})", 'INFO')
                    else:
                        # Gap too large, log but don't fill
                        self.validation_summary['gaps_too_large'] += 1
                        
                        # Store detailed gap information for large gaps
                        self.validation_summary['detailed_violations']['gap_filling_events'].append({
                            'column': col,
                            'start_timestamp': start_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'end_timestamp': end_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'gap_size': gap_size,
                            'method': 'not_filled_too_large',
                            'description': f'Gap of {gap_size} steps too large (max allowed: {max_gap_steps})'
                        })
                        
                        self.log(f"Gap in {col} from {start_timestamp} to {end_timestamp} too large (size: {gap_size} > {max_gap_steps})", 'WARNING')
                        
            except Exception as e:
                error_msg = f"Error filling gaps in column {col}: {str(e)}"
                self.log(error_msg, 'ERROR')
        
        self.log(f"Gap filling completed. Filled {self.validation_summary['gaps_filled']} gaps, {self.validation_summary['gaps_too_large']} gaps too large")
        return df_filled
    
    def advanced_gap_filling(self, df: pd.DataFrame, method=None) -> pd.DataFrame:
        """
        Fill gaps using advanced interpolation methods.
        
        Args:
            df: DataFrame to fill gaps in
            method: Gap filling method ('adaptive', 'spline', 'polynomial', 'knn', 'ml', None uses config default)
        
        Methods:
        - 'adaptive': Choose method based on gap characteristics
        - 'spline': Cubic spline interpolation
        - 'polynomial': Polynomial interpolation
        - 'knn': K-Nearest Neighbors imputation
        - 'ml': Machine learning-based imputation
        """
        # Use config default if not specified
        if method is None:
            method = ENHANCED_DATA_VALIDATION['advanced_gap_filling']['default_method']
            
        self.log(f"Starting advanced gap filling with method: {method}")
        
        df_filled = df.copy()
        gap_settings = DATA_VALIDATION['gap_filling']
        advanced_settings = ENHANCED_DATA_VALIDATION['advanced_gap_filling']
        max_gap_steps = gap_settings['advanced_max_gap_steps']
        remove_threshold = gap_settings['remove_large_gaps_threshold']
        
        # Track advanced gap filling statistics
        advanced_gaps_filled = 0
        large_gaps_removed = 0
        
        for col in df_filled.columns:
            if col == df_filled.index.name:
                continue
                
            try:
                series = df_filled[col]
                gaps = self._find_gaps(series)
                
                for gap_start, gap_end in gaps:
                    gap_size = gap_end - gap_start + 1
                    
                    if gap_size <= max_gap_steps:
                        # Use advanced gap filling for medium-sized gaps
                        if method == 'adaptive':
                            # Choose method based on gap size and data characteristics
                            fill_method = self._select_adaptive_method(series, gap_start, gap_end)
                        else:
                            fill_method = method
                        
                        self._fill_gap_advanced(df_filled, col, gap_start, gap_end, fill_method)
                        advanced_gaps_filled += 1
                        
                        start_timestamp = series.index[gap_start]
                        end_timestamp = series.index[gap_end]
                        self.log(f"Advanced filled gap in {col} from {start_timestamp} to {end_timestamp} (size: {gap_size}, method: {fill_method})", 'INFO')
                        
                    elif gap_size >= remove_threshold:
                        # Remove very large gaps completely
                        df_filled.iloc[gap_start:gap_end+1, df_filled.columns.get_loc(col)] = np.nan
                        large_gaps_removed += 1
                        
                        start_timestamp = series.index[gap_start]
                        end_timestamp = series.index[gap_end]
                        self.log(f"Removed large gap in {col} from {start_timestamp} to {end_timestamp} (size: {gap_size})", 'WARNING')
                        
                    # Medium gaps (between max_gap_steps and remove_threshold) are left as NaN
                        
            except Exception as e:
                error_msg = f"Error in advanced gap filling for {col}: {str(e)}"
                self.log(error_msg, 'ERROR')
        
        self.log(f"Advanced gap filling completed. Filled {advanced_gaps_filled} gaps, removed {large_gaps_removed} large gaps")
        return df_filled
    
    def _select_adaptive_method(self, series: pd.Series, gap_start: int, gap_end: int) -> str:
        """Select the best gap filling method based on data characteristics."""
        gap_size = gap_end - gap_start + 1
        thresholds = ENHANCED_DATA_VALIDATION['advanced_gap_filling']['adaptive_thresholds']
        
        # Analyze data around the gap
        context_size = min(48, max(10, int(len(series) * ENHANCED_DATA_VALIDATION['advanced_gap_filling']['context_size_ratio'])))
        start_context = max(0, gap_start - context_size)
        end_context = min(len(series), gap_end + context_size + 1)
        
        # Get context data before and after the gap
        before_gap = series.iloc[start_context:gap_start].dropna()
        after_gap = series.iloc[gap_end+1:end_context].dropna()
        context_data = pd.concat([before_gap, after_gap])
        
        if len(context_data) < ENHANCED_DATA_VALIDATION['advanced_gap_filling']['min_context_points']:
            return 'linear'
        
        # Calculate data characteristics
        variance = context_data.var()
        mean_value = context_data.mean()
        
        # Calculate trend if we have enough data
        if len(before_gap) >= 5 and len(after_gap) >= 5:
            trend = abs(after_gap.iloc[:5].mean() - before_gap.iloc[-5:].mean())
        else:
            trend = 0
        
        # Decision logic based on gap size and data characteristics
        if gap_size <= thresholds['small_gap_size']:
            return 'linear'
        elif gap_size <= thresholds['medium_gap_size'] and trend < variance * thresholds['variance_trend_ratio']:
            return 'spline'
        elif gap_size <= thresholds['large_gap_size'] and variance > mean_value * thresholds['high_variance_multiplier']:
            return 'knn'
        else:
            return 'polynomial'
    
    def _fill_gap_advanced(self, df: pd.DataFrame, col: str, gap_start: int, gap_end: int, method: str):
        """Fill gap using specified advanced method."""
        series = df[col]
        gap_size = gap_end - gap_start + 1
        advanced_settings = ENHANCED_DATA_VALIDATION['advanced_gap_filling']
        
        # Get context data for interpolation
        context_size = min(48, max(10, int(len(series) * advanced_settings['context_size_ratio'])))
        start_context = max(0, gap_start - context_size)
        end_context = min(len(series), gap_end + context_size + 1)
        
        context_series = series.iloc[start_context:end_context].copy()
        gap_indices = list(range(gap_start - start_context, gap_end - start_context + 1))
        
        try:
            if method == 'spline':
                # Use cubic spline interpolation
                valid_mask = ~context_series.isna()
                valid_indices = np.where(valid_mask)[0]
                valid_values = context_series.iloc[valid_indices].values
                
                if len(valid_values) >= 4:  # Need at least 4 points for cubic spline
                    spline = UnivariateSpline(valid_indices, valid_values, 
                                            s=advanced_settings['spline_smoothing'])
                    interpolated_values = spline(gap_indices)
                    
                    for i, value in enumerate(interpolated_values):
                        df.iloc[gap_start + i, df.columns.get_loc(col)] = value
                else:
                    # Fall back to linear interpolation
                    self._fill_gap_linear(df, col, gap_start, gap_end)
                    
            elif method == 'polynomial':
                # Polynomial interpolation
                valid_mask = ~context_series.isna()
                valid_indices = np.where(valid_mask)[0]
                valid_values = context_series.iloc[valid_indices].values
                
                if len(valid_values) >= max(3, gap_size):
                    poly_degree = min(advanced_settings['polynomial_max_degree'], len(valid_values) - 1)
                    poly_interp = interp1d(valid_indices, valid_values, kind=poly_degree, 
                                         fill_value='extrapolate')
                    interpolated_values = poly_interp(gap_indices)
                    
                    for i, value in enumerate(interpolated_values):
                        df.iloc[gap_start + i, df.columns.get_loc(col)] = value
                else:
                    self._fill_gap_linear(df, col, gap_start, gap_end)
                    
            elif method == 'knn':
                # KNN imputation using time-based features
                self._fill_gap_knn(df, col, gap_start, gap_end, context_size)
                    
            elif method == 'ml':
                # Machine learning-based imputation
                self._fill_gap_ml(df, col, gap_start, gap_end, context_size)
                
            else:  # Default to linear
                self._fill_gap_linear(df, col, gap_start, gap_end)
                
        except Exception as e:
            self.log(f"Advanced method {method} failed for {col}, using linear interpolation: {str(e)}", 'WARNING')
            self._fill_gap_linear(df, col, gap_start, gap_end)
    
    def _fill_gap_knn(self, df: pd.DataFrame, col: str, gap_start: int, gap_end: int, context_size: int):
        """Fill gap using KNN imputation with time-based features."""
        try:
            series = df[col]
            
            # Create time-based features for the context window
            start_context = max(0, gap_start - context_size)
            end_context = min(len(series), gap_end + context_size + 1)
            
            # Extract time features if datetime index
            if hasattr(series.index, 'hour'):
                time_features = pd.DataFrame({
                    'hour': series.index[start_context:end_context].hour,
                    'day_of_week': series.index[start_context:end_context].dayofweek,
                    'is_weekend': (series.index[start_context:end_context].dayofweek >= 5).astype(int)
                })
            else:
                # Use position-based features if no datetime index
                positions = np.arange(start_context, end_context)
                time_features = pd.DataFrame({
                    'position': positions,
                    'position_sin': np.sin(2 * np.pi * positions / len(series)),
                    'position_cos': np.cos(2 * np.pi * positions / len(series))
                })
            
            # Add the target column
            features_with_target = time_features.copy()
            features_with_target[col] = series.iloc[start_context:end_context].values
            
            # Use KNN imputer
            n_neighbors = ENHANCED_DATA_VALIDATION['advanced_gap_filling']['knn_neighbors']
            imputer = KNNImputer(n_neighbors=min(n_neighbors, len(features_with_target.dropna())))
            imputed_data = imputer.fit_transform(features_with_target)
            
            # Extract the filled values for the gap
            gap_relative_start = gap_start - start_context
            gap_relative_end = gap_end - start_context
            
            filled_values = imputed_data[gap_relative_start:gap_relative_end+1, -1]  # Last column is the target
            
            for i, value in enumerate(filled_values):
                df.iloc[gap_start + i, df.columns.get_loc(col)] = value
                
        except Exception as e:
            self.log(f"KNN imputation failed for {col}: {str(e)}, using linear interpolation", 'WARNING')
            self._fill_gap_linear(df, col, gap_start, gap_end)
    
    def _fill_gap_ml(self, df: pd.DataFrame, col: str, gap_start: int, gap_end: int, context_size: int):
        """Fill gap using machine learning-based imputation (Random Forest)."""
        try:
            series = df[col]
            
            # Create features from surrounding time periods and other columns
            start_context = max(0, gap_start - context_size)
            end_context = min(len(series), gap_end + context_size + 1)
            
            # Time-based features
            if hasattr(series.index, 'hour'):
                time_features = pd.DataFrame({
                    'hour': series.index[start_context:end_context].hour,
                    'day_of_week': series.index[start_context:end_context].dayofweek,
                    'month': series.index[start_context:end_context].month,
                    'is_weekend': (series.index[start_context:end_context].dayofweek >= 5).astype(int)
                })
            else:
                positions = np.arange(start_context, end_context)
                time_features = pd.DataFrame({
                    'position': positions,
                    'position_sin': np.sin(2 * np.pi * positions / len(series)),
                    'position_cos': np.cos(2 * np.pi * positions / len(series))
                })
            
            # Add lagged features from the same column
            target_data = series.iloc[start_context:end_context]
            for lag in [1, 2, 3, 6, 12]:  # Various lags
                time_features[f'{col}_lag_{lag}'] = target_data.shift(lag)
            
            # Add features from other columns if available
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            other_cols = [c for c in numeric_cols if c != col][:3]  # Use up to 3 other columns
            
            for other_col in other_cols:
                other_series = df[other_col].iloc[start_context:end_context]
                time_features[f'{other_col}_current'] = other_series.values
                time_features[f'{other_col}_lag_1'] = other_series.shift(1).values
            
            # Prepare training data
            time_features['target'] = target_data.values
            training_data = time_features.dropna()
            
            if len(training_data) >= 10:  # Need sufficient training data
                X_train = training_data.drop('target', axis=1)
                y_train = training_data['target']
                
                # Train Random Forest
                rf = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=10)
                rf.fit(X_train, y_train)
                
                # Predict gap values
                gap_relative_start = gap_start - start_context
                gap_relative_end = gap_end - start_context
                
                gap_features = time_features.iloc[gap_relative_start:gap_relative_end+1].drop('target', axis=1)
                
                # Fill any remaining NaN in features with forward/backward fill
                gap_features = gap_features.fillna(method='ffill').fillna(method='bfill')
                
                predicted_values = rf.predict(gap_features)
                
                for i, value in enumerate(predicted_values):
                    df.iloc[gap_start + i, df.columns.get_loc(col)] = value
            else:
                # Fall back to KNN if insufficient training data
                self._fill_gap_knn(df, col, gap_start, gap_end, context_size)
                
        except Exception as e:
            self.log(f"ML imputation failed for {col}: {str(e)}, using KNN imputation", 'WARNING')
            self._fill_gap_knn(df, col, gap_start, gap_end, context_size)
    
    def remove_rows_with_excessive_gaps(self, df: pd.DataFrame, max_nan_percentage: float = 50.0) -> pd.DataFrame:
        """
        Remove rows that have too many NaN values (indicating large gaps that couldn't be filled).
        
        Args:
            df: DataFrame to clean
            max_nan_percentage: Maximum percentage of NaN values allowed in a row (default: 50%)
            
        Returns:
            DataFrame with rows containing excessive gaps removed
        """
        self.log("Checking for rows with excessive gaps...")
        
        initial_rows = len(df)
        
        # Calculate percentage of NaN values in each row
        nan_percentage = (df.isna().sum(axis=1) / len(df.columns)) * 100
        
        # Find rows with too many NaN values
        excessive_gaps_mask = nan_percentage > max_nan_percentage
        
        if excessive_gaps_mask.any():
            rows_to_remove = excessive_gaps_mask.sum()
            self.validation_summary['rows_removed_due_to_gaps'] = rows_to_remove
            
            # Get timestamps of rows being removed
            removed_timestamps = df.index[excessive_gaps_mask]
            self.log(f"Removing {rows_to_remove} rows with >{max_nan_percentage}% NaN values", 'WARNING')
            
            # Log some examples of removed timestamps
            if len(removed_timestamps) <= 5:
                for ts in removed_timestamps:
                    self.log(f"  Removed row: {ts}", 'WARNING')
            else:
                for ts in removed_timestamps[:3]:
                    self.log(f"  Removed row: {ts}", 'WARNING')
                self.log(f"  ... and {len(removed_timestamps) - 3} more rows", 'WARNING')
            
            # Remove the rows
            df_cleaned = df[~excessive_gaps_mask]
            
            self.log(f"Removed {rows_to_remove} rows with excessive gaps. DataFrame shape: {initial_rows} -> {len(df_cleaned)}")
        else:
            df_cleaned = df
            self.log("No rows with excessive gaps found")
        
        return df_cleaned
    
    def _convert_shunt_tap_to_integers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert shunt tap columns to integers after all validation and rounding is complete.
        
        Args:
            df: DataFrame with validated data
            
        Returns:
            DataFrame with shunt tap columns converted to integers
        """
        self.log("Converting shunt tap columns to integers...")
        
        df_converted = df.copy()
        type_checks = DATA_VALIDATION['type_checks']
        
        for col in df_converted.columns:
            if any(prefix in col for prefix in type_checks['integers']):
                try:
                    # At this point, all values should be valid numbers (no NaN from validation errors)
                    # and any real numbers should have been rounded in the limit validation
                    df_converted[col] = df_converted[col].astype('Int64')
                    self.log(f"Successfully converted {col} to integer type")
                except Exception as e:
                    error_msg = f"Error converting {col} to integer: {str(e)}"
                    self.validation_summary['type_errors'].append(error_msg)
                    self.log(error_msg, 'ERROR')
                    # Keep as float64 if conversion fails
                    self.log(f"Keeping {col} as float64 due to conversion error")
        
        return df_converted
    
    def _find_gaps(self, series: pd.Series) -> List[Tuple[int, int]]:
        """
        Find gaps (consecutive NaN values) in a series.
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            List of tuples (start_index, end_index) for each gap
        """
        gaps = []
        in_gap = False
        gap_start = None
        
        for i, value in enumerate(series):
            if pd.isna(value):
                if not in_gap:
                    gap_start = i
                    in_gap = True
            else:
                if in_gap:
                    gaps.append((gap_start, i - 1))
                    in_gap = False
        
        # Handle gap at the end
        if in_gap:
            gaps.append((gap_start, len(series) - 1))
        
        return gaps
    
    def _fill_gap_linear(self, df: pd.DataFrame, col: str, gap_start: int, gap_end: int):
        """
        Fill a specific gap using linear interpolation.
        
        Args:
            df: DataFrame containing the data
            col: Column name to fill
            gap_start: Start index of the gap
            gap_end: End index of the gap
        """
        series = df[col]
        
        # Get values before and after the gap
        before_gap = None
        after_gap = None
        
        # Find the last valid value before the gap
        for i in range(gap_start - 1, -1, -1):
            if not pd.isna(series.iloc[i]):
                before_gap = series.iloc[i]
                break
        
        # Find the first valid value after the gap
        for i in range(gap_end + 1, len(series)):
            if not pd.isna(series.iloc[i]):
                after_gap = series.iloc[i]
                break
        
        # Perform linear interpolation
        gap_size = gap_end - gap_start + 1
        if before_gap is not None and after_gap is not None:
            for i in range(gap_size):
                # Linear interpolation: y = y1 + (y2-y1)*(x-x1)/(x2-x1)
                weight = (i + 1) / (gap_size + 1)
                interpolated_value = before_gap + (after_gap - before_gap) * weight
                df.iloc[gap_start + i, df.columns.get_loc(col)] = interpolated_value
        elif before_gap is not None:
            # Only value before gap available, use forward fill
            for i in range(gap_size):
                df.iloc[gap_start + i, df.columns.get_loc(col)] = before_gap
        elif after_gap is not None:
            # Only value after gap available, use backward fill
            for i in range(gap_size):
                df.iloc[gap_start + i, df.columns.get_loc(col)] = after_gap
    
    def validate_load_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate load consistency (Total Load > Net Load).
        
        Args:
            df: DataFrame containing load data
            
        Returns:
            Dictionary with validation results
        """
        self.log("Validating load consistency...")
        
        results = {
            'total_load_columns': [],
            'net_load_columns': [],
            'inconsistencies': []
        }
        
        # Find load-related columns
        for col in df.columns:
            if 'ss_mw_' in col:  # Substation active power contributes to total load
                results['total_load_columns'].append(col)
            elif 'net_load' in col.lower():
                results['net_load_columns'].append(col)
        
        # If we have both total load and net load columns, check consistency
        if results['total_load_columns'] and results['net_load_columns']:
            for net_load_col in results['net_load_columns']:
                for total_load_col in results['total_load_columns']:
                    # Calculate total load from substation data
                    total_load = df[total_load_col].sum(axis=1) if len(total_load_col) > 1 else df[total_load_col]
                    net_load = df[net_load_col]
                    
                    # Check if total load > net load
                    inconsistency_mask = (total_load <= net_load) & ~pd.isna(total_load) & ~pd.isna(net_load)
                    if inconsistency_mask.any():
                        inconsistency_count = inconsistency_mask.sum()
                        max_violation = (net_load - total_load)[inconsistency_mask].max()
                        error_msg = f"Load inconsistency: {inconsistency_count} records where total load <= net load (max violation: {max_violation:.2f} MW)"
                        results['inconsistencies'].append(error_msg)
                        self.log(error_msg, 'WARNING')
        
        self.log(f"Load consistency validation completed. {len(results['inconsistencies'])} inconsistencies found")
        return results
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all validation results.
        
        Returns:
            Dictionary with validation summary
        """
        return {
            'type_errors_count': len(self.validation_summary['type_errors']),
            'limit_errors_count': len(self.validation_summary['limit_errors']),
            'gaps_filled': self.validation_summary['gaps_filled'],
            'gaps_too_large': self.validation_summary['gaps_too_large'],
            'total_records_processed': self.validation_summary['total_records_processed'],
            'records_with_errors': self.validation_summary['records_with_errors'],
            'values_rounded': self.validation_summary['values_rounded'],
            'rows_removed_due_to_gaps': self.validation_summary['rows_removed_due_to_gaps'],
            'type_errors': self.validation_summary['type_errors'],
            'limit_errors': self.validation_summary['limit_errors']
        }
    
    def validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform comprehensive validation on a DataFrame.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Validated DataFrame
        """
        self.log("Starting comprehensive data validation...")
        
        # Update record counts
        self.validation_summary['total_records_processed'] = len(df) * len(df.columns)
        
        # Step 0: Handle duplicated timestamps from DST fall-back (keep second pair)
        df_validated = self._handle_dst_duplicate_hours(df)
        
        # Step 1: Validate data types
        df_validated = self.validate_data_types(df_validated)
        
        # Step 2: Validate limits
        df_validated = self.validate_limits(df_validated)
        
        # Step 3: Fill gaps
        df_validated = self.fill_gaps(df_validated)
        
        # Step 4: Remove rows with excessive gaps (that couldn't be filled)
        max_nan_percentage = DATA_VALIDATION['gap_filling']['max_nan_percentage']
        df_validated = self.remove_rows_with_excessive_gaps(df_validated, max_nan_percentage)
        
        # Step 5: Convert shunt tap columns to integers after all validation and rounding
        df_validated = self._convert_shunt_tap_to_integers(df_validated)
        
        # Step 6: Validate load consistency
        load_results = self.validate_load_consistency(df_validated)
        
        # Update error counts
        total_errors = len(self.validation_summary['type_errors']) + len(self.validation_summary['limit_errors']) + len(load_results['inconsistencies'])
        self.validation_summary['records_with_errors'] = total_errors
        
        self.log(f"Comprehensive validation completed. {total_errors} total validation issues found")
        
        return df_validated 


class EnhancedDataValidator(DataValidator):
    """
    Enhanced data validator with advanced outlier detection and anomaly identification.
    
    Features:
    - Statistical outlier detection (IQR, Z-score, Modified Z-score)
    - Machine learning-based anomaly detection (Isolation Forest, LOF)
    - Rate of change violation detection
    - Correlation anomaly detection
    - Power balance validation
    - Advanced clustering-based anomaly detection
    """
    
    def __init__(self, logger=None, enable_ml_validation=None):
        """
        Initialize the enhanced data validator.
        
        Args:
            logger: Optional logger object for recording validation results
            enable_ml_validation: Enable machine learning-based validation methods (None uses config default)
        """
        super().__init__(logger)
        self.enable_ml_validation = (enable_ml_validation if enable_ml_validation is not None 
                                   else ENHANCED_DATA_VALIDATION['enable_ml_validation'])
        self.config = ENHANCED_DATA_VALIDATION
        self.enhanced_messages = ENHANCED_VALIDATION_MESSAGES
        self.validation_summary.update({
            'statistical_outliers': [],
            'ml_anomalies': [],
            'rate_violations': [],
            'correlation_anomalies': [],
            'power_balance_violations': [],
            'clustering_anomalies': []
        })
    
    def detect_statistical_outliers(self, df: pd.DataFrame, method=None, contamination=None) -> pd.DataFrame:
        """
        Detect outliers using multiple statistical methods.
        
        Args:
            df: DataFrame to analyze
            method: 'iqr', 'zscore', 'modified_zscore', 'isolation_forest', 'lof' (None uses config default)
            contamination: Expected proportion of outliers (for ML methods, None uses config default)
        
        Returns:
            DataFrame with outliers handled
        """
        # Use config defaults if not specified
        if method is None:
            method = self.config['outlier_detection']['default_methods'][0]
        if contamination is None:
            contamination = self.config['outlier_detection']['contamination']
        
        self.log(f"Starting statistical outlier detection using {method}...")
        
        df_cleaned = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        min_data_points = self.config['min_data_points']
        
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < min_data_points:  # Skip columns with insufficient data
                continue
                
            outlier_mask = pd.Series(False, index=df.index)
            
            if method == 'iqr':
                Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
                IQR = Q3 - Q1
                iqr_multiplier = self.config['outlier_detection']['iqr_multiplier']
                lower_bound = Q1 - iqr_multiplier * IQR
                upper_bound = Q3 + iqr_multiplier * IQR
                outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(series))
                zscore_threshold = self.config['outlier_detection']['zscore_threshold']
                outlier_indices = series.index[z_scores > zscore_threshold]
                outlier_mask.loc[outlier_indices] = True
                
            elif method == 'modified_zscore':
                median = series.median()
                mad = np.median(np.abs(series - median))
                if mad == 0:  # Handle constant values
                    mad = np.std(series)
                if mad > 0:
                    mad_constant = self.config['outlier_detection']['mad_constant']
                    modified_zscore_threshold = self.config['outlier_detection']['modified_zscore_threshold']
                    modified_z_scores = mad_constant * (series - median) / mad
                    outlier_indices = series.index[np.abs(modified_z_scores) > modified_zscore_threshold]
                    outlier_mask.loc[outlier_indices] = True
                
            elif method == 'isolation_forest' and self.enable_ml_validation:
                try:
                    iso_forest = IsolationForest(contamination=contamination, random_state=42)
                    outlier_labels = iso_forest.fit_predict(series.values.reshape(-1, 1))
                    outlier_indices = series.index[outlier_labels == -1]
                    outlier_mask.loc[outlier_indices] = True
                except Exception as e:
                    self.log(f"Isolation Forest failed for {col}: {str(e)}", 'WARNING')
                
            elif method == 'lof' and self.enable_ml_validation:
                try:
                    lof = LocalOutlierFactor(contamination=contamination)
                    outlier_labels = lof.fit_predict(series.values.reshape(-1, 1))
                    outlier_indices = series.index[outlier_labels == -1]
                    outlier_mask.loc[outlier_indices] = True
                except Exception as e:
                    self.log(f"LOF failed for {col}: {str(e)}", 'WARNING')
            
            # Log and handle outliers
            if outlier_mask.any():
                outlier_count = outlier_mask.sum()
                outlier_values = df.loc[outlier_mask, col]
                error_msg = f"Column {col}: {outlier_count} {method} outliers detected"
                self.validation_summary['statistical_outliers'].append(error_msg)
                self.log(error_msg, 'WARNING')
                
                # Set outliers to NaN for interpolation
                df_cleaned.loc[outlier_mask, col] = np.nan
        
        self.log(f"Statistical outlier detection completed using {method}")
        return df_cleaned
    
    def detect_rate_violations(self, df: pd.DataFrame, max_change_rate=None) -> pd.DataFrame:
        """
        Detect violations in rate of change for time series data.
        
        Args:
            df: DataFrame to analyze
            max_change_rate: Maximum allowed rate of change per time step (None uses adaptive threshold)
        
        Returns:
            DataFrame with rate violations handled
        """
        if not self.config['rate_validation']['enable_rate_check']:
            return df
            
        self.log("Starting rate of change violation detection...")
        
        df_cleaned = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        min_points = self.config['rate_validation']['min_points_for_rate_check']
        
        for col in numeric_cols:
            series = df[col]
            if series.dropna().shape[0] < min_points:  # Need sufficient non-null points for rate calculation
                continue
            
            # Calculate rate of change for the entire series (keeping NaN alignment)
            rate_of_change = series.diff().abs()
            
            # Use adaptive threshold if not provided
            if max_change_rate is None:
                # Use configured multiplier * standard deviation as threshold
                multiplier = self.config['rate_validation']['adaptive_threshold_multiplier']
                threshold = multiplier * rate_of_change.dropna().std()
            else:
                threshold = max_change_rate
            
            # Find rate violations (excluding NaN values)
            violation_mask = (rate_of_change > threshold) & ~pd.isna(rate_of_change)
            
            if violation_mask.any():
                violation_count = violation_mask.sum()
                max_rate = rate_of_change[violation_mask].max()
                error_msg = f"Column {col}: {violation_count} rate violations detected (max rate: {max_rate:.2f}, threshold: {threshold:.2f})"
                self.validation_summary['rate_violations'].append(error_msg)
                self.log(error_msg, 'WARNING')
                
                # Set violating values to NaN
                df_cleaned.loc[violation_mask, col] = np.nan
        
        self.log("Rate violation detection completed")
        return df_cleaned
    
    def detect_correlation_anomalies(self, df: pd.DataFrame, correlation_threshold=None) -> pd.DataFrame:
        """
        Detect anomalies based on correlation patterns between related variables.
        
        Args:
            df: DataFrame to analyze
            correlation_threshold: Minimum correlation threshold for related variables (None uses config default)
        
        Returns:
            DataFrame with correlation anomalies flagged
        """
        if not self.config['correlation_validation']['enable_correlation_check']:
            return df
            
        # Use config default if not specified
        if correlation_threshold is None:
            correlation_threshold = self.config['correlation_validation']['correlation_threshold']
            
        self.log("Starting correlation anomaly detection...")
        
        df_cleaned = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Group related columns using config
        variable_groups = self.config['variable_groups']
        power_groups = {}
        for group_name, prefixes in variable_groups.items():
            power_groups[group_name] = [col for col in numeric_cols 
                                      if any(prefix in col for prefix in prefixes)]
        
        for group_name, group_cols in power_groups.items():
            if len(group_cols) < 2:
                continue
            
            # Calculate correlation matrix
            group_data = df[group_cols].dropna()
            min_window_size = self.config['correlation_validation']['min_window_size']
            if len(group_data) < min_window_size:
                continue
            
            corr_matrix = group_data.corr()
            
            # Find pairs with expected high correlation
            for i, col1 in enumerate(group_cols):
                for j, col2 in enumerate(group_cols[i+1:], i+1):
                    expected_corr = corr_matrix.loc[col1, col2]
                    
                    if abs(expected_corr) > correlation_threshold:
                        # Check for correlation breaks in sliding windows
                        window_size_ratio = self.config['correlation_validation']['window_size_ratio']
                        max_window_size = self.config['correlation_validation']['max_window_size']
                        window_size = min(max_window_size, int(len(group_data) * window_size_ratio))
                        window_size = max(window_size, min_window_size)
                        
                        for start_idx in range(0, len(group_data) - window_size, window_size // 2):
                            end_idx = start_idx + window_size
                            window_data = group_data.iloc[start_idx:end_idx]
                            
                            if len(window_data) < min_window_size:
                                continue
                            
                            window_corr = window_data[[col1, col2]].corr().iloc[0, 1]
                            
                            # Check for significant correlation break
                            correlation_break_threshold = self.config['correlation_validation']['correlation_break_threshold']
                            if abs(window_corr - expected_corr) > correlation_break_threshold:
                                error_msg = f"Correlation anomaly in {group_name}: {col1} vs {col2} correlation dropped from {expected_corr:.2f} to {window_corr:.2f}"
                                self.validation_summary['correlation_anomalies'].append(error_msg)
                                self.log(error_msg, 'WARNING')
        
        self.log("Correlation anomaly detection completed")
        return df_cleaned
    
    def validate_power_balance(self, df: pd.DataFrame, tolerance=None) -> pd.DataFrame:
        """
        Validate power balance equations in the system.
        
        Args:
            df: DataFrame to analyze
            tolerance: Tolerance for power balance violations (as fraction, None uses config default)
        
        Returns:
            DataFrame with power balance violations flagged
        """
        if not self.config['power_balance']['enable_power_balance_check']:
            return df
            
        # Use config default if not specified
        if tolerance is None:
            tolerance = self.config['power_balance']['tolerance']
            
        self.log("Starting power balance validation...")
        
        df_cleaned = df.copy()
        
        # Find generation and load columns
        wind_mw_cols = [col for col in df.columns if 'wind_mw_' in col]
        ss_mw_cols = [col for col in df.columns if 'ss_mw_' in col]
        
        if len(wind_mw_cols) > 0 and len(ss_mw_cols) > 0:
            # Calculate total generation and total load (only wind generation available)
            total_generation = df[wind_mw_cols].sum(axis=1)
            total_load = df[ss_mw_cols].sum(axis=1)
            
            # Calculate power imbalance
            power_imbalance = total_generation - total_load
            epsilon = self.config['power_balance']['epsilon']
            relative_imbalance = power_imbalance / (total_generation + epsilon)  # Avoid division by zero
            
            # Find violations
            violation_mask = abs(relative_imbalance) > tolerance
            
            if violation_mask.any():
                violation_count = violation_mask.sum()
                max_imbalance = abs(relative_imbalance[violation_mask]).max()
                error_msg = f"Power balance violations: {violation_count} records with imbalance > {tolerance*100:.1f}% (max: {max_imbalance*100:.2f}%)"
                self.validation_summary['power_balance_violations'].append(error_msg)
                self.log(error_msg, 'WARNING')
                
                # Log specific violation timestamps
                violation_timestamps = df.index[violation_mask]
                if len(violation_timestamps) <= 5:
                    for ts in violation_timestamps:
                        imb = relative_imbalance.loc[ts] * 100
                        self.log(f"  Power imbalance at {ts}: {imb:.2f}%", 'WARNING')
                else:
                    for ts in violation_timestamps[:3]:
                        imb = relative_imbalance.loc[ts] * 100
                        self.log(f"  Power imbalance at {ts}: {imb:.2f}%", 'WARNING')
                    self.log(f"  ... and {len(violation_timestamps) - 3} more violations", 'WARNING')
        
        self.log("Power balance validation completed")
        return df_cleaned
    
    def detect_clustering_anomalies(self, df: pd.DataFrame, eps=None, min_samples=None) -> pd.DataFrame:
        """
        Detect anomalies using clustering techniques (DBSCAN).
        
        Args:
            df: DataFrame to analyze
            eps: The maximum distance between samples (None uses config default)
            min_samples: The number of samples in neighborhood for core point (None uses config default)
        
        Returns:
            DataFrame with clustering anomalies flagged
        """
        if not self.enable_ml_validation or not self.config['clustering_validation']['enable_clustering_check']:
            return df
        
        # Use config defaults if not specified
        if eps is None:
            eps = self.config['clustering_validation']['eps']
        if min_samples is None:
            min_samples = self.config['clustering_validation']['min_samples']
        
        self.log("Starting clustering-based anomaly detection...")
        
        df_cleaned = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Select relevant columns for clustering using config
        power_prefixes = self.config['clustering_validation']['power_column_prefixes']
        power_cols = [col for col in numeric_cols if any(prefix in col for prefix in power_prefixes)]
        
        if len(power_cols) < 2:
            self.log("Insufficient power columns for clustering analysis", 'WARNING')
            return df_cleaned
        
        # Prepare data for clustering
        clustering_data = df[power_cols].dropna()
        min_points_multiplier = self.config['clustering_validation']['min_points_multiplier']
        min_required_points = min_samples * min_points_multiplier
        if len(clustering_data) < min_required_points:
            self.log("Insufficient data points for clustering analysis", 'WARNING')
            return df_cleaned
        
        try:
            # Standardize the data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(clustering_data)
            
            # Apply DBSCAN clustering
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            cluster_labels = dbscan.fit_predict(scaled_data)
            
            # Find anomalies (points labeled as -1)
            anomaly_mask = cluster_labels == -1
            
            if anomaly_mask.any():
                anomaly_count = anomaly_mask.sum()
                anomaly_indices = clustering_data.index[anomaly_mask]
                
                error_msg = f"Clustering anomalies: {anomaly_count} points detected as outliers"
                self.validation_summary['clustering_anomalies'].append(error_msg)
                self.log(error_msg, 'WARNING')
                
                # Log some example anomalous timestamps
                if len(anomaly_indices) <= 5:
                    for idx in anomaly_indices:
                        self.log(f"  Clustering anomaly at {idx}", 'WARNING')
                else:
                    for idx in anomaly_indices[:3]:
                        self.log(f"  Clustering anomaly at {idx}", 'WARNING')
                    self.log(f"  ... and {len(anomaly_indices) - 3} more clustering anomalies", 'WARNING')
            
        except Exception as e:
            self.log(f"Clustering anomaly detection failed: {str(e)}", 'ERROR')
        
        self.log("Clustering anomaly detection completed")
        return df_cleaned
    
    def comprehensive_anomaly_detection(self, df: pd.DataFrame, 
                                      outlier_methods=None,
                                      enable_rate_check=None,
                                      enable_correlation_check=None,
                                      enable_power_balance_check=None,
                                      enable_clustering_check=None) -> pd.DataFrame:
        """
        Perform comprehensive anomaly detection using multiple methods.
        
        Args:
            df: DataFrame to analyze
            outlier_methods: List of outlier detection methods to apply (None uses config default)
            enable_rate_check: Enable rate of change violation detection (None uses config default)
            enable_correlation_check: Enable correlation anomaly detection (None uses config default)
            enable_power_balance_check: Enable power balance validation (None uses config default)
            enable_clustering_check: Enable clustering-based anomaly detection (None uses config default)
        
        Returns:
            DataFrame with all anomalies detected and handled
        """
        # Use config defaults if not specified
        if outlier_methods is None:
            outlier_methods = self.config['outlier_detection']['default_methods']
        if enable_rate_check is None:
            enable_rate_check = self.config['rate_validation']['enable_rate_check']
        if enable_correlation_check is None:
            enable_correlation_check = self.config['correlation_validation']['enable_correlation_check']
        if enable_power_balance_check is None:
            enable_power_balance_check = self.config['power_balance']['enable_power_balance_check']
        if enable_clustering_check is None:
            enable_clustering_check = self.config['clustering_validation']['enable_clustering_check']
            
        self.log("Starting comprehensive anomaly detection...")
        
        df_processed = df.copy()
        
        # Apply statistical outlier detection methods
        for method in outlier_methods:
            df_processed = self.detect_statistical_outliers(df_processed, method=method)
        
        # Apply rate violation detection
        if enable_rate_check:
            df_processed = self.detect_rate_violations(df_processed)
        
        # Apply correlation anomaly detection
        if enable_correlation_check:
            df_processed = self.detect_correlation_anomalies(df_processed)
        
        # Apply power balance validation
        if enable_power_balance_check:
            df_processed = self.validate_power_balance(df_processed)
        
        # Apply clustering-based anomaly detection
        if enable_clustering_check:
            df_processed = self.detect_clustering_anomalies(df_processed)
        
        # Fill gaps created by anomaly removal if configured
        if self.config['comprehensive_detection']['fill_gaps_after_detection']:
            df_processed = self.fill_gaps(df_processed)
        
        self.log("Comprehensive anomaly detection completed")
        return df_processed
    
    def get_enhanced_validation_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of all validation and anomaly detection results.
        
        Returns:
            Dictionary with detailed validation summary
        """
        base_summary = self.get_validation_summary()
        enhanced_summary = {
            'statistical_outliers_count': len(self.validation_summary['statistical_outliers']),
            'ml_anomalies_count': len(self.validation_summary['ml_anomalies']),
            'rate_violations_count': len(self.validation_summary['rate_violations']),
            'correlation_anomalies_count': len(self.validation_summary['correlation_anomalies']),
            'power_balance_violations_count': len(self.validation_summary['power_balance_violations']),
            'clustering_anomalies_count': len(self.validation_summary['clustering_anomalies']),
            'statistical_outliers': self.validation_summary['statistical_outliers'],
            'ml_anomalies': self.validation_summary['ml_anomalies'],
            'rate_violations': self.validation_summary['rate_violations'],
            'correlation_anomalies': self.validation_summary['correlation_anomalies'],
            'power_balance_violations': self.validation_summary['power_balance_violations'],
            'clustering_anomalies': self.validation_summary['clustering_anomalies']
        }
        
        # Merge with base summary
        base_summary.update(enhanced_summary)
        return base_summary
    
    def detect_large_gaps(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect large gaps in the data that might affect enhanced validation.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with gap analysis results
        """
        self.log("Analyzing data for large gaps that might affect enhanced validation...")
        
        gap_analysis = {
            'large_gaps_found': False,
            'gap_columns': [],
            'gap_percentages': {},
            'recommendations': []
        }
        
        max_gap_steps = DATA_VALIDATION['gap_filling']['max_gap_steps']
        max_nan_percentage = DATA_VALIDATION['gap_filling']['max_nan_percentage']
        
        for col in df.columns:
            if col == df.index.name:
                continue
                
            series = df[col].dropna()
            total_points = len(df)
            missing_points = total_points - len(series)
            missing_percentage = (missing_points / total_points) * 100
            
            # Find gaps
            gaps = self._find_gaps(df[col])
            large_gaps = [gap for gap in gaps if (gap[1] - gap[0] + 1) > max_gap_steps]
            
            if large_gaps or missing_percentage > 20:  # Significant missing data
                gap_analysis['large_gaps_found'] = True
                gap_analysis['gap_columns'].append(col)
                gap_analysis['gap_percentages'][col] = missing_percentage
                
                if missing_percentage > max_nan_percentage:
                    gap_analysis['recommendations'].append(
                        f"Column {col}: {missing_percentage:.1f}% missing data - consider excluding from enhanced validation"
                    )
                elif large_gaps:
                    gap_analysis['recommendations'].append(
                        f"Column {col}: {len(large_gaps)} large gaps found - enhanced validation may be less reliable"
                    )
        
        if gap_analysis['large_gaps_found']:
            self.log("Large gaps detected - enhanced validation reliability may be reduced", 'WARNING')
            for rec in gap_analysis['recommendations']:
                self.log(f"  Recommendation: {rec}", 'WARNING')
        else:
            self.log("No significant gaps detected - enhanced validation should be reliable")
            
        return gap_analysis

    def validate_dataframe_enhanced(self, df: pd.DataFrame, 
                                  use_comprehensive_anomaly_detection=None,
                                  use_advanced_gap_filling=None) -> pd.DataFrame:
        """
        Perform enhanced comprehensive validation on a DataFrame with advanced gap filling.
        
        Workflow:
        1. Simple validation (basic gap filling, type validation, etc.)
        2. Comprehensive validation (anomaly detection, if enabled)
        3. Advanced gap filling (with large gap removal)
        
        Args:
            df: DataFrame to validate
            use_comprehensive_anomaly_detection: Whether to use advanced anomaly detection (None uses config default)
            use_advanced_gap_filling: Whether to use advanced gap filling (None uses config default)
        
        Returns:
            Validated DataFrame with comprehensive validation and advanced gap filling applied
        """
        # Use config defaults if not specified
        if use_comprehensive_anomaly_detection is None:
            use_comprehensive_anomaly_detection = self.config['comprehensive_detection']['enable_all_methods']
        if use_advanced_gap_filling is None:
            use_advanced_gap_filling = (DATA_VALIDATION['gap_filling']['enable_advanced_gap_filling'] and 
                                      ENHANCED_DATA_VALIDATION['advanced_gap_filling']['enable_advanced_gap_filling'])
            
        self.log("Starting enhanced comprehensive data validation workflow...")
        
        # Step 1: Simple validation (standard gap filling, type validation, limits)
        self.log("Step 1: Performing simple validation...")
        df_validated = self.validate_dataframe(df)
        
        # Step 2: Comprehensive validation (anomaly detection) if enabled
        if use_comprehensive_anomaly_detection:
            self.log("Step 2: Performing comprehensive anomaly detection...")
            
            # Analyze gaps before anomaly detection
            gap_analysis = self.detect_large_gaps(df_validated)
            
            if gap_analysis['large_gaps_found']:
                self.log("Large gaps detected - applying enhanced validation with gap-aware settings", 'WARNING')
                # Use more conservative settings for data with large gaps
                df_validated = self.comprehensive_anomaly_detection_gap_aware(df_validated, gap_analysis)
            else:
                # Use standard enhanced validation for clean data
                df_validated = self.comprehensive_anomaly_detection(df_validated)
        else:
            self.log("Step 2: Skipping comprehensive anomaly detection (disabled in config)")
        
        # Step 3: Advanced gap filling (with large gap removal)
        if use_advanced_gap_filling:
            self.log("Step 3: Performing advanced gap filling...")
            df_validated = self.advanced_gap_filling(df_validated)
        else:
            self.log("Step 3: Skipping advanced gap filling (disabled in config)")
        
        # Step 4: Final cleanup - remove rows with excessive gaps
        max_nan_percentage = DATA_VALIDATION['gap_filling']['max_nan_percentage']
        df_validated = self.remove_rows_with_excessive_gaps(df_validated, max_nan_percentage)
        
        self.log("Enhanced comprehensive validation workflow completed")
        
        return df_validated 

    def comprehensive_anomaly_detection_gap_aware(self, df: pd.DataFrame, gap_analysis: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply enhanced validation with awareness of large gaps in the data.
        
        Args:
            df: DataFrame to validate
            gap_analysis: Results from gap analysis
            
        Returns:
            DataFrame with gap-aware enhanced validation applied
        """
        self.log("Applying gap-aware enhanced validation...")
        
        df_processed = df.copy()
        
        # Get columns with significant gaps
        problematic_columns = gap_analysis['gap_columns']
        
        # Apply enhanced validation with modified settings for problematic columns
        for method in self.config['outlier_detection']['default_methods']:
            if method in ['iqr', 'zscore', 'modified_zscore']:
                # Statistical methods are generally safe even with gaps
                df_processed = self.detect_statistical_outliers(df_processed, method=method)
            elif method in ['isolation_forest', 'lof']:
                # ML methods may be affected by interpolated data
                if problematic_columns:
                    self.log(f"Applying {method} with caution due to gaps in {len(problematic_columns)} columns", 'WARNING')
                df_processed = self.detect_statistical_outliers(df_processed, method=method)
        
        # Rate validation - be more conservative with gap-affected data
        if self.config['rate_validation']['enable_rate_check']:
            # Use higher threshold for rate violations when gaps are present
            conservative_multiplier = self.config['rate_validation']['adaptive_threshold_multiplier'] * 1.5
            df_processed = self.detect_rate_violations_gap_aware(df_processed, conservative_multiplier)
        
        # Correlation analysis - skip or be very conservative
        if self.config['correlation_validation']['enable_correlation_check']:
            if len(problematic_columns) < len(df.columns) * 0.3:  # Less than 30% columns affected
                self.log("Applying correlation analysis with reduced sensitivity due to gaps", 'WARNING')
                df_processed = self.detect_correlation_anomalies_gap_aware(df_processed)
            else:
                self.log("Skipping correlation analysis due to extensive gaps", 'WARNING')
        
        # Power balance validation - generally safe
        if self.config['power_balance']['enable_power_balance_check']:
            df_processed = self.validate_power_balance(df_processed)
        
        # Clustering - skip if too many gaps
        if self.config['clustering_validation']['enable_clustering_check']:
            if len(problematic_columns) < len(df.columns) * 0.2:  # Less than 20% columns affected
                df_processed = self.detect_clustering_anomalies(df_processed)
            else:
                self.log("Skipping clustering analysis due to extensive gaps", 'WARNING')
        
        return df_processed

    def detect_rate_violations_gap_aware(self, df: pd.DataFrame, threshold_multiplier: float) -> pd.DataFrame:
        """
        Detect rate violations with awareness of potential interpolation artifacts.
        
        Args:
            df: DataFrame to analyze
            threshold_multiplier: Conservative threshold multiplier for gap-affected data
            
        Returns:
            DataFrame with rate violations handled
        """
        self.log("Starting gap-aware rate violation detection...")
        
        df_cleaned = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            series = df[col]
            if series.dropna().shape[0] < 3:
                continue
            
            # Calculate rate of change
            rate_of_change = series.diff().abs()
            
            # Use more conservative threshold for gap-affected data
            threshold = threshold_multiplier * rate_of_change.std()
            
            # Find rate violations
            violation_mask = rate_of_change > threshold
            
            if violation_mask.any():
                violation_count = violation_mask.sum()
                max_rate = rate_of_change[violation_mask].max()
                error_msg = f"Column {col}: {violation_count} rate violations detected (max rate: {max_rate:.2f}, threshold: {threshold:.2f}) - GAP-AWARE"
                self.validation_summary['rate_violations'].append(error_msg)
                self.log(error_msg, 'WARNING')
                
                # Set violating values to NaN (more conservative approach)
                df_cleaned.loc[violation_mask, col] = np.nan
        
        return df_cleaned

    def detect_correlation_anomalies_gap_aware(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect correlation anomalies with reduced sensitivity for gap-affected data.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            DataFrame with correlation anomalies flagged
        """
        self.log("Starting gap-aware correlation anomaly detection...")
        
        df_cleaned = df.copy()
        
        # Use more conservative correlation threshold
        conservative_threshold = self.config['correlation_validation']['correlation_threshold'] * 1.2
        
        # Apply correlation analysis with conservative settings
        return self.detect_correlation_anomalies(df_cleaned, correlation_threshold=conservative_threshold)


def example_enhanced_validation():
    """
    Example usage of the EnhancedDataValidator class.
    
    This function demonstrates how to use the enhanced validation features
    for power system data analysis.
    """
    import pandas as pd
    import numpy as np
    
    # Create sample power system data
    np.random.seed(42)
    timestamps = pd.date_range('2024-01-01', periods=1000, freq='5min')
    
    sample_data = pd.DataFrame({
        'gen_mvar_1': np.random.normal(20, 5, 1000),
        'gen_mvar_2': np.random.normal(25, 6, 1000),
        'ss_mw_1': np.random.normal(60, 12, 1000),
        'ss_mw_2': np.random.normal(70, 14, 1000),
        'wind_mw_1': np.random.normal(30, 20, 1000),
        'gen_v_1': np.random.normal(1.05, 0.02, 1000),
        'gen_v_2': np.random.normal(1.05, 0.02, 1000),
        'shunt_tap_1': np.random.randint(-10, 11, 1000)
    }, index=timestamps)
    
    # Add some artificial outliers and anomalies
    sample_data.iloc[100:105, 0] = 100   # Extreme outliers in gen_mvar_1
    sample_data.iloc[200:202, 1] = -50   # Negative values in gen_mvar_2
    sample_data.iloc[300, 5] = 2.0       # Voltage outlier in gen_v_1
    
    # Create enhanced validator (uses config defaults)
    enhanced_validator = EnhancedDataValidator()
    
    print("Starting enhanced data validation example...")
    
    # Method 1: Use individual detection methods
    print("\n1. Individual outlier detection methods:")
    
    # IQR-based outlier detection
    df_iqr = enhanced_validator.detect_statistical_outliers(
        sample_data, method='iqr'
    )
    print(f"   IQR outliers detected: {len(enhanced_validator.validation_summary['statistical_outliers'])}")
    
    # Reset for next method
    enhanced_validator.validation_summary['statistical_outliers'] = []
    
    # Isolation Forest detection (uses config default contamination)
    df_iso = enhanced_validator.detect_statistical_outliers(
        sample_data, method='isolation_forest'
    )
    print(f"   Isolation Forest outliers detected: {len(enhanced_validator.validation_summary['statistical_outliers'])}")
    
    # Rate violation detection
    df_rate = enhanced_validator.detect_rate_violations(sample_data)
    print(f"   Rate violations detected: {len(enhanced_validator.validation_summary['rate_violations'])}")
    
    # Power balance validation (uses config default tolerance)
    df_balance = enhanced_validator.validate_power_balance(sample_data)
    print(f"   Power balance violations: {len(enhanced_validator.validation_summary['power_balance_violations'])}")
    
    print("\n2. Comprehensive anomaly detection:")
    
    # Reset validator for comprehensive test
    enhanced_validator = EnhancedDataValidator()
    
    # Method 2: Use comprehensive anomaly detection (uses config defaults)
    df_comprehensive = enhanced_validator.comprehensive_anomaly_detection(sample_data)
    
    # Get enhanced validation summary
    summary = enhanced_validator.get_enhanced_validation_summary()
    
    print(f"   Statistical outliers: {summary['statistical_outliers_count']}")
    print(f"   Rate violations: {summary['rate_violations_count']}")
    print(f"   Correlation anomalies: {summary['correlation_anomalies_count']}")
    print(f"   Power balance violations: {summary['power_balance_violations_count']}")
    print(f"   Clustering anomalies: {summary['clustering_anomalies_count']}")
    
    print("\n3. Enhanced comprehensive validation:")
    
    # Reset validator for full validation test
    enhanced_validator = EnhancedDataValidator()
    
    # Method 3: Use full enhanced validation with advanced gap filling (uses config defaults)
    df_final = enhanced_validator.validate_dataframe_enhanced(sample_data)
    
    final_summary = enhanced_validator.get_enhanced_validation_summary()
    
    print(f"   Total records processed: {final_summary['total_records_processed']}")
    print(f"   Records with errors: {final_summary['records_with_errors']}")
    print(f"   Gaps filled: {final_summary['gaps_filled']}")
    print(f"   Advanced anomalies detected: {final_summary['statistical_outliers_count'] + final_summary['rate_violations_count']}")
    
    print(f"\n3. Advanced gap filling demonstration:")
    
    # Reset validator for advanced gap filling test
    gap_validator = EnhancedDataValidator()
    
    # Create data with various gap sizes for advanced gap filling demonstration
    gap_demo_data = sample_data.copy()
    
    # Add various types of gaps to demonstrate different methods
    gap_demo_data.iloc[50:53, 0] = np.nan    # Small gap (3 points) - should use linear
    gap_demo_data.iloc[100:107, 1] = np.nan  # Medium gap (7 points) - should use spline
    gap_demo_data.iloc[200:212, 2] = np.nan  # Large gap (12 points) - should use advanced methods
    gap_demo_data.iloc[300:330, 3] = np.nan  # Very large gap (30 points) - should be removed
    
    print(f"   Created demo data with gaps: {gap_demo_data.isna().sum().sum()} total NaN values")
    
    # Test different advanced gap filling methods
    methods_to_test = ['adaptive', 'spline', 'polynomial', 'knn']
    
    for method in methods_to_test:
        test_validator = EnhancedDataValidator()
        df_method = test_validator.advanced_gap_filling(gap_demo_data.copy(), method=method)
        filled_count = gap_demo_data.isna().sum().sum() - df_method.isna().sum().sum()
        print(f"   Method '{method}': Filled {filled_count} gaps")
    
    print(f"\nData shape: {sample_data.shape} -> {df_final.shape}")
    print("Enhanced validation with advanced gap filling example completed!")
    
    return df_final, enhanced_validator


if __name__ == "__main__":
    # Run the example when this module is executed directly
    example_enhanced_validation() 