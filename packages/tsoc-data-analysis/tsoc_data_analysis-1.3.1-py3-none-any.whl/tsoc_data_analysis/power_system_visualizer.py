"""
Plotting Module for Power System Data Visualization

Author: Sustainable Power Systems Lab (SPSL)
Web: https://sps-lab.org
Contact: info@sps-lab.org

This module provides functions for creating various plots and visualizations of power system
operational data, including load time series, daily profiles, monthly profiles, and comprehensive
analysis plots.

The module creates publication-quality plots with consistent styling and formatting,
suitable for reports and presentations.

Functions:
- plot_load_timeseries(): Create time series plots of total and net load
- plot_total_load_daily_profile(): Generate daily profile for total load
- plot_net_load_daily_profile(): Generate daily profile for net load
- plot_monthly_profile(): Create monthly load profile comparisons
- create_comprehensive_plots(): Generate a comprehensive multi-panel analysis plot

Plot Features:
- Consistent styling with seaborn theme
- Professional color schemes
- Clear labels and legends
- Grid lines for readability
- Optimized figure sizes for different use cases
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from .system_configuration import PLOT_STYLE, PLOT_PALETTE, FIGURE_SIZES, FONT_SIZES

# Set style for better-looking plots
plt.style.use(PLOT_STYLE)
sns.set_palette(PLOT_PALETTE)

# Task 4.1: Function to plot load time series
def plot_load_timeseries(total_load, net_load, ax=None, figsize=FIGURE_SIZES['timeseries']):
    """
    Generate a time series plot of total load and net load.
    
    Args:
        total_load (pandas.Series): Time series of total load values
        net_load (pandas.Series): Time series of net load values
        ax (matplotlib.axes.Axes, optional): Matplotlib axes object for plotting
        figsize (tuple, optional): Figure size (width, height)
        
    Returns:
        matplotlib.axes.Axes: The axes object with the plot
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Plot total load and net load
    ax.plot(total_load.index, total_load.values, label='Total Load', linewidth=1.5, alpha=0.8)
    ax.plot(net_load.index, net_load.values, label='Net Load', linewidth=1.5, alpha=0.8)
    
    # Customize the plot
    ax.set_title('Load Time Series', fontsize=FONT_SIZES['title'], fontweight='bold')
    ax.set_xlabel('Time', fontsize=FONT_SIZES['axis_label'])
    ax.set_ylabel('Load (MW)', fontsize=FONT_SIZES['axis_label'])
    ax.legend(fontsize=FONT_SIZES['legend'])
    ax.grid(True, alpha=0.3)
    
    # Rotate x-axis labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    return ax



def plot_total_load_daily_profile(total_load, ax=None, figsize=FIGURE_SIZES['daily_profile']):
    """
    Plot the daily profile for total load showing average, minimum, and maximum values.
    
    Args:
        total_load (pandas.Series): Time series of total load values
        ax (matplotlib.axes.Axes, optional): Matplotlib axes object for plotting
        figsize (tuple, optional): Figure size (width, height)
        
    Returns:
        matplotlib.axes.Axes: The axes object with the plot
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate daily statistics for total load
    daily_avg = total_load.groupby(total_load.index.time).mean()
    daily_min = total_load.groupby(total_load.index.time).min()
    daily_max = total_load.groupby(total_load.index.time).max()
    
    # Helper function to convert to hourly data
    def convert_to_hourly(daily_data):
        hourly_data = {}
        for time, value in daily_data.items():
            hour = time.hour
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(value)
        
        hourly_values = []
        for hour in range(24):
            if hour in hourly_data:
                hourly_values.append(np.mean(hourly_data[hour]))
            else:
                hourly_values.append(0)
        return hourly_values
    
    # Convert to hourly data
    hourly_avg = convert_to_hourly(daily_avg)
    hourly_min = convert_to_hourly(daily_min)
    hourly_max = convert_to_hourly(daily_max)
    
    # Create time labels for x-axis (24-hour format)
    time_labels = [f"{hour:02d}:00" for hour in range(24)]
    
    # Plot daily profile with all statistics
    ax.plot(range(24), hourly_avg, label='Avg Total Load', linewidth=2, marker='o', markersize=4)
    ax.plot(range(24), hourly_min, label='Min Total Load', linewidth=2, marker='v', markersize=4, linestyle='--')
    ax.plot(range(24), hourly_max, label='Max Total Load', linewidth=2, marker='^', markersize=4, linestyle='--')
    
    # Customize the plot
    ax.set_title('Total Load Daily Profile', fontsize=FONT_SIZES['title'], fontweight='bold')
    ax.set_xlabel('Hour of Day', fontsize=FONT_SIZES['axis_label'])
    ax.set_ylabel('Load (MW)', fontsize=FONT_SIZES['axis_label'])
    ax.legend(fontsize=FONT_SIZES['legend'])
    ax.grid(True, alpha=0.3)
    
    # Set x-axis ticks and labels
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([time_labels[i] for i in range(0, 24, 2)])
    
    # Adjust layout
    plt.tight_layout()
    
    return ax

def plot_net_load_daily_profile(net_load, ax=None, figsize=FIGURE_SIZES['daily_profile']):
    """
    Plot the daily profile for net load showing average, minimum, and maximum values.
    
    Args:
        net_load (pandas.Series): Time series of net load values
        ax (matplotlib.axes.Axes, optional): Matplotlib axes object for plotting
        figsize (tuple, optional): Figure size (width, height)
        
    Returns:
        matplotlib.axes.Axes: The axes object with the plot
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate daily statistics for net load
    daily_avg = net_load.groupby(net_load.index.time).mean()
    daily_min = net_load.groupby(net_load.index.time).min()
    daily_max = net_load.groupby(net_load.index.time).max()
    
    # Helper function to convert to hourly data
    def convert_to_hourly(daily_data):
        hourly_data = {}
        for time, value in daily_data.items():
            hour = time.hour
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(value)
        
        hourly_values = []
        for hour in range(24):
            if hour in hourly_data:
                hourly_values.append(np.mean(hourly_data[hour]))
            else:
                hourly_values.append(0)
        return hourly_values
    
    # Convert to hourly data
    hourly_avg = convert_to_hourly(daily_avg)
    hourly_min = convert_to_hourly(daily_min)
    hourly_max = convert_to_hourly(daily_max)
    
    # Create time labels for x-axis (24-hour format)
    time_labels = [f"{hour:02d}:00" for hour in range(24)]
    
    # Plot daily profile with all statistics
    ax.plot(range(24), hourly_avg, label='Avg Net Load', linewidth=2, marker='s', markersize=4)
    ax.plot(range(24), hourly_min, label='Min Net Load', linewidth=2, marker='v', markersize=4, linestyle='--')
    ax.plot(range(24), hourly_max, label='Max Net Load', linewidth=2, marker='^', markersize=4, linestyle='--')
    
    # Customize the plot
    ax.set_title('Net Load Daily Profile', fontsize=FONT_SIZES['title'], fontweight='bold')
    ax.set_xlabel('Hour of Day', fontsize=FONT_SIZES['axis_label'])
    ax.set_ylabel('Load (MW)', fontsize=FONT_SIZES['axis_label'])
    ax.legend(fontsize=FONT_SIZES['legend'])
    ax.grid(True, alpha=0.3)
    
    # Set x-axis ticks and labels
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([time_labels[i] for i in range(0, 24, 2)])
    
    # Adjust layout
    plt.tight_layout()
    
    return ax

# Task 4.3: Function to plot monthly load profile
def plot_monthly_profile(total_load, net_load=None, ax=None, figsize=FIGURE_SIZES['monthly_profile']):
    """
    Calculate and plot the average load profile across months.
    
    Args:
        total_load (pandas.Series): Time series of total load values
        net_load (pandas.Series, optional): Time series of net load values
        ax (matplotlib.axes.Axes, optional): Matplotlib axes object for plotting
        figsize (tuple, optional): Figure size (width, height)
        
    Returns:
        matplotlib.axes.Axes: The axes object with the plot
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate monthly average for total load
    monthly_total = total_load.groupby(total_load.index.month).mean()
    
    # Month names for x-axis labels
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Check if we have data for all months or just some months
    available_months = monthly_total.index.tolist()
    
    # Plot monthly profile for total load
    # Use only available months for x-axis
    x_values = available_months
    y_values = monthly_total.values
    
    ax.plot(x_values, y_values, label='Total Load', linewidth=2, marker='o', markersize=6)
    
    # Calculate and plot monthly average for net load if provided
    if net_load is not None:
        monthly_net = net_load.groupby(net_load.index.month).mean()
        
        # Use same x-axis as total load
        ax.plot(x_values, monthly_net.values, label='Net Load', linewidth=2, marker='s', markersize=6)
    
    # Customize the plot
    ax.set_title('Average Monthly Load Profile', fontsize=FONT_SIZES['title'], fontweight='bold')
    ax.set_xlabel('Month', fontsize=FONT_SIZES['axis_label'])
    ax.set_ylabel('Average Load (MW)', fontsize=FONT_SIZES['axis_label'])
    ax.legend(fontsize=FONT_SIZES['legend'])
    ax.grid(True, alpha=0.3)
    
    # Set x-axis ticks and labels based on available months
    ax.set_xticks(x_values)
    ax.set_xticklabels([month_names[i-1] for i in x_values])
    
    # Adjust layout
    plt.tight_layout()
    
    return ax 

# Task 4.4: Summary function to demonstrate plotting flexibility
def create_comprehensive_plots(total_load, net_load, figsize=FIGURE_SIZES['comprehensive']):
    """
    Create a comprehensive set of plots demonstrating the flexibility of the plotting functions.
    This function shows how all plotting functions accept Matplotlib axes objects and include
    clear titles, labels, and legends.
    
    Args:
        total_load (pandas.Series): Time series of total load values
        net_load (pandas.Series): Time series of net load values
        figsize (tuple, optional): Figure size (width, height)
        
    Returns:
        matplotlib.figure.Figure: The figure containing all plots
    """
    # Create a figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # Plot 1: Time series (top left)
    plot_load_timeseries(total_load, net_load, ax=axes[0, 0])
    
    # Plot 2: Total Load Daily Profile (top right)
    plot_total_load_daily_profile(total_load, ax=axes[0, 1])
    
    # Plot 3: Monthly profile (bottom left)
    plot_monthly_profile(total_load, net_load, ax=axes[1, 0])
    
    # Plot 4: Statistics summary (bottom right)
    stats = {
        'Max Load': total_load.max(),
        'Min Load': total_load.min(),
        'Mean Load': total_load.mean(),
        'Max Net Load': net_load.max(),
        'Min Net Load': net_load.min(),
        'Mean Net Load': net_load.mean()
    }
    
    # Create a bar plot of statistics
    axes[1, 1].bar(range(len(stats)), list(stats.values()))
    axes[1, 1].set_title('Load Statistics Summary', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Statistics', fontsize=12)
    axes[1, 1].set_ylabel('Load (MW)', fontsize=12)
    axes[1, 1].set_xticks(range(len(stats)))
    axes[1, 1].set_xticklabels(list(stats.keys()), rotation=45, ha='right')
    axes[1, 1].grid(True, alpha=0.3)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig 