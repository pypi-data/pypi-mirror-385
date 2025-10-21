from .simulate_th import simulate_th
from .simulate_NN import simulate_NN
from .simulate_Poly import simulate_Poly
from .simulate_SymbR import simulate_SymbR
from .simulate_from_evals_interp import simulate_from_evals_interp

def simulate(equations, method='Theoretical', params=None):
    """
    Manager to select simulation method.
    method: 'Theoretical', 'NN', 'Poly', 'SymbReg', etc.
    params: dict with simulation parameters (t_span, y0, noise, etc.)
    """
    if method == 'Theoretical':
        return simulate_th(equations, params=params)
    elif method == 'NN':
         return simulate_NN(equations, params=params)
    elif method == 'Poly':
         return simulate_Poly(equations, params=params)
    elif method == 'SymbR':
         return simulate_SymbR(equations, params=params)
    elif method == 'Interp':
         return simulate_from_evals_interp(equations, params=params)
    else:
        raise ValueError(f"Unknown simulation method '{method}'")
        
        

