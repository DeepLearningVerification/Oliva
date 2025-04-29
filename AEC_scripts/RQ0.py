import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def readCSV(file_path):
    column_names = ['id', 'eps',
                    'oliva_greedy', 'oliva_greedy_time', 'oliva_greedy_visit', 'oliva_greedy_status', 'oliva_greedy_lb',
                    'oliva_balance', 'oliva_balance_time', 'oliva_balance_visit', 'oliva_balance_status', 'oliva_balance_lb',
                    'neuralsat', 'neuralsat_time', 'neuralsat_status',
                    'bab_baseline', 'bab_baseline_time', 'bab_baseline_visit', 'bab_baseline_status',
                    'abcrown', 'abcrown_status', 'abcrown_time']
    dataframe = pd.read_csv(file_path, sep=",", header=0, names=column_names)
    return dataframe


def table_1():
    l2_instance = len(readCSV('./ECOOPResults/all_results/all_mnistL2.csv'))
    l4_instance = len(readCSV('./ECOOPResults/all_results/all_mnistL4.csv'))
    oval21_base_instance = len(readCSV('./ECOOPResults/all_results/all_oval21_base.csv'))
    oval21_wide_instance = len(readCSV('./ECOOPResults/all_results/all_oval21_wide.csv'))
    oval21_deep_instance = len(readCSV('./ECOOPResults/all_results/all_oval21_deep.csv'))

    l2_images = readCSV('./ECOOPResults/all_results/all_mnistL2.csv')["id"].nunique()
    l4_images = readCSV('./ECOOPResults/all_results/all_mnistL4.csv')["id"].nunique()
    oval21_base_images = readCSV('./ECOOPResults/all_results/all_oval21_base.csv')["id"].nunique()
    oval21_wide_images = readCSV('./ECOOPResults/all_results/all_oval21_wide.csv')["id"].nunique()
    oval21_deep_images = readCSV('./ECOOPResults/all_results/all_oval21_deep.csv')["id"].nunique()

    # Create a formatted table with aligned columns
    print("Model\t\tArchitecture\t\tDataset\t\t#Activations\t# Instances\t#Images")
    print(f"MNISTL2\t\t2 × 256 linear\t\tMNIST\t\t512\t\t{l2_instance}\t\t{l2_images}")
    print(f"MNISTL4\t\t4 × 256 linear\t\tMNIST\t\t1024\t\t{l4_instance}\t\t{l4_images}")
    print(f"OVAL21BASE\t2 Conv, 2 linear\tCIFAR-10\t3172\t\t{oval21_base_instance}\t\t{oval21_base_images}")
    print(f"OVAL21WIDE\t2 Conv, 2 linear\tCIFAR-10\t6244\t\t{oval21_wide_instance}\t\t{oval21_wide_images}")
    print(f"OVAL21DEEP\t4 Conv, 2 linear\tCIFAR-10\t6756\t\t{oval21_deep_instance}\t\t{oval21_deep_images}")
    
def figure3():
    # Read all dataframes
    df1 = pd.read_csv('./ECOOPResults/all_results/all_mnistL2.csv')
    df2 = pd.read_csv('./ECOOPResults/all_results/all_mnistL4.csv')
    df3 = pd.read_csv('./ECOOPResults/all_results/all_oval21_base.csv')
    df4 = pd.read_csv('./ECOOPResults/all_results/all_oval21_deep.csv')
    df5 = pd.read_csv('./ECOOPResults/all_results/all_oval21_wide.csv')
    
    dataframes = [df1, df2, df3, df4, df5]
    names = ['mnistL2', 'mnistL4', 'oval21_base', 'oval21_deep', 'oval21_wide']
    data = []

    # Function to count status types
    def get_status_counts(df):
        status_df = df[["id", "eps", "oliva_greedy_status", "oliva_balance_status", 
                        "bab_baseline_status", "abcrown_status", "neuralsat_status"]]
        
        verified = status_df[(status_df["bab_baseline_status"] == "Status.VERIFIED")].shape[0]
        
        falsified = status_df[(status_df["bab_baseline_status"] == "Status.ADV_EXAMPLE")].shape[0]
        
        total = status_df.shape[0]
        unknown = total - verified - falsified
        
        return verified, falsified, unknown, total

    # Print counts for each dataset
    print("Dataset\t\t\tTotal\tVerified\tFalsified\tUnknown")
    results = {}
    for i, df in enumerate(dataframes):
        verified, falsified, unknown, total = get_status_counts(df)
        data.append([verified, falsified, unknown])
        results[names[i]] = {"total": total, "verified": verified, "falsified": falsified, "unknown": unknown}
    
    print(results)
    
    
def histoData(file_path):
    df = readCSV(file_path)
    ins_num_10 = df[df['bab_baseline_visit'].astype(int) <= 10].shape[0]
    ins_num_50 = df[(df['bab_baseline_visit'].astype(int) > 10) & (df['bab_baseline_visit'].astype(int) <= 50)].shape[0]
    ins_num_100 = df[(df['bab_baseline_visit'].astype(int) > 50) & (df['bab_baseline_visit'].astype(int) <= 100)].shape[0]
    ins_num_200 = df[(df['bab_baseline_visit'].astype(int) > 100) & (df['bab_baseline_visit'].astype(int) <= 200)].shape[0]
    ins_num_500 = df[(df['bab_baseline_visit'].astype(int) > 200) & (df['bab_baseline_visit'].astype(int) <= 500)].shape[0]
    ins_num_1000 = df[(df['bab_baseline_visit'].astype(int) > 500) & (df['bab_baseline_visit'].astype(int) <= 1000)].shape[0]
    return [ins_num_10, ins_num_50, ins_num_100, ins_num_200, ins_num_500, ins_num_1000]


import numpy as np
import matplotlib.pyplot as plt

def getFigure4():
    files_list = [
        './ECOOPResults/all_results/all_mnistL2',
        './ECOOPResults/all_results/all_mnistL4',
        './ECOOPResults/all_results/all_oval21_base',
        './ECOOPResults/all_results/all_oval21_deep',
        './ECOOPResults/all_results/all_oval21_wide'
    ]
    colors = plt.cm.RdYlBu(np.linspace(0.1, 0.9, len(files_list)))
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = ['$\mathdefault{MNIST_{L2}}$', '$\mathdefault{MNIST_{L4}}$',
              '$\mathdefault{OVAL21_{BASE}}$', '$\mathdefault{OVAL21_{DEEP}}$', 
              '$\mathdefault{OVAL21_{WIDE}}$']

    bin_data = []
    for file_name in files_list:
        file_path = f'{file_name}.csv'
        bin_data.append(histoData(file_path))

    bins_tick = [0, 10, 50, 100, 200, 500, 1000]
    custom_labels = ['0-10', '11-50', '51-100', '101-200', '201-500', '501-1000']

    bin_data = np.array(bin_data)
    
    # Store distribution values in a dictionary
    distribution_dict = {}
    for i, dataset in enumerate(labels):
        distribution_dict[dataset] = {
            '0-10': bin_data[i][0],
            '11-50': bin_data[i][1],
            '51-100': bin_data[i][2],
            '101-200': bin_data[i][3],
            '201-500': bin_data[i][4],
            '501-1000': bin_data[i][5]
        }
    
    # Add total for each bin across all datasets
    distribution_dict['Total'] = {
        '0-10': np.sum(bin_data[:, 0]),
        '11-50': np.sum(bin_data[:, 1]),
        '51-100': np.sum(bin_data[:, 2]),
        '101-200': np.sum(bin_data[:, 3]),
        '201-500': np.sum(bin_data[:, 4]),
        '501-1000': np.sum(bin_data[:, 5])
    }
    
    # Print the dictionary directly
    print("Distribution of instances by number of visited nodes:")
    for key, value in distribution_dict.items():
        print(f"{key}: {value}")







    
    

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run RQ0 analysis and visualization')
    parser.add_argument('--table1', action='store_true', help='Generate Table 1 analysis')
    parser.add_argument('--figure3', action='store_true', help='Generate Figure 3 analysis')
    parser.add_argument('--figure4', action='store_true', help='Generate Figure 4 analysis')
    args = parser.parse_args()
    
    if args.table1:
        print("Generating Table 1 analysis...")
        table_1()
    elif args.figure3:
        print("Generating Figure 3 analysis...")
        figure3()
    elif args.figure4:
        print("Generating Figure 4 analysis...")
        getFigure4()
    else:
        # If no specific argument is provided, run figure3 by default
        print("No specific option provided. Running Figure 3 analysis by default...")
        figure3()

    
