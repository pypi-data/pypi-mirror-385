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
    alpha = float(params.get('alpha', 1e-2))
    scaling = bool(params.get('scaling', True))
    n_eval = int(params.get('n_eval', 200))
    library_config = params.get('library', {})

    # Provide a sensible default library if the user doesn't specify one
    if not library_config or not any(k in library_config for k in ['default', *[f'f{i}' for i in range(10)]]):
        print("Warning: No function library specified in params. Using default polynomial library.")
        library_config['default'] = [f'x**{i}' for i in range(1, 6)]

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
    
    df_syms = {col: sp.Symbol(col) for col in df.columns}
    a_syms = {p: sp.Symbol(p) for p in all_params_list}
    f_classes = {f_name: sp.Function(f_name) for f_name in all_funcs_map.keys()}
    
    full_expr = sp.sympify(lhs_str, locals=df_syms) - sp.sympify(rhs_str, locals={**df_syms, **a_syms, **f_classes})
    
    # --- New: Check for non-additive/non-linear function combinations ---
    for term in sp.Add.make_args(full_expr):
        present_funcs = [f.name for f in term.atoms(sp.Function) if f.name in all_funcs_map]
        if len(set(present_funcs)) > 1:
            raise NotImplementedError(
                f"Equation contains non-additive term '{term}' with multiple unknown functions "
                f"({list(set(present_funcs))}). The sparse regression solver expects functions to be additively separable. "
                "It cannot solve for terms like f1*f2 or f1/f2 directly."
            )

    known_terms_expr = sp.S(0)
    unknown_terms_expr = sp.S(0)
    for term in sp.Add.make_args(full_expr):
        has_unknown_func = any(f.name in all_funcs_map for f in term.atoms(sp.Function))
        if has_unknown_func:
            unknown_terms_expr += term
        else:
            known_terms_expr += term

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
        
        sign_expr = sp.diff(unknown_terms_expr, f_instance)
        if not sign_expr.is_constant():
             raise ValueError(f"Coefficient of function '{f_name}' is not constant. This can happen with e.g. f1/f2 terms.")
        sign_coeff = float(sign_expr)

        print(f"Building library for '{f_name}({var_name})' with combined coefficient: {sign_coeff:.2f}")
        
        x_data = df[var_name].values.reshape(-1, 1)
        scaler = StandardScaler() if scaling else None
        x_data_scaled = scaler.fit_transform(x_data).flatten() if scaler else x_data.flatten()
        scalers[var_name] = scaler
        
        # --- New: Flexible library generation ---
        basis_function_strings = library_config.get(f_name, library_config.get('default', []))
        lib_var_sym = sp.Symbol('x') # Placeholder symbol for library definition
        
        for basis_str in basis_function_strings:
            try:
                basis_expr = sp.sympify(basis_str, locals={'x': lib_var_sym, 'sin': sp.sin, 'cos': sp.cos, 'tanh': sp.tanh, 'exp': sp.exp})
                basis_lambda = sp.lambdify(lib_var_sym, basis_expr, 'numpy')
                basis_values = basis_lambda(x_data_scaled)
                
                library_funcs.append(sign_coeff * basis_values)
                
                actual_var_sym = sp.Symbol(var_name)
                library_syms.append(basis_expr.subs({lib_var_sym: actual_var_sym}))
                library_term_map.append(f_name)
            except Exception as e:
                print(f"Warning: Could not parse basis function '{basis_str}'. Skipping. Error: {e}")
                continue

    if not library_funcs:
        raise ValueError("The feature library is empty. Check the 'library' definition in your parameters.")

    Theta = np.vstack(library_funcs).T
    print(f"Constructed library Theta with {Theta.shape[1]} candidate functions.")

    # --- 4. Fit the Sparse Regression Model ---
    model = Lasso(alpha=alpha, fit_intercept=True, max_iter=10000, tol=1e-6)
    model.fit(Theta, Y)
    
    Xi = model.coef_
    intercept = model.intercept_

    # --- 5. Decompose Results ---
    print("\n--- Sparse Regression Results ---")
    models = {f_name: {'expr': sp.S(0), 'var': var_name, 'scaler': scalers.get(var_name)} for f_name, var_name in all_funcs_map.items()}
    final_scalars = {'intercept': intercept}

    for i, coef in enumerate(Xi):
        if np.abs(coef) > 1e-8:
            term_origin = library_term_map[i]
            symbolic_term = library_syms[i]
            models[term_origin]['expr'] += coef * symbolic_term

    for f_name, model_info in models.items():
        print(f"\nFinal expression for {f_name}({model_info['var']}):")
        sp.pprint(model_info['expr'], use_unicode=True)

    # --- 6. Generate Evaluation Data for Plotting ---
    evals = []
    for f_name, model_info in models.items():
        var_name = model_info['var']
        f_expr = model_info['expr']
        scaler = model_info['scaler']
        
        x_data_orig = df[var_name].values
        x_plot = np.linspace(x_data_orig.min(), x_data_orig.max(), n_eval)
        
        if f_expr.free_symbols:
            var_sym = sp.Symbol(var_name)
            x_plot_scaled = scaler.transform(x_plot.reshape(-1, 1)).flatten() if scaler else x_plot
            f_lambda = sp.lambdify(var_sym, f_expr, 'numpy')
            y_plot = f_lambda(x_plot_scaled)
        else:
            y_plot = np.full_like(x_plot, float(f_expr))
            
        evals.extend([x_plot, y_plot])

    return models, evals, final_scalars


