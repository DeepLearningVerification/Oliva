import pandas as pd 
import warnings


df1 = pd.read_csv("./ECOOPResults/all_results/mnistL2_sensi_existconclusive.csv")
df2 = pd.read_csv("./ECOOPResults/all_results/mnistL4_sensi_existconclusive.csv")
df3 = pd.read_csv("./ECOOPResults/all_results/ovalbase_sensi_existconclusive.csv")
df4 = pd.read_csv("./ECOOPResults/all_results/ovaldeep_sensi_existconclusive.csv")
df5 = pd.read_csv("./ECOOPResults/all_results/ovalwide_sensi_existconclusive.csv")


dfs = [df1]  # First dataframe with header
# Add other dataframes without headers
for df in [df2, df3, df4, df5]:
    dfs.append(df.iloc[:])  # Get all rows without header

# Combine all
combined_df = pd.concat(dfs, ignore_index=True)




import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Assuming any_known_df is already defined
methods = ['sa0', 'sa1', 'sa2', 'sa3', 'sa4', 'sa5']
method_names = ['sa0', 'sa1', 'sa2', 'sa3', 'sa4', 'sa5']

# Calculate ratios
scatter = combined_df[["id", "eps", "dfs_time"] + [f"{method}_time" for method in methods]]
for method in methods:
    scatter[f'ratio_{method}'] = scatter['dfs_time'] / scatter[f'{method}_time']

# Create a list to store data for each method
plot_data = []

for method in methods:
    df = pd.DataFrame({
        'Time': scatter[f'{method}_time'],
        'Ratio': scatter[f'ratio_{method}'],
        'Method': method_names[methods.index(method)]
    })
    plot_data.append(df)

# Combine all data
plot_data = pd.concat(plot_data, ignore_index=True)

# Filter out data points above 1000s
plot_data = plot_data[plot_data['Time'] <= 1000]

# Define ratio labels with interpretations
ratio_labels = ['0-0.5', '0.5-1', '1-2', '2-5', '5-10']
ratio_interpretations = {
    '0-0.5': 'Slower',
    '0.5-1': 'Slower',
    '1-2': 'Faster',
    '2-5': 'Faster',
    '5-10': 'Much Faster'
}

# Define 6 time bins
time_bins = [0, 100, 200, 400, 600, 800, 1000]
time_labels = ['0-100s', '100-200s', '200-400s', '400-600s', '600-800s', '800-1000s']
plot_data['Time_bin'] = pd.cut(plot_data['Time'], bins=time_bins, labels=time_labels, include_lowest=True, right=False)

# Create a function to bin ratios
def bin_ratios(ratios, labels):
    bins = [0, 0.5, 1, 2, 5, 10]
    return pd.cut(ratios, bins=bins, labels=labels, include_lowest=True, right=False)

# Find the global maximum count for reference
global_max = 0
for method in method_names:
    method_data = plot_data[plot_data['Method'] == method]
    heatmap_data = pd.DataFrame(index=ratio_labels, columns=time_labels)
    
    for time_bin in time_labels:
        time_data = method_data[method_data['Time_bin'] == time_bin]
        binned_ratios = bin_ratios(time_data['Ratio'], ratio_labels)
        counts = binned_ratios.value_counts().reindex(ratio_labels).fillna(0)
        heatmap_data[time_bin] = counts
    
    current_max = heatmap_data.max().max()
    if current_max > global_max:
        global_max = current_max

print("\n===== HEATMAP DATA FOR EACH METHOD =====")
print(f"Global maximum count across all heatmaps: {global_max}\n")

# Print heatmap data for each method
for method, method_name in zip(methods, method_names):
    print(f"\n{'=' * 50}")
    print(f"Method: {method_name}")
    print(f"{'=' * 50}")
    
    # Create a pivot table for the heatmap
    method_data = plot_data[plot_data['Method'] == method_name]
    heatmap_data = pd.DataFrame(index=ratio_labels, columns=time_labels)
    
    for time_bin in time_labels:
        time_data = method_data[method_data['Time_bin'] == time_bin]
        binned_ratios = bin_ratios(time_data['Ratio'], ratio_labels)
        counts = binned_ratios.value_counts().reindex(ratio_labels).fillna(0)
        heatmap_data[time_bin] = counts
    
    # Print the heatmap data with interpretations
    print("\nHeatmap Data (Values represent count of instances in each bin):")
    print("Performance Categories:")
    for label, interp in ratio_interpretations.items():
        print(f"  {label}: {interp}")
    print("\n" + "-" * 80)
    
    # Calculate the relative intensity for each cell (comparable to color intensity in heatmap)
    relative_intensities = heatmap_data / global_max
    
    # Print the heatmap with formatted output to mimic visual representation
    print("\nHeatmap Representation (count / intensity):")
    for ratio in ratio_labels:
        row_values = []
        for time in time_labels:
            value = heatmap_data.loc[ratio, time]
            intensity = relative_intensities.loc[ratio, time]
            intensity_str = "" * int(intensity * 1) if intensity > 0 else ""
            row_values.append(f"{int(value):3d} {intensity_str}")
        row_str = " | ".join(row_values)
        print(f"{ratio:5s} | {row_str}")
        
        # Add separator line after the specific category
        if ratio == '1-2':
            print("-" * 80)
    
    # Print row sums
    print("\nRow sums (by ratio category):")
    row_sums = heatmap_data.sum(axis=1).astype(int)
    for label, sum_val in zip(ratio_labels, row_sums):
        interp = ratio_interpretations[label]
        print(f"  {label} ({interp}): {sum_val}")
    
    # Group by performance categories
    slower_count = row_sums.iloc[0] + row_sums.iloc[1]  # 0-0.5 and 0.5-1
    faster_count = row_sums.iloc[2] + row_sums.iloc[3]  # 1-2 and 2-5
    much_faster_count = row_sums.iloc[4]  # 5-10
    total = heatmap_data.sum().sum()
    
    print("\nPerformance Summary:")
    print(f"  Slower:      {slower_count:4d} ({slower_count/total*100:.1f}%)")
    print(f"  Faster:      {faster_count:4d} ({faster_count/total*100:.1f}%)")
    print(f"  Much Faster: {much_faster_count:4d} ({much_faster_count/total*100:.1f}%)")
    
    # Print column sums
    print("\nColumn sums (by time bin):")
    col_sums = heatmap_data.sum(axis=0).astype(int)
    for label, sum_val in zip(time_labels, col_sums):
        print(f"  {label}: {sum_val}")
    
    # Print total count
    total = heatmap_data.sum().sum().astype(int)
    print(f"\nTotal count: {total}")

# Print summary statistics
print("\n\n===== SUMMARY STATISTICS =====")
for method, method_name in zip(methods, method_names):
    method_data = plot_data[plot_data['Method'] == method_name]
    print(f"\n--- {method_name} ---")
    print(f"Count: {len(method_data)}")
    print(f"Mean ratio: {method_data['Ratio'].mean():.2f}")
    print(f"Median ratio: {method_data['Ratio'].median():.2f}")
    print(f"Min ratio: {method_data['Ratio'].min():.2f}")
    print(f"Max ratio: {method_data['Ratio'].max():.2f}")
    print(f"25th percentile: {method_data['Ratio'].quantile(0.25):.2f}")
    print(f"75th percentile: {method_data['Ratio'].quantile(0.75):.2f}")
    
    # Add interpretation of the statistics
    mean_ratio = method_data['Ratio'].mean()
    if mean_ratio < 1:
        performance = "slower"
    elif mean_ratio < 2:
        performance = "slightly faster"
    elif mean_ratio < 5:
        performance = "significantly faster"
    else:
        performance = "much faster"
    
    print(f"Performance interpretation: {method_name} is {performance} than GR on average")