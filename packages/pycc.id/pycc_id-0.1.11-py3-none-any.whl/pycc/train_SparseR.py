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

    # --- 1. Find the target equation and parse all components ---
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

    # --- 2. Robustly and Symbolically Define the Regression Target (Y) ---
    lhs_str, rhs_str = target_eq.split('=', 1)
    
    # Define all symbols
    df_syms = {col: sp.Symbol(col) for col in df.columns}
    a_syms = {p: sp.Symbol(p) for p in all_params_list}
    # Important: define f symbols as classes for sympy to parse f1(x2) correctly
    f_classes = {f_name: sp.Function(f_name) for f_name in all_funcs_map.keys()}
    
    # Create the full symbolic expression: LHS - RHS = 0
    full_expr = sp.sympify(lhs_str, locals=df_syms) - sp.sympify(rhs_str, locals={**df_syms, **a_syms, **f_classes})
    
    # Separate the expression into known and unknown parts
    known_terms_expr = sp.S(0)
    unknown_terms_expr = sp.S(0)

    for term in sp.Add.make_args(full_expr):
        has_unknown_func = any(f.name in all_funcs_map for f in term.atoms(sp.Function))
        if has_unknown_func:
            unknown_terms_expr += term
        else:
            known_terms_expr += term

    # The regression is Y = Theta * Xi, where Theta * Xi models the unknown part.
    # From `known + unknown = 0`, we get `unknown = -known`.
    # So, our regression target Y is the numerical evaluation of `-known_terms_expr`.
    Y_expr = -known_terms_expr
    Y_lambda = sp.lambdify(list(df_syms.values()), Y_expr, 'numpy')
    Y = Y_lambda(*[df[col].values for col in df_syms.keys()])
    
    print(f"Regression target Y defined as: {Y_expr}")
    print(f"Library Theta will be built to model: {unknown_terms_expr}")

    # --- 3. Build the Library of Candidate Functions (Theta) ---
    library_funcs = []
    library_syms = []
    library_term_map = []
    scalers = {}

    for f_name, var_name in all_funcs_map.items():
        f_instance = f_classes[f_name](df_syms[var_name])
        
        # Determine the sign/coefficient of this function in the unknown expression
        sign_expr = sp.diff(unknown_terms_expr, f_instance)
        if not sign_expr.is_constant():
             raise ValueError(f"Coefficient of function '{f_name}' is not constant. Check your equation.")
        sign_coeff = float(sign_expr)

        print(f"Building library for '{f_name}({var_name})' with combined coefficient: {sign_coeff:.2f}")
        
        x_data = df[var_name].values.reshape(-1, 1)
        if scaling:
            scaler = StandardScaler()
            x_data_scaled = scaler.fit_transform(x_data).flatten()
            scalers[var_name] = scaler
        else:
            x_data_scaled = x_data.flatten()
            scalers[var_name] = None
        
        var_sym = sp.Symbol(var_name)
        # Build basis functions, multiplied by the function's coefficient
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

    # --- 4. Fit the Sparse Regression Model ---
    model = Lasso(alpha=alpha, fit_intercept=True, max_iter=10000, tol=1e-6)
    model.fit(Theta, Y)
    
    Xi = model.coef_
    intercept = model.intercept_

    # --- 5. Decompose Results ---
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

    # --- 6. Generate Evaluation Data for Plotting ---
    evals = []
    for f_name, model_info in models.items():
        var_name = model_info['var']
        f_expr = model_info['expr']
        scaler = model_info['scaler']
        
        # Check if the expression is non-trivial before plotting
        if f_expr.free_symbols:
            var_sym = sp.Symbol(var_name)
            x_data_orig = df[var_name].values
            x_plot = np.linspace(x_data_orig.min(), x_data_orig.max(), n_eval)
            
            x_plot_scaled = x_plot
            if scaler:
                x_plot_scaled = scaler.transform(x_plot.reshape(-1, 1)).flatten()

            f_lambda = sp.lambdify(var_sym, f_expr, 'numpy')
            y_plot = f_lambda(x_plot_scaled)
            evals.extend([x_plot, y_plot])
        else: # Handle cases where a function is identified as zero or a constant
            x_data_orig = df[var_name].values
            x_plot = np.linspace(x_data_orig.min(), x_data_orig.max(), n_eval)
            # Evaluate the constant expression
            y_plot = np.full_like(x_plot, float(f_expr))
            evals.extend([x_plot, y_plot])

    return models, evals, final_scalars


