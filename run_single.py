import csv
import os
from datetime import datetime
from optparse import Option
import time
import torch
import sys
import math
import random 
import nnverify
from nnverify.common import Status
from nnverify.common import Domain
from nnverify.common.dataset import Dataset

import nnverify.proof_transfer.proof_transfer as pt
from nnverify.analyzer import Analyzer
from nnverify.bnb import bnb, Split, is_relu_split
import nnverify.specs.spec as specs

from nnverify import config
from nnverify.domains.deepz import ZonoTransformer

import nnverify.proof_transfer.approximate as ap
from nnverify.bnb.proof_tree import ProofTree
import nnverify.attack

import verifier_util
from verifier_util import Result_Olive, Results_Olive, Spec_D

from verifier import *


def generate_csv_filename(dataset_name, model_name, verifier_type):
    """Generate CSV filename with dataset, model, and verifier type"""
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"separate_verification_{dataset_name}_{model_name}_{verifier_type}.csv"

def get_dataset_model_names(option):
    """Extract dataset and model names from option"""
    if "mnist" in option.lower():
        dataset_name = "MNIST"
        if option == "mnist01":
            model_name = "FFN_01"
        elif option == "mnist03":
            model_name = "FFN_03"
        elif option == "mnistL2":
            model_name = "mnistL2"
        elif option == "mnistL4":
            model_name = "mnistL4"
        elif option == "mnistL6":
            model_name = "FFN_L6"
        else:
            model_name = "FFN"
    elif "cifar" in option.lower():
        dataset_name = "CIFAR10"
        if option == "cifarbase":
            model_name = "OVAL_BASE"
        elif option == "cifarwide":
            model_name = "OVAL_WIDE"
        elif option == "cifardeep":
            model_name = "OVAL_DEEP"
        else:
            model_name = "OVAL"
    else:
        dataset_name = "UNKNOWN"
        model_name = "UNKNOWN"
    
    return dataset_name, model_name

def save_results_to_csv(results, image_index, eps, verifier, option, csv_filename):
    """Save separate verification results to CSV file"""
    dataset_name, model_name = get_dataset_model_names(option)
    
    # Create results directory if it doesn't exist
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    csv_filepath = os.path.join(results_dir, csv_filename)
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.exists(csv_filepath)
    
    with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'image_index', 'epsilon', 'dataset', 'model', 'verifier_type',
            'adv_label', 'true_label', 'status', 'tree_size', 'nodes_visited', 
            'lower_bound', 'verification_time'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        # Write results
        # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for res in results:
            writer.writerow({
                'image_index': image_index,
                'epsilon': eps,
                'dataset': dataset_name,
                'model': model_name,
                'verifier_type': verifier,
                'adv_label': res['adv_label'],
                'true_label': res['true_label'],
                'status': str(res['status']),
                'tree_size': res.get('tree_size', 'N/A'),
                'nodes_visited': res.get('nodes_visited', 0),
                'lower_bound': res.get('lower_bound', 'N/A'),
                'verification_time': res.get('verification_time', 0)
            })
    
    print(f"\nResults saved to: {csv_filepath}")




def run_single_mnist(image_index, eps, verifier = "GR", option = "mnist01", approx = 0, timeout = 1000, separate_labels = False):
    # Create approx_method variable to allow flexibility for different model alterations
    # Current implementation uses Prune but this could be replaced with other techniques
    approx_method = ap.Prune(approx)
    
    if option == "mnist01":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_01, domain=Domain.LP, approx=approx_method,
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=timeout)
    elif option == "mnist03":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_03, domain=Domain.LP, approx=approx_method,
                                 dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=timeout)
    elif option == "mnistL2":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_L2, domain=Domain.LP, approx=approx_method,
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=timeout)
    elif option =="mnistL4":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_L4, domain=Domain.LP, approx=approx_method,
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=timeout)
    elif option == "mnistL6":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_L6, domain=Domain.LP, approx=approx_method,
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=timeout)
    elif option == "cifarbase":
        pt_args = pt.TransferArgs(net=config.CIFAR_OVAL_BASE, domain=Domain.LP, approx=approx_method,
                                dataset=Dataset.OVAL_CIFAR, split=Split.RELU_ESIP_SCORE, count=467, 
                                timeout=timeout)
    elif option == "cifarwide":
        pt_args = pt.TransferArgs(net=config.CIFAR_OVAL_WIDE, domain=Domain.LP, approx=approx_method,
                                dataset=Dataset.OVAL_CIFAR, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=timeout)
    elif option == "cifardeep":
        pt_args = pt.TransferArgs(net=config.CIFAR_OVAL_DEEP, domain=Domain.LP, approx=approx_method,
                                dataset=Dataset.OVAL_CIFAR, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=timeout)
    args = pt_args.get_verification_arg()
    
    if verifier == "GR":
        if approx == 0:
            analyzer = Analyzer_NDFS(args)
        else:  
            approx_net = pt.get_perturbed_network(pt_args)
            analyzer = Analyzer_NDFS(args, net=approx_net)
    elif verifier == "SA":
        if approx == 0:
            analyzer = Analyzer_annealing(args)
        else:
            approx_net = pt.get_perturbed_network(pt_args)
            analyzer = Analyzer_annealing(args, net=approx_net)
    elif verifier == "BnB":
        if approx == 0:
            analyzer = AnalyzerBase(args)
        else:
            approx_net = pt.get_perturbed_network(pt_args)
            analyzer = AnalyzerBase(args, net=approx_net)
    else:
        raise ValueError(f"Invalid verifier: {verifier}")

    if separate_labels:
        # Use the new separate verification functionality
        
        # Determine number of classes based on dataset
        if args.dataset == Dataset.MNIST:
            n_classes = 10
        elif args.dataset == Dataset.OVAL_CIFAR:
            n_classes = 10
        else:
            n_classes = 10  # Default
        
        # Run separate verification for each adversarial label through the analyzer
        separate_results = analyzer.run_analyzer_separate_labels(image_index, eps, n_classes=n_classes)
        return separate_results
        
    else:
        # Regular verification
        result = analyzer.run_analyzer(image_index, eps)
        res = result.results_list[0]
        return res.time, res.visited, res.ver_output, res.lb
    

def main(image_index, eps, verifier="GR", option="mnist01", approx=0, timeout=1000, separate_labels=False):
    result = run_single_mnist(
        image_index=image_index,
        eps=eps,
        verifier=verifier,
        option=option,
        approx=approx,
        timeout=timeout,
        separate_labels=separate_labels
    )
    
    if separate_labels:
        # Handle separate verification results
        print(f"\n=== Separate Verification Results for Image {image_index} ===")
        print(f"Epsilon: {eps}")
        print("-" * 95)
        print(f"{'Adv Label':<10} {'Status':<12} {'Tree Size':<10} {'Nodes':<8} {'Lower Bound':<12} {'Time (s)':<10}")
        print("-" * 95)
        
        total_time = 0
        total_nodes = 0
        verified_count = 0
        adversarial_count = 0
        unknown_count = 0
        
        for res in result:
            status = res['status']
            if status == Status.VERIFIED:
                verified_count += 1
                status_str = "VERIFIED"
            elif status == Status.ADV_EXAMPLE:
                adversarial_count += 1
                status_str = "ADV_EXAMPLE"
            else:
                unknown_count += 1
                status_str = "UNKNOWN"
                
            # Handle None values safely
            tree_size = res.get('tree_size', 'N/A') if res.get('tree_size') is not None else 'N/A'
            nodes_visited = res.get('nodes_visited', 0) if res.get('nodes_visited') is not None else 0
            lower_bound = res.get('lower_bound', 'N/A') if res.get('lower_bound') is not None else 'N/A'
            verification_time = res.get('verification_time', 0) if res.get('verification_time') is not None else 0
            
            print(f"{res['adv_label']:<10} {status_str:<12} {tree_size:<10} "
                  f"{nodes_visited:<8} {lower_bound:<12} {verification_time:<10.3f}")
            
            total_nodes += nodes_visited if isinstance(nodes_visited, int) else 0
            total_time += verification_time if isinstance(verification_time, (int, float)) else 0
        
        print("-" * 95)
        print(f"Summary: {verified_count} verified, {adversarial_count} adversarial, {unknown_count} unknown")
        print(f"Total nodes visited: {total_nodes}")
        print(f"Total verification time: {total_time:.3f}s")
        
        # Overall robustness assessment
        if adversarial_count > 0:
            print(f"Result: NOT ROBUST (found adversarial examples for {adversarial_count} labels)")
        elif unknown_count > 0:
            print(f"Result: UNKNOWN (could not verify {unknown_count} labels)")
        else:
            print("Result: ROBUST against all adversarial labels")
            
        # Save results to CSV
        dataset_name, model_name = get_dataset_model_names(option)
        csv_filename = generate_csv_filename(dataset_name, model_name, verifier)
        save_results_to_csv(result, image_index, eps, verifier, option, csv_filename)
            
    else:
        # Handle regular verification results
        time_taken, nodes_visited, verification_result, lower_bound = result
        print(f"Verification Result: {verification_result}")
        print(f"Time Taken: {time_taken:.2f} seconds")
        print(f"Nodes Visited: {nodes_visited}")
        print(f"Lower Bound: {lower_bound}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python run_single.py <image_index> <eps> [verifier] [option] [approx] [timeout] [separate_labels]")
        print("  separate_labels: 1 to use separate verification for each adversarial label (BnB only), 0 for regular (default)")
        sys.exit(1)
    
    image_index = int(sys.argv[1])
    eps = float(sys.argv[2])
    verifier = sys.argv[3] if len(sys.argv) > 3 else "GR"
    option = sys.argv[4] if len(sys.argv) > 4 else "mnist01"
    approx = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    timeout = int(sys.argv[6]) if len(sys.argv) > 6 else 1000
    separate_labels = bool(int(sys.argv[7])) if len(sys.argv) > 7 else False
    
    main(image_index, eps, verifier, option, approx, timeout, separate_labels)


