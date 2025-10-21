import numpy as np
import random
import re
import sympy as sp
from collections import OrderedDict
import operator

# --- Symbolic and Numerical Operations ---
OPS = {
    'add': {'func': operator.add, 'sym': sp.Add, 'arity': 2},
    'sub': {'func': operator.sub, 'sym': lambda a, b: a - b, 'arity': 2},
    'mul': {'func': operator.mul, 'sym': sp.Mul, 'arity': 2},
    'div': {'func': lambda a, b: a / (b + 1e-6), 'sym': lambda a, b: a / b, 'arity': 2},
    'sin': {'func': np.sin, 'sym': sp.sin, 'arity': 1},
    'cos': {'func': np.cos, 'sym': sp.cos, 'arity': 1},
    'exp': {'func': np.exp, 'sym': sp.exp, 'arity': 1},
    'tanh': {'func': np.tanh, 'sym': sp.tanh, 'arity': 1},
}

# --- Core Genetic Programming Classes ---

class Gene:
    """ A node in the expression tree. """
    def __init__(self, value):
        self.value = value
        self.children = []

    def __repr__(self):
        if self.children:
            return f"{self.value}({', '.join(map(str, self.children))})"
        return str(self.value)

class Individual:
    """ Represents a candidate solution (a set of expression trees for f1, f2, etc.). """
    def __init__(self, func_trees):
        self.func_trees = func_trees  # dict: {'f1': tree, 'f2': tree}
        self.fitness = -np.inf

    def evaluate_tree(self, tree, data_dict):
        """ Numerically evaluate a single expression tree. """
        if not tree.children:
            val = tree.value
            if isinstance(val, str) and val in data_dict:
                return data_dict[val]
            return float(val)
        
        op = OPS[tree.value]['func']
        child_values = [self.evaluate_tree(child, data_dict) for child in tree.children]
        return op(*child_values)
        
    def to_symbolic_tree(self, tree, var_name):
        """ Convert a single expression tree to a sympy expression. """
        if not tree.children:
            val = tree.value
            return sp.Symbol(var_name) if val == 'x' else sp.sympify(val)
            
        op_sym = OPS[tree.value]['sym']
        child_syms = [self.to_symbolic_tree(child, var_name) for child in tree.children]
        return op_sym(*child_syms)

# --- GP Helper Functions ---

def generate_tree(max_depth, functions, terminals, depth=0):
    """ Creates a random expression tree. """
    if depth == max_depth or (depth > 0 and random.random() < 0.4): # Grow method
        val = random.choice(terminals)
        return Gene(val)
    
    op_name = random.choice(functions)
    op_arity = OPS[op_name]['arity']
    node = Gene(op_name)
    node.children = [generate_tree(max_depth, functions, terminals, depth + 1) for _ in range(op_arity)]
    return node

def subtree_crossover(tree1, tree2):
    """ Swaps a random subtree between two parent trees. """
    t1, t2 = tree1, tree2 # No deepcopy needed if we replace nodes
    
    # Select random node from tree1
    nodes1 = get_all_nodes(t1)
    node1_to_replace = random.choice(nodes1)
    
    # Select random node from tree2
    nodes2 = get_all_nodes(t2)
    node2_subtree = random.choice(nodes2)

    # Replace (by changing value and children)
    node1_to_replace.value = node2_subtree.value
    node1_to_replace.children = node2_subtree.children
    return t1

def point_mutation(tree, functions, terminals):
    """ Randomly changes a single node in the tree. """
    nodes = get_all_nodes(tree)
    node_to_mutate = random.choice(nodes)
    
    if node_to_mutate.children: # It's a function node
        new_op = random.choice(functions)
        if OPS[new_op]['arity'] == len(node_to_mutate.children):
            node_to_mutate.value = new_op
    else: # It's a terminal node
        node_to_mutate.value = random.choice(terminals)
    return tree

def get_all_nodes(tree, nodes_list=None):
    if nodes_list is None: nodes_list = []
    nodes_list.append(tree)
    for child in tree.children:
        get_all_nodes(child, nodes_list)
    return nodes_list

# --- Main Training Function ---
def parse_functions(equation_str):
    pattern = r'(f\d+)\((\w+)\)'
    return list(OrderedDict.fromkeys(re.findall(pattern, equation_str)))

def train_GP(df, equations, params=None):
    if params is None: params = {}

    # --- GP Hyperparameters ---
    n_generations = int(params.get('n_generations', 50))
    population_size = int(params.get('population_size', 100))
    crossover_rate = float(params.get('crossover_rate', 0.7))
    mutation_rate = float(params.get('mutation_rate', 0.2))
    max_depth = int(params.get('max_depth', 4))
    tournament_size = int(params.get('tournament_size', 3))
    library = params.get('library', {'functions': ['add', 'sub', 'mul'], 'terminals': ['x', -1, 1]})
    n_eval = int(params.get('n_eval', 200))
    
    # --- 1. Find Target Equation and Parse ---
    target_eq = None
    all_funcs_map = OrderedDict()
    for eq in equations:
        funcs = parse_functions(eq)
        if funcs:
            if target_eq is not None:
                raise ValueError("GP method currently supports only one equation with unknown functions.")
            target_eq = eq
            all_funcs_map = OrderedDict(funcs)

    if not target_eq:
        raise ValueError("No equation with unknown functions (e.g., f1(x)) found.")
        
    print(f"Evolving functions {list(all_funcs_map.keys())} for equation: {target_eq}")

    # --- 2. Create Lambdified Fitness Function ---
    lhs_str, rhs_str = target_eq.split('=', 1)
    df_syms = {col: sp.Symbol(col) for col in df.columns}
    f_syms = {fname: sp.Symbol(fname) for fname in all_funcs_map}
    
    residual_expr = sp.sympify(lhs_str, locals=df_syms) - sp.sympify(rhs_str, locals={**df_syms, **{fname: sp.Function(fname) for fname in all_funcs_map}})
    # Substitute function calls f1(x1) with placeholders f1
    for fname, var in all_funcs_map.items():
        residual_expr = residual_expr.subs(sp.Function(fname)(df_syms[var]), f_syms[fname])
    
    ordered_syms = sorted(df_syms.values(), key=lambda s: s.name) + sorted(f_syms.values(), key=lambda s: s.name)
    residual_lambda = sp.lambdify(ordered_syms, residual_expr, 'numpy')

    # --- 3. Initialize Population ---
    population = []
    for _ in range(population_size):
        func_trees = {fname: generate_tree(max_depth, library['functions'], library['terminals']) for fname in all_funcs_map}
        population.append(Individual(func_trees))

    # --- 4. Main Evolution Loop ---
    best_overall_individual = None
    
    for gen in range(n_generations):
        # Evaluate fitness for each individual
        for ind in population:
            data_dict = {col: df[col].values for col in df.columns}
            f_vals = {fname: ind.evaluate_tree(tree, {'x': df[var_name].values}) for fname, (tree, var_name) in zip(ind.func_trees, zip(ind.func_trees.values(), all_funcs_map.values()))}
            
            args = [data_dict[s.name] for s in sorted(df_syms.values(), key=lambda s: s.name)] + \
                   [f_vals[s.name] for s in sorted(f_syms.values(), key=lambda s: s.name)]
            
            residuals = residual_lambda(*args)
            mse = np.mean(residuals**2)
            ind.fitness = 1 / (1 + mse) # Higher is better

        # Track best individual
        best_gen_individual = max(population, key=lambda x: x.fitness)
        if best_overall_individual is None or best_gen_individual.fitness > best_overall_individual.fitness:
            best_overall_individual = best_gen_individual
        
        print(f"Generation {gen+1}/{n_generations} - Best Fitness: {best_overall_individual.fitness:.4f}")

        # --- 5. Selection and Evolution ---
        new_population = [best_overall_individual] # Elitism
        while len(new_population) < population_size:
            # Tournament Selection
            p1 = max(random.sample(population, tournament_size), key=lambda x: x.fitness)
            
            if random.random() < crossover_rate:
                p2 = max(random.sample(population, tournament_size), key=lambda x: x.fitness)
                new_trees = {}
                for fname in p1.func_trees:
                     new_trees[fname] = subtree_crossover(p1.func_trees[fname], p2.func_trees[fname])
                new_ind = Individual(new_trees)
            elif random.random() < mutation_rate:
                mutated_trees = {fname: point_mutation(tree, library['functions'], library['terminals']) for fname, tree in p1.func_trees.items()}
                new_ind = Individual(mutated_trees)
            else: # Reproduction
                new_ind = p1
            
            new_population.append(new_ind)
        population = new_population

    # --- 6. Finalize and Return Results ---
    print("\n--- Genetic Programming Results ---")
    models = {}
    for f_name, var_name in all_funcs_map.items():
        best_tree = best_overall_individual.func_trees[f_name]
        final_expr = best_overall_individual.to_symbolic_tree(best_tree, var_name)
        try: # Simplify the final expression
            final_expr = sp.simplify(final_expr)
        except: pass
        
        models[f_name] = {'expr': final_expr, 'var': var_name}
        print(f"\nFinal expression for {f_name}({var_name}):")
        sp.pprint(final_expr, use_unicode=True)
    
    evals = []
    for f_name, model_info in models.items():
        var_name = model_info['var']
        f_expr = model_info['expr']
        x_plot = np.linspace(df[var_name].min(), df[var_name].max(), n_eval)
        f_lambda = sp.lambdify(sp.Symbol(var_name), f_expr, 'numpy')
        y_plot = f_lambda(x_plot)
        evals.extend([x_plot, y_plot])

    return models, evals, {}

