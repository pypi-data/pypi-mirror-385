"""
Representative Operating Points Extraction Module

Author: Sustainable Power Systems Lab (SPSL)
Web: https://sps-lab.org
Contact: info@sps-lab.org

This module provides functions to extract representative operating points 
from power system data using K-means clustering with automatic cluster count selection.

CLUSTERING METHODOLOGY:
======================

The module implements the methodology described in "Automated Extraction of 
Representative Operating Points for a 132 kV Transmission System":

1. DATA FILTERING: Based on power limits and MAPGL constraints
2. FEATURE EXTRACTION: Uses power injection features (ss_mw_*, ss_mvar_*, wind_mw_*)
3. STANDARDIZATION: Applies StandardScaler for feature normalization
4. CLUSTERING: K-means with automatic cluster count selection using multiple metrics
5. MEDOID SELECTION: Returns actual snapshots closest to cluster centers
6. MAPGL BELT: Includes critical low-load operating points near MAPGL threshold
7. OUTPUT GENERATION: Saves results with clean column names and comprehensive reports

CONFIGURATION INTEGRATION:
=========================

All parameters are imported from config.REPRESENTATIVE_OPS:

- defaults: k_max, random_state, mapgl_belt_multiplier, fallback_clusters
- kmeans: n_init, algorithm settings
- quality_thresholds: min_silhouette, excellent/good/acceptable thresholds  
- ranking_weights: Multi-objective ranking weights for cluster selection
- feature_columns: Column prefixes for clustering features
- output_files: Standardized output file names
- validation: Display limits and data requirements

ENHANCED FEATURES:
=================

- CLEAN OUTPUT: Uses centralized clean_column_name() for readable CSV files
- QUALITY ASSESSMENT: Multi-objective cluster quality evaluation
- COMPREHENSIVE REPORTING: Detailed clustering summary with diagnostics
- ADAPTIVE ALGORITHMS: Automatically adjusts to data characteristics
- POWER SYSTEM FOCUS: Specialized for electrical power system analysis
- ENHANCED CLUSTERING: Advanced preprocessing and alternative algorithms for better quality

Functions:
- loadallpowerdf(): Load all_power*.csv files from directory
- extract_representative_ops(): Main function to extract representative points
- extract_representative_ops_enhanced(): Enhanced version with advanced preprocessing
- _select_feature_columns(): Helper to identify clustering features (config-driven)
- _auto_kmeans(): Helper for automatic K-means cluster selection (config-driven)
- _create_clustering_summary(): Generates comprehensive analysis reports
- _analyze_clustering_potential(): Analyze data structure for clustering
- _improve_data_for_clustering(): Preprocess data to improve clusterability
- _engineer_clustering_features(): Create better features for clustering
- _try_alternative_clustering(): Test different clustering algorithms
- _cluster_with_dimensionality_reduction(): Use PCA/t-SNE before clustering

USAGE EXAMPLES:
==============

# Load all_power data from directory
df = loadallpowerdf('results')

# Basic usage with default configuration
rep_df, diagnostics = extract_representative_ops(
    all_power=df, max_power=850, MAPGL=200
)

# Enhanced clustering for better quality
rep_df, diagnostics = extract_representative_ops_enhanced(
    all_power=df, max_power=850, MAPGL=200, 
    output_dir="results"  # Uses enhanced preprocessing
)

# Save results with automatic file naming
rep_df, diagnostics = extract_representative_ops(
    all_power=df, max_power=850, MAPGL=200, 
    output_dir="results"  # Uses config file names
)

# Combined workflow: load data and extract representative points
rep_df, diagnostics = extract_representative_ops(
    loadallpowerdf('results'), max_power=850, MAPGL=200, output_dir='results'
)

# Custom parameters (overrides config defaults)
rep_df, diagnostics = extract_representative_ops(
    all_power=df, max_power=850, MAPGL=200,
    k_max=15, random_state=123  # Override config values
)
"""

from __future__ import annotations
from typing import Tuple, Dict, Optional

import pandas as pd
import numpy as np
import os

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
)
from .system_configuration import clean_column_name, REPRESENTATIVE_OPS, convert_numpy_types

__all__ = ["extract_representative_ops", "extract_representative_ops_enhanced", "loadallpowerdf"]


def loadallpowerdf(directory: str) -> pd.DataFrame:
    """
    Load all_power*.csv file from the specified directory into a DataFrame.
    
    This function searches for files matching the pattern 'all_power*.csv' in the
    specified directory and loads the first matching file. It's designed to work
    with the power system analysis workflow where all_power data files are
    generated with timestamps or version suffixes.
    
    Parameters
    ----------
    directory : str
        Directory path to search for all_power*.csv files.
        
    Returns
    -------
    pd.DataFrame
        Loaded DataFrame with power system data. The index is preserved as
        timestamps if present in the original CSV file.
        
    Raises
    ------
    FileNotFoundError
        If no all_power*.csv file is found in the specified directory.
    ValueError
        If the directory doesn't exist or is not accessible.
        
    Examples
    --------
    >>> # Load all_power data from results directory
    >>> df = loadallpowerdf('results')
    >>> print(f"Loaded {len(df)} snapshots with {len(df.columns)} columns")
    
    >>> # Use in representative operating points extraction
    >>> rep_df, diagnostics = extract_representative_ops(
    ...     loadallpowerdf('results'), max_power=850, MAPGL=200, output_dir='results'
    ... )
    
    Notes
    -----
    - Searches for files matching pattern 'all_power*.csv'
    - Uses pandas.read_csv() with automatic index parsing
    - Preserves original column names and data types
    - Handles common CSV formats with comma or semicolon separators
    """
    import glob
    
    # Check if directory exists
    if not os.path.exists(directory):
        raise ValueError(f"Directory '{directory}' does not exist")
    
    if not os.path.isdir(directory):
        raise ValueError(f"'{directory}' is not a directory")
    
    # Search for all_power*.csv files
    pattern = os.path.join(directory, "all_power*.csv")
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        raise FileNotFoundError(
            f"No all_power*.csv files found in directory '{directory}'. "
            f"Searched pattern: {pattern}"
        )
    
    # Use the first matching file (most recent if sorted)
    file_path = sorted(matching_files)[0]
    
    try:
        # Try to read with automatic index parsing (for timestamps), skip comment lines
        df = pd.read_csv(file_path, index_col=0, parse_dates=True, comment='#')
    except (ValueError, TypeError, IndexError):
        # Fallback: read without index parsing if it fails
        try:
            df = pd.read_csv(file_path, index_col=0, comment='#')
        except (ValueError, TypeError, IndexError):
            # Final fallback: read without index, skip comment lines
            df = pd.read_csv(file_path, comment='#')
    
    print(f"Loaded all_power data from: {file_path}")
    print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"  Columns: {list(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
    
    return df


def _validate_inputs(all_power: pd.DataFrame, max_power: float, MAPGL: float, k_max: int) -> None:
    """Shared validation for inputs."""
    if all_power.empty:
        raise ValueError("Input DataFrame is empty")
    if max_power <= 0:
        raise ValueError(f"max_power must be positive, got {max_power}")
    if MAPGL <= 0:
        raise ValueError(f"MAPGL must be positive, got {MAPGL}")
    if MAPGL >= max_power:
        raise ValueError(f"MAPGL ({MAPGL}) must be less than max_power ({max_power})")
    if k_max < 2:
        raise ValueError(f"k_max must be at least 2, got {k_max}")


def _ensure_net_load_column(df: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
    """Ensure 'net_load' exists; compute if missing. Returns (df_copy, used_existing)."""
    working = df.copy()
    if 'net_load' not in working.columns:
        from .power_system_analytics import calculate_total_load, calculate_net_load
        total_load = calculate_total_load(working)
        net_load = calculate_net_load(working, total_load)
        working['net_load'] = net_load
        print("Calculated net_load from power system data")
        return working, False
    else:
        print("Using existing net_load column from input data")
        return working, True


def _filter_by_limits_and_validate_MAPGL(working: pd.DataFrame, max_power: float, MAPGL: float) -> pd.DataFrame:
    """Apply max power filter and validate MAPGL constraint."""
    working_filtered = working[working["net_load"] <= max_power]
    if (working_filtered["net_load"] < MAPGL).any():
        bad = working_filtered[working_filtered["net_load"] < MAPGL]
        raise ValueError(
            f"{len(bad)} snapshots violate MAPGL ({MAPGL} MW). "
            "Aborting; please correct input."
        )
    return working_filtered


def _exclude_zero_variance_features(df: pd.DataFrame, feat_cols: list[str], error_if_all: bool = True) -> Tuple[list[str], int]:
    """Remove zero-variance features; return (filtered_cols, excluded_count)."""
    feature_data = df[feat_cols]
    zero_variance_mask = feature_data.var() == 0
    excluded = int(zero_variance_mask.sum())
    if excluded > 0:
        print(f"Warning: {excluded} features have zero variance and will be excluded")
    filtered = [col for col in feat_cols if not zero_variance_mask[col]]
    if error_if_all and len(filtered) == 0:
        raise ValueError("No features with non-zero variance found")
    return filtered, excluded


def _compute_medoids(x: np.ndarray, labels: np.ndarray, centres: np.ndarray, index: pd.Index) -> list:
    """Identify medoid indices per cluster given data matrix, labels, and centres."""
    medoid_ids: list = []
    n_clusters = centres.shape[0]
    for k in range(n_clusters):
        members = np.where(labels == k)[0]
        if members.size == 0:
            continue
        centre = centres[k]
        member_vecs = x[members]
        dist2 = ((member_vecs - centre) ** 2).sum(axis=1)
        medoid_pos = members[int(dist2.argmin())]
        medoid_id = index[medoid_pos]
        medoid_ids.append(medoid_id)
    return medoid_ids


def _compute_mapgl_belt_ids(df: pd.DataFrame, MAPGL: float) -> list:
    """Compute indices within the MAPGL belt using configured multiplier."""
    mapgl_multiplier = REPRESENTATIVE_OPS['defaults']['mapgl_belt_multiplier']
    belt_mask = (df["net_load"] > MAPGL) & (df["net_load"] < mapgl_multiplier * MAPGL)
    return df.index[belt_mask].tolist()


def _select_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return columns starting with ss_mw_, ss_mvar_ or wind_mw_."""
    keep_prefix = tuple(REPRESENTATIVE_OPS['feature_columns']['clustering_prefixes'])
    return [c for c in df.columns if c.startswith(keep_prefix)]


def _analyze_clustering_potential(df: pd.DataFrame, feat_cols: list[str]) -> Dict:
    """
    Analyze data structure to understand clustering potential.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with power system data
    feat_cols : list[str]
        List of feature columns for clustering
        
    Returns
    -------
    Dict
        Analysis results including variance, correlations, and dimensionality info
    """
    print("🔍 Analyzing clustering potential...")
    
    feature_data = df[feat_cols]
    
    # Check feature variance
    variances = feature_data.var()
    zero_var_features = (variances == 0).sum()
    low_var_features = (variances < 0.01).sum()
    
    print(f"  Found {len(feat_cols)} features for clustering")
    print(f"  Zero variance features: {zero_var_features}")
    print(f"  Low variance features: {low_var_features}")
    print(f"  Total variance: {variances.sum():.2f}")
    
    # Check for highly correlated features
    corr_matrix = feature_data.corr()
    high_corr_pairs = 0
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) > 0.95:
                high_corr_pairs += 1
    
    print(f"  Highly correlated feature pairs (>0.95): {high_corr_pairs}")
    
    # PCA analysis to see data dimensionality
    try:
        from sklearn.decomposition import PCA
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(feature_data.fillna(0))
        
        pca = PCA()
        pca.fit(X_scaled)
        
        # Find components explaining 95% variance
        cumsum = np.cumsum(pca.explained_variance_ratio_)
        n_components_95 = np.argmax(cumsum >= 0.95) + 1
        
        print(f"  Components for 95% variance: {n_components_95}")
        print(f"  First 5 component variance ratios: {pca.explained_variance_ratio_[:5]}")
        
        return {
            'features': feat_cols,
            'zero_variance': zero_var_features,
            'low_variance': low_var_features,
            'high_correlations': high_corr_pairs,
            'effective_dimensions': n_components_95,
            'variance_ratios': pca.explained_variance_ratio_,
            'feature_variances': variances
        }
    except ImportError:
        print("  Warning: PCA analysis skipped (sklearn not available)")
        return {
            'features': feat_cols,
            'zero_variance': zero_var_features,
            'low_variance': low_var_features,
            'high_correlations': high_corr_pairs,
            'feature_variances': variances
        }


def _improve_data_for_clustering(df: pd.DataFrame, feat_cols: list[str]) -> Tuple[pd.DataFrame, list[str]]:
    """
    Preprocess data to improve clustering potential.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with power system data
    feat_cols : list[str]
        List of feature columns for clustering
        
    Returns
    -------
    Tuple[pd.DataFrame, list[str]]
        Improved DataFrame and updated feature column list
    """
    print("🛠️ Improving data for clustering...")
    
    df_improved = df.copy()
    improved_feat_cols = feat_cols.copy()
    
    # 1. Remove zero variance features
    to_remove = []
    for col in improved_feat_cols:
        if df[col].var() == 0:
            print(f"  Removing zero variance feature: {col}")
            to_remove.append(col)
    
    for col in to_remove:
        improved_feat_cols.remove(col)
    
    # 2. Remove highly correlated features
    if len(improved_feat_cols) > 1:
        feature_data = df_improved[improved_feat_cols]
        corr_matrix = feature_data.corr()
        
        # Find highly correlated pairs and remove one from each pair
        to_remove = set()
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.95:
                    # Remove the feature with lower variance
                    col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                    if feature_data[col1].var() < feature_data[col2].var():
                        to_remove.add(col1)
                    else:
                        to_remove.add(col2)
        
        for col in to_remove:
            if col in improved_feat_cols:
                print(f"  Removing highly correlated feature: {col}")
                improved_feat_cols.remove(col)
    
    # 3. Add temporal features that might improve clustering
    if 'net_load' in df_improved.columns:
        print("  Adding temporal load features...")
        # Add rolling statistics
        df_improved['net_load_ma_24h'] = df_improved['net_load'].rolling(24, min_periods=1).mean()
        df_improved['net_load_std_24h'] = df_improved['net_load'].rolling(24, min_periods=1).std().fillna(0)
        df_improved['net_load_trend'] = df_improved['net_load'].diff().fillna(0)
        
        # Add these to clustering features
        improved_feat_cols.extend(['net_load_ma_24h', 'net_load_std_24h', 'net_load_trend'])
    
    # 4. Add time-based features
    if isinstance(df_improved.index, pd.DatetimeIndex):
        print("  Adding temporal cyclical features...")
        df_improved['hour_of_day'] = df_improved.index.hour
        df_improved['day_of_week'] = df_improved.index.dayofweek
        df_improved['month'] = df_improved.index.month
        
        # Convert to cyclical features
        df_improved['hour_sin'] = np.sin(2 * np.pi * df_improved['hour_of_day'] / 24)
        df_improved['hour_cos'] = np.cos(2 * np.pi * df_improved['hour_of_day'] / 24)
        df_improved['day_sin'] = np.sin(2 * np.pi * df_improved['day_of_week'] / 7)
        df_improved['day_cos'] = np.cos(2 * np.pi * df_improved['day_of_week'] / 7)
        
        improved_feat_cols.extend(['hour_sin', 'hour_cos', 'day_sin', 'day_cos'])
    
    # 5. Remove extreme outliers that might hurt clustering
    outliers_removed = 0
    for col in improved_feat_cols:
        if col in df_improved.columns:
            Q1 = df_improved[col].quantile(0.05)
            Q3 = df_improved[col].quantile(0.95)
            IQR = Q3 - Q1
            if IQR > 0:  # Only process if there's variance
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (df_improved[col] < lower_bound) | (df_improved[col] > upper_bound)
                outlier_count = outlier_mask.sum()
                
                if outlier_count > 0 and outlier_count < len(df_improved) * 0.1:  # Don't remove more than 10%
                    df_improved = df_improved[~outlier_mask]
                    outliers_removed += outlier_count
    
    if outliers_removed > 0:
        print(f"  Removed {outliers_removed} outlier data points")
    
    print(f"  Final clustering features: {len(improved_feat_cols)}")
    print(f"  Data shape after preprocessing: {df_improved.shape}")
    
    return df_improved, improved_feat_cols


def _engineer_clustering_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer better features for clustering.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with power system data
        
    Returns
    -------
    pd.DataFrame
        DataFrame with engineered features
    """
    print("⚙️ Engineering clustering features...")
    
    df_engineered = df.copy()
    
    # 1. Calculate ratios and differences between related variables
    ss_mw_cols = [col for col in df.columns if col.startswith('ss_mw_')]
    ss_mvar_cols = [col for col in df.columns if col.startswith('ss_mvar_')]
    wind_cols = [col for col in df.columns if col.startswith('wind_mw_')]
    
    # Create power factor features (MW/MVAR ratios)
    pf_features_added = 0
    for mw_col in ss_mw_cols:
        corresponding_mvar = mw_col.replace('ss_mw_', 'ss_mvar_')
        if corresponding_mvar in ss_mvar_cols:
            # Avoid division by zero
            mvar_safe = df_engineered[corresponding_mvar].replace(0, 0.001)
            pf_col = mw_col.replace('ss_mw_', 'pf_')
            df_engineered[pf_col] = df_engineered[mw_col] / mvar_safe
            pf_features_added += 1
    
    if pf_features_added > 0:
        print(f"  Added {pf_features_added} power factor features")
    
    # 2. Create load diversity features
    if len(ss_mw_cols) > 1:
        print("  Adding load diversity features...")
        substation_data = df_engineered[ss_mw_cols]
        df_engineered['load_diversity'] = substation_data.std(axis=1) / (substation_data.mean(axis=1) + 0.001)
        df_engineered['load_skewness'] = substation_data.skew(axis=1).fillna(0)
    
    # 3. Create wind penetration features
    if len(wind_cols) > 0 and len(ss_mw_cols) > 0:
        print("  Adding wind penetration features...")
        total_wind = df_engineered[wind_cols].sum(axis=1)
        total_load = df_engineered[ss_mw_cols].sum(axis=1)
        df_engineered['wind_penetration'] = total_wind / (total_load + 0.001)
        if len(wind_cols) > 1:
            df_engineered['wind_variability'] = df_engineered[wind_cols].std(axis=1)
    
    # 4. Create temporal patterns
    if isinstance(df_engineered.index, pd.DatetimeIndex):
        print("  Adding temporal pattern features...")
        # Peak/off-peak indicators
        df_engineered['is_peak_hour'] = df_engineered.index.hour.isin([17, 18, 19, 20]).astype(int)
        df_engineered['is_weekend'] = (df_engineered.index.dayofweek >= 5).astype(int)
        
        # Seasonal patterns
        df_engineered['season'] = df_engineered.index.month % 12 // 3
    
    print(f"  Engineered features added. New shape: {df_engineered.shape}")
    
    return df_engineered


def _try_alternative_clustering(df: pd.DataFrame, feat_cols: list[str]) -> Tuple[Optional[np.ndarray], Optional[float], Optional[str]]:
    """
    Try different clustering algorithms to find better results.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with power system data
    feat_cols : list[str]
        List of feature columns for clustering
        
    Returns
    -------
    Tuple[Optional[np.ndarray], Optional[float], Optional[str]]
        Best labels, best silhouette score, best method name
    """
    print("🔄 Trying alternative clustering algorithms...")
    
    try:
        from sklearn.cluster import DBSCAN, AgglomerativeClustering
        from sklearn.mixture import GaussianMixture
    except ImportError:
        print("  Warning: Alternative clustering algorithms not available")
        return None, None, None
    
    # Prepare data
    X = df[feat_cols].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    results = {}
    
    # Try DBSCAN
    try:
        eps_values = [0.3, 0.5, 0.7, 1.0]
        for eps in eps_values:
            dbscan = DBSCAN(eps=eps, min_samples=max(5, len(X_scaled)//100))
            labels_dbscan = dbscan.fit_predict(X_scaled)
            n_clusters = len(set(labels_dbscan)) - (1 if -1 in labels_dbscan else 0)
            if n_clusters > 1:  # More than just noise
                sil_dbscan = silhouette_score(X_scaled, labels_dbscan)
                results[f'DBSCAN_eps_{eps}'] = {'labels': labels_dbscan, 'silhouette': sil_dbscan}
                print(f"    DBSCAN (eps={eps}): {n_clusters} clusters, silhouette: {sil_dbscan:.3f}")
    except Exception as e:
        print(f"    DBSCAN failed: {e}")
    
    # Try Hierarchical Clustering
    for n_clusters in range(2, min(11, len(X_scaled)//10)):
        try:
            agg = AgglomerativeClustering(n_clusters=n_clusters)
            labels_agg = agg.fit_predict(X_scaled)
            sil_agg = silhouette_score(X_scaled, labels_agg)
            results[f'Hierarchical_{n_clusters}'] = {'labels': labels_agg, 'silhouette': sil_agg}
            print(f"    Hierarchical ({n_clusters}): silhouette: {sil_agg:.3f}")
        except Exception as e:
            print(f"    Hierarchical ({n_clusters}) failed: {e}")
            continue
    
    # Try Gaussian Mixture
    for n_components in range(2, min(11, len(X_scaled)//10)):
        try:
            gmm = GaussianMixture(n_components=n_components, random_state=42)
            labels_gmm = gmm.fit_predict(X_scaled)
            sil_gmm = silhouette_score(X_scaled, labels_gmm)
            results[f'GMM_{n_components}'] = {'labels': labels_gmm, 'silhouette': sil_gmm}
            print(f"    GMM ({n_components}): silhouette: {sil_gmm:.3f}")
        except Exception as e:
            print(f"    GMM ({n_components}) failed: {e}")
            continue
    
    # Find best result
    if results:
        best_method = max(results.keys(), key=lambda k: results[k]['silhouette'])
        best_silhouette = results[best_method]['silhouette']
        best_labels = results[best_method]['labels']
        print(f"  Best alternative method: {best_method} with silhouette: {best_silhouette:.3f}")
        return best_labels, best_silhouette, best_method
    
    return None, None, None


def _cluster_with_dimensionality_reduction(df: pd.DataFrame, feat_cols: list[str]) -> Dict:
    """
    Use PCA before clustering to improve results.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with power system data
    feat_cols : list[str]
        List of feature columns for clustering
        
    Returns
    -------
    Dict
        Results from different PCA approaches
    """
    print("📉 Trying dimensionality reduction before clustering...")
    
    try:
        from sklearn.decomposition import PCA
    except ImportError:
        print("  Warning: PCA not available")
        return {}
    
    # Prepare data
    X = df[feat_cols].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    results = {}
    
    # Try PCA reduction
    for n_components in [0.95, 0.90, 0.85]:  # Variance ratios
        try:
            pca = PCA(n_components=n_components)
            X_pca = pca.fit_transform(X_scaled)
            
            print(f"  PCA with {n_components} variance: {X_pca.shape[1]} components")
            
            # Cluster in reduced space
            best_sil = -1
            best_k = 2
            best_labels = None
            for k in range(2, min(11, len(X_pca)//5)):
                try:
                    kmeans = KMeans(n_clusters=k, random_state=42, n_init=20)
                    labels = kmeans.fit_predict(X_pca)
                    sil = silhouette_score(X_pca, labels)
                    if sil > best_sil:
                        best_sil = sil
                        best_k = k
                        best_labels = labels
                except:
                    continue
            
            results[f'PCA_{n_components}'] = {
                'silhouette': best_sil, 
                'k': best_k,
                'labels': best_labels,
                'components': X_pca.shape[1],
                'pca_data': X_pca
            }
            print(f"    Best: k={best_k}, silhouette={best_sil:.3f}")
        except Exception as e:
            print(f"    PCA ({n_components}) failed: {e}")
    
    return results


def _auto_kmeans(
    x: np.ndarray,
    k_max: int = REPRESENTATIVE_OPS['defaults']['k_max'],
    random_state: int | None = REPRESENTATIVE_OPS['defaults']['random_state'],
) -> Tuple[KMeans, Dict[str, float]]:
    """Fit k-means while automatically selecting k with performance optimizations."""
    best_model: KMeans | None = None
    best_score: float = -np.inf
    best_k: int = 0
    best_metrics: dict[str, float] = {}

    # Optimize k range based on data size
    n_samples = len(x)
    k_max = min(k_max, n_samples - 1, 20)  # Cap at 20 for performance
    k_min = max(2, min(5, n_samples // 100))  # Adaptive minimum k
    
    # Use parallel processing for multiple k values
    from joblib import Parallel, delayed
    
    def evaluate_k(k):
        try:
            km = KMeans(
                n_clusters=k, 
                random_state=random_state, 
                n_init=REPRESENTATIVE_OPS['kmeans']['n_init']
            )
            labels = km.fit_predict(x)

            sil = silhouette_score(x, labels)
            ch = calinski_harabasz_score(x, labels)
            db = davies_bouldin_score(x, labels)

            # Multi-objective ranking: maximise CH & Sil, minimise DB
            weights = REPRESENTATIVE_OPS['ranking_weights']
            combo = (ch * weights['calinski_harabasz_weight'] + 
                    sil * weights['silhouette_weight'] - 
                    db * weights['davies_bouldin_weight'])
            
            min_silhouette = REPRESENTATIVE_OPS['quality_thresholds']['min_silhouette']
            if sil > min_silhouette:
                return k, combo, km, {"silhouette": sil, "ch": ch, "db": db}
            return k, -np.inf, None, {}
        except Exception:
            return k, -np.inf, None, {}

    # Evaluate k values in parallel
    results = Parallel(n_jobs=-1, prefer="threads")(
        delayed(evaluate_k)(k) for k in range(k_min, k_max + 1)
    )
    
    # Find best result
    for k, score, model, metrics in results:
        if score > best_score and model is not None:
            best_score = score
            best_model = model
            best_k = k
            best_metrics = metrics

    if best_model is None:  # fall-back to default clusters
        fallback_k = REPRESENTATIVE_OPS['defaults']['fallback_clusters']
        best_model = KMeans(
            n_clusters=fallback_k, 
            random_state=random_state, 
            n_init=REPRESENTATIVE_OPS['kmeans']['n_init']
        ).fit(x)
        best_k = fallback_k
        labels = best_model.labels_
        best_metrics = {
            "silhouette": silhouette_score(x, labels),
            "ch": calinski_harabasz_score(x, labels),
            "db": davies_bouldin_score(x, labels),
        }

    best_metrics["k"] = best_k
    return best_model, best_metrics


def _create_visualizations(
    output_dir: str,
    working: pd.DataFrame,
    rep_df: pd.DataFrame,
    info: dict,
    model: KMeans,
    scaler: StandardScaler,
    feat_cols: list,
    max_power: float,
    MAPGL: float,
) -> None:
    """Create comprehensive visualizations for clustering analysis."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        from matplotlib.patches import Rectangle
        import warnings
        warnings.filterwarnings('ignore')
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Clustering Quality Metrics Dashboard
        ax1 = plt.subplot(3, 3, 1)
        metrics = ['Silhouette', 'Calinski-Harabasz', 'Davies-Bouldin']
        values = [info['silhouette'], info['ch'], info['db']]
        colors = ['green' if info['silhouette'] > 0.5 else 'orange' if info['silhouette'] > 0.25 else 'red',
                 'green' if info['ch'] > 100 else 'orange' if info['ch'] > 50 else 'red',
                 'green' if info['db'] < 0.5 else 'orange' if info['db'] < 1.0 else 'red']
        
        bars = ax1.bar(metrics, values, color=colors, alpha=0.7)
        ax1.set_title('Clustering Quality Metrics', fontweight='bold')
        ax1.set_ylabel('Score')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{value:.3f}', ha='center', va='bottom', fontsize=9)
        
        # 2. Cluster Size Distribution
        ax2 = plt.subplot(3, 3, 2)
        cluster_sizes = info['cluster_sizes']
        cluster_labels = [f'C{i+1}' for i in range(len(cluster_sizes))]
        colors = plt.cm.Set3(np.linspace(0, 1, len(cluster_sizes)))
        
        wedges, texts, autotexts = ax2.pie(cluster_sizes, labels=cluster_labels, 
                                          colors=colors, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Cluster Size Distribution', fontweight='bold')
        
        # 3. Net Load Distribution
        ax3 = plt.subplot(3, 3, 3)
        if 'net_load' in working.columns:
            # Original vs Representative
            ax3.hist(working['net_load'], bins=30, alpha=0.6, label='Original', density=True)
            ax3.hist(rep_df['net_load'], bins=15, alpha=0.8, label='Representative', density=True)
            ax3.axvline(MAPGL, color='red', linestyle='--', label=f'MAPGL ({MAPGL} MW)')
            ax3.axvline(max_power, color='red', linestyle='--', label=f'Max Power ({max_power} MW)')
            ax3.set_xlabel('Net Load (MW)')
            ax3.set_ylabel('Density')
            ax3.set_title('Net Load Distribution', fontweight='bold')
            ax3.legend()
        
        # 4. Feature Importance (Variance)
        ax4 = plt.subplot(3, 3, 4)
        if len(feat_cols) > 0:
            feature_vars = working[feat_cols].var().sort_values(ascending=False)
            top_features = feature_vars.head(10)
            
            # Check if we have meaningful variance values
            if len(top_features) > 0 and top_features.max() > 0:
                feature_names = [col.replace('ss_mw_', '').replace('ss_mvar_', '').replace('wind_mw_', '') 
                               for col in top_features.index]
                
                bars = ax4.barh(range(len(top_features)), top_features.values, alpha=0.7)
                ax4.set_yticks(range(len(top_features)))
                ax4.set_yticklabels(feature_names, fontsize=8)
                ax4.set_xlabel('Variance')
                ax4.set_title('Top 10 Features by Variance', fontweight='bold')
                ax4.invert_yaxis()
            else:
                # All variances are zero or very small
                ax4.text(0.5, 0.5, 'All features have\nzero or near-zero variance', 
                        ha='center', va='center', transform=ax4.transAxes, fontsize=10,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.7))
                ax4.set_title('Top 10 Features by Variance', fontweight='bold')
                ax4.set_xlim(0, 1)
                ax4.set_ylim(0, 1)
        else:
            # No feature columns available
            ax4.text(0.5, 0.5, 'No feature columns\navailable for analysis', 
                    ha='center', va='center', transform=ax4.transAxes, fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.7))
            ax4.set_title('Top 10 Features by Variance', fontweight='bold')
            ax4.set_xlim(0, 1)
            ax4.set_ylim(0, 1)
        
        # 5. Compression Analysis
        ax5 = plt.subplot(3, 3, 5)
        categories = ['Original', 'Filtered', 'Representative']
        sizes = [info['original_size'], info['filtered_size'], info['n_total']]
        colors = ['lightblue', 'lightgreen', 'orange']
        
        bars = ax5.bar(categories, sizes, color=colors, alpha=0.7)
        ax5.set_title('Data Reduction Analysis', fontweight='bold')
        ax5.set_ylabel('Number of Snapshots')
        
        # Add percentage labels
        for bar, size in zip(bars, sizes):
            height = bar.get_height()
            percentage = (size / info['original_size']) * 100
            ax5.text(bar.get_x() + bar.get_width()/2., height + max(sizes)*0.01,
                    f'{percentage:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # 6. MAPGL Belt Analysis
        ax6 = plt.subplot(3, 3, 6)
        if 'net_load' in working.columns:
            mapgl_multiplier = REPRESENTATIVE_OPS['defaults']['mapgl_belt_multiplier']
            belt_mask = (working["net_load"] > MAPGL) & (working["net_load"] < mapgl_multiplier * MAPGL)
            
            # Create histogram with MAPGL belt highlighted
            n, bins, patches = ax6.hist(working['net_load'], bins=50, alpha=0.6, color='lightblue')
            
            # Highlight MAPGL belt
            belt_indices = np.where((bins[:-1] >= MAPGL) & (bins[1:] <= mapgl_multiplier * MAPGL))[0]
            for idx in belt_indices:
                patches[idx].set_facecolor('red')
                patches[idx].set_alpha(0.8)
            
            ax6.axvline(MAPGL, color='red', linestyle='--', linewidth=2, label=f'MAPGL ({MAPGL} MW)')
            ax6.axvline(mapgl_multiplier * MAPGL, color='red', linestyle='--', linewidth=2, 
                       label=f'MAPGL Belt Upper ({mapgl_multiplier * MAPGL:.1f} MW)')
            ax6.set_xlabel('Net Load (MW)')
            ax6.set_ylabel('Frequency')
            ax6.set_title('MAPGL Belt Analysis', fontweight='bold')
            ax6.legend()
        
        # 7. Top Features Cluster Analysis
        ax7 = plt.subplot(3, 3, 7)
        
        if len(feat_cols) == 0:
            # No feature columns available
            ax7.text(0.5, 0.5, 'No feature columns\navailable for analysis', 
                    ha='center', va='center', transform=ax7.transAxes, fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.7))
            ax7.set_title('Top Features Cluster Analysis', fontweight='bold')
            ax7.set_xlim(0, 1)
            ax7.set_ylim(0, 1)
        else:
            try:
                # Get the most variable features for cluster analysis
                feature_vars = working[feat_cols].var().sort_values(ascending=False)
                n_top_features = min(10, len(feat_cols))  # Show top 10 or fewer
                top_feature_cols = feature_vars.head(n_top_features).index.tolist()
                
                # Get cluster centers for top features only
                top_feature_indices = [feat_cols.index(col) for col in top_feature_cols]
                cluster_centers_orig = scaler.inverse_transform(model.cluster_centers_)
                top_cluster_centers = cluster_centers_orig[:, top_feature_indices]
                
                # Create simplified feature names
                feature_names_short = [col.replace('ss_mw_', '').replace('ss_mvar_', '').replace('wind_mw_', '') 
                                     for col in top_feature_cols]
                
                # Create heatmap for top features
                im = ax7.imshow(top_cluster_centers.T, cmap='RdYlBu_r', aspect='auto')
                ax7.set_xticks(range(model.n_clusters))
                ax7.set_xticklabels([f'C{i+1}' for i in range(model.n_clusters)])
                ax7.set_yticks(range(len(feature_names_short)))
                ax7.set_yticklabels(feature_names_short, fontsize=8)
                ax7.set_title(f'Top {n_top_features} Features by Variance\n({len(feat_cols)} total features)', fontweight='bold')
                plt.colorbar(im, ax=ax7, label='Feature Value', shrink=0.8)
                
            except Exception as e:
                # Fallback: show cluster statistics summary
                ax7.text(0.5, 0.5, f'Cluster Analysis:\n{model.n_clusters} clusters\n{len(feat_cols)} features\n\nSilhouette: {info.get("silhouette", 0):.3f}', 
                        ha='center', va='center', transform=ax7.transAxes, fontsize=10,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
                ax7.set_title('Cluster Summary', fontweight='bold')
                ax7.set_xlim(0, 1)
                ax7.set_ylim(0, 1)
        
        # 8. Quality Assessment Summary
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        # Determine overall quality
        silhouette_val = info.get('silhouette', 0)
        compression_ratio = info['original_size'] / info['n_total']
        
        if silhouette_val > 0.7 and compression_ratio > 20:
            overall_quality = "EXCELLENT"
            quality_color = "green"
        elif silhouette_val > 0.5 and compression_ratio > 10:
            overall_quality = "GOOD"
            quality_color = "orange"
        elif silhouette_val > 0.25:
            overall_quality = "ACCEPTABLE"
            quality_color = "red"
        else:
            overall_quality = "POOR"
            quality_color = "darkred"
        
        summary_text = f"""
OVERALL QUALITY: {overall_quality}

CLUSTERING METRICS:
• Silhouette Score: {silhouette_val:.3f}
• Calinski-Harabasz: {info['ch']:.1f}
• Davies-Bouldin: {info['db']:.3f}
• Optimal Clusters: {info['k']}

DATA REDUCTION:
• Original: {info['original_size']:,} snapshots
• Representative: {info['n_total']} snapshots
• Compression: {compression_ratio:.1f}:1
• Retention: {(info['n_total']/info['original_size'])*100:.1f}%

REPRESENTATIVE POINTS:
• Medoids: {info['n_medoid']}
• MAPGL Belt: {info['n_belt']}
• Total: {info['n_total']}
        """
        
        ax8.text(0.05, 0.95, summary_text, transform=ax8.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor=quality_color, alpha=0.1))
        
        # 9. Recommendations
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        recommendations = []
        if silhouette_val < 0.25:
            recommendations.append("WARNING: Consider increasing dataset size")
            recommendations.append("WARNING: Review feature selection")
            recommendations.append("WARNING: Check data quality")
        elif silhouette_val < 0.5:
            recommendations.append("CAUTION: Validate results carefully")
            recommendations.append("CAUTION: Consider parameter adjustment")
        
        if compression_ratio < 5:
            recommendations.append("INFO: Low data reduction - high diversity")
        
        if info['n_belt'] == 0:
            recommendations.append("INFO: No MAPGL belt snapshots found")
        
        if not recommendations:
            recommendations.append("SUCCESS: Results look good for analysis")
            recommendations.append("SUCCESS: Proceed with power system studies")
        
        rec_text = "RECOMMENDATIONS:\n\n" + "\n".join(recommendations)
        ax9.text(0.05, 0.95, rec_text, transform=ax9.transAxes, fontsize=9,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.3))
        
        plt.tight_layout()
        
        # Save the visualization
        output_files = REPRESENTATIVE_OPS['output_files']
        viz_filename = os.path.join(output_dir, 'clustering_visualization.png')
        plt.savefig(viz_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  Visualization: {viz_filename}")
        
    except ImportError:
        print("Warning: matplotlib/seaborn not available. Skipping visualizations.")
    except Exception as e:
        print(f"Warning: Could not create visualizations: {e}")


def _create_clustering_summary(
    filename: str,
    all_power: pd.DataFrame,
    working: pd.DataFrame,
    rep_df: pd.DataFrame,
    info: dict,
    max_power: float,
    MAPGL: float,
    k_max: int,
    random_state: int,
    feat_cols: list,
    model: KMeans,
    scaler: StandardScaler,
) -> None:
    """Create a comprehensive clustering summary report with improved formatting."""
    with open(filename, "w", encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("REPRESENTATIVE OPERATING POINTS CLUSTERING SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Author: Sustainable Power Systems Lab (SPSL)\n")
        f.write(f"Web: https://sps-lab.org\n")
        f.write(f"Contact: info@sps-lab.org\n")
        f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # EXECUTIVE SUMMARY
        f.write("📋 EXECUTIVE SUMMARY\n")
        f.write("="*50 + "\n")
        
        # Determine overall quality
        silhouette_val = info.get('silhouette', 0)
        compression_ratio = info['original_size'] / info['n_total']
        
        if silhouette_val > 0.7 and compression_ratio > 20:
            overall_quality = "EXCELLENT"
            quality_emoji = "🟢"
        elif silhouette_val > 0.5 and compression_ratio > 10:
            overall_quality = "GOOD"
            quality_emoji = "🟡"
        elif silhouette_val > 0.25:
            overall_quality = "ACCEPTABLE"
            quality_emoji = "🟠"
        else:
            overall_quality = "POOR"
            quality_emoji = "🔴"
        
        f.write(f"{quality_emoji} Overall Quality: {overall_quality}\n")
        f.write(f"📊 Clustering Score: {silhouette_val:.3f} (Silhouette)\n")
        f.write(f"📈 Data Reduction: {compression_ratio:.1f}:1 ({((compression_ratio-1)/compression_ratio)*100:.1f}% reduction)\n")
        f.write(f"⚡ Representative Points: {info['n_total']} from {info['original_size']:,} original\n")
        f.write(f"🎯 Optimal Clusters: {info['k']}\n\n")
        
        # 1. METHODOLOGY OVERVIEW
        f.write("1. 📚 METHODOLOGY OVERVIEW\n")
        f.write("-"*30 + "\n")
        f.write("This analysis implements the methodology described in:\n")
        f.write("'Automated Extraction of Representative Operating Points for a 132 kV Transmission System'\n\n")
        f.write("🔄 Process Steps:\n")
        f.write("   1️⃣ Data filtering based on power limits and MAPGL constraints\n")
        f.write("   2️⃣ Feature extraction from power injection variables\n")
        f.write("   3️⃣ Data standardization using StandardScaler\n")
        f.write("   4️⃣ K-means clustering with automatic cluster count selection\n")
        f.write("   5️⃣ Medoid identification (actual snapshots closest to cluster centers)\n")
        f.write("   6️⃣ Addition of MAPGL-belt snapshots for critical low-load conditions\n\n")
        
        # 2. INPUT PARAMETERS
        f.write("2. ⚙️ INPUT PARAMETERS\n")
        f.write("-"*30 + "\n")
        f.write(f"🔋 Maximum Power Limit:        {max_power:.2f} MW\n")
        f.write(f"⚡ MAPGL (Min Generation):     {MAPGL:.2f} MW\n")
        f.write(f"🎯 Maximum Clusters Tested:    {k_max}\n")
        f.write(f"🎲 Random State:               {random_state}\n")
        mapgl_multiplier = REPRESENTATIVE_OPS['defaults']['mapgl_belt_multiplier']
        f.write(f"📏 MAPGL Belt Range:           {MAPGL:.2f} - {mapgl_multiplier*MAPGL:.2f} MW\n\n")
        
        # 3. DATA PROCESSING SUMMARY
        f.write("3. 📊 DATA PROCESSING SUMMARY\n")
        f.write("-"*30 + "\n")
        f.write(f"📁 Original Dataset Size:      {info['original_size']:,} snapshots\n")
        f.write(f"🔍 After Power Filtering:      {info['filtered_size']:,} snapshots\n")
        f.write(f"📉 Reduction Factor:           {info['original_size']/info['filtered_size']:.2f}x\n\n")
        
        # Data quality information
        if 'data_quality' in info:
            f.write("🔍 Data Quality Assessment:\n")
            f.write(f"   • Missing Values: {info['data_quality']['missing_values']}\n")
            f.write(f"   • Infinite Values: {info['data_quality']['infinite_values']}\n")
            f.write(f"   • Zero Variance Features Excluded: {info['data_quality']['zero_variance_features_excluded']}\n\n")
        
        f.write("🎯 Feature Columns Used for Clustering:\n")
        for i, col in enumerate(feat_cols, 1):
            f.write(f"   {i:2d}. {col}\n")
        f.write(f"\n📊 Total Features:             {len(feat_cols)}\n\n")
        
        # 4. CLUSTERING RESULTS
        f.write("4. 🎯 CLUSTERING RESULTS\n")
        f.write("-"*30 + "\n")
        f.write(f"🏆 Optimal Number of Clusters: {info['k']}\n")
        f.write(f"📈 Silhouette Score:           {info['silhouette']:.4f}\n")
        f.write(f"📊 Calinski-Harabasz Index:    {info['ch']:.2f}\n")
        f.write(f"📉 Davies-Bouldin Index:       {info['db']:.4f}\n\n")
        
        f.write("📊 Cluster Composition:\n")
        for i, size in enumerate(info['cluster_sizes']):
            percentage = (size / info['filtered_size']) * 100
            f.write(f"   Cluster {i+1:2d}: {size:6,} snapshots ({percentage:5.1f}%)\n")
        f.write(f"   Total:       {sum(info['cluster_sizes']):6,} snapshots (100.0%)\n\n")
        
        # 5. REPRESENTATIVE POINTS SELECTION
        f.write("5. ⚡ REPRESENTATIVE POINTS SELECTION\n")
        f.write("-"*30 + "\n")
        f.write(f"🎯 Medoids from Clusters:      {info['n_medoid']}\n")
        f.write(f"📏 MAPGL Belt Snapshots:       {info['n_belt']}\n")
        f.write(f"📊 Total Representative Points: {info['n_total']}\n")
        f.write(f"📉 Compression Ratio:          {info['original_size']/info['n_total']:.1f}:1\n")
        f.write(f"📈 Retention Rate:             {(info['n_total']/info['original_size'])*100:.2f}%\n\n")
        
        # 6. QUALITY ASSESSMENT
        f.write("6. ✅ QUALITY ASSESSMENT\n")
        f.write("-"*30 + "\n")
        
        f.write("📊 Silhouette Score Analysis:\n")
        if silhouette_val > 0.7:
            f.write("   ✅ Excellent separation: Clusters are well-defined and distinct\n")
            f.write("   ✅ Representative points are highly reliable\n")
            f.write("   ✅ Strong confidence in operating point selection\n")
        elif silhouette_val > 0.5:
            f.write("   ✅ Good separation: Clusters are reasonably well-defined\n")
            f.write("   ✅ Representative points are reliable\n")
            f.write("   ⚠️ Minor overlap between some clusters is acceptable\n")
        elif silhouette_val > 0.25:
            f.write("   ⚠️ Moderate separation: Some cluster overlap present\n")
            f.write("   ⚠️ Representative points should be validated carefully\n")
            f.write("   ⚠️ Consider additional validation of selected points\n")
        else:
            f.write("   ❌ Poor separation: Significant cluster overlap\n")
            f.write("   ❌ Representative points may not be reliable\n")
            f.write("   ❌ Strong recommendation to revise approach\n")
        
        f.write(f"\n📈 Calinski-Harabasz Index Analysis (Current: {info['ch']:.1f}):\n")
        if info['ch'] > 100:
            f.write("   ✅ High index: Well-separated, compact clusters\n")
            f.write("   ✅ Strong internal cluster cohesion\n")
        elif info['ch'] > 50:
            f.write("   ✅ Moderate index: Reasonably good cluster structure\n")
        else:
            f.write("   ⚠️ Low index: Clusters may be poorly separated or too diffuse\n")
        
        f.write(f"\n📉 Davies-Bouldin Index Analysis (Current: {info['db']:.3f}):\n")
        if info['db'] < 0.5:
            f.write("   ✅ Excellent: Very low similarity between clusters\n")
        elif info['db'] < 1.0:
            f.write("   ✅ Good: Low similarity between clusters\n")
        elif info['db'] < 1.5:
            f.write("   ⚠️ Acceptable: Moderate similarity between clusters\n")
        else:
            f.write("   ❌ Poor: High similarity between clusters indicates overlap\n")
        f.write("\n")
        
        # 7. RECOMMENDATIONS
        f.write("7. 💡 RECOMMENDATIONS AND NEXT STEPS\n")
        f.write("-"*30 + "\n")
        
        if silhouette_val < 0.25:
            f.write("⚠️ LOW CLUSTERING QUALITY WARNING:\n")
            f.write("   Consider:\n")
            f.write("   • Increasing the dataset size\n")
            f.write("   • Reviewing feature selection\n")
            f.write("   • Adjusting power limits or MAPGL\n\n")
        
        if info['n_total'] < 10:
            f.write("⚠️ FEW REPRESENTATIVE POINTS:\n")
            f.write("   Consider lowering k_max or adjusting clustering parameters\n\n")
        
        f.write("🔧 For power system analysis:\n")
        f.write("   1. Validate representative points against operational constraints\n")
        f.write("   2. Verify load flow convergence for all selected snapshots\n")
        f.write("   3. Check that critical operating conditions are captured\n")
        f.write("   4. Consider seasonal or temporal patterns if relevant\n\n")
        
        # 8. USAGE RECOMMENDATIONS
        f.write("8. 🎯 RECOMMENDED USAGE BASED ON RESULTS\n")
        f.write("-"*30 + "\n")
        
        if overall_quality in ["EXCELLENT", "GOOD"]:
            f.write("✅ HIGH CONFIDENCE APPLICATIONS:\n")
            f.write("   • Long-term transmission planning studies\n")
            f.write("   • Investment analysis and capacity expansion\n")
            f.write("   • Security assessment and contingency analysis\n")
            f.write("   • Renewable integration studies\n")
            f.write("   • Grid code compliance verification\n\n")
        
        if overall_quality in ["ACCEPTABLE"]:
            f.write("⚠️ MODERATE CONFIDENCE APPLICATIONS:\n")
            f.write("   • Preliminary planning studies (with validation)\n")
            f.write("   • Scenario development for detailed analysis\n")
            f.write("   • Identification of critical operating conditions\n")
            f.write("   ⚠️ Recommend additional validation before final decisions\n\n")
        
        if overall_quality in ["POOR"]:
            f.write("❌ LIMITED CONFIDENCE APPLICATIONS:\n")
            f.write("   • Initial screening studies only\n")
            f.write("   • Pattern identification in operational data\n")
            f.write("   • Troubleshooting and methodology development\n")
            f.write("   ❌ NOT recommended for critical planning decisions\n\n")
        
        f.write("="*80 + "\n")
        f.write("END OF CLUSTERING SUMMARY\n")
        f.write("="*80 + "\n")


def extract_representative_ops_enhanced(
    all_power: pd.DataFrame,
    max_power: float,
    MAPGL: float,
    k_max: int = REPRESENTATIVE_OPS['defaults']['k_max'],
    random_state: int = REPRESENTATIVE_OPS['defaults']['random_state'],
    output_dir: Optional[str] = None,
    use_enhanced_preprocessing: bool = True,
    try_alternative_algorithms: bool = True,
    use_dimensionality_reduction: bool = True,
) -> Tuple[pd.DataFrame, dict]:
    """
    Extract representative operating points with enhanced clustering techniques.

    This function provides advanced clustering capabilities beyond the standard
    extract_representative_ops function. It includes sophisticated preprocessing,
    feature engineering, alternative clustering algorithms, and dimensionality
    reduction to achieve better clustering quality.

    ENHANCED FEATURES:
    ==================
    - Advanced data preprocessing and outlier removal
    - Feature engineering (power factors, load diversity, temporal patterns)
    - Alternative clustering algorithms (DBSCAN, Hierarchical, Gaussian Mixture)
    - Dimensionality reduction using PCA
    - Comprehensive quality analysis and reporting
    - Automatic algorithm selection based on performance

    CLUSTERING WORKFLOW:
    ===================
    1. Standard data filtering and validation
    2. Enhanced preprocessing (outlier removal, correlation analysis)
    3. Feature engineering (power factors, temporal features)
    4. Alternative algorithm testing (DBSCAN, Hierarchical, GMM)
    5. Dimensionality reduction clustering (PCA + K-means)
    6. Best method selection based on silhouette score
    7. Medoid identification and MAPGL belt analysis
    8. Enhanced reporting with method comparison

    Parameters
    ----------
    all_power : pandas.DataFrame
        Input time-series DataFrame with power system data
    max_power : float
        Maximum dispatchable generation for the horizon under study [MW]
    MAPGL : float
        Minimum active-power generation limit [MW]
    k_max : int, optional
        Upper bound for clusters to test (default from config)
    random_state : int, optional
        Reproducibility parameter (default from config)
    output_dir : str or None, optional
        Directory to save results with enhanced reports
    use_enhanced_preprocessing : bool, optional
        Enable advanced preprocessing and feature engineering (default: True)
    try_alternative_algorithms : bool, optional
        Test alternative clustering algorithms (default: True)
    use_dimensionality_reduction : bool, optional
        Try PCA-based dimensionality reduction (default: True)

    Returns
    -------
    rep_df : pandas.DataFrame
        Representative operating points with enhanced selection
    info : dict
        Enhanced diagnostics including:
        - Standard clustering metrics (silhouette, ch, db, k)
        - Method comparison results
        - Enhanced preprocessing statistics
        - Alternative algorithm performance
        - Dimensionality reduction results
        - Feature engineering summary

    Examples
    --------
    >>> # Enhanced clustering with all features enabled
    >>> rep_df, diag = extract_representative_ops_enhanced(
    ...     df, max_power=850, MAPGL=200, output_dir='results'
    ... )
    >>> print(f"Enhanced quality: {diag['best_silhouette']:.3f}")
    >>> print(f"Best method: {diag['best_method']}")
    
    >>> # Enhanced clustering with specific features
    >>> rep_df, diag = extract_representative_ops_enhanced(
    ...     df, max_power=850, MAPGL=200,
    ...     use_enhanced_preprocessing=True,
    ...     try_alternative_algorithms=False,
    ...     use_dimensionality_reduction=True
    ... )
    
    >>> # Compare with standard method
    >>> std_df, std_diag = extract_representative_ops(df, max_power=850, MAPGL=200)
    >>> enh_df, enh_diag = extract_representative_ops_enhanced(df, max_power=850, MAPGL=200)
    >>> print(f"Standard: {std_diag['silhouette']:.3f}")
    >>> print(f"Enhanced: {enh_diag['best_silhouette']:.3f}")
    """
    
    print("🚀 Starting Enhanced Representative Operating Points Extraction")
    print("="*70)
    
    # Input validation (shared)
    _validate_inputs(all_power, max_power, MAPGL, k_max)
    
    # Data quality checks
    missing_data = all_power.isnull().sum().sum()
    if missing_data > 0:
        print(f"Warning: {missing_data} missing values detected in input data")
    
    # Check for infinite values
    inf_count = np.isinf(all_power.select_dtypes(include=[np.number])).sum().sum()
    if inf_count > 0:
        raise ValueError(f"Input data contains {inf_count} infinite values")
    
    # Prepare net_load and filter by limits
    working, _ = _ensure_net_load_column(all_power)
    working = _filter_by_limits_and_validate_MAPGL(working, max_power, MAPGL)

    # Initialize enhanced diagnostics
    enhanced_info = {
        'original_size': len(all_power),
        'filtered_size': len(working),
        'preprocessing_enabled': use_enhanced_preprocessing,
        'alternative_algorithms_enabled': try_alternative_algorithms,
        'dimensionality_reduction_enabled': use_dimensionality_reduction,
        'method_comparison': {},
        'best_method': 'Standard K-means',
        'best_silhouette': 0.0,
        'feature_engineering_summary': {},
    }

    # Step 1: Get initial feature columns
    feat_cols = _select_feature_columns(working)
    if len(feat_cols) == 0:
        raise ValueError("No suitable feature columns found (ss_mw_*, ss_mvar_*, wind_mw_*)")
    
    print(f"\n📊 Initial feature analysis:")
    print(f"  Found {len(feat_cols)} initial features")
    
    # Step 2: Analyze clustering potential
    analysis_results = _analyze_clustering_potential(working, feat_cols)
    enhanced_info['clustering_analysis'] = analysis_results
    
    # Step 3: Enhanced preprocessing if enabled
    if use_enhanced_preprocessing:
        print(f"\n🛠️ Enhanced Preprocessing Phase")
        
        # Improve data for clustering
        working_improved, improved_feat_cols = _improve_data_for_clustering(working, feat_cols)
        
        # Engineer additional features
        working_engineered = _engineer_clustering_features(working_improved)
        
        # Update feature list with engineered features
        engineered_cols = [col for col in working_engineered.columns 
                          if col.startswith(('pf_', 'wind_', 'load_', 'is_', 'season', 
                                           'net_load_ma', 'net_load_std', 'net_load_trend',
                                           'hour_sin', 'hour_cos', 'day_sin', 'day_cos'))]
        final_feat_cols = improved_feat_cols + engineered_cols
        
        # Remove duplicates and missing columns
        final_feat_cols = [col for col in final_feat_cols if col in working_engineered.columns]
        final_feat_cols = list(dict.fromkeys(final_feat_cols))  # Remove duplicates preserving order
        
        working_final = working_engineered
        enhanced_info['feature_engineering_summary'] = {
            'original_features': len(feat_cols),
            'after_preprocessing': len(improved_feat_cols),
            'engineered_features': len(engineered_cols),
            'final_features': len(final_feat_cols),
            'data_shape_change': f"{working.shape} -> {working_final.shape}"
        }
        
        print(f"  Feature engineering complete: {len(feat_cols)} -> {len(final_feat_cols)} features")
    else:
        working_final = working
        final_feat_cols = feat_cols
        enhanced_info['feature_engineering_summary'] = {
            'original_features': len(feat_cols),
            'final_features': len(final_feat_cols),
            'preprocessing_skipped': True
        }
    
    # Check final feature data quality
    feature_data = working_final[final_feat_cols]
    final_feat_cols, zero_var_excluded = _exclude_zero_variance_features(working_final, final_feat_cols, error_if_all=True)
    
    # Prepare data for clustering
    x_raw = working_final[final_feat_cols].fillna(0).to_numpy(float)
    
    # Check if we have any samples after filtering
    if x_raw.shape[0] == 0:
        raise ValueError(
            "No samples remaining after data filtering. This can occur when:\n"
            "1. All data points violate the power limits or MAPGL constraints\n"
            "2. The filtering criteria are too restrictive for the available data\n"
            "3. The input dataset is empty or contains only invalid data\n\n"
            "Please check your input data and filtering parameters:\n"
            f"- max_power: {max_power} MW\n"
            f"- MAPGL: {MAPGL} MW\n"
            f"- Original dataset size: {len(all_power)} snapshots\n"
            f"- After filtering: {len(working_final)} snapshots"
        )
    
    scaler = StandardScaler()
    x = scaler.fit_transform(x_raw)
    
    # Step 4: Try standard K-means first
    print(f"\n🎯 Standard K-means Clustering")
    standard_model, standard_metrics = _auto_kmeans(x, k_max=k_max, random_state=random_state)
    enhanced_info['method_comparison']['Standard K-means'] = standard_metrics
    enhanced_info['best_silhouette'] = standard_metrics['silhouette']
    enhanced_info['best_method'] = 'Standard K-means'
    best_model = standard_model
    best_labels = standard_model.labels_
    
    print(f"  Standard K-means: k={standard_metrics['k']}, silhouette={standard_metrics['silhouette']:.3f}")
    
    # Step 5: Try alternative algorithms if enabled
    if try_alternative_algorithms:
        print(f"\n🔄 Alternative Clustering Algorithms")
        alt_labels, alt_score, alt_method = _try_alternative_clustering(working_final, final_feat_cols)
        
        if alt_score is not None and alt_score > enhanced_info['best_silhouette']:
            enhanced_info['best_silhouette'] = alt_score
            enhanced_info['best_method'] = alt_method
            best_labels = alt_labels
            print(f"  🎉 Alternative algorithm improved quality: {alt_score:.3f}")
            enhanced_info['method_comparison'][alt_method] = {'silhouette': alt_score}
    
    # Step 6: Try dimensionality reduction if enabled
    if use_dimensionality_reduction:
        print(f"\n📉 Dimensionality Reduction Clustering")
        pca_results = _cluster_with_dimensionality_reduction(working_final, final_feat_cols)
        
        for method_name, result in pca_results.items():
            enhanced_info['method_comparison'][method_name] = result
            if result['silhouette'] > enhanced_info['best_silhouette']:
                enhanced_info['best_silhouette'] = result['silhouette']
                enhanced_info['best_method'] = method_name
                best_labels = result['labels']
                print(f"  🎉 PCA method improved quality: {result['silhouette']:.3f}")
    
    # Step 7: Generate medoids using best clustering result
    print(f"\n🎯 Generating Representative Points")
    print(f"  Best method: {enhanced_info['best_method']}")
    print(f"  Best quality: {enhanced_info['best_silhouette']:.3f}")
    
    # For non-standard methods, we need to recompute cluster centers
    if enhanced_info['best_method'] != 'Standard K-means':
        # Create a simple K-means model with the best number of clusters for medoid calculation
        n_clusters = len(np.unique(best_labels))
        if n_clusters < 2:
            print("  Warning: Best method produced < 2 clusters, falling back to standard K-means")
            best_model = standard_model
            best_labels = standard_model.labels_
            enhanced_info['best_method'] = 'Standard K-means (fallback)'
        else:
            # Create K-means model for medoid calculation
            temp_model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
            temp_model.fit(x)
            best_model = temp_model
    
    # Medoid identification
    centres = best_model.cluster_centers_
    medoid_ids = _compute_medoids(x, best_labels, centres, working_final.index)

    # MAPGL belt snapshots
    belt_ids = _compute_mapgl_belt_ids(working_final, MAPGL)

    all_ids = sorted(set(medoid_ids).union(belt_ids))
    rep_df = working_final.loc[all_ids].copy()
    
    # Step 8: Compile comprehensive diagnostics
    enhanced_info.update({
        **standard_metrics,  # Include standard metrics
        'cluster_sizes': np.bincount(best_labels, minlength=best_model.n_clusters).tolist(),
        'n_medoid': len(medoid_ids),
        'n_belt': len(belt_ids),
        'n_total': len(rep_df),
        'filtered_size': len(working_final),
        'feature_columns': final_feat_cols,
        'data_quality': {
            'missing_values': missing_data,
            'infinite_values': inf_count,
            'zero_variance_features_excluded': zero_var_excluded
        }
    })
    
    # Step 9: Save enhanced results
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        # Save representative operating points
        output_files = REPRESENTATIVE_OPS['output_files']
        filename_rep = os.path.join(output_dir, 'enhanced_' + output_files['representative_points'])
        
        rep_df_clean = rep_df.copy()
        rep_df_clean.columns = [clean_column_name(col) for col in rep_df_clean.columns]
        # Sort by net_load in descending order for easier inspection
        if 'net_load' in rep_df_clean.columns:
            rep_df_clean = rep_df_clean.sort_values(by='net_load', ascending=False)
        rep_df_clean.to_csv(filename_rep, index=True)
        
        # Create enhanced clustering summary
        summary_filename = os.path.join(output_dir, 'enhanced_' + output_files['clustering_summary'])
        _create_enhanced_clustering_summary(
            summary_filename, all_power, working_final, rep_df, enhanced_info, 
            max_power, MAPGL, k_max, random_state, final_feat_cols
        )
        
        # Create visualizations
        _create_visualizations(
            output_dir, working_final, rep_df, enhanced_info, best_model, scaler, final_feat_cols, max_power, MAPGL
        )

        print(f"\n💾 Enhanced results saved to:")
        print(f"  Representative points: {filename_rep}")
        print(f"  Enhanced summary: {summary_filename}")
    
    print(f"\n🎉 Enhanced clustering complete!")
    print(f"  Quality improvement: {enhanced_info['best_silhouette']:.3f} (method: {enhanced_info['best_method']})")
    print(f"  Representative points: {len(rep_df)}")
    
    return rep_df, enhanced_info


def _create_enhanced_clustering_summary(
    filename: str,
    all_power: pd.DataFrame,
    working: pd.DataFrame,
    rep_df: pd.DataFrame,
    info: dict,
    max_power: float,
    MAPGL: float,
    k_max: int,
    random_state: int,
    feat_cols: list,
) -> None:
    """Create an enhanced clustering summary report."""
    
    with open(filename, "w", encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("ENHANCED REPRESENTATIVE OPERATING POINTS CLUSTERING SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Author: Sustainable Power Systems Lab (SPSL)\n")
        f.write(f"Web: https://sps-lab.org\n")
        f.write(f"Contact: info@sps-lab.org\n")
        f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # EXECUTIVE SUMMARY
        f.write("📋 ENHANCED EXECUTIVE SUMMARY\n")
        f.write("="*50 + "\n")
        
        best_quality = info['best_silhouette']
        compression_ratio = info['original_size'] / info['n_total']
        
        if best_quality > 0.7 and compression_ratio > 20:
            overall_quality = "EXCELLENT"
            quality_emoji = "🟢"
        elif best_quality > 0.5 and compression_ratio > 10:
            overall_quality = "GOOD"
            quality_emoji = "🟡"
        elif best_quality > 0.25:
            overall_quality = "ACCEPTABLE"
            quality_emoji = "🟠"
        else:
            overall_quality = "POOR"
            quality_emoji = "🔴"
        
        f.write(f"{quality_emoji} Overall Quality: {overall_quality}\n")
        f.write(f"🎯 Best Method: {info['best_method']}\n")
        f.write(f"📊 Best Clustering Score: {best_quality:.3f} (Silhouette)\n")
        f.write(f"📈 Data Reduction: {compression_ratio:.1f}:1\n")
        f.write(f"⚡ Representative Points: {info['n_total']} from {info['original_size']:,} original\n\n")
        
        # METHOD COMPARISON
        f.write("🔄 METHOD COMPARISON RESULTS\n")
        f.write("-"*50 + "\n")
        
        for method_name, method_result in info['method_comparison'].items():
            if isinstance(method_result, dict) and 'silhouette' in method_result:
                sil_score = method_result['silhouette']
                status = "🏆 BEST" if method_name == info['best_method'] else "   "
                f.write(f"{status} {method_name:<25}: {sil_score:.3f}\n")
        f.write("\n")
        
        # FEATURE ENGINEERING SUMMARY
        if 'feature_engineering_summary' in info:
            f.write("⚙️ FEATURE ENGINEERING SUMMARY\n")
            f.write("-"*50 + "\n")
            fe_summary = info['feature_engineering_summary']
            
            if info['preprocessing_enabled']:
                f.write(f"✅ Enhanced preprocessing: ENABLED\n")
                f.write(f"   📊 Original features: {fe_summary.get('original_features', 'N/A')}\n")
                f.write(f"   🛠️ After preprocessing: {fe_summary.get('after_preprocessing', 'N/A')}\n")
                f.write(f"   ⚙️ Engineered features: {fe_summary.get('engineered_features', 'N/A')}\n")
                f.write(f"   🎯 Final features: {fe_summary.get('final_features', 'N/A')}\n")
                f.write(f"   📈 Data shape change: {fe_summary.get('data_shape_change', 'N/A')}\n")
            else:
                f.write(f"⚠️ Enhanced preprocessing: DISABLED\n")
                f.write(f"   📊 Features used: {fe_summary.get('final_features', 'N/A')}\n")
            f.write("\n")
        
        # CLUSTERING ANALYSIS
        if 'clustering_analysis' in info:
            f.write("🔍 CLUSTERING POTENTIAL ANALYSIS\n")
            f.write("-"*50 + "\n")
            analysis = info['clustering_analysis']
            f.write(f"📊 Zero variance features: {analysis.get('zero_variance', 'N/A')}\n")
            f.write(f"📉 Low variance features: {analysis.get('low_variance', 'N/A')}\n")
            f.write(f"🔗 Highly correlated pairs: {analysis.get('high_correlations', 'N/A')}\n")
            if 'effective_dimensions' in analysis:
                f.write(f"📐 Effective dimensions (95% var): {analysis['effective_dimensions']}\n")
            f.write("\n")
        
        # STANDARD CLUSTERING RESULTS
        f.write("🎯 DETAILED CLUSTERING RESULTS\n")
        f.write("-"*50 + "\n")
        f.write(f"🏆 Best Method: {info['best_method']}\n")
        f.write(f"📈 Best Silhouette Score: {info['best_silhouette']:.4f}\n")
        f.write(f"📊 Optimal Clusters: {info.get('k', 'N/A')}\n")
        
        if 'ch' in info:
            f.write(f"📊 Calinski-Harabasz Index: {info['ch']:.2f}\n")
        if 'db' in info:
            f.write(f"📉 Davies-Bouldin Index: {info['db']:.4f}\n")
        f.write("\n")
        
        # REPRESENTATIVE POINTS SELECTION
        f.write("⚡ REPRESENTATIVE POINTS SELECTION\n")
        f.write("-"*50 + "\n")
        f.write(f"🎯 Medoids from Best Clusters: {info['n_medoid']}\n")
        f.write(f"📏 MAPGL Belt Snapshots: {info['n_belt']}\n")
        f.write(f"📊 Total Representative Points: {info['n_total']}\n")
        f.write(f"📉 Compression Ratio: {info['original_size']/info['n_total']:.1f}:1\n")
        f.write(f"📈 Retention Rate: {(info['n_total']/info['original_size'])*100:.2f}%\n\n")
        
        # RECOMMENDATIONS
        f.write("💡 ENHANCED RECOMMENDATIONS\n")
        f.write("-"*50 + "\n")
        
        if best_quality < 0.25:
            f.write("❌ CRITICAL: Very poor clustering quality\n")
            f.write("   • Consider alternative data sources\n")
            f.write("   • Review system operating patterns\n")
            f.write("   • Increase data collection period\n\n")
        elif best_quality < 0.5:
            f.write("⚠️ WARNING: Moderate clustering quality\n")
            f.write("   • Validate results carefully\n")
            f.write("   • Consider longer analysis periods\n")
            f.write("   • Review operational diversity\n\n")
        else:
            f.write("✅ SUCCESS: Good clustering quality achieved\n")
            f.write("   • Results suitable for planning studies\n")
            f.write("   • Proceed with power system analysis\n\n")
        
        if info['best_method'] != 'Standard K-means':
            f.write(f"🎉 ENHANCEMENT SUCCESS:\n")
            f.write(f"   • Enhanced method '{info['best_method']}' outperformed standard K-means\n")
            f.write(f"   • Quality improvement achieved through advanced techniques\n")
            f.write(f"   • Recommended for future analyses\n\n")
        
        f.write("="*80 + "\n")
        f.write("END OF ENHANCED CLUSTERING SUMMARY\n")
        f.write("="*80 + "\n")


def extract_representative_ops(
    all_power: pd.DataFrame,
    max_power: float,
    MAPGL: float,
    k_max: int = REPRESENTATIVE_OPS['defaults']['k_max'],
    random_state: int = REPRESENTATIVE_OPS['defaults']['random_state'],
    output_dir: Optional[str] = None,
) -> Tuple[pd.DataFrame, dict]:
    """
    Extract representative operating points from power system data using clustering.

    This function implements the methodology described in "Automated Extraction of 
    Representative Operating Points for a 132 kV Transmission System" with a 
    configuration-driven approach for enhanced maintainability and customization.

    CONFIGURATION-DRIVEN FEATURES:
    ==============================
    - All clustering parameters imported from config.REPRESENTATIVE_OPS
    - Default values managed centrally for consistency across analyses
    - Feature column selection based on config.REPRESENTATIVE_OPS['feature_columns']
    - Output file names standardized via config.REPRESENTATIVE_OPS['output_files']
    - Clean column names in CSV output using config.clean_column_name()

    CLUSTERING WORKFLOW:
    ===================
    1. Data filtering based on power limits and MAPGL constraints
    2. Feature extraction using power injection variables (config-driven prefixes)
    3. Data standardization using StandardScaler
    4. K-means clustering with automatic cluster count selection
    5. Multi-objective quality assessment (silhouette, Calinski-Harabasz, Davies-Bouldin)
    6. Medoid identification (actual snapshots closest to cluster centers)
    7. MAPGL belt analysis for critical low-load operating points
    8. Results saved with clean column names and comprehensive diagnostics

    NET LOAD HANDLING:
    ==================
    - If 'net_load' column exists in input data, it will be used directly
    - If 'net_load' is missing, it will be calculated from power system data
    - This avoids redundant calculations when data already contains computed values

    Parameters
    ----------
    all_power : pandas.DataFrame
        Input time-series DataFrame with power system data including columns:
        - ss_mw_*: Substation active power (MW)
        - ss_mvar_*: Substation reactive power (MVAR) 
        - wind_mw_*: Wind farm active power (MW)
        - net_load: Net load (optional, will be calculated if not present)
        - total_load: Total load (optional, will be calculated if net_load not present)
    max_power : float
        Maximum dispatchable generation for the horizon under study [MW].
    MAPGL : float
        Minimum active-power generation limit [MW].
    k_max : int, optional
        Upper bound for clusters to test. 
        Default from config.REPRESENTATIVE_OPS['defaults']['k_max'].
    random_state : int or None, optional
        Reproducibility parameter for k-means.
        Default from config.REPRESENTATIVE_OPS['defaults']['random_state'].
    output_dir : str or None, optional
        Directory to save results. If provided, saves files with standardized names:
        - representative_operating_points.csv: Clean column names, timestamps as index
        - clustering_summary.txt: Comprehensive clustering analysis report
        - clustering_info.json: Detailed clustering metrics for programmatic access

    Returns
    -------
    rep_df : pandas.DataFrame
        Subset of input DataFrame containing representative operating points
        (medoids from clusters plus MAPGL-belt snapshots). Column names retain
        original structure for compatibility with analysis functions.
    info : dict
        Comprehensive diagnostics including:
        - 'k': Optimal number of clusters selected
        - 'silhouette': Silhouette score for clustering quality
        - 'ch': Calinski-Harabasz index
        - 'db': Davies-Bouldin index  
        - 'cluster_sizes': Number of points in each cluster
        - 'n_medoid': Number of medoid representatives
        - 'n_belt': Number of MAPGL belt snapshots
        - 'n_total': Total representative points
        - 'original_size': Size of input dataset
        - 'filtered_size': Size after filtering
        - 'feature_columns': Columns used for clustering

    Raises
    ------
    ValueError
        If any surviving snapshot violates net_load < MAPGL, or if no suitable
        feature columns are found for clustering.

    Configuration Dependencies
    -------------------------
    This function relies on config.REPRESENTATIVE_OPS for:
    - Default parameter values (k_max, random_state, etc.)
    - Clustering quality thresholds
    - Feature column prefixes for automatic selection
    - Multi-objective ranking weights
    - Output file naming conventions

    Examples
    --------
    >>> from operating_point_extractor import extract_representative_ops
    >>> # Basic usage with config defaults
    >>> rep_df, diag = extract_representative_ops(df, max_power=850, MAPGL=200)
    >>> print(f"Selected {len(rep_df)} representative points from {len(df)} total")
    >>> print(f"Optimal clusters: {diag['k']} (quality: {diag['silhouette']:.3f})")
    
    >>> # Save results with clean column names and comprehensive reports
    >>> rep_df, diag = extract_representative_ops(
    ...     df, max_power=850, MAPGL=200, output_dir="./results"
    ... )
    >>> # Files saved: representative_operating_points.csv (clean names),
    >>> #               clustering_summary.txt, clustering_info.json
    
    >>> # Override config defaults for custom analysis
    >>> rep_df, diag = extract_representative_ops(
    ...     df, max_power=850, MAPGL=200, k_max=15, random_state=123
    ... )
    
    >>> # Access comprehensive diagnostics
    >>> print(f"Compression ratio: {diag['original_size']/diag['n_total']:.1f}:1")
    >>> print(f"Feature columns: {len(diag['feature_columns'])}")
    >>> print(f"Cluster sizes: {diag['cluster_sizes']}")
    """
    
    # Input validation (shared)
    _validate_inputs(all_power, max_power, MAPGL, k_max)
    
    # Data quality checks
    missing_data = all_power.isnull().sum().sum()
    if missing_data > 0:
        print(f"Warning: {missing_data} missing values detected in input data")
    
    # Check for infinite values
    inf_count = np.isinf(all_power.select_dtypes(include=[np.number])).sum().sum()
    if inf_count > 0:
        raise ValueError(f"Input data contains {inf_count} infinite values")
    
    # Create working copy with net_load and apply integrity checks
    working, _ = _ensure_net_load_column(all_power)
    working = _filter_by_limits_and_validate_MAPGL(working, max_power, MAPGL)

    # 2 ───────────────── Feature extraction & scaling
    feat_cols = _select_feature_columns(working)
    if len(feat_cols) == 0:
        raise ValueError("No suitable feature columns found (ss_mw_*, ss_mvar_*, wind_mw_*)")
    
    # Check feature data quality
    feat_cols, zero_var_excluded = _exclude_zero_variance_features(working, feat_cols, error_if_all=True)
    
    x_raw = working[feat_cols].to_numpy(float)
    
    # Check if we have any samples after filtering
    if x_raw.shape[0] == 0:
        raise ValueError(
            "No samples remaining after data filtering. This can occur when:\n"
            "1. All data points violate the power limits or MAPGL constraints\n"
            "2. The filtering criteria are too restrictive for the available data\n"
            "3. The input dataset is empty or contains only invalid data\n\n"
            "Please check your input data and filtering parameters:\n"
            f"- max_power: {max_power} MW\n"
            f"- MAPGL: {MAPGL} MW\n"
            f"- Original dataset size: {len(all_power)} snapshots\n"
            f"- After filtering: {len(working)} snapshots"
        )
    
    scaler = StandardScaler()
    x = scaler.fit_transform(x_raw)

    # 3 ───────────────── K-means with automatic k
    model, metrics = _auto_kmeans(x, k_max=k_max, random_state=random_state)
    labels = model.labels_
    centres = model.cluster_centers_

    # 4 ───────────────── Medoid identification
    medoid_ids = _compute_medoids(x, labels, centres, working.index)

    # 5 ───────────────── Append MAPGL belt snapshots
    belt_ids = _compute_mapgl_belt_ids(working, MAPGL)

    all_ids = sorted(set(medoid_ids).union(belt_ids))
    rep_df = working.loc[all_ids].copy()

    # 6 ───────────────── Return with diagnostics
    info = {
        **metrics,
        "cluster_sizes": np.bincount(labels, minlength=model.n_clusters).tolist(),
        "n_medoid": len(medoid_ids),
        "n_belt": len(belt_ids),
        "n_total": len(rep_df),
        "original_size": len(all_power),
        "filtered_size": len(working),
        "feature_columns": feat_cols,
        "data_quality": {
            "missing_values": missing_data,
            "infinite_values": inf_count,
            "zero_variance_features_excluded": zero_var_excluded
        }
    }

    # 7 ───────────────── Save results
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        # Save representative operating points as CSV (include timestamps in index)
        output_files = REPRESENTATIVE_OPS['output_files']
        filename_rep = os.path.join(output_dir, output_files['representative_points'])
        
        # Create a copy with cleaned column names for better readability
        rep_df_clean = rep_df.copy()
        rep_df_clean.columns = [clean_column_name(col) for col in rep_df_clean.columns]
        # Sort by net_load in descending order for easier inspection
        if 'net_load' in rep_df_clean.columns:
            rep_df_clean = rep_df_clean.sort_values(by='net_load', ascending=False)
        
        rep_df_clean.to_csv(filename_rep, index=True)
        
        # Create comprehensive clustering summary
        summary_filename = os.path.join(output_dir, output_files['clustering_summary'])
        _create_clustering_summary(
            summary_filename, all_power, working, rep_df, info, 
            max_power, MAPGL, k_max, random_state, feat_cols, model, scaler
        )
        
        # Create visualizations
        _create_visualizations(
            output_dir, working, rep_df, info, model, scaler, feat_cols, max_power, MAPGL
        )

        print(f"Results saved to:")
        print(f"  Representative points: {filename_rep}")
        print(f"  Clustering summary: {summary_filename}")

    return rep_df, info 