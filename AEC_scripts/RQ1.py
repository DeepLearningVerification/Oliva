from calendar import day_name
import pandas as pd 
import warnings
warnings.filterwarnings('ignore')



def solved(df):
    
    return df[df.bab_baseline_status!= 'Status.UNKNOWN'].shape[0], df[df.abcrown_status!= 'Status.UNKNOWN'].shape[0], df[df.neuralsat_status!= 'Status.UNKNOWN'].shape[0], df[df.oliva_greedy_status!= 'Status.UNKNOWN'].shape[0], df[df.oliva_balance_status!= 'Status.UNKNOWN'].shape[0]

def timeAverage(df):
    df = df[(df.oliva_greedy_status!= 'Status.UNKNOWN')|(df.oliva_balance_status!= 'Status.UNKNOWN')|(df.abcrown_status!= 'Status.UNKNOWN')|(df.neuralsat_status!= 'Status.UNKNOWN')]
    return (
        round(df.bab_baseline_time.mean(), 2),
        round(df.abcrown_time.mean(), 2),
        round(df.neuralsat_time.mean(), 2),
        round(df.oliva_greedy_time.mean(), 2),
        round(df.oliva_balance_time.mean(), 2)
    )
    
def print_lines(columName, all_data):
    a, b, c, d , e = solved(all_data)
    at, bt, ct, dt, et = timeAverage(all_data)
    print(f'{columName} &{a}&{at} &{b}&{bt} &{c}&{ct} &{d}&{dt} &{e}&{et}  \\\\')
    
    
def getTable2():
    all_data1 = pd.read_csv('./ECOOPResults/all_results/all_mnistL2.csv')
    print_lines( '$\mnist_{{{\ltwo}}}$ ', all_data1)
    
    all_data2 = pd.read_csv('./ECOOPResults/all_results/all_mnistL4.csv')
    print_lines( '$\mnist_{{{\lfour}}}$ ', all_data2)
    
    all_data3 = pd.read_csv('./ECOOPResults/all_results/all_oval21_base.csv')
    print_lines( '$\OVAL_{{\\base}}$', all_data3)
    
    all_data4 = pd.read_csv('./ECOOPResults/all_results/all_oval21_deep.csv')
    print_lines( '$\OVAL_{{\\deep}}$', all_data4)
    
    all_data5 = pd.read_csv('./ECOOPResults/all_results/all_oval21_wide.csv')
    print_lines( '$\OVAL_{{\wide}}$', all_data5)
    

def getTable3():
    df1 = pd.read_csv('./ECOOPResults/all_results/all_mnistL2.csv')
    df2 = pd.read_csv('./ECOOPResults/all_results/all_mnistL4.csv')
    df3 = pd.read_csv('./ECOOPResults/all_results/all_oval21_base.csv')
    df4 = pd.read_csv('./ECOOPResults/all_results/all_oval21_deep.csv')
    df5 = pd.read_csv('./ECOOPResults/all_results/all_oval21_wide.csv')
    combined_df = pd.concat([df1, df2, df3, df4, df5], axis=0)
    
    a1 = combined_df[(combined_df.bab_baseline_status!= 'Status.UNKNOWN')&(combined_df.abcrown_status== 'Status.UNKNOWN')].shape[0]
    a2 = combined_df[(combined_df.bab_baseline_status!= 'Status.UNKNOWN')&(combined_df.neuralsat_status== 'Status.UNKNOWN')].shape[0]
    a3 = combined_df[(combined_df.bab_baseline_status!= 'Status.UNKNOWN')&(combined_df.oliva_greedy_status== 'Status.UNKNOWN')].shape[0]
    a4 = combined_df[(combined_df.bab_baseline_status!= 'Status.UNKNOWN')&(combined_df.oliva_balance_status== 'Status.UNKNOWN')].shape[0]

    b1 = combined_df[(combined_df.abcrown_status!= 'Status.UNKNOWN') & (combined_df.bab_baseline_status== 'Status.UNKNOWN')].shape[0]
    b2 = combined_df[(combined_df.abcrown_status!= 'Status.UNKNOWN')&(combined_df.neuralsat_status== 'Status.UNKNOWN')].shape[0]
    b3 = combined_df[(combined_df.abcrown_status!= 'Status.UNKNOWN')&(combined_df.oliva_greedy_status== 'Status.UNKNOWN')].shape[0]
    b4 = combined_df[(combined_df.abcrown_status!= 'Status.UNKNOWN')&(combined_df.oliva_balance_status== 'Status.UNKNOWN')].shape[0]

    c1 = combined_df[(combined_df.neuralsat_status!= 'Status.UNKNOWN') & (combined_df.bab_baseline_status== 'Status.UNKNOWN')].shape[0]
    c2 = combined_df[(combined_df.neuralsat_status!= 'Status.UNKNOWN')&(combined_df.abcrown_status== 'Status.UNKNOWN')].shape[0]
    c3 = combined_df[(combined_df.neuralsat_status!= 'Status.UNKNOWN')&(combined_df.oliva_greedy_status== 'Status.UNKNOWN')].shape[0]
    c4 = combined_df[(combined_df.neuralsat_status!= 'Status.UNKNOWN')&(combined_df.oliva_balance_status== 'Status.UNKNOWN')].shape[0]

    d1 = combined_df[(combined_df.oliva_greedy_status!= 'Status.UNKNOWN') & (combined_df.bab_baseline_status== 'Status.UNKNOWN')].shape[0]
    d2 = combined_df[(combined_df.oliva_greedy_status!= 'Status.UNKNOWN')&(combined_df.abcrown_status == 'Status.UNKNOWN')].shape[0]
    d3 = combined_df[(combined_df.oliva_greedy_status!= 'Status.UNKNOWN')&(combined_df.neuralsat_status== 'Status.UNKNOWN')].shape[0]
    d4 = combined_df[(combined_df.oliva_greedy_status!= 'Status.UNKNOWN')&(combined_df.oliva_balance_status== 'Status.UNKNOWN')].shape[0]

    e1 = combined_df[(combined_df.oliva_balance_status!= 'Status.UNKNOWN') & (combined_df.bab_baseline_status== 'Status.UNKNOWN')].shape[0]
    e2 = combined_df[(combined_df.oliva_balance_status!= 'Status.UNKNOWN')&(combined_df.abcrown_status == 'Status.UNKNOWN')].shape[0]
    e3 = combined_df[(combined_df.oliva_balance_status!= 'Status.UNKNOWN')&(combined_df.neuralsat_status== 'Status.UNKNOWN')].shape[0]
    e4 = combined_df[(combined_df.oliva_balance_status!= 'Status.UNKNOWN')&(combined_df.oliva_greedy_status== 'Status.UNKNOWN')].shape[0]
    
    print(f"\\bab-Baseline  & 0 & {a1} &{a2} &{a3}& {a4}\\\\ \\hline")
    print(f"\\abcrown & {b1} & 0 & {b2} &{b3}& {b4}\\\\ \\hline")
    print(f"\\neuralsat & {c1} &{c2} & 0  &{c3}& {c4}\\\\\\hline")
    print(f"\\toolg & {d1} &{d2} &{d3}& 0 &  {d4}\\\\\\hline")
    print(f"\\toolb & {e1} &{e2} &{e3}& {e4} & 0  \\\\\\hline")


    
def calculate_ratio_statistics(df, data_name):
    tools = {
        'Oliva$^{GR}$': ('oliva_greedy_time', 'oliva_greedy_status'),
        'Oliva$^{SA}$': ('oliva_balance_time', 'oliva_balance_status')
    }
    
    stats_data = {}  # Dictionary to store statistics for each method
    
    for tool_name, (time_col, status_col) in tools.items():
        # Filter out UNKNOWN status cases for each method
        valid_cases = df[status_col] != "Status.UNKNOWN"
        filtered_df = df[valid_cases]
       
        ratio = filtered_df['bab_baseline_time'] / filtered_df[time_col]
        mask = ratio <= 150
        filtered_ratio = ratio[mask]
        
        # Calculate statistics
        stats_data[tool_name] = {
            'min': filtered_ratio.min(),
            'max': filtered_ratio.max(),
            'median': filtered_ratio.median(),
            'mean': filtered_ratio.mean()
        }
    
    # Print statisticsxx
    print(f"\nStatistics for {data_name}:")
    for tool_name, stats in stats_data.items():
        print(f"\n{tool_name}:")
        print(f"Min: {stats['min']:.2f}")
        print(f"Max: {stats['max']:.2f}")
        print(f"Median: {stats['median']:.2f}")
        print(f"Mean: {stats['mean']:.2f}")
    
    

def getTable4():
    df1 = pd.read_csv('./ECOOPResults/all_results/all_mnistL2.csv')
    df2 = pd.read_csv('./ECOOPResults/all_results/all_mnistL4.csv')
    df3 = pd.read_csv('./ECOOPResults/all_results/all_oval21_base.csv')
    df4 = pd.read_csv('./ECOOPResults/all_results/all_oval21_deep.csv')
    df5 = pd.read_csv('./ECOOPResults/all_results/all_oval21_wide.csv')
    combined_df = pd.concat([df1, df2, df3, df4, df5], axis=0)
    calculate_ratio_statistics(combined_df, "overall")
    calculate_ratio_statistics(df1, "mnistL2")
    calculate_ratio_statistics(df2, "mnistL4")
    calculate_ratio_statistics(df3, "oval21_base")
    calculate_ratio_statistics(df4, "oval21_deep")
    calculate_ratio_statistics(df5, "oval21_wide")
    

   

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run RQ1 analysis')
    parser.add_argument('--table2', action='store_true', help='Generate Table 2 analysis')
    parser.add_argument('--table3', action='store_true', help='Generate Table 3 analysis')
    parser.add_argument('--table4', action='store_true', help='Generate Figure 4 analysis')
    args = parser.parse_args()
    
    if args.table2:
        print("Generating Table 2 analysis:")
        getTable2()
    elif args.table3:
        print("Generating Table 3 analysis:")
        getTable3()
    elif args.table4:
        print("Generating Table 4 analysis:")
        getTable4()
    else:
        # If no specific argument is provided, run figure3 by default
        print("No specific option provided. Running Figure 3 analysis by default...")
        # figure3()

    
