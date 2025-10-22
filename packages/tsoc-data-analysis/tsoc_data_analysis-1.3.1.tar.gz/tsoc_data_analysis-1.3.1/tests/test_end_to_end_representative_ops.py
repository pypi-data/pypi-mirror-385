
from tsoc_data_analysis import execute, extract_representative_ops, REPRESENTATIVE_OPS
import os
import shutil
from pathlib import Path
import pandas as pd

results_folder = 'results'

# Clean and prepare results folder
if os.path.exists(results_folder):
    shutil.rmtree(results_folder)

# Execute full data analysis
success, all_data_df = execute(
    month='2024-07',
    data_dir='../raw_data',
    output_dir=results_folder,
    save_plots=True,
    save_csv=True,
    verbose=True
)

if success:
    print("Data analysis successful. Proceeding to representative points extraction...")
else:
    print("Data analysis failed. Exiting...")
    exit(1)

REPRESENTATIVE_OPS['defaults']['mapgl_belt_multiplier'] = 1.00
REPRESENTATIVE_OPS['defaults']['k_max'] = 10

sum_pmin_on = 210.0
sum_pmax_on = 430.00

rep_df, diagnostics = extract_representative_ops(
        all_data_df,
        max_power=sum_pmax_on,  # uses your existing variable
        MAPGL=sum_pmin_on,     # uses your existing variable
        output_dir=results_folder 
    )

print("\n" + "="*100)
print("\nAnalysis Summary:")
print(f"  Total records: {len(all_data_df)}")
print(f"Representative points extracted: {len(rep_df)} points")
print(f"  Clustering quality: {diagnostics['silhouette']:.3f}")
print("\n" + "="*100)