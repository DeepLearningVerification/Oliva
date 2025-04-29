import csv
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



# Traditional BaB analysis
class AnalyzerBase(Analyzer):
    @classmethod
    def class_name(cls):
        return cls.__name__

    def sub_class_name(self):
        if self.class_name( )== "Analyzer_Reuse" and len(self.template_store.template_map)== 0:
            return "Template_Gen"
        return self.class_name()

    def analyze_domain(self, props):
        results = Results_Olive(self.args, props = props, option=self.sub_class_name())
        for i in range(len(props)):
            print("************************** Proof %d *****************************" % ( i +1))
            num_clauses = props[i].get_input_clause_count()
            clause_ver_status = []
            ver_start_time = time.time()

            for j in range(num_clauses):
                cl_status, tree_size, visited_nodes, lb = self.analyze(props[i].get_input_clause(j))
                clause_ver_status.append(cl_status)
            status = self.extract_status(clause_ver_status)
            print(status)
            ver_time = time.time() - ver_start_time
            results.add_result(Result_Olive(ver_time, status, tree_size=tree_size, visited_nodes = visited_nodes, lb = lb))
        return results
    
    def serialize_sets(self,obj):
        if isinstance(obj, set):
            return list(obj)
        return obj
    
    def run_analyzer(self, index, eps=1/255, mode = "easy"):
        print('Using %s abstract domain' % self.args.domain)
        index = int(index)
        eps = float(eps)
        props, inputs = verifier_util.get_specs(self.args.dataset, spec_type=self.args.spec_type, count=self.args.count, eps=eps, mode = mode)
        props = [props[index]]
        results = self.analyze_domain(props)
        results.compute_stats()
        print('Results: ', results.output_count)
        print('Average time:', results.avg_time)
        return results
    
    def analyze(self, prop):
        self.update_transformer(prop)
        tree_size = 1
        node_visited= 1
        
        # Check if classified correctly
        if nnverify.attack.check_adversarial(prop.input, self.net, prop):
            return Status.MISS_CLASSIFIED, tree_size, node_visited, None

        # Check Adv Example with an Attack
        if self.args.attack is not None:
            adv = self.args.attack.search_adversarial(self.net, prop, self.args)
            if nnverify.attack.check_adversarial(adv, self.net, prop):
                return Status.ADV_EXAMPLE, tree_size, node_visited, None

        if self.args.split is None:
            status = self.analyze_no_split()
        elif self.args.split is None:
            status = self.analyze_no_split_adv_ex(prop)
        else:
            bnb_analyzer = BnBBase(self.net, self.transformer, prop, self.args, self.template_store)
            if self.args.parallel:
                bnb_analyzer.run_parallel()
            else:
                bnb_analyzer.run()

            status = bnb_analyzer.global_status
            tree_size = bnb_analyzer.tree_size
            node_visited = bnb_analyzer.node_visited
            lb = bnb_analyzer.cur_lb
        return status, tree_size, node_visited, lb

class BnBBase(bnb.BnB):
    def __init__(self, net, transformer, init_prop, args, template_store, print_result=False):
        self.node_visited = 0
        super().__init__(net, transformer, init_prop, args, template_store, print_result)
    
    
    @classmethod
    def class_name(cls):
        return cls.__name__


    def sub_class_name(self):
        if self.class_name( )== "BaB_Reuse" and len(self.template_store.template_map)== 0:
            return "Template_Gen_BaB"
        return self.class_name()
    
    
    def store_final_tree(self):
        self.proof_tree = ProofTree(self.root_spec)
        self.template_store.add_tree(self.init_prop, self.proof_tree)
        # formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        # with open(f'./pickle/tree_{self.sub_class_name()}_{formatted_time}.pkl', 'wb') as file:
        #     # Pickle the variable and write it to the file
        #     pickle.dump(self.template_store, file)
    
    def verify_specs(self):
        for spec in self.cur_specs:
            self.update_transformer(spec.input_spec, relu_spec=spec.relu_spec)

            # Transformer is updated with new mask
            status, lb = self.verify_node(self.transformer, spec.input_spec)
            self.update_cur_lb(lb)
            spec.update_status(status, lb)
            print("\nSpecNode \t Depth: ", spec.depth, "LB: ", lb)
            if status == Status.ADV_EXAMPLE:
                self.global_status = status
                self.store_final_tree()
                if status == Status.ADV_EXAMPLE:
                    print(f"BnB baseline Finished Verified Specicications, visited nodes: {self.node_visited}, find a counterexample")
                    # with open("file.pickle", "wb") as handle:
                    #     pickle.dump(self.template_store, handle)
                    return
            if self.is_timeout():
                print(f"Time is up, visited nodes: {self.node_visited}")
                self.store_final_tree()
                self.check_verified_status()
                return

    def verify_node(self, transformer, prop):
        """
        It is called from bnb_relu_complete. Attempts to verify (ilb, iub), there are three possible outcomes that
        are indicated by the status: 1) verified 2) adversarial example is found 3) Unknown
        """
        lb, is_feasible, adv_ex = transformer.compute_lb(complete=True)
        status = self.get_status(adv_ex, is_feasible, lb)
        if lb is not None:
            lb = float(lb)
        self.node_visited += 1
        return status, lb

    def create_initial_specs(self, prop, unstable_relus):
        if is_relu_split(self.split):
            relu_spec = specs.create_relu_spec(unstable_relus)
            self.root_spec = Spec_D(prop, relu_spec=relu_spec, status=self.global_status)
            cur_specs = specs.SpecList([self.root_spec])
            config.write_log("Unstable relus: " + str(unstable_relus))
        else:
            if self.args.initial_split:
                # Do a smarter initial split similar to ERAN
                # This works only for ACAS-XU
                zono_transformer = ZonoTransformer(prop, complete=True)
                zono_transformer = nnverify.domains.build_transformer(zono_transformer, self.net, prop)

                center = zono_transformer.centers[-1]
                cof = zono_transformer.cofs[-1]
                cof_abs = torch.sum(torch.abs(cof), dim=0)
                lb = center - cof_abs
                adv_index = torch.argmin(lb)
                input_len = len(prop.input_lb)
                smears = torch.abs(cof[:input_len, adv_index])
                split_multiple = 10 / torch.sum(smears)  # Dividing the initial splits in the proportion of above score
                num_splits = [int(torch.ceil(smear * split_multiple)) for smear in smears]

                inp_specs = prop.multiple_splits(num_splits)
                cur_specs = specs.SpecList([Spec_D(prop, status=self.global_status) for prop in inp_specs])
                # TODO: Add a root spec in this case as well
            else:
                self.root_spec = Spec_D(prop, status=self.global_status)
                cur_specs = specs.SpecList([self.root_spec])

        return cur_specs

    def run(self):

        """
        It is the public method called from the analyzer. @param split is a string that chooses the mode for relu
        or input splitting.
        """
        if self.global_status != Status.UNKNOWN:
            return

        while self.continue_search():

            self.prev_lb = self.cur_lb
            self.reset_cur_lb()

            # Main verification loop
            if self.args.parallel:
                self.verify_specs_parallel()
            else:
                self.verify_specs()

            split_score = self.set_split_score(self.init_prop, self.cur_specs, inp_template=self.inp_template)
            # Each spec should hold the prev lb and current lb
            self.cur_specs, verified_specs = verifier_util.branch_unsolved(self.cur_specs, self.split, split_score=split_score,
                                                                  inp_template=self.inp_template, args=self.args,
                                                                  net=self.net, transformer=self.transformer)
            # Update the tree size
            self.tree_size += len(self.cur_specs)

        print(f"BnB Baseline Finished Verified Specicications, visited nodes: {self.node_visited}")
        self.check_verified_status()
        self.store_final_tree()

    def get_unstable_relus(self):
        lb, is_feasible, adv_ex = self.transformer.compute_lb(complete=True)
        status = self.get_status(adv_ex, is_feasible, lb)

        if 'unstable_relus' in dir(self.transformer):
            unstable_relus = self.transformer.unstable_relus
        else:
            unstable_relus = None

        if status != Status.UNKNOWN:
            self.global_status = status
            if status == Status.VERIFIED and self.print_result:
                print(status)
        return unstable_relus

# Oliva-Greedy on reward
class Analyzer_NDFS(AnalyzerBase):
     def analyze(self, prop):
        self.update_transformer(prop)
        tree_size = 1
        node_visited= 1
        
        # Check if classified correctly
        if nnverify.attack.check_adversarial(prop.input, self.net, prop):
            return Status.MISS_CLASSIFIED, tree_size, node_visited, None

        # Check Adv Example with an Attack
        if self.args.attack is not None:
            adv = self.args.attack.search_adversarial(self.net, prop, self.args)
            if nnverify.attack.check_adversarial(adv, self.net, prop):
                return Status.ADV_EXAMPLE, tree_size, node_visited, None

        if self.args.split is None:
            status = self.analyze_no_split()
        elif self.args.split is None:
            status = self.analyze_no_split_adv_ex(prop)
        else:
            bnb_analyzer = BnB_NDFS(self.net, self.transformer, prop, self.args, self.template_store)
            if self.args.parallel:
                bnb_analyzer.run_parallel()
            else:
                bnb_analyzer.run()

            status = bnb_analyzer.global_status
            tree_size = bnb_analyzer.tree_size
            node_visited = bnb_analyzer.node_visited
            lb = bnb_analyzer.cur_lb
        return status, tree_size, node_visited, lb
        
class BnB_NDFS(BnBBase):
    def __init__(self, net, transformer, init_prop, args, template_store, print_result=False):
        super().__init__(net, transformer, init_prop, args, template_store, print_result)
        self.sigma = 0.5    # TODO: this is the balance of depth and specdist, delete later
        self.reward = dict()
        self.mini_bound = math.inf
        
    def helper(self, node, tree_set):
        node_name = str(node).split()[-1]
        if node_name not in tree_set:
            tree_set[node_name] = list()  
        if len(node.children) > 1: 
            for i in node.get_children():
                child_node = str(i).split()[-1]
                tree_set[child_node] = list()  
                tree_set[node_name].append(child_node)
                self.helper(i, tree_set)
        return 

    def verify_node(self, transformer, prop):
        """
        It is called from bnb_relu_complete. Attempts to verify (ilb, iub), there are three possible outcomes that
        are indicated by the status: 1) verified 2) adversarial example is found 3) Unknown
        """
        lb, is_feasible, adv_ex = transformer.compute_lb(complete=True)
        status = self.get_status(adv_ex, is_feasible, lb)
        if lb is not None:
            lb = float(lb)
        self.node_visited += 1
        return status, lb
    
    def maxG_order(self):
        max_reward = -math.inf
        max_item = None
        # rootnode = self.cur_specs[0].get_root()
        # mini_lb_node = verifier_util.get_mini_lb(rootnode)
        max_index = None
        # num_relus = len(self.get_unstable_relus())
        for index in range(len(self.cur_specs)):
            i = self.cur_specs[index]
            if i.parent is None: 
                # self.cur_specs.pop(index)
                return i, index 
            
            # reward = self.sigma*i.depth/num_relus + (1-self.sigma)*i.lb/mini_lb_node.lb
            reward = abs(i.lb)
            
            if reward > max_reward:
                max_item = i
                max_index= index
                max_reward = reward
        # self.cur_specs.pop(max_index)
        return max_item, max_index
    def run(self):

        """
        It is the public method called from the analyzer. @param split is a string that chooses the mode for relu
        or input splitting.
        """
        if self.global_status != Status.UNKNOWN:
            return
        
        while self.continue_search():
            
            spec, index = self.maxG_order()
            if spec.parent is None:
                self.update_transformer(spec.input_spec, relu_spec=spec.relu_spec)

                # Transformer is updated with new mask
                status, lb = self.verify_node(self.transformer, spec.input_spec)
                # self.update_cur_lb(lb)
               
                spec.update_status(status, lb)
                print("\nSpecNode \t ",  "LB: ", lb, "status: ", status)
                if status == Status.ADV_EXAMPLE:
                    self.global_status = status
                    self.check_verified_status()
                    print(f"BnB Greedy Finished Verified Specicications, visited nodes: {self.node_visited}, find a counterexample")
                    return False
            if spec.lb < 0:
                self.update_transformer(spec.input_spec, relu_spec=spec.relu_spec)
                split_score = self.set_split_score(self.init_prop, self.cur_specs, inp_template=self.inp_template)
                spec_a, spec_b = verifier_util.split_spec(spec=spec, split_type=self.split, split_score=split_score,
                                                                    inp_template=self.inp_template, args=self.args,
                                                                    net=self.net, transformer=self.transformer)
                for i in [spec_a, spec_b]:
                    self.update_transformer(i.input_spec, relu_spec=i.relu_spec)
                    status, lb = self.verify_node(self.transformer, i.input_spec)
                    # if lb == None:
                    #     continue
                    self.update_cur_lb(lb)
                    i.update_status(status, lb)
                    print("\nSpecNode \t ", "LB: ", lb, "status: ", status)
                    if status == Status.ADV_EXAMPLE:
                        self.global_status = status
                        print(f"BnB Greedy Finished Verified Specicications, visited nodes: {self.node_visited}, find a counterexample")
                        self.check_verified_status()
                        self.store_final_tree()
                        return False
                    else:
                        if status == Status.UNKNOWN:
                            self.cur_specs.append(i)
            self.cur_specs.pop(index)
        print(f"BnB Greedy Finished Verified Specicications, visited nodes: {self.node_visited}")
        self.check_verified_status()
        self.store_final_tree()


# Oliva for simulated annealling
class Analyzer_annealing(Analyzer_NDFS):
    def __init__(self, args, net=None, template_store=None, alpha_config = 0.99):
        self.alpha_config = alpha_config 
        super().__init__(args, net=None, template_store=None)
    def analyze(self, prop):
        self.update_transformer(prop)
        tree_size = 1
        node_visited= 1
        
        # Check if classified correctly
        if nnverify.attack.check_adversarial(prop.input, self.net, prop):
            return Status.MISS_CLASSIFIED, tree_size, node_visited, None

        # Check Adv Example with an Attack
        if self.args.attack is not None:
            adv = self.args.attack.search_adversarial(self.net, prop, self.args)
            if nnverify.attack.check_adversarial(adv, self.net, prop):
                return Status.ADV_EXAMPLE, tree_size, node_visited, None

        if self.args.split is None:
            status = self.analyze_no_split()
        elif self.args.split is None:
            status = self.analyze_no_split_adv_ex(prop)
        else:
            bnb_analyzer = BnB_balance(self.net, self.transformer, prop, self.args, self.template_store,alpha_config=self.alpha_config)
            if self.args.parallel:
                bnb_analyzer.run_parallel()
            else:
                bnb_analyzer.run()

            status = bnb_analyzer.global_status
            tree_size = bnb_analyzer.tree_size
            node_visited = bnb_analyzer.node_visited
            lb = bnb_analyzer.cur_lb
        return status, tree_size, node_visited, lb
 
class BnB_balance(BnB_NDFS):  
     
    def __init__(self, net, transformer, init_prop, args, template_store, print_result=False, alpha_config=0.99):
        super().__init__(net, transformer, init_prop, args, template_store, print_result=False)
        self.alpha = alpha_config
        self.T = 1 ## simulated annealling for initialized temperature
    
    def helper_SA(self, spec, mini_lb, temperature):
        specA = spec.get_children()[0]
        if specA == 0:
            return spec
        specB = spec.get_children()[1]
        if specA.lb > 0:
            return self.helper_SA(specB, mini_lb,temperature)
        if specB.lb > 0:
            return self.helper_SA(specA, mini_lb,temperature)
        if specA.lb > specB.lb:
            specA, specB = specB, specA
        delta_p = (specB.lb-specA.lb)/(mini_lb*temperature)
        # print(f"specA: {specA.lb}, specB, {specB.lb}, mini_lb, {mini_lb}" )
        # assert delta_p >= 0 and delta_p <= 1, "delta_p is out of bound"
        if math.exp(delta_p) > random.uniform(0, 1):
            _spec = random.choice([specA, specB])
            # print(f"exp delta_p: {math.exp(delta_p)}, " )
            return self.helper_SA(_spec, mini_lb,temperature) 
        
        return self.helper_SA(specA, mini_lb,temperature)
    
    # Simulated annealling 
    def SA_order(self, temperature):
        max_item = None
        rootnode = self.cur_specs[0].get_root()
        # mini_lb_node = verifier_util.get_mini_lb(rootnode)
        max_item = self.helper_SA(rootnode, rootnode.lb,temperature)
        if max_item in self.cur_specs:
            self.cur_specs.remove(max_item)
        return max_item
    
    def run(self):

        """
        It is the public method called from the analyzer. @param split is a string that chooses the mode for relu
        or input splitting.
        """
        if self.global_status != Status.UNKNOWN:
            return
        
        while self.continue_search():
            self.T = self.alpha * self.T
            spec = self.SA_order(self.T)
            if spec.parent is None:
                self.update_transformer(spec.input_spec, relu_spec=spec.relu_spec)

                # Transformer is updated with new mask
                status, lb = self.verify_node(self.transformer, spec.input_spec)
                self.mini_bound = lb
                # self.update_cur_lb(lb)
                spec.update_status(status, lb)
                # print("\nSpecNode \t Depth: ", spec.depth, "LB: ", lb, "status: ", status)
                print("\nSpecNode \t", "LB: ", lb, "status: ", status)
                if status == Status.ADV_EXAMPLE:
                    self.global_status = status
                    self.check_verified_status()
                    print(f"BnB SA Finished Verified Specicications, visited nodes: {self.node_visited}, find a counterexample")
                    return False
            if spec.lb < 0:
                self.update_transformer(spec.input_spec, relu_spec=spec.relu_spec)
                split_score = self.set_split_score(self.init_prop, self.cur_specs, inp_template=self.inp_template)
                spec_a, spec_b = verifier_util.split_spec(spec=spec, split_type=self.split, split_score=split_score,
                                                                    inp_template=self.inp_template, args=self.args,
                                                                    net=self.net, transformer=self.transformer)
                for i in [spec_a, spec_b]:
                    self.update_transformer(i.input_spec, relu_spec=i.relu_spec)
                    status, lb = self.verify_node(self.transformer, i.input_spec)
                    # if lb == None:
                    #     continue
                    self.update_cur_lb(lb)
                    i.update_status(status, lb) ## TODO ： backpopagation
                    print("\nSpecNode ", "LB: ", lb, "status: ", status)
                    if status == Status.ADV_EXAMPLE:
                        self.global_status = status
                        print(f"BnB SA Finished Verified Specicications, visited nodes: {self.node_visited}, find a counterexample")
                        self.check_verified_status()
                        self.store_final_tree()
                        return False
                    else:
                        if status == Status.UNKNOWN:
                            self.cur_specs.append(i)
            
        print(f"BnB Balancd Finished Verified Specicications, visited nodes: {self.node_visited}")
        self.check_verified_status()
        self.store_final_tree()

    
# Tune Wrapper for NDFS
class Analyzer_dfs_configure(Analyzer_NDFS):
    def __init__(self, args, net=None, template_store=None, lambda_config = 0.5):
        self.lambda_config = lambda_config
        super().__init__(args, net=None, template_store=None)
    def analyze(self, prop):
        self.update_transformer(prop)
        tree_size = 1
        node_visited= 1
        
        # Check if classified correctly
        if nnverify.attack.check_adversarial(prop.input, self.net, prop):
            return Status.MISS_CLASSIFIED, tree_size, node_visited, None

        # Check Adv Example with an Attack
        if self.args.attack is not None:
            adv = self.args.attack.search_adversarial(self.net, prop, self.args)
            if nnverify.attack.check_adversarial(adv, self.net, prop):
                return Status.ADV_EXAMPLE, tree_size, node_visited, None

        if self.args.split is None:
            status = self.analyze_no_split()
        elif self.args.split is None:
            status = self.analyze_no_split_adv_ex(prop)
        else:
            bnb_analyzer = BnB_NDFS_configure(self.net, self.transformer, prop, self.args, self.template_store,lambda_config=self.lambda_config)
            if self.args.parallel:
                bnb_analyzer.run_parallel()
            else:
                bnb_analyzer.run()

            status = bnb_analyzer.global_status
            tree_size = bnb_analyzer.tree_size
            node_visited = bnb_analyzer.node_visited
            lb = bnb_analyzer.cur_lb
        return status, tree_size, node_visited, lb

# Tune Wrapper for BnB_NDFS   
class BnB_NDFS_configure(BnB_NDFS):   
      def __init__(self, net, transformer, init_prop, args, template_store, print_result=False, lambda_config=0.5):
          super().__init__(net, transformer, init_prop, args, template_store, print_result=False)
          self.sigma = lambda_config

# Compare Results    
def summarize_results(file_name, image_index, eps, greedy, balance, bab):
    with open(file_name, 'a+') as f:
            writer = csv.writer(f)
            writer.writerow([image_index, eps,
                             "DFS:", greedy.time, greedy.visited, greedy.ver_output,greedy.lb,
                             "Balance", balance.time, balance.visited, balance.ver_output,balance.lb,
                             "Baseline:", bab.time, bab.visited, bab.ver_output, bab.lb] )

def summarize_result_RQ3(file_name, image_index, eps, greedy0, greedy1, greedy2, greedy3, greedy4, greedy5):
    # "Balanced:", balance.time, balance.visited, balance.ver_output, balance.lb,
    with open(file_name, 'a+') as f:
            writer = csv.writer(f)
            writer.writerow([image_index, eps,
                             "SA0:", greedy0.time, greedy0.visited, greedy0.ver_output, greedy0.lb,
                             "SA1:", greedy1.time, greedy1.visited, greedy1.ver_output, greedy1.lb,
                             "SA2:", greedy2.time, greedy2.visited, greedy2.ver_output, greedy2.lb,
                             "SA3:", greedy3.time, greedy3.visited, greedy3.ver_output, greedy3.lb,
                             "SA4:", greedy4.time, greedy4.visited, greedy4.ver_output, greedy4.lb,
                             "SA5:", greedy5.time, greedy5.visited, greedy5.ver_output, greedy5.lb] )
            
# RQ 1 & 2 - MNIST performances
def testing_MNIST_sensitive(filename, inputFile, option = "mnist01"):
    if option == "mnist01":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_01, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=1000)
    elif option == "mnist03":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_03, domain=Domain.LP, approx=ap.Prune(1),
                                 dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=1000)
    elif option == "mnistL2":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_L2, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=1000)
    elif option =="mnistL4":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_L4, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=1000)
    elif option == "mnistL6":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_L6, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=1000)
    elif option == "mnistvgg16":
        pt_args = pt.TransferArgs(net=config.MNIST_VGG_16, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=1000)
    args = pt_args.get_verification_arg()
    lines = list()
    with open(inputFile, "r") as f:
        lines = f.readlines()
    coutlines = 0

    
    for line in lines:
        line_data = eval(line.strip())
        line_data = [int(line_data[0]), float(line_data[1])]
        print(f"============current processing : {line_data},  in the line {coutlines}==============")
        
        image_index = line_data[0]
        eps = line_data[1]
        
        print(f"+++++++++++++++++run Analyer_Sensitive 0 ++++++++++++++\n")
        analyzer0 = Analyzer_annealing(args )
        res0 = analyzer0.run_analyzer(image_index, eps )
        
        print(f"+++++++++++++++++run Analyer_Sensitive 1 ++++++++++++++\n")
        analyzer1 = Analyzer_annealing(args )
        res1 = analyzer1.run_analyzer(image_index, eps )
        
        print(f"+++++++++++++++++run Analyer_Sensitive 2 ++++++++++++++\n")
        analyzer2 = Analyzer_annealing(args )
        res2 = analyzer2.run_analyzer(image_index, eps )
        
        print(f"+++++++++++++++++run Analyer_Sensitive 3 ++++++++++++++\n")
        analyzer3 = Analyzer_annealing(args )
        res3 = analyzer3.run_analyzer(image_index, eps )
        
        print(f"+++++++++++++++++run Analyer_Sensitive 4 ++++++++++++++\n")
        analyzer4 = Analyzer_annealing(args )
        res4 = analyzer4.run_analyzer(image_index, eps )
        
        print(f"+++++++++++++++++run Analyer_Sensitive 5 ++++++++++++++\n")
        analyzer5 = Analyzer_annealing(args )
        res5 = analyzer5.run_analyzer(image_index, eps )

        summarize_result_RQ3(filename, image_index, eps, 
                                                        res0.results_list[0], 
                                                        res1.results_list[0], 
                                                        res2.results_list[0], 
                                                        res3.results_list[0], 
                                                        res4.results_list[0], 
                                                        res5.results_list[0])
        coutlines += 1
    return


def testing_MNIST(filename, inputFile, option = "mnist01"):
    if option == "mnist01":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_01, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=1000)
    elif option == "mnist03":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_03, domain=Domain.LP, approx=ap.Prune(1),
                                 dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=1000)
    elif option == "mnistL2":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_L2, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=1000)
    elif option =="mnistL4":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_L4, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=1000)
    elif option == "mnistL6":
        pt_args = pt.TransferArgs(net=config.MNIST_FFN_L6, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=1000)
    elif option == "mnistvgg16":
        pt_args = pt.TransferArgs(net=config.MNIST_VGG_16, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.MNIST, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=1000)
    args = pt_args.get_verification_arg()
    lines = list()
    with open(inputFile, "r") as f:
        lines = f.readlines()
    coutlines = 0

    for line in lines:
        line_data = eval(line.strip())
        line_data = [int(line_data[0]), float(line_data[1])]
        print(f"============current processing : {line_data},  in the line {coutlines}==============")
        
        image_index = line_data[0]
        eps = line_data[1]
        
        print(f"+++++++++++++++++run Analyer_Baseline++++++++++++++\n")
        analyzer = AnalyzerBase(args)
        resbaseline = analyzer.run_analyzer(image_index, eps)
        print(f"+++++++++++++++++run Analyer_G++++++++++++++\n")
        analyzer_NDFS = Analyzer_NDFS(args)
        resDFS = analyzer_NDFS.run_analyzer(image_index,eps)
        print(f"+++++++++++++++++run Analyer_B++++++++++++++\n")
        analyzer_B = Analyzer_annealing(args)
        resB = analyzer_B.run_analyzer(image_index,eps)
        
        summarize_results(filename,image_index, eps, 
                          resDFS.results_list[0], 
                          resB.results_list[0],
                          resbaseline.results_list[0]) 
        coutlines += 1
    return 


# RQ 1 & 2 - OVAL performances
def testing_OVAL(filename, inputFile, mode="easy", option="cifar10ovalbase") -> None:
    MLmodel = mode
    if option == "cifar10ovalbase": #base model has mode = "easy"/ mode = "med"/ mode = "hard"
        pt_args = pt.TransferArgs(net=config.CIFAR_OVAL_BASE, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.CIFAR10, split=Split.RELU_ESIP_SCORE, count=467, 
                                 timeout=1000)
    elif option == "cifar10ovalwide": # model = "wide"
        # assert(mode=="wide")
        pt_args = pt.TransferArgs(net=config.CIFAR_OVAL_WIDE, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.CIFAR10, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=1000)
        MLmodel = "wide"
    elif option == "cifar10ovaldeep": # mode = "deep"
        # assert(mode=="deep")
        pt_args = pt.TransferArgs(net=config.CIFAR_OVAL_DEEP, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.CIFAR10, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=1000)
        MLmodel = "deep"
    args = pt_args.get_verification_arg()
    
    with open(inputFile, "r") as f:
        lines = f.readlines()
    coutlines = 0

    for line in lines:
        line_data = eval(line.strip())
        line_data = [int(line_data[0]), float(line_data[1])]
        print(f"============current processing : {line_data},  in the line {coutlines}==============")
        
        image_index = line_data[0]
        eps = line_data[1]
        
        print(f"+++++++++++++++++run Analyer_Baseline++++++++++++++\n")
        analyzer = AnalyzerBase(args)
        resbaseline = analyzer.run_analyzer(image_index, eps, mode = MLmodel)
        print(f"+++++++++++++++++run Analyer_G++++++++++++++\n")
        analyzer_NDFS = Analyzer_NDFS(args)
        resDFS = analyzer_NDFS.run_analyzer(image_index,eps, mode = MLmodel)
        print(f"+++++++++++++++++run Analyer_B++++++++++++++\n")
        analyzer_B = Analyzer_annealing(args)
        resB = analyzer_B.run_analyzer(image_index,eps, mode=MLmodel)
        
        summarize_results(filename,image_index, eps, 
                          resDFS.results_list[0], 
                          resB.results_list[0],
                          resbaseline.results_list[0]) 
    return 


def testing_OVAL_sensitive(filename, inputFile, mode="easy", option="cifar10ovalbase") -> None:
    MLmodel = mode
    if option == "cifar10ovalbase": #base model has mode = "easy"/ mode = "med"/ mode = "hard"
        pt_args = pt.TransferArgs(net=config.CIFAR_OVAL_BASE, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.CIFAR10, split=Split.RELU_ESIP_SCORE, count=467, 
                                 timeout=1000)
    elif option == "cifar10ovalwide": # model = "wide"
        # assert(mode=="wide")
        pt_args = pt.TransferArgs(net=config.CIFAR_OVAL_WIDE, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.CIFAR10, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=1000)
        MLmodel = "wide"
    elif option == "cifar10ovaldeep": # mode = "deep"
        # assert(mode=="deep")
        pt_args = pt.TransferArgs(net=config.CIFAR_OVAL_DEEP, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.CIFAR10, split=Split.RELU_ESIP_SCORE, count=100, 
                                 timeout=1000)
        MLmodel = "deep"
    args = pt_args.get_verification_arg()
    
    with open(inputFile, "r") as f:
        lines = f.readlines()
    coutlines = 0

    for line in lines:
        line_data = eval(line.strip())
        line_data = [int(line_data[0]), float(line_data[1])]
        print(f"============current processing : {line_data},  in the line {coutlines}==============")
        
        image_index = line_data[0]
        eps = line_data[1]
        
        print(f"+++++++++++++++++run Analyer_Sensitive 0 ++++++++++++++\n")
        analyzer0 = Analyzer_annealing(args)
        res0 = analyzer0.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 1 ++++++++++++++\n")
        analyzer1 = Analyzer_annealing(args)
        res1 = analyzer1.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 2 ++++++++++++++\n")
        analyzer2 = Analyzer_annealing(args)
        res2 = analyzer2.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 3 ++++++++++++++\n")
        analyzer3 = Analyzer_annealing(args)
        res3 = analyzer3.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 4 ++++++++++++++\n")
        analyzer4 = Analyzer_annealing(args)
        res4 = analyzer4.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 5 ++++++++++++++\n")
        analyzer5 = Analyzer_annealing(args)
        res5 = analyzer5.run_analyzer(image_index, eps, mode = MLmodel)

        summarize_result_RQ3(filename, image_index, eps, 
                                                        res0.results_list[0], 
                                                        res1.results_list[0], 
                                                        res2.results_list[0], 
                                                        res3.results_list[0], 
                                                        res4.results_list[0], 
                                                        res5.results_list[0])
        coutlines += 1
    return 




# RQ 3 sensitivity analysis on lambda_config
def testing_sensitive_lambda(filename, inputFile):
    pt_args = pt.TransferArgs(net=config.CIFAR_OVAL_WIDE, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.CIFAR10, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=1000)
    MLmodel = "wide"
    args = pt_args.get_verification_arg()
    
    with open(inputFile, "r") as f:
        lines = f.readlines()
    coutlines = 0

    for line in lines:
        line_data = eval(line.strip())
        line_data = [int(line_data[0]), float(line_data[1])]
        print(f"============current processing : {line_data},  in the line {coutlines}==============")
        
        image_index = line_data[0]
        eps = line_data[1]
        
        print(f"+++++++++++++++++run Analyer_Sensitive 0 ++++++++++++++\n")
        analyzer0 = Analyzer_dfs_configure(args, lambda_config = 0)
        res0 = analyzer0.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 1 ++++++++++++++\n")
        analyzer1 = Analyzer_dfs_configure(args, lambda_config = 0.2)
        res1 = analyzer1.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 2 ++++++++++++++\n")
        analyzer2 = Analyzer_dfs_configure(args, lambda_config = 0.4)
        res2 = analyzer2.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 3 ++++++++++++++\n")
        analyzer3 = Analyzer_dfs_configure(args, lambda_config = 0.6)
        res3 = analyzer3.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 4 ++++++++++++++\n")
        analyzer4 = Analyzer_dfs_configure(args, lambda_config = 0.8)
        res4 = analyzer4.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 5 ++++++++++++++\n")
        analyzer5 = Analyzer_dfs_configure(args, lambda_config = 1)
        res5 = analyzer5.run_analyzer(image_index, eps, mode = MLmodel)

        summarize_result_RQ3(filename, image_index, eps, 
                                                        res0.results_list[0], 
                                                        res1.results_list[0], 
                                                        res2.results_list[0], 
                                                        res3.results_list[0], 
                                                        res4.results_list[0], 
                                                        res5.results_list[0])
  
  
def testing_sensitive_alpha(filename, inputFile):
    pt_args = pt.TransferArgs(net=config.CIFAR_OVAL_WIDE, domain=Domain.LP, approx=ap.Prune(1),
                                dataset=Dataset.CIFAR10, split=Split.RELU_ESIP_SCORE, count=100, 
                                timeout=1000)
    MLmodel = "wide"
    args = pt_args.get_verification_arg()
    
    with open(inputFile, "r") as f:
        lines = f.readlines()
    coutlines = 0

    for line in lines:
        line_data = eval(line.strip())
        line_data = [int(line_data[0]), float(line_data[1])]
        print(f"============current processing : {line_data},  in the line {coutlines}==============")
        
        image_index = line_data[0]
        eps = line_data[1]
        
        print(f"+++++++++++++++++run Analyer_Sensitive 0 ++++++++++++++\n")
        analyzer0 = Analyzer_annealing(args, alpha_config = 0.95)
        res0 = analyzer0.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 1 ++++++++++++++\n")
        analyzer1 = Analyzer_annealing(args, alpha_config = 0.96)
        res1 = analyzer1.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 2 ++++++++++++++\n")
        analyzer2 = Analyzer_annealing(args, alpha_config = 0.97)
        res2 = analyzer2.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 3 ++++++++++++++\n")
        analyzer3 = Analyzer_annealing(args, alpha_config = 0.98)
        res3 = analyzer3.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 4 ++++++++++++++\n")
        analyzer4 = Analyzer_annealing(args, alpha_config = 0.99)
        res4 = analyzer4.run_analyzer(image_index, eps, mode = MLmodel)
        
        print(f"+++++++++++++++++run Analyer_Sensitive 5 ++++++++++++++\n")
        analyzer5 = Analyzer_annealing(args, alpha_config = 0.999)
        res5 = analyzer5.run_analyzer(image_index, eps, mode = MLmodel)

        summarize_result_RQ3(filename, image_index, eps, 
                                                        res0.results_list[0], 
                                                        res1.results_list[0], 
                                                        res2.results_list[0], 
                                                        res3.results_list[0], 
                                                        res4.results_list[0], 
                                                        res5.results_list[0])
  
    
if __name__ == '__main__':
    program_option = sys.argv[1]
    file_number = sys.argv[2]
    sensi = sys.argv[3] if len(sys.argv) > 3 else -1
    if program_option == "mnist01" or program_option == "mnist03" or program_option == "mnistL2" or program_option == "mnistL4" or program_option == "mnistL6" or program_option=="mnistvgg16":
        if sensi == -1:
            testing_MNIST(f"Result_{program_option}_{file_number}.csv", 
                        f"./data/treeSpecification/{program_option}_{file_number}.txt", 
                        option=program_option)
        else:
            testing_MNIST_sensitive(f"Result_sensi_{program_option}_{file_number}.csv", 
                        f"./data/treeSpecification/{program_option}_{file_number}.txt", 
                        option=program_option)
        
    elif program_option == "cifar10ovalbase" or program_option == "cifar10ovaldeep" or program_option == "cifar10ovalwide":
        if sensi == -1:
            testing_OVAL(f"Result_{program_option}_{file_number}_oval.csv", 
                        f"./data/treeSpecification/{program_option}_{file_number}.txt", 
                        mode="easy", option=program_option)
        else:
            testing_OVAL_sensitive(f"Result_sensi_{program_option}_{file_number}_oval.csv", 
                        f"./data/treeSpecification/{program_option}_{file_number}.txt", 
                        mode="easy", option=program_option)
    elif program_option == "sensitive":
        if sensi =="lambda":
            testing_sensitive_lambda(f"Result_Sensitive_{file_number}_lambda.csv", f"./data/treeSpecification/sensitive_{file_number}_lambda.txt")
        elif sensi =="alpha":
            testing_sensitive_alpha(f"Result_Sensitive_{file_number}_alpha.csv", f"./data/treeSpecification/sensitive_{file_number}_alpha.txt")
        
    