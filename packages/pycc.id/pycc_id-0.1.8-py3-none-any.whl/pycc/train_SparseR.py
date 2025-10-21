import numpy as np
import re
import sympy as sp
from collections import OrderedDict
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler
from itertools import product

def parse_functions(equation_str):
    """
    Parses an equation string to find all function calls like f1(x), f2(y).
    Returns a list of unique (function_name, variable_name) tuples.
    """
    pattern = r'(f\d+)\((\w+)\)'
    all_funcs = re.findall(pattern, equation_str)
    unique_funcs = list(OrderedDict.fromkeys(all_funcs))
    return unique_funcs

def extract_parameters(equation_str):
    """Parses for scalar parameters like a0, a1, etc."""
    return sorted(set(re.findall(r'\ba\d+\b', equation_str)))

def train_SparseR(df, equations, params=None):
    """
    Identifies unknown functions and parameters in an ODE using sparse regression (LASSO).
    The equation with unknown terms should be in the form: derivative = expression.
    """
    if params is None:
        params = {}

    # --- Hyperparameters for the sparse regression ---
    poly_order = int(params.get('poly_order', 5))
    trig_order = int(params.get('trig_order', 0))
    include_tanh = bool(params.get('include_tanh', False))
    alpha = float(params.get('alpha', 1e-2))
    scaling = bool(params.get('scaling', True))
    n_eval = int(params.get('n_eval', 200))

    # --- 1. Find the target equation with unknown functions ---
    target_eq = None
    all_funcs = []
    for eq in equations:
        funcs = parse_functions(eq)
        if funcs:
            if target_eq is not None:
                raise ValueError("SparseR method currently supports only one equation with unknown functions.")
            target_eq = eq
            all_funcs = funcs
    
    if target_eq is None:
        raise ValueError("No equation with unknown functions (e.g., f1(x)) found.")

    func_map = OrderedDict(all_funcs)
    print(f"Identifying unknown functions {list(func_map.keys())} in equation: {target_eq}")

    # --- 2. Define regression target (Y) and library sources ---
    lhs_str, rhs_str = target_eq.split('=', 1)
    target_col_name = lhs_str.strip()
    if target_col_name not in df.columns:
        raise ValueError(f"LHS term '{target_col_name}' not found in dataframe columns.")
    
    Y = df[target_col_name].values
    print(f"Regression target (Y) set to column: {target_col_name}")

    # --- 3. Build the library of candidate functions (Theta matrix) ---
    library_funcs = []      # List of numerical columns
    library_syms = []       # List of symbolic expressions for each column
    library_term_map = []   # Maps each column to its origin (e.g., 'f1', 'F_ext', 'a1*x1')

    # --- FIX: Create symbols correctly for sympy parsing ---
    # Create symbols for dataframe columns, which are known variables
    df_syms = {col: sp.Symbol(col) for col in df.columns}
    # Create Function classes (e.g., f1) for the parser to recognize
    f_classes = {f_name: sp.Function(f_name) for f_name in func_map.keys()}
    # Create symbols for scalar parameters (e.g., a1)
    a_syms = {p: sp.Symbol(p) for p in extract_parameters(rhs_str)}
    
    # Sympy will parse the string, using the locals dict to understand what each name means
    rhs_expr = sp.sympify(rhs_str, locals={**df_syms, **f_classes, **a_syms})
    
    # Create specific function call instances (e.g., f1(x2)) for matching terms later
    f_instances = {f_name: sp.Function(f_name)(df_syms[var_name]) for f_name, var_name in func_map.items()}
    
    # Process each term on the RHS of the equation
    for term in sp.Add.make_args(rhs_expr):
        
        # Case 1: The term is an unknown function call, e.g., -f1(x2)
        is_func_term = False
        for f_name, var_name in func_map.items():
            # Check if the function instance (e.g., f1(x2)) is in the current term
            if f_instances[f_name] in term.free_symbols:
                sign_coeff = term.as_coeff_Mul(f_instances[f_name])[0]
                var_sym = sp.Symbol(var_name)
                
                print(f"Building library for function '{f_name}' with variable '{var_name}'...")
                
                # Get numerical data and scale it if needed
                x_data = df[var_name].values.reshape(-1, 1)
                scaler = StandardScaler() if scaling else None
                x_data_scaled = scaler.fit_transform(x_data).flatten() if scaling else x_data.flatten()

                # Build basis functions for this variable
                # Polynomials
                for order in range(1, poly_order + 1):
                    library_funcs.append(sign_coeff * (x_data_scaled**order))
                    library_syms.append(sign_coeff * (var_sym**order))
                    library_term_map.append(f_name)
                # Trigonometric
                for k in range(1, trig_order + 1):
                    library_funcs.append(sign_coeff * np.sin(k * x_data_scaled))
                    library_syms.append(sign_coeff * sp.sin(k * var_sym))
                    library_term_map.append(f_name)
                    library_funcs.append(sign_coeff * np.cos(k * x_data_scaled))
                    library_syms.append(sign_coeff * sp.cos(k * var_sym))
                    library_term_map.append(f_name)
                # Tanh
                if include_tanh:
                    library_funcs.append(sign_coeff * np.tanh(x_data_scaled))
                    library_syms.append(sign_coeff * sp.tanh(var_sym))
                    library_term_map.append(f_name)
                
                is_func_term = True
                break
        if is_func_term:
            continue

        # Case 2: The term is a known variable or parameter, e.g., F_ext or -a1*x1
        # Lambdify the expression to get its numerical values
        term_lambda = sp.lambdify([df_syms[c] for c in df.columns], term, 'numpy')
        term_values = term_lambda(*[df[c].values for c in df.columns])
        
        library_funcs.append(term_values)
        library_syms.append(term)
        library_term_map.append(str(term))

    Theta = np.vstack(library_funcs).T
    print(f"Constructed library Theta with {Theta.shape[1]} candidate functions.")

    # --- 4. Fit the sparse regression model ---
    model = Lasso(alpha=alpha, fit_intercept=True, max_iter=10000, tol=1e-6)
    model.fit(Theta, Y)
    
    Xi = model.coef_
    intercept = model.intercept_

    # --- 5. Decompose results and reconstruct symbolic expressions ---
    print("\n--- Sparse Regression Results ---")
    models = {f_name: {'expr': 0, 'var': var_name} for f_name, var_name in func_map.items()}
    final_scalars = {}
    
    # Add intercept to the expression
    full_identified_rhs = sp.Float(intercept)
    
    for i, coef in enumerate(Xi):
        if np.abs(coef) > 1e-8: # Thresholding
            term_origin = library_term_map[i]
            symbolic_term = library_syms[i]
            
            # Re-scale coefficient back if it was part of a function library
            if term_origin in models:
                var_name = models[term_origin]['var']
                # This part is complex; for now, we present the scaled result.
                # A full un-scaling would require substituting x with (x-mean)/std.
                pass

            # Add to the full expression
            full_identified_rhs += coef * symbolic_term
            
            # Decompose into individual functions
            if term_origin in models:
                models[term_origin]['expr'] += coef * symbolic_term

    print(f"Identified full RHS expression for {target_col_name}:")
    sp.pprint(full_identified_rhs, use_unicode=True)

    for f_name, model_info in models.items():
        print(f"\nFinal expression for {f_name}({model_info['var']}):")
        sp.pprint(model_info['expr'], use_unicode=True)

    # --- 6. Generate evaluation data for plotting ---
    evals = []
    for f_name, model_info in models.items():
        var_name = model_info['var']
        f_expr = model_info['expr']
        
        if f_expr != 0:
            var_sym = sp.Symbol(var_name)
            x_data_orig = df[var_name].values
            x_plot = np.linspace(x_data_orig.min(), x_data_orig.max(), n_eval)
            
            f_lambda = sp.lambdify(var_sym, f_expr, 'numpy')
            y_plot = f_lambda(x_plot)
            evals.extend([x_plot, y_plot])
        else: # Handle case where function is identified as zero
            var_name = model_info['var']
            x_data_orig = df[var_name].values
            x_plot = np.linspace(x_data_orig.min(), x_data_orig.max(), n_eval)
            y_plot = np.zeros_like(x_plot)
            evals.extend([x_plot, y_plot])

    return models, evals, final_scalars



