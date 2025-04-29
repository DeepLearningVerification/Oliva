import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def readCSV(file_path):
    df = pd.read_csv(file_path)
    return df

df1 = pd.read_csv('./ECOOPResults/all_results/all_mnistL2.csv')
df2 = pd.read_csv('./ECOOPResults/all_results/all_mnistL4.csv')
df3 = pd.read_csv('./ECOOPResults/all_results/all_oval21_base.csv')
df4 = pd.read_csv('./ECOOPResults/all_results/all_oval21_deep.csv')
df5 = pd.read_csv('./ECOOPResults/all_results/all_oval21_wide.csv')
combined_df = pd.concat([df1, df2, df3, df4, df5], axis=0)   


def RQ2csv(file_path):
    column_names = ["id","eps",
                    'bab_baseline', 'bab_baseline_time', 'bab_baseline_visit', 'bab_baseline_status',
                    "abcrown","abcrown_status","abcrown_time",
                    "neuralsat","neuralsat_time", "neuralsat_status",
                    'oliva_greedy','oliva_greedy_time', 'oliva_greedy_visit', 'oliva_greedy_status', 'oliva_greedy_lb',
                    'oliva_balance','oliva_balance_time','oliva_balance_visit', 'oliva_balance_status','oliva_balance_lb',
                    ]
    dataframe = pd.read_csv(file_path, sep=",", header=None, names=column_names)
    return dataframe


def plot_ratio_boxplots(df):
    # Create filtered datasets
    adv_df = df[df['oliva_greedy_status'] == "Status.ADV_EXAMPLE"].copy()
    verified_df = df[df['oliva_greedy_status'] == "Status.VERIFIED"].copy()
    
    # Calculate ratios for greedy method
    adv_greedy_ratio = adv_df['bab_baseline_time'] / adv_df['oliva_greedy_time']
    verified_greedy_ratio = verified_df['bab_baseline_time'] / verified_df['oliva_greedy_time']
    
    # Calculate ratios for balance method
    adv_balance_ratio = adv_df['bab_baseline_time'] / adv_df['oliva_balance_time']
    verified_balance_ratio = verified_df['bab_baseline_time'] / verified_df['oliva_balance_time']
    
    # Print summary statistics for each category
    print("\n===== BOXPLOT STATISTICS =====")
    
    print("\n--- Violated Instances (Status.ADV_EXAMPLE) ---")
    print("Oliva^GR:")
    print(f"  Count: {len(adv_greedy_ratio)}")
    print(f"  Mean: {adv_greedy_ratio.mean():.2f}")
    print(f"  Median: {adv_greedy_ratio.median():.2f}")
    print(f"  Min: {adv_greedy_ratio.min():.2f}")
    print(f"  Max: {adv_greedy_ratio.max():.2f}")
    print(f"  25th percentile: {adv_greedy_ratio.quantile(0.25):.2f}")
    print(f"  75th percentile: {adv_greedy_ratio.quantile(0.75):.2f}")
    
    print("\nOliva^SA:")
    print(f"  Count: {len(adv_balance_ratio)}")
    print(f"  Mean: {adv_balance_ratio.mean():.2f}")
    print(f"  Median: {adv_balance_ratio.median():.2f}")
    print(f"  Min: {adv_balance_ratio.min():.2f}")
    print(f"  Max: {adv_balance_ratio.max():.2f}")
    print(f"  25th percentile: {adv_balance_ratio.quantile(0.25):.2f}")
    print(f"  75th percentile: {adv_balance_ratio.quantile(0.75):.2f}")
    
    print("\n--- Certified Instances (Status.VERIFIED) ---")
    print("Oliva^GR:")
    print(f"  Count: {len(verified_greedy_ratio)}")
    print(f"  Mean: {verified_greedy_ratio.mean():.2f}")
    print(f"  Median: {verified_greedy_ratio.median():.2f}")
    print(f"  Min: {verified_greedy_ratio.min():.2f}")
    print(f"  Max: {verified_greedy_ratio.max():.2f}")
    print(f"  25th percentile: {verified_greedy_ratio.quantile(0.25):.2f}")
    print(f"  75th percentile: {verified_greedy_ratio.quantile(0.75):.2f}")
    
    print("\nOliva^SA:")
    print(f"  Count: {len(verified_balance_ratio)}")
    print(f"  Mean: {verified_balance_ratio.mean():.2f}")
    print(f"  Median: {verified_balance_ratio.median():.2f}")
    print(f"  Min: {verified_balance_ratio.min():.2f}")
    print(f"  Max: {verified_balance_ratio.max():.2f}")
    print(f"  25th percentile: {verified_balance_ratio.quantile(0.25):.2f}")
    print(f"  75th percentile: {verified_balance_ratio.quantile(0.75):.2f}")
    
    print("\n--- Speedup Summary ---")
    print("Average speedup for Oliva^GR:")
    print(f"  Violated instances: {adv_greedy_ratio.mean():.2f}x")
    print(f"  Certified instances: {verified_greedy_ratio.mean():.2f}x")
    
    print("\nAverage speedup for Oliva^SA:")
    print(f"  Violated instances: {adv_balance_ratio.mean():.2f}x")
    print(f"  Certified instances: {verified_balance_ratio.mean():.2f}x")
    
    # Return None since we're not creating a plot
    return None


if __name__ == "__main__":
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run RQ2 analysis')
    parser.add_argument('--a', action='store_true', help='Use dataset a (./ECOOPResults/all_results/0.csv)')
    parser.add_argument('--b', action='store_true', help='Use dataset b (./ECOOPResults/all_results/1.csv)')
    parser.add_argument('--c', action='store_true', help='Use dataset c (./ECOOPResults/all_results/2.csv)')
    parser.add_argument('--d', action='store_true', help='Use dataset d (./ECOOPResults/all_results/3.csv)')
    parser.add_argument('--e', action='store_true', help='Use dataset e (./ECOOPResults/all_results/4.csv)')
    parser.add_argument('--file', type=str, help='Custom input CSV file path')
    args = parser.parse_args()
    
    # Determine input file
    if args.a:
        input_file = "./ECOOPResults/all_results/0.csv"
    elif args.b:
        input_file = "./ECOOPResults/all_results/1.csv"
    elif args.c:
        input_file = "./ECOOPResults/all_results/2.csv"
    elif args.d:
        input_file = "./ECOOPResults/all_results/3.csv"
    elif args.e:
        input_file = "./ECOOPResults/all_results/4.csv"
    elif args.file:
        input_file = args.file
    else:
        # Default to dataset a if no option specified
        input_file = "./ECOOPResults/all_results/0.csv"
    
    # Call the main function to run the analysis
    df = RQ2csv(input_file)
    plot = plot_ratio_boxplots(df)


