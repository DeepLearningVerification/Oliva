import pandas as pd
def readCSVhyper(file_path):
    column_names = ['index', 'eps', 
                    'base_type', 'base_time', 'base_visit', 'base_status', 
                    'oliva_type', 'oliva_time', 'oliva_visit', 'oliva_status', 
                    'g0_type', 'g0_time', 'g0_visit', 'g0_status', 
                    'g1_type', 'g1_time', 'g1_visit', 'g1_status', 
                    'g2_type', 'g2_time', 'g2_visit', 'g2_status', 
                    'g3_type', 'g3_time', 'g3_visit', 'g3_status', 
                    'g4_type', 'g4_time', 'g4_visit', 'g4_status', 
                    'g5_type', 'g5_time', 'g5_visit', 'g5_status']
    dataframe = pd.read_csv(file_path, sep=",", header=None, names=column_names)
    return dataframe


def lamda_show():
    df = readCSVhyper("ECOOPResults/all_results/hyper_lambda.csv")

    dfp = df[ (df.oliva_status != "Status.UNKNOWN") | (df.g0_status != "Status.UNKNOWN") | (df.g1_status != "Status.UNKNOWN") | (df.g1_status != "Status.UNKNOWN") | (df.g2_status != "Status.UNKNOWN") | (df.g3_status != "Status.UNKNOWN") | (df.g4_status != "Status.UNKNOWN") | (df.g5_status != "Status.UNKNOWN")].copy()

    ratios_df = pd.DataFrame()
    ratios_df['λ=0'] = dfp['base_time'] / dfp['g0_time']
    ratios_df['λ=0.2'] = dfp['base_time'] / dfp['g1_time']
    ratios_df['λ=0.4'] = dfp['base_time'] / dfp['g2_time']
    ratios_df['λ=0.5\n(Default)'] = dfp['base_time'] / dfp['oliva_time']
    ratios_df['λ=0.6'] = dfp['base_time'] / dfp['g3_time']
    ratios_df['λ=0.8'] = dfp['base_time'] / dfp['g4_time']
    ratios_df['λ=1'] = dfp['base_time'] / dfp['g5_time']

    # Print statistics for each lambda value
    print("\n===== LAMBDA PARAMETER ANALYSIS =====")
    
    for column in ratios_df.columns:
        print(f"\n--- {column} ---")
        print(f"  Count: {len(ratios_df[column].dropna())}")
        print(f"  Mean: {ratios_df[column].mean():.2f}")
        print(f"  Median: {ratios_df[column].median():.2f}")
        print(f"  Min: {ratios_df[column].min():.2f}")
        print(f"  Max: {ratios_df[column].max():.2f}")
        print(f"  25th percentile: {ratios_df[column].quantile(0.25):.2f}")
        print(f"  75th percentile: {ratios_df[column].quantile(0.75):.2f}")
    
    print("\n--- Summary of Mean Speedups ---")
    for column in ratios_df.columns:
        print(f"  {column}: {ratios_df[column].mean():.2f}x")
    
    print("\n--- Box Plot Details ---")
    print("  X-axis: Speedup ratio (Base/Lambda variant)")
    print("  Y-axis: Lambda values from 0 to 1")
    print("  Red dashed line at ratio=1 (equal performance)")
    print("  Black dots represent mean values")
    print("  Box shows 25th to 75th percentile")
    print("  Whiskers extend to min/max values (excluding outliers)")
    

def readCSVhypersa(file_path):
    column_names = ['id', 'eps',
                    'dfs_type', 'dfs_time', 'dfs_visit', 'dfs_status',
                    'sa0_type', 'sa0_time', 'sa0_visit', 'sa0_status', 'sa0_status_lb',
                    'sa1_type', 'sa1_time', 'sa1_visit', 'sa1_status', 'sa1_status_lb',
                    'sa2_type', 'sa2_time', 'sa2_visit', 'sa2_status', 'sa2_status_lb',
                    'sa3_type', 'sa3_time', 'sa3_visit', 'sa3_status', 'sa3_status_lb',
                    'sa4_type', 'sa4_time', 'sa4_visit', 'sa4_status', 'sa4_status_lb',
                    'sa5_type', 'sa5_time', 'sa5_visit', 'sa5_status','sa5_status_lb']
    dataframe = pd.read_csv(file_path, sep=",", names=column_names)
    return dataframe


def sa_show():
    
    df = readCSVhypersa("ECOOPResults/all_results/Result_Sensitive_01_alpha.csv")

    dfp = df[ (df.dfs_status != "Status.UNKNOWN") | (df.sa0_status != "Status.UNKNOWN") | (df.sa1_status != "Status.UNKNOWN") | (df.sa2_status != "Status.UNKNOWN") | (df.sa3_status != "Status.UNKNOWN") | (df.sa4_status != "Status.UNKNOWN")  | (df.sa5_status != "Status.UNKNOWN")].copy()
    
    
    ratios_df = pd.DataFrame()
    ratios_df["id"] = dfp['id']
    ratios_df["eps"] = dfp['eps']
    ratios_df['α=0.95'] = dfp['dfs_time'] / dfp['sa0_time']
    ratios_df['α=0.96'] = dfp['dfs_time'] / dfp['sa1_time']
    ratios_df['α=0.97'] = dfp['dfs_time'] / dfp['sa2_time']
    ratios_df['α=0.98'] = dfp['dfs_time'] / dfp['sa3_time']
    ratios_df['α=0.99'] = dfp['dfs_time'] / dfp['sa4_time']
    ratios_df['α=0.999'] = dfp['dfs_time'] / dfp['sa5_time']
    
    # Print statistics for each alpha value
    print("\n===== ALPHA PARAMETER ANALYSIS =====")
    
    # Skip the first two columns (id and eps)
    for column in ratios_df.columns[2:]:
        print(f"\n--- {column} ---")
        print(f"  Count: {len(ratios_df[column].dropna())}")
        print(f"  Mean: {ratios_df[column].mean():.2f}")
        print(f"  Median: {ratios_df[column].median():.2f}")
        print(f"  Min: {ratios_df[column].min():.2f}")
        print(f"  Max: {ratios_df[column].max():.2f}")
        print(f"  25th percentile: {ratios_df[column].quantile(0.25):.2f}")
        print(f"  75th percentile: {ratios_df[column].quantile(0.75):.2f}")
    
    print("\n--- Summary of Mean Speedups ---")
    for column in ratios_df.columns[2:]:
        print(f"  {column}: {ratios_df[column].mean():.2f}x")
    
    # Calculate quartiles and IQR for outlier information
    print("\n--- Outlier Information ---")
    for column in ratios_df.columns[2:]:
        data = ratios_df[column]
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr
        outliers = data[data > upper_bound]
        
        print(f"\n  {column}:")
        print(f"    Number of outliers: {len(outliers)}")
        if len(outliers) > 0:
            print(f"    Outlier values: {', '.join([f'{x:.2f}' for x in outliers.values[:5]])}" + 
                  (f" (and {len(outliers) - 5} more)" if len(outliers) > 5 else ""))







 
if __name__ == "__main__":
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run RQ3 analysis')
    parser.add_argument('--lambda', '--alpha', dest='lambda_param', action='store_true', 
                        help='Run lambda parameter analysis')
    args = parser.parse_args()
    
    # Run the lambda analysis if specified
    if args.lambda_param:
        lamda_show()
    elif args.sa_param:
        sa_show()
    else:
        print("Please specify an analysis to run. Use --lambda or --alpha to run the lambda parameter analysis.")
