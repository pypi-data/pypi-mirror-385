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
    'div': {'func': lambda a, b: a / (b + 1e-9), 'sym': lambda a, b: a / b, 'arity': 2},
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

    def copy(self):
        """Creates a deep copy of this node and all its descendants."""
        new_gene = Gene(self.value)
        new_gene.children = [child.copy() for child in self.children]
        return new_gene

    def __repr__(self):
        if self.children:
            return f"{self.value}({', '.join(map(str, self.children))})"
        return str(self.value)

class Individual:
    """ Represents a candidate solution (expression trees + scalar parameter values). """
    def __init__(self, func_trees, scalar_params):
        self.func_trees = func_trees      # dict: {'f1': tree, 'f2': tree}
        self.scalar_params = scalar_params # dict: {'a0': 1.2, 'a1': -0.5}
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

def generate_tree(max_depth, functions, terminals, depth=0, method='grow'):
    """ Creates a random expression tree using either 'grow' or 'full' method. """
    if depth == max_depth or (method == 'grow' and random.random() < 0.5 and depth > 0):
        val = random.choice(terminals)
        return Gene(val)
    
    op_name = random.choice(functions)
    op_arity = OPS[op_name]['arity']
    node = Gene(op_name)
    node.children = [generate_tree(max_depth, functions, terminals, depth + 1, method) for _ in range(op_arity)]
    return node

def subtree_crossover(tree1, tree2):
    """ Performs a proper subtree crossover, returning a new tree. """
    child_tree = tree1.copy()
    child_nodes = get_all_nodes(child_tree)
    parent2_nodes = get_all_nodes(tree2)
    
    crossover_point_child = random.choice(child_nodes)
    subtree_to_insert = random.choice(parent2_nodes).copy()
    
    crossover_point_child.value = subtree_to_insert.value
    crossover_point_child.children = subtree_to_insert.children
    
    return child_tree

def point_mutation(tree, functions, terminals):
    """ Randomly changes a single node in the tree (in place). """
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

def extract_parameters(equation_str):
    return sorted(set(re.findall(r'\ba\d+\b', equation_str)))

def train_GP(df, equations, params=None):
    if params is None: params = {}

    # --- GP Hyperparameters ---
    n_generations = int(params.get('n_generations', 50))
    population_size = int(params.get('population_size', 100))
    crossover_rate = float(params.get('crossover_rate', 0.2))
    gene_mutation_prob = float(params.get('gene_mutation_prob', 0.1)) # Per-gene mutation
    max_depth = int(params.get('max_depth', 7))
    tournament_size = int(params.get('tournament_size', 3))
    n_eval = int(params.get('n_eval', 200))
    
    # Scalar parameter hyperparameters
    scalar_mutation_prob = float(params.get('scalar_mutation_prob', 0.1))
    scalar_creep_rate = float(params.get('scalar_creep_rate', 0.1))
    scalar_init_range = params.get('scalar_init_range', (-2, 2))
    
    # Robustly handle library defaults
    library = params.get('library', {})
    library.setdefault('functions', ['add', 'sub', 'mul'])
    library.setdefault('terminals', ['x', -1, 1])

    # --- 1. Find Target Equation and Parse ---
    target_eq = None
    all_funcs_map = OrderedDict()
    all_params_list = []
    for eq in equations:
        funcs = parse_functions(eq)
        params_in_eq = extract_parameters(eq)
        if funcs and target_eq is None:
            target_eq = eq
            all_funcs_map = OrderedDict(funcs)
        elif funcs and target_eq is not None:
            raise ValueError("GP method currently supports only one equation with unknown components.")
        all_params_list.extend(params_in_eq)

    if not target_eq:
        raise ValueError("No equation with unknown functions (e.g., f1(x)) found.")
    
    all_params_list = sorted(list(set(all_params_list)))
    print(f"Evolving functions {list(all_funcs_map.keys())} and params {all_params_list} for equation: {target_eq}")

    # --- 2. Create Lambdified Fitness Function ---
    lhs_str, rhs_str = target_eq.split('=', 1)
    df_syms = {col: sp.Symbol(col) for col in df.columns}
    f_syms = {fname: sp.Symbol(fname) for fname in all_funcs_map}
    a_syms = {pname: sp.Symbol(pname) for pname in all_params_list}
    
    residual_expr = sp.sympify(lhs_str, locals=df_syms) - sp.sympify(rhs_str, locals={**df_syms, **a_syms, **{fname: sp.Function(fname) for fname in all_funcs_map}})
    for fname, var in all_funcs_map.items():
        residual_expr = residual_expr.subs(sp.Function(fname)(df_syms[var]), f_syms[fname])
    
    ordered_syms = sorted(df_syms.values(), key=lambda s: s.name) + \
                   sorted(f_syms.values(), key=lambda s: s.name) + \
                   sorted(a_syms.values(), key=lambda s: s.name)
    residual_lambda = sp.lambdify(ordered_syms, residual_expr, 'numpy')

    # --- 3. Initialize Population ---
    population = []
    for i in range(population_size):
        # **FIX**: Ramped half-and-half initialization for better diversity
        depth = (i % (max_depth - 1)) + 2  # Cycle depth from 2 to max_depth
        method = 'full' if (i // (max_depth-1)) % 2 == 0 else 'grow' # Alternate methods
        
        func_trees = {fname: generate_tree(depth, library['functions'], library['terminals'], method=method) for fname in all_funcs_map}
        scalar_params = {pname: random.uniform(*scalar_init_range) for pname in all_params_list}
        population.append(Individual(func_trees, scalar_params))

    # --- 4. Main Evolution Loop ---
    best_overall_individual = None
    stagnation_counter = 0
    
    for gen in range(n_generations):
        # Evaluate fitness for each individual
        for ind in population:
            data_dict = {col: df[col].values for col in df.columns}
            f_vals = {fname: ind.evaluate_tree(tree, {'x': df[all_funcs_map[fname]].values}) for fname, tree in ind.func_trees.items()}
            
            args = [data_dict[s.name] for s in sorted(df_syms.values(), key=lambda s: s.name)] + \
                   [f_vals[s.name] for s in sorted(f_syms.values(), key=lambda s: s.name)] + \
                   [ind.scalar_params.get(s.name, 0) for s in sorted(a_syms.values(), key=lambda s: s.name)]
            
            residuals = residual_lambda(*args)
            mse = np.mean(residuals**2)
            ind.fitness = 1 / (1 + mse) if np.isfinite(mse) else 0

        # Track best individual
        best_gen_individual = max(population, key=lambda x: x.fitness)
        if best_overall_individual is None or best_gen_individual.fitness > best_overall_individual.fitness:
            best_overall_individual = best_gen_individual
            stagnation_counter = 0
        else:
            stagnation_counter += 1
        
        param_str = ", ".join([f"{p}: {v:.3f}" for p, v in best_overall_individual.scalar_params.items()])
        print(f"Gen {gen+1}/{n_generations} - Best Fitness: {best_overall_individual.fitness:.4f} | Stagnation: {stagnation_counter} | Params: {param_str}")

        # --- 5. Selection and Evolution ---
        new_population = [best_overall_individual] # Elitism
        while len(new_population) < population_size:
            p1 = max(random.sample(population, tournament_size), key=lambda x: x.fitness)
            child_trees = {fname: tree.copy() for fname, tree in p1.func_trees.items()}
            child_scalars = {pname: val for pname, val in p1.scalar_params.items()}

            if random.random() < crossover_rate:
                p2 = max(random.sample(population, tournament_size), key=lambda x: x.fitness)
                # Perform crossover for ALL function trees
                for fname in child_trees:
                    child_trees[fname] = subtree_crossover(p1.func_trees[fname], p2.func_trees[fname])
                
                # Arithmetic crossover for scalars
                for pname in child_scalars:
                    child_scalars[pname] = (p1.scalar_params[pname] + p2.scalar_params[pname]) / 2.0
            
            # Apply mutation to each gene (tree) independently
            for fname in child_trees:
                if random.random() < gene_mutation_prob:
                    point_mutation(child_trees[fname], library['functions'], library['terminals'])

            # Creep mutation for scalars
            for pname in child_scalars:
                if random.random() < scalar_mutation_prob:
                    change = np.random.normal(0, scalar_creep_rate * (scalar_init_range[1] - scalar_init_range[0]))
                    child_scalars[pname] += change

            new_population.append(Individual(child_trees, child_scalars))
        population = new_population

    # --- 6. Finalize and Return Results ---
    print("\n--- Genetic Programming Results ---")
    models = {}
    final_scalars = best_overall_individual.scalar_params
    for f_name, var_name in all_funcs_map.items():
        best_tree = best_overall_individual.func_trees[f_name]
        final_expr = best_overall_individual.to_symbolic_tree(best_tree, var_name)
        try:
            final_expr = sp.simplify(final_expr)
        except: pass
        
        models[f_name] = {'expr': final_expr, 'var': var_name}
        print(f"\nFinal expression for {f_name}({var_name}):")
        sp.pprint(final_expr, use_unicode=True)
    
    print("\nFinal Optimized Scalar Parameters:")
    for pname, val in final_scalars.items():
        print(f"{pname}: {val:.6f}")

    evals = []
    for f_name, model_info in models.items():
        var_name = model_info['var']
        f_expr = model_info['expr']
        x_plot = np.linspace(df[var_name].min(), df[var_name].max(), n_eval)
        f_lambda = sp.lambdify(sp.Symbol(var_name), f_expr, 'numpy')
        y_plot = f_lambda(x_plot)
        evals.extend([x_plot, y_plot])

    return models, evals, final_scalars


