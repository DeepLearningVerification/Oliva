import csv
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




def run_single_mnist(image_index, eps, verifier = "GR", option = "mnist01", approx = 0, timeout = 1000):
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

    result = analyzer.run_analyzer(image_index, eps)
    res = result.results_list[0]
    return res.time, res.visited, res.ver_output,res.lb
    

def main(image_index, eps, verifier="GR", option="mnist01", approx=0, timeout=1000):
    time_taken, nodes_visited, verification_result, lower_bound = run_single_mnist(
        image_index=image_index,
        eps=eps,
        verifier=verifier,
        option=option,
        approx=approx,
        timeout=timeout
    )
    
    print(f"Verification Result: {verification_result}")
    print(f"Time Taken: {time_taken:.2f} seconds")
    print(f"Nodes Visited: {nodes_visited}")
    print(f"Lower Bound: {lower_bound}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python run_single.py <image_index> <eps> [verifier] [option] [approx] [timeout]")
        sys.exit(1)
    
    image_index = int(sys.argv[1])
    eps = float(sys.argv[2])
    verifier = sys.argv[3] if len(sys.argv) > 3 else "GR"
    option = sys.argv[4] if len(sys.argv) > 4 else "mnist01"
    approx = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    timeout = int(sys.argv[6]) if len(sys.argv) > 6 else 1000
    
    main(image_index, eps, verifier, option, approx, timeout)


