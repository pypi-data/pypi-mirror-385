import numpy as np
import re
import sympy as sp
from collections import OrderedDict
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler

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

    # --- Hyperparameters ---
    poly_order = int(params.get('poly_order', 5))
    trig_order = int(params.get('trig_order', 0))
    include_tanh = bool(params.get('include_tanh', False))
    alpha = float(params.get('alpha', 1e-2))
    scaling = bool(params.get('scaling', True))
    n_eval = int(params.get('n_eval', 200))

    # --- 1. Find the target equation with unknown functions ---
    target_eq = None
    all_funcs_map = OrderedDict()
    all_params_list = []
    
    for eq in equations:
        funcs = parse_functions(eq)
        if funcs:
            if target_eq is not None:
                raise ValueError("SparseR method currently supports only one equation with unknown functions.")
            target_eq = eq
            all_funcs_map = OrderedDict(funcs)
        all_params_list.extend(extract_parameters(eq))

    if target_eq is None:
        raise ValueError("No equation with unknown functions (e.g., f1(x)) found.")
    
    all_params_list = sorted(list(set(all_params_list)))
    print(f"Identifying unknown functions {list(all_funcs_map.keys())} in equation: {target_eq}")

    # --- 2. Symbolically define the regression target (Y) ---
    lhs_str, rhs_str = target_eq.split('=', 1)
    target_col_name = lhs_str.strip()
    if target_col_name not in df.columns:
        raise ValueError(f"LHS term '{target_col_name}' not found in dataframe columns.")
    
    # Define all symbols
    df_syms = {col: sp.Symbol(col) for col in df.columns}
    f_syms = {f_name: sp.Symbol(f_name) for f_name in all_funcs_map.keys()}
    a_syms = {p: sp.Symbol(p) for p in all_params_list}
    
    # Map function calls like f1(x2) to a simple symbol f1 for manipulation
    func_call_to_sym_map = {sp.Function(f_name)(df_syms[var_name]): f_syms[f_name] for f_name, var_name in all_funcs_map.items()}

    # Create the full symbolic expression: LHS - RHS = 0
    full_expr = sp.sympify(lhs_str, locals=df_syms) - sp.sympify(rhs_str, locals={**df_syms, **a_syms, **{fname: sp.Function(fname) for fname in all_funcs_map}})
    
    # Isolate known terms to create the regression target Y
    known_terms_expr = full_expr
    for f_call, f_sym in func_call_to_sym_map.items():
        known_terms_expr = known_terms_expr.subs(f_call, 0) # Remove function calls
        
    # Lambdify the expression for known terms to compute Y numerically
    known_terms_lambda = sp.lambdify([df_syms[c] for c in df.columns], known_terms_expr, 'numpy')
    Y = known_terms_lambda(*[df[c].values for c in df.columns])
    print(f"Regression target (Y) created from expression: {known_terms_expr}")

    # --- 3. Build the library of candidate functions (Theta matrix) ---
    library_funcs = []
    library_syms = []
    library_term_map = []
    scalers = {}

    for f_name, var_name in all_funcs_map.items():
        # The coefficient for each f(...) term in the original equation is its contribution to Theta
        # e.g., in Y = ... - f1(x2), f1's contribution must be added to the library to match Y
        f_symbol = f_syms[f_name]
        # Differentiate the expression with respect to the placeholder symbol to get its coefficient
        coeff_expr = sp.diff(full_expr.subs(func_call_to_sym_map), f_symbol)
        coeff_lambda = sp.lambdify([df_syms[c] for c in df.columns], coeff_expr, 'numpy')
        sign_coeff = coeff_lambda(*[df[c].values for c in df.columns])

        print(f"Building library for '{f_name}({var_name})' with sign coefficient: {np.mean(sign_coeff):.2f}")
        
        x_data = df[var_name].values.reshape(-1, 1)
        if scaling:
            scaler = StandardScaler()
            x_data_scaled = scaler.fit_transform(x_data).flatten()
            scalers[var_name] = scaler
        else:
            x_data_scaled = x_data.flatten()
            scalers[var_name] = None
        
        var_sym = sp.Symbol(var_name)
        # Build basis functions
        # Polynomials
        for order in range(1, poly_order + 1):
            library_funcs.append(sign_coeff * (x_data_scaled**order))
            library_syms.append(var_sym**order)
            library_term_map.append(f_name)
        # Trigonometric
        for k in range(1, trig_order + 1):
            library_funcs.append(sign_coeff * np.sin(k * x_data_scaled))
            library_syms.append(sp.sin(k * var_sym))
            library_term_map.append(f_name)
            library_funcs.append(sign_coeff * np.cos(k * x_data_scaled))
            library_syms.append(sp.cos(k * var_sym))
            library_term_map.append(f_name)
        # Tanh
        if include_tanh:
            library_funcs.append(sign_coeff * np.tanh(x_data_scaled))
            library_syms.append(sp.tanh(var_sym))
            library_term_map.append(f_name)

    Theta = np.vstack(library_funcs).T
    print(f"Constructed library Theta with {Theta.shape[1]} candidate functions.")

    # --- 4. Fit the sparse regression model ---
    model = Lasso(alpha=alpha, fit_intercept=True, max_iter=10000, tol=1e-6)
    model.fit(Theta, Y)
    
    Xi = model.coef_
    intercept = model.intercept_

    # --- 5. Decompose results ---
    print("\n--- Sparse Regression Results ---")
    models = {f_name: {'expr': 0, 'var': var_name, 'scaler': scalers.get(var_name)} for f_name, var_name in all_funcs_map.items()}
    final_scalars = {'intercept': intercept}

    for i, coef in enumerate(Xi):
        if np.abs(coef) > 1e-8:
            term_origin = library_term_map[i]
            symbolic_term = library_syms[i]
            models[term_origin]['expr'] += coef * symbolic_term

    # Print identified functions
    for f_name, model_info in models.items():
        print(f"\nFinal expression for {f_name}({model_info['var']}):")
        sp.pprint(model_info['expr'], use_unicode=True)

    # --- 6. Generate evaluation data for plotting ---
    evals = []
    for f_name, model_info in models.items():
        var_name = model_info['var']
        f_expr = model_info['expr']
        scaler = model_info['scaler']
        
        if f_expr != 0:
            var_sym = sp.Symbol(var_name)
            x_data_orig = df[var_name].values
            x_plot = np.linspace(x_data_orig.min(), x_data_orig.max(), n_eval)
            
            x_plot_scaled = x_plot
            if scaler:
                x_plot_scaled = scaler.transform(x_plot.reshape(-1, 1)).flatten()

            f_lambda = sp.lambdify(var_sym, f_expr, 'numpy')
            y_plot = f_lambda(x_plot_scaled)
            evals.extend([x_plot, y_plot])
        else:
            x_data_orig = df[var_name].values
            x_plot = np.linspace(x_data_orig.min(), x_data_orig.max(), n_eval)
            y_plot = np.zeros_like(x_plot)
            evals.extend([x_plot, y_plot])

    return models, evals, final_scalars


