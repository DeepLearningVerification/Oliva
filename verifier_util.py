
from nnverify.common.result import Result, Results
from nnverify.common import RESULT_DIR
from nnverify.bnb import Split, is_relu_split, is_input_split, branch
from nnverify import config
from nnverify.common import Status
from nnverify.specs.spec import Spec, SpecList
import nnverify.specs.spec as specs
import torch.nn as nn
import copy
import random
import csv

import torch
import torchvision
from torchvision import transforms

from nnverify import util
from nnverify.specs.properties.acasxu import get_acas_spec
from nnverify.specs.property import Property, InputSpecType, OutSpecType
from nnverify.specs.out_spec import Constraint
from nnverify.specs.relu_spec import Reluspec
from nnverify.util import prepare_data
from nnverify.common import Status
from nnverify.common.dataset import Dataset

class Result_Olive(Result):
    def __init__(self, _time, _ver_output, tree_size=1, visited_nodes=1, lb=0):
        super().__init__(_time, _ver_output, tree_size)
        self.visited = visited_nodes
        self.lb = lb

class Results_Olive(Results):
    def __init__(self, args, props=None, option=None):
        super().__init__(args)
        self.avg_nodes = 0
        self.option = option
        self.props = props
    def compute_stats(self):
        count = len(self.results_list)
        for res in self.results_list:
            self.avg_time += (res.time / count)
            self.avg_tree_size += (res.tree_size / count)
            self.avg_nodes += (res.visited / count)
            if res.ver_output not in self.output_count:
                self.output_count[res.ver_output] = 0
            self.output_count[res.ver_output] += 1

        dir_name = RESULT_DIR + 'csv/'
        file_name = dir_name + self.option + "_" + self.get_csv_file_name()
        with open(file_name, 'a+') as f:
            writer = csv.writer(f)

            for i in range(len(self.results_list)):
                res = self.results_list[i]
                writer.writerow([i, res.ver_output, ' tree size:', res.tree_size, ' time:', res.time, ' visited nodes',
                                 res.visited])

            writer.writerow(['Average time:', self.avg_time, ' Average tree size', self.avg_tree_size])
            writer.writerow([self.output_count])


class Spec_D(Spec):
    def __init__(self, input_spec, relu_spec=None, parent=None, status=Status.UNKNOWN, depth=0):
        super().__init__(input_spec, relu_spec, parent, status)
        self.lb_pre = 0
        self.depth = depth
        self.mctsVisited= 1

    def reset_status(self):
        self.status = Status.UNKNOWN
        self.lb_pre = self.lb
        self.lb = 0

    def get_children(self):
        if len(self.children) == 0:
            return 0, 0
        if len(self.children) == 2:
            return self.children[0], self.children[1]

    def get_root(self):
        if self.parent is None:
            return self
        return self.parent.get_root()
    
def split_spec(spec, split_type, split_score=None, inp_template=None, args=None, net=None, transformer=None):
    if is_relu_split(split_type):
        spec.chosen_split = choose_relu(split_type, spec.relu_spec, spec=spec, split_score=split_score,
                                               inp_template=inp_template, args=args, transformer=transformer)
        split_relu_specs = spec.relu_spec.split_spec(split_type, spec.chosen_split)
        child_specs = [Spec_D(spec.input_spec, rs, parent=spec, depth=spec.depth + 1) for rs in split_relu_specs]
    elif is_input_split(split_type):
        spec.chosen_split = branch.choose_split_dim(spec.input_spec, split_type, net=net)
        split_inp_specs = spec.input_spec.split_spec(split_type, spec.chosen_split)
        child_specs = [Spec_D(ins, spec.relu_spec, parent=spec, depth=spec.depth + 1) for ins in split_inp_specs]
    else:
        raise ValueError("Unknown split!")
    spec.children += child_specs
    return child_specs


def split_chosen_spec(spec, split_type, chosen_split):
    spec.chosen_split = chosen_split
    if is_relu_split(split_type):
        split_relu_specs = spec.relu_spec.split_spec(split_type, chosen_split)
        child_specs = [Spec_D(spec.input_spec, rs, parent=spec, depth=spec.depth + 1) for rs in split_relu_specs]
    elif is_input_split(split_type):
        split_inp_specs = spec.input_spec.split_spec(split_type, chosen_split)
        child_specs = [Spec_D(ins, spec.relu_spec, parent=spec, depth=spec.depth + 1) for ins in split_inp_specs]
    else:
        raise ValueError("Unknown split!")
    spec.children += child_specs
    return child_specs


def choose_relu(split, relu_spec, spec=None, split_score=None, inp_template=None, args=None, transformer=None):
    """
    Chooses the relu that is split in branch and bound.
    @param: relu_spec contains relu_mask which is a map that maps relus to -1/0/1. 0 here indicates that the relu
        is ambiguous
    """
    relu_mask = relu_spec.relu_mask
    if split == Split.RELU_RAND:
        all_relus = []

        # Collect all un-split relus
        for relu in relu_mask.keys():
            if relu_mask[relu] == 0 and relu[0] == 2:
                all_relus.append(relu)

        return random.choice(all_relus)

    # BaBSR based on various estimates of importance
    elif split == Split.RELU_GRAD or split == Split.RELU_ESIP_SCORE or split == Split.RELU_ESIP_SCORE2:
        # Choose the ambiguous relu that has the maximum score in relu_score
        if split_score is None:
            raise ValueError("relu_score should be set while using relu_grad splitting mode")

        max_score, chosen_relu = 0, None

        for relu in relu_mask.keys():
            if relu_mask[relu] == 0 and relu in split_score.keys():
                if split_score[relu] >= max_score:
                    max_score, chosen_relu = split_score[relu], relu

        if chosen_relu is None:
            raise ValueError("Attempt to split should only take place if there are ambiguous relus!")

        print("Chosen relu for splitting: " + str(chosen_relu) + " " + str(max_score))
        return chosen_relu
    elif split == Split.RELU_KFSB:
        k = 3
        if split_score is None:
            raise ValueError("relu_score should be set while using kFSB splitting mode")
        if spec is None:
            raise ValueError("spec should be set while using kFSB splitting mode")

        candidate_relu_score_list = []
        for relu in relu_mask.keys():
            if relu_mask[relu] == 0 and relu in split_score.keys():
                candidate_relu_score_list.append((relu, split_score[relu]))
        candidate_relu_score_list = sorted(candidate_relu_score_list, key=lambda x: x[1], reverse=True)
        candidate_relus = [candidate_relu_score_list[i][0] for i in range(k)]

        candidate_relu_lbs = {}
        for relu in candidate_relus:
            cp_spec = copy.deepcopy(spec)
            split_relu_specs = cp_spec.relu_spec.split_spec(split, relu)
            child_specs = [Spec_D(cp_spec.input_spec, rs, parent=cp_spec, depth=cp_spec.depth + 1) for rs in
                           split_relu_specs]

            candidate_lb = 0
            for child_spec in child_specs:
                transformer.update_spec(child_spec.input_spec, relu_mask=child_spec.relu_spec.relu_mask)
                lb, _, _ = transformer.compute_lb(complete=True)
                if lb is not None:
                    candidate_lb = min(candidate_lb, lb)

            candidate_relu_lbs[relu] = candidate_lb
        return max(candidate_relu_lbs, key=candidate_relu_lbs.get)
    else:
        # Returning just the first un-split relu
        for relu in relu_mask.keys():
            if relu_mask[relu] == 0:
                return relu
    raise ValueError("No relu chosen!")


def branch_unsolved(spec_list, split, split_score=None, inp_template=None, args=None, net=None, transformer=None):
    new_spec_list = SpecList()
    verified_specs = SpecList()

    for spec in spec_list:
        if spec.status == Status.UNKNOWN:
            add_spec = split_spec(spec, split, split_score=split_score,
                                  inp_template=inp_template,
                                  args=args, net=net, transformer=transformer)
            new_spec_list += SpecList(add_spec)
        else:
            verified_specs.append(spec)
    return new_spec_list, verified_specs


def get_verified_nodes(spec_List):
    num_nodes = 0

    def _helper(spec):
        if (spec == 0):
            return 0

        left = _helper(spec.get_children()[0])
        right = _helper(spec.get_children()[1])
        return 1 + left + right

    for spec in spec_List:
        num_nodes += _helper(spec)
    return num_nodes


def get_verified_spec(spec):
    def _helper(spec):
        if (spec == 0):
            return 0

        left = _helper(spec.get_children()[0])
        right = _helper(spec.get_children()[1])
        return 1 + left + right

    return _helper(spec)


def get_mini_lb(root):
    if root == 0 or root is None:
        return None
    left_min = get_mini_lb(root.get_children()[0])
    right_min = get_mini_lb(root.get_children()[1])
    mini_node = min([node for node in [root, left_min, right_min] if node is not None], key=lambda x: x.lb)

    return mini_node


def count_relu_layers(model):
    relu_count = 0
    for layer in model.children():
        if isinstance(layer, nn.ReLU):
            relu_count += 1
    assert (relu_count != 0)
    return relu_count




def get_specs(dataset, spec_type=InputSpecType.LINF, eps=0.01, count=None, mode="easy"):
    if dataset == Dataset.MNIST or dataset == Dataset.CIFAR10:
        if spec_type == InputSpecType.LINF:
            if count is None:
                count = 100
            testloader = prepare_data(dataset, batch_size=count)
            inputs, labels = next(iter(testloader))
            props = specs.get_linf_spec(inputs, labels, eps, dataset)
        elif spec_type == InputSpecType.PATCH:
            if count is None:
                count = 10
            testloader = prepare_data(dataset, batch_size=count)
            inputs, labels = next(iter(testloader))
            props = specs.get_patch_specs(inputs, labels, eps, dataset, p_width=2, p_length=2)
            width = inputs.shape[2] - 2 + 1
            length = inputs.shape[3] - 2 + 1
            pos_patch_count = width * length
            specs_per_patch = pos_patch_count
            # labels = labels.unsqueeze(1).repeat(1, pos_patch_count).flatten()
        return props, inputs
    elif dataset == Dataset.ACAS:
        return specs.get_acas_props(count), None
    elif dataset == Dataset.OVAL_CIFAR:
        return get_oval_cifar_props(count, mode)
    else:
        raise ValueError("Unsupported specification dataset!")


def get_oval_cifar_props(count, mode="easy"):
    if mode == "easy":
        pdprops = 'base_easy.pkl'  # pdprops = 'base_med.pkl' or pdprops = 'base_hard.pkl'
    elif mode =="med":
        pdprops = 'base_med.pkl'
    elif mode =="hard":
        pdprops = 'base_hard.pkl'
    elif mode =="deep":
        pdprops = 'deep.pkl'
    elif mode =="wide":
        pdprops = 'wide.pkl'
    path = 'data/cifar_exp/'
    import pandas as pd
    gt_results = pd.read_pickle(path + pdprops)
    # batch ids were used for parallel processing in the original paper.
    batch_ids = gt_results.index[0:count]
    props = []
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.225, 0.225, 0.225])
    cifar_test = torchvision.datasets.CIFAR10('./data/', train=False, download=True,
                                              transform=transforms.Compose([transforms.ToTensor(), normalize]))
    for new_idx, idx in enumerate(batch_ids):
        imag_idx = gt_results.loc[idx]['Idx']
        adv_label = gt_results.loc[idx]['prop']
        eps_temp = gt_results.loc[idx]['Eps']

        ilb, iub, true_label = util.ger_property_from_id(imag_idx, eps_temp, cifar_test)
        out_constr = Constraint(OutSpecType.LOCAL_ROBUST, label=true_label, adv_label=adv_label)
        props.append(Property(ilb, iub, InputSpecType.LINF, out_constr, Dataset.CIFAR10))
    return props, None