import copy
import gurobipy as grb


class NN:
    layers = []

    def __init__(self, layers):
        self.layers = layers


    def get_output(self, input, from_layer = 0, to_layer = -1):
        self.bounds = []
        if to_layer == -1:
            to_layer = len(self.layers)

        out = input
        for i in range(from_layer, to_layer):
            out = self.layers[i].apply(out)
            self.bounds.append(out)
        return out

    def get_point_output(self, input, from_layer = 0, to_layer = -1):
        if to_layer == -1:
            to_layer = len(self.layers)

        out = input
        for i in range(from_layer, to_layer):
            out = self.layers[i].apply_point(out)
        return out

    def create_gurobi(self, inp, model, relu_mask):
        self.gurobi_vars = []
        out = [inp[0], inp[1]]
        for i in range(0, len(self.layers)):
            if type(self.layers[i]) == ReluTransform:
                out = self.layers[i].apply_gurobi(out, model, self.bounds, i, relu_mask=relu_mask)
            else:
                out = self.layers[i].apply_gurobi(out, model, self.bounds, i)
            self.gurobi_vars.append(out)
        return out


class ReluTransform:
    def __init__(self):
        # DO nothing
        return

    def apply(self, input):
        out = []
        for i in range(len(input)):
            out.append((max(input[i][0], 0), max(input[i][1], 0)))
        return out

    def apply_gurobi(self, input, model, bounds, layer, relu_mask=None):
        out = []
        for i in range(len(input)):
            v = model.addVar(obj=0, vtype=grb.GRB.CONTINUOUS, lb=bounds[layer][i][0], ub=bounds[layer][i][1])

            pre_lb, pre_ub = bounds[layer-1][i][0], bounds[layer-1][i][1]

            relu_decision = 0
            if relu_mask is not None and (layer, i) in relu_mask.keys():
                relu_decision = relu_mask[(layer, i)]

            if (pre_lb >= 0 and pre_ub >= 0) or relu_decision == 1:
                model.addConstr(v == input[i])
                model.addConstr(input[i] >= 0)
            elif (pre_lb <= 0 and pre_ub <= 0) or relu_decision == -1:
                model.addConstr(v == 0)
                model.addConstr(input[i] <= 0)
            elif pre_lb <= 0 and pre_ub >= 0:
                slope = pre_ub / (pre_ub - pre_lb)
                bias = - pre_lb * slope
                model.addConstr(v <= slope * input[i] + bias)
                model.addConstr(v >= input[i])
                # model.addConstr(v >= 0)
            out.append(v)
        return out

    def apply_point(self, input):
        # print(input)
        out = []
        for i in range(len(input)):
            out.append(max(input[i], 0))
        return out


class AffineTransform:
    W = []

    def __init__(self, mat, bias=[0, 0]):
        self.W = mat
        self.bias = bias

    def apply(self, input):
        out = []
        for i in range(len(self.W)):
            val1 = 0
            val2 = 0
            for j in range(len(self.W[i])):
                add1 = self.W[i][j]*input[j][0]
                add2 = self.W[i][j]*input[j][1]
                val1 += min(add1, add2)
                val2 += max(add1, add2)
            out.append((min(val1, val2) + self.bias[i], max(val1, val2) + self.bias[i]))

        return out

    def apply_gurobi(self, input, model, bounds, layer):
        out = []
        for i in range(len(self.W)):
            v = model.addVar(obj=0, vtype=grb.GRB.CONTINUOUS, lb=bounds[layer][i][0], ub=bounds[layer][i][1])
            rhs = 0
            for j in range(len(self.W[i])):
                rhs += self.W[i][j]*input[j]
            out.append(v)
            model.addConstr(v == rhs)
        return out

    def apply_point(self, input):
        out = []
        for i in range(len(self.W)):
            val1 = 0
            for j in range(len(self.W[i])):
                add1 = self.W[i][j]*input[j]
                val1 += add1
            out.append(val1 + self.bias[i])

        return out


class Spec():
    def __init__(self, input_spec, depth = 0, relu_spec=None, parent=None, status=None):
        self.input_spec = input_spec
        self.relu_spec = relu_spec
        self.children = []
        self.status = status
        self.lb = 0
        self.chosen_split = None
        self.parent = parent
        self.depth = depth

def olive_split(relu_mask, relu_id, spec):
    rm1 = copy.deepcopy(relu_mask)
    rm2 = copy.deepcopy(relu_mask)

    rm1[relu_id] = -1
    rm2[relu_id] = 1
    
    child_specs = [Spec(spec.input_spec, parent=spec, depth=spec.depth + 1, relu_spec=rm1), Spec(spec.input_spec, parent=spec, depth=spec.depth + 1, relu_spec=rm2)]
    spec.children += child_specs
    return child_specs

# predefined order as H 
def chooseRelu(rm, order=None):
    if order is None:
        order = [ (1,1), (1,0), (3, 0) ]
        # order = [ (3, 1), (3, 0), (1,0), (1, 1)]

    for r in order:
        if r not in rm.keys():
            return r

def olive_subproblem_order(min_lb, subproblems):
    max_reward = 0
    max_item = None
    max_index = None
    for index in range(len(subproblems)):
        i = subproblems[index]
        reward = 0.5*i.depth/3 + 0.5*i.lb/min_lb
        if reward > max_reward:
                max_item = i
                max_index = index
                max_reward = reward
    return max_item, max_index

def bab_oliva(N, active=None, order=None):
    min_lb = 0
    psi = -2.5
    # Prove (cy - psi >= 0)
    input = [(0, 1), (0, 1)]
    if active is None:
        spec = Spec(input_spec = input, relu_spec={})
        cy, x1, x2 = gurobi_bound(N, spec.relu_spec)
        print("cur_spec: ", cy-psi, spec.relu_spec)
        if cy < psi and N.get_point_output([x1,x2])[0] < psi:
            print("find a counterexample", x1, x2, N.get_point_output([x1,x2]) )
            return
        spec.lb = cy - psi
        # if min_lb> spec.lb:
        min_lb = spec.lb
        assert(min_lb < 0)
        active  = []
        active.append(spec)
    else:
        active = active.get_childNodes()

    
    node_cnt = 1
    while len(active) != 0:
        # node_cnt += len(active)
        spec, index = olive_subproblem_order(min_lb, active)
        relu = chooseRelu(spec.relu_spec, order=order)
        specs = olive_split(spec.relu_spec, relu, spec)
        for child in specs:
            cy, x1, x2 = gurobi_bound(N, child.relu_spec)
            node_cnt += 1
            print("cur_spec: ", cy-psi, child.relu_spec)
            if cy < psi and N.get_point_output([x1,x2])[0] < psi:  # real counterexample
                print("find a counterexample", x1, x2, N.get_point_output([x1,x2]) )
                print("Total analyzer calls: ", node_cnt)
                return
            elif cy < psi and N.get_point_output([x1,x2])[0] >= psi:   # spurious
                child.lb = cy - psi
                active.append(child)
        active.pop(index)

    print("Total analyzer calls: ", node_cnt)
    return 

def bab(N, active=None, order=None):
   
    input = [(0, 1), (0, 1)]
    if active is None:
        spec = Spec(input_spec = input, relu_spec={})
        active  = []
        active.append(spec)
    else:
        active = active.get_childNodes()
    psi = -2.5
    # Prove (cy - psi >= 0)
    node_cnt = 0
    while len(active) != 0:
        node_cnt += len(active)
        new_active = []
        for spec in active:
            cy, x1, x2 = gurobi_bound(N, spec.relu_spec)
            print("cur_spec: ", cy-psi, spec.relu_spec)
            if cy < psi and N.get_point_output([x1,x2])[0] >= psi:
                relu = chooseRelu(spec.relu_spec, order=order)
                specs = olive_split(spec.relu_spec, relu, spec)
                new_active = new_active + specs
            elif cy < psi and N.get_point_output([x1,x2])[0] < psi:
                print("find a counterexample", x1, x2, N.get_point_output([x1,x2]) )
                print("Total analyzer calls: ", node_cnt)
                return
        active = new_active

    print("Total analyzer calls: ", node_cnt)
    return 


def gurobi_bound(N, relu_mask):
    # Input specification
    input = [(0, 1), (0, 1)]
    # Output from network (grb placeholder)
    output = N.get_output(input)
    # Use gurobi to get better bounds for the output now
    # Set the Gurobi model
    model = grb.Model()
    model.setParam('OutputFlag', False)
    x1 = model.addVar(obj=0, vtype=grb.GRB.CONTINUOUS, name=f'x1', lb=input[0][0], ub=input[0][1])
    x2 = model.addVar(obj=0, vtype=grb.GRB.CONTINUOUS, name=f'x2', lb=input[1][0], ub=input[1][1])
    grb_input = [x1, x2]
    model.update()
    grb_out = N.create_gurobi(grb_input, model, relu_mask)
    model.setObjective(grb_out[0], grb.GRB.MINIMIZE)
    model.optimize()
    return grb_out[0].X, model.getVarByName("x1"). X,model.getVarByName("x2").X


if __name__ == "__main__":
    
    N =  NN([AffineTransform([[1.88, -3], [1, -2]]), ReluTransform(), AffineTransform([[2, -2], [0.6, -3]]),
            ReluTransform(), AffineTransform([[-1.61, 0.505]])])
    print("===========Performing Traditional BaB ===========\n\n")
    _ = bab(N)
    
    print("===========Performing Oliva ===========\n")
    _ = bab_oliva(N)

