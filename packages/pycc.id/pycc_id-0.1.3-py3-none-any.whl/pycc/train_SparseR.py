import numpy as np
import re
import sympy as sp
from collections import OrderedDict
from sklearn.linear_model import Lasso, LassoCV
from sklearn.preprocessing import StandardScaler
from itertools import combinations_with_replacement

def parse_functions(equation_str):
    """
    Parses an equation string to find all function calls like f1(x), f2(y).
    Returns a list of unique (function_name, variable_name) tuples.
    """
    pattern = r'(f\d+)\((\w+)\)'
    all_funcs = re.findall(pattern, equation_str)
    unique_funcs = list(OrderedDict.fromkeys(all_funcs))
    return unique_funcs

def train_SparseR(df, equations, params=None):
    """
    Identifies unknown functions in a system of ODEs using sparse regression (LASSO).
    """
    if params is None:
        params = {}

    # --- Hyperparameters for the sparse regression ---
    poly_order = int(params.get('poly_order', 5))
    use_trig = bool(params.get('include_trig', False))
    trig_freqs = params.get('trig_freqs', [1.0])
    alpha = float(params.get('alpha', 1e-2)) # LASSO regularization parameter
    scaling = bool(params.get('scaling', True))
    n_eval = int(params.get('n_eval', 200))

    # --- 1. Isolate the equation to identify ---
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
    func_names = list(func_map.keys())
    var_names = list(func_map.values())
    
    print(f"Identifying unknown functions {func_names} in equation: {target_eq}")

    # --- 2. Symbolically parse the equation to define the regression target ---
    lhs_str, rhs_str = target_eq.split('=', 1)
    
    # Create symbolic variables for dataframe columns and functions
    df_syms = {col: sp.Symbol(col) for col in df.columns}
    f_syms = {f_name: sp.Function(f_name)(sp.Symbol(var_name)) for f_name, var_name in func_map.items()}
    
    # Sympify expressions
    lhs_expr = sp.sympify(lhs_str, locals=df_syms)
    rhs_expr = sp.sympify(rhs_str, locals={**df_syms, **f_syms})

    # Isolate the unknown terms on one side and knowns on the other
    # We are solving for: sum_of_funcs = known_expr
    known_expr = lhs_expr
    sum_of_funcs = 0
    for term in sp.Add.make_args(rhs_expr):
        if any(f in term.free_symbols for f in f_syms.values()):
            sum_of_funcs -= term
        else:
            known_expr -= term
            
    # --- 3. Compute the numerical target vector Y from the data ---
    target_lambda = sp.lambdify(list(df_syms.values()), known_expr, 'numpy')
    Y = target_lambda(**{col: df[col].values for col in df.columns})
    
    print(f"Regression target (Y) created from expression: {known_expr}")

    # --- 4. Build the library of candidate functions (Theta matrix) ---
    library_funcs = []
    library_syms = []
    
    # Get data and symbols for variables used in the unknown functions
    X_data = df[var_names].values
    X_syms = [sp.Symbol(var) for var in var_names]

    # Apply scaling if enabled
    if scaling:
        scaler = StandardScaler()
        X_data_scaled = scaler.fit_transform(X_data)
    else:
        X_data_scaled = X_data

    # a) Polynomial terms
    for order in range(1, poly_order + 1):
        for combo_indices in combinations_with_replacement(range(len(var_names)), order):
            # Numerical column
            col = np.prod([X_data_scaled[:, i] for i in combo_indices], axis=0)
            library_funcs.append(col)
            # Symbolic representation
            sym = sp.prod([X_syms[i] for i in combo_indices])
            library_syms.append(sym)

    # b) Trigonometric terms
    if use_trig:
        for i, var_sym in enumerate(X_syms):
            for freq in trig_freqs:
                # Sine
                library_funcs.append(np.sin(freq * X_data_scaled[:, i]))
                library_syms.append(sp.sin(freq * var_sym))
                # Cosine
                library_funcs.append(np.cos(freq * X_data_scaled[:, i]))
                library_syms.append(sp.cos(freq * var_sym))

    Theta = np.vstack(library_funcs).T
    print(f"Constructed library Theta with {Theta.shape[1]} candidate functions.")

    # --- 5. Fit the sparse regression model ---
    # Using LassoCV to find the best alpha can be useful, but for now, we use the provided alpha.
    model = Lasso(alpha=alpha, fit_intercept=True, max_iter=10000, tol=1e-6)
    model.fit(Theta, Y)
    
    Xi = model.coef_
    intercept = model.intercept_

    # --- 6. Reconstruct the identified symbolic expression ---
    identified_sum_of_funcs = sp.Float(intercept)
    for i, coef in enumerate(Xi):
        if np.abs(coef) > 1e-10: # Thresholding to ignore negligible coefficients
            identified_sum_of_funcs += coef * library_syms[i]

    print("\n--- Sparse Regression Results ---")
    print(f"Identified expression for ({sum_of_funcs}):")
    sp.pprint(identified_sum_of_funcs, use_unicode=True)

    # --- 7. Decompose the combined expression into individual functions ---
    # This assumes f_i(0) = 0, which is a common physical constraint.
    models = {}
    for f_name, var_name in func_map.items():
        var_sym = sp.Symbol(var_name)
        
        # Create a substitution dict to set all other variables to zero
        subs_dict = {s: 0 for s in X_syms if s != var_sym}
        
        # Isolate the function by substituting other variables
        # The sign is flipped because we identified `sum_of_funcs` which was e.g., -f1-f2
        f_expr_unscaled = -identified_sum_of_funcs.subs(subs_dict)
        
        # Create a model dictionary for each identified function
        models[f_name] = {
            'var': var_name,
            'expr_unscaled': f_expr_unscaled,
            'scaler': scaler if scaling else None
        }

    # --- 8. Generate evaluation data for plotting ---
    evals = []
    for f_name, model in models.items():
        var_name = model['var']
        var_sym = sp.Symbol(var_name)
        
        # Create a plotting range based on the original data
        x_data_orig = df[var_name].values
        x_plot = np.linspace(x_data_orig.min(), x_data_orig.max(), n_eval)
        
        # Scale the plotting data if necessary
        if scaling:
            var_idx = var_names.index(var_name)
            mean = model['scaler'].mean_[var_idx]
            scale = model['scaler'].scale_[var_idx]
            x_plot_scaled = (x_plot - mean) / scale
        else:
            x_plot_scaled = x_plot
            
        # Lambdify and evaluate the identified expression
        f_lambda = sp.lambdify(var_sym, model['expr_unscaled'], 'numpy')
        y_plot = f_lambda(x_plot_scaled)
        
        evals.extend([x_plot, y_plot])
        
        print(f"\nFinal expression for {f_name}({var_name}):")
        sp.pprint(model['expr_unscaled'], use_unicode=True)

    # Sparse regression typically doesn't identify isolated scalar parameters like 'a1'
    final_scalars = {}

    return models, evals, final_scalars

