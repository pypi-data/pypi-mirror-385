from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple, Union, Optional
import numpy as np
import pandas as pd
from scipy.special import expit, logsumexp
from scipy.optimize import minimize
from EqUMP.base import IRF, gauss_hermite_quadrature
from EqUMP.base.irf import ItemParams, ItemParamsInit

# -------------------------
# Helpers: starts, transforms, numerics
# -------------------------
def _inv_logit(p: float) -> float:
    p = np.clip(p, 1e-8, 1 - 1e-8)
    return np.log(p / (1 - p))

def _starts_for_item(
        x: np.ndarray,
        model: str,
        K: Optional[int],
        D: float
    ) -> ItemParams:
    """Heuristic starting values based on marginal proportions."""
    x = x[~np.isnan(x)]
    if model == "2PL":
        # proportion correct
        if x.size == 0:
            return {"a": 1.0, "b": 0.0}
        p = np.mean(x > 0.5)
        a0 = 1.0
        b0 = -_inv_logit(p) / (D * a0)
        return {"a": np.clip(a0, 0.25, 2.5), "b": np.clip(b0, -2.5, 2.5)}
    elif model == "3PL":
        if x.size == 0:
            return {"a": 1.0, "b": 0.0, "c": 0.0}
        p = np.mean(x > 0.5)
        a0 = 1.0
        b0 = -_inv_logit(p) / (D * a0)
        # For 3PL, set a modest guessing parameter
        c0 = 0.1 if p > 0.1 else p * 0.5
        return {
            "a": np.clip(a0, 0.25, 2.5), 
            "b": np.clip(b0, -2.5, 2.5),
            "c": np.clip(c0, 1e-6, 0.499)
        }
    elif model == "GPC":
        if K is None:
            K = int(np.nanmax(x))
        # evenly spaced step parameters centered to 0
        tau = np.linspace(-1.0, 1.0, K)
        tau -= tau.mean()
        return {"a": 1.0, "b": tau.astype(float)}
    else:
        raise ValueError(model)

def _center_gpcm_steps(tau: np.ndarray) -> np.ndarray:
    return tau - np.mean(tau)

def _pack_params_2pl(a: float, b: float) -> np.ndarray:
    return np.array([np.log(np.clip(a, 1e-4, 1e4)), b], dtype=float)

def _unpack_params_2pl(p: np.ndarray) -> Tuple[float, float]:
    loga, b = p
    return float(np.exp(loga)), float(b)

def _pack_params_3pl(a: float, b: float, c: float) -> np.ndarray:
    return np.array([np.log(np.clip(a, 1e-4, 1e4)), b, _inv_logit(c)], dtype=float)

def _unpack_params_3pl(p: np.ndarray) -> Tuple[float, float, float]:
    loga, b, logit_c = p
    return float(np.exp(loga)), float(b), float(expit(logit_c))

def _pack_params_gpcm(a: float, tau: np.ndarray) -> np.ndarray:
    # unconstrained u; centered during unpack
    tau_array = np.atleast_1d(np.asarray(tau, dtype=float))
    return np.concatenate([[np.log(np.clip(a, 1e-4, 1e4))], tau_array])

def _unpack_params_gpcm(p: np.ndarray) -> Tuple[float, np.ndarray]:
    loga = p[0]
    tau = _center_gpcm_steps(np.asarray(p[1:], dtype=float))
    return float(np.exp(loga)), tau.astype(float)

def _numeric_hessian(func, x: np.ndarray, eps: float = 1e-4) -> np.ndarray:
    """Symmetric numeric Hessian of a scalar function."""
    x = x.astype(float)
    n = x.size
    H = np.zeros((n, n), dtype=float)
    # Precompute f(x) only if helpful? We use 2nd diff formula.
    for i in range(n):
        for j in range(i, n):
            ei = np.zeros_like(x); ei[i] = eps
            ej = np.zeros_like(x); ej[j] = eps
            fpp = func(x + ei + ej)
            fpm = func(x + ei - ej)
            fmp = func(x - ei + ej)
            fmm = func(x - ei - ej)
            H[i, j] = (fpp - fpm - fmp + fmm) / (4 * eps * eps)
            H[j, i] = H[i, j]
    return H


# -------------------------
# Per-item EM objective (M-step)
# -------------------------
def _q_objective_2pl(pvec: np.ndarray, theta_q: np.ndarray, s_qk: np.ndarray, D: float) -> float:
    a, b = _unpack_params_2pl(pvec)
    z = D * a * (theta_q - b)
    p1 = expit(z)
    p0 = 1.0 - p1
    P = np.column_stack([p0, p1])                # (Q,2)
    P = np.clip(P, 1e-12, 1.0)
    # Q_j = sum_q sum_k s_qk * log P_qk ; we return negative for minimize
    return -np.sum(s_qk * np.log(P))

def _q_objective_3pl(pvec: np.ndarray, theta_q: np.ndarray, s_qk: np.ndarray, D: float) -> float:
    a, b, c = _unpack_params_3pl(pvec)
    z = D * a * (theta_q - b)
    p1 = c + (1 - c) * expit(z)
    p0 = 1.0 - p1
    P = np.column_stack([p0, p1])                # (Q,2)
    P = np.clip(P, 1e-12, 1.0)
    # Q_j = sum_q sum_k s_qk * log P_qk ; we return negative for minimize
    return -np.sum(s_qk * np.log(P))

def _q_objective_gpcm(pvec: np.ndarray, theta_q: np.ndarray, s_qk: np.ndarray, D: float) -> float:
    a, tau = _unpack_params_gpcm(pvec)            # tau shape (K,)
    K = tau.size
    csum_tau = np.cumsum(tau)
    k_vec = np.arange(K + 1, dtype=float)[None, :]
    sum_tau_upto_k = np.concatenate([np.array([0.0]), csum_tau])[None, :]
    scores = D * a * (k_vec * theta_q[:, None] - sum_tau_upto_k)  # (Q,K+1)
    scores -= scores.max(axis=1, keepdims=True)
    P = np.exp(scores)
    P /= P.sum(axis=1, keepdims=True)
    P = np.clip(P, 1e-12, 1.0)
    return -np.sum(s_qk * np.log(P))


# -------------------------
# Main MMLE-EM
# -------------------------
@dataclass
class MMLEEMResult:
    loglik: float
    converged: bool
    n_iter: int
    theta_nodes: np.ndarray
    theta_weights: np.ndarray
    items: List[Dict[str, object]]               # per-item dicts with params, SEs, model, etc.

def mmle_em(
    responses: Union[np.ndarray, pd.DataFrame],
    item_models: Sequence[str],
    init_params: Optional[Sequence[ItemParamsInit]] = None,
    Q: int = 41,
    D: float = 1.702,
    tol: float = 1e-6,
    max_iter: int = 200,
    compute_se: bool = True,
    random_state: Optional[int] = None
) -> MMLEEMResult:
    """
    Mixed-format MMLE-EM for 2PL, 3PL, and GPC items.

    Parameters
    ----------
    responses : (N, J)
        array-like of integers (0..K_j), np.nan for missing.
    item_models : list[str] of length J;
        each in {"2PL","3PL","GPC"}.
    init_params : optional list[dict],
        initial parameters per item; if None, auto-starts.
    Q : int
        Gauss-Hermite nodes.
    D : float
        logistic scaling constant (default 1.702).
    tol : float
        convergence tolerance on log-likelihood and sup-norm of parameter change.
    max_iter : int
        maximum EM iterations.
    compute_se : bool
        if True, numeric Hessian of M-step objective for SEs.
    
    Usage
    ----------
    >>> import numpy as np
    >>> from EqUMP.base.estimation import mmle_em
    >>> responses = np.array([[0, 1, 2], [1, 2, np.nan]])
    >>> item_models = ["2PL", "3PL", "GPC"]
    >>> init_params = None
    >>> Q = 41
    >>> D = 1.702
    >>> tol = 1e-6
    >>> max_iter = 200
    >>> compute_se = True
    >>> random_state = None
    >>> result = mmle_em(responses, item_models, init_params, Q, D, tol, max_iter, compute_se, random_state)

    Details
    ----------
    - Assumptions
        - Latent trait: theta ~ N(0,1); integrated by Gauss–Hermite quadrature (Q nodes).
        - Logistic IRFs with scaling constant D (default 1.702).
        - Missing responses are MAR and omitted from the per-examinee likelihood.

    References
    -----------
    Bock, R. D., & Aitkin, M. (1981). Marginal maximum likelihood estimation of item parameters: Application of an EM algorithm. Psychometrika, 46(4), 443–459. https://doi.org/10.1007/BF02293801
    Muraki, E. (1992). A generalized partial credit model: Application of an EM algorithm. Applied Psychological Measurement, 16(2), 159–176. https://doi.org/10.1177/014662169201600206
    Baker, F. B., & Kim, S. H. (2004). Item response theory: Parameter estimation techniques (2nd ed.). CRC Press, Boca Raton.
    """
    rng = np.random.default_rng(random_state)

    X = np.asarray(responses, dtype=float)  # allow np.nan
    if X.ndim != 2:
        raise ValueError("responses must be 2D (N, J)")
    N, J = X.shape
    if len(item_models) != J:
        raise ValueError("item_models length mismatch.")

    # Determine category maxima per item (observed). If you know theoretical K, pass via init_params 'b' length.
    K_list = []
    for j, m in enumerate(item_models):
        if init_params and init_params[j] and "b" in init_params[j]:
            b = np.asarray(init_params[j]["b"])
            K = (b.size if m in ("GPC") else 1)
        else:
            K = int(np.nanmax(X[:, j])) if np.isfinite(X[:, j]).any() else (1 if m == "2PL" else 2)
        K_list.append(K)

    # Starts
    starts: List[ItemParams] = []
    for j, m in enumerate(item_models):
        if init_params is not None and init_params[j] is not None:
            s = init_params[j]
        else:
            s = _starts_for_item(X[:, j], m, K_list[j], D)
        # basic sanitization
        if m == "GPC":
            s["b"] = _center_gpcm_steps(np.asarray(s["b"], dtype=float))
        starts.append(s)

    # Quadrature
    theta_q, pi_q = gauss_hermite_quadrature(Q)

    # Parameter containers
    items = []
    for j, m in enumerate(item_models):
        items.append({"model": m, "params": starts[j].copy(), "SE": None, "history": []})

    # EM loop
    last_loglik = -np.inf
    for it in range(1, max_iter + 1):
        # ---------------- E-step ----------------
        # log posterior up to a constant: log w_iq ∝ log pi_q + sum_j log p_ij(q)
        log_pi = np.log(pi_q)[None, :]                # (1,Q)
        loglike_iq = np.zeros((N, Q), dtype=float) + log_pi

        # For per-item M-step suff stats: s_qk[j] = (Q, K_j+1)
        s_qk_list: List[np.ndarray] = []

        for j, model_name in enumerate(item_models):
            # Build IRF at nodes for item j - create IRF object once
            irf_obj = IRF(params=items[j]["params"], model=model_name, D=D)
            prob_df = irf_obj.prob(theta_q)
            P_qk = prob_df.values  # Shape: (Q, n_categories)
            P_qk = np.clip(P_qk, 1e-12, 1.0)

            # Pull observed categories for each person for this item
            xj = X[:, j]
            valid = ~np.isnan(xj)
            kj = np.zeros(N, dtype=int)
            kj[valid] = xj[valid].astype(int)

            # log p for observed category per (i,q)
            # index P_qk[q, k_i]
            logP_obs = np.log(P_qk[:, kj[valid]].T)  # (sum_valid, Q)
            loglike_iq[valid, :] += logP_obs

            # For M-step, compute s_qk = sum_i w_iq * 1(x_i=k)
            # we need w_iq; but first compute normalized posterior weights
            # We'll defer s_qk until after w is available.
            s_qk_list.append((P_qk, kj, valid))

        # normalize to get w_iq
        loglike_i = logsumexp(loglike_iq, axis=1)     # (N,)
        log_w_iq = loglike_iq - loglike_i[:, None]
        w_iq = np.exp(log_w_iq)                       # (N,Q)

        # ---------------- M-step ----------------
        new_params = []
        max_param_change = 0.0

        for j, m in enumerate(item_models):
            P_qk, kj, valid = s_qk_list[j]
            K = P_qk.shape[1] - 1
            # s_qk: (Q,K+1)
            # Build indicators for categories only over valid persons
            onehot = np.zeros((valid.sum(), K + 1), dtype=float)
            onehot[np.arange(valid.sum()), kj[valid]] = 1.0
            s_qk = w_iq[valid, :].T @ onehot          # (Q, K+1)

            # objective binding
            if m == "2PL":
                p0 = _pack_params_2pl(float(items[j]["params"]["a"]), float(items[j]["params"]["b"]))
                obj = lambda pv: _q_objective_2pl(pv, theta_q, s_qk, D)
                bounds = [(np.log(1e-4), np.log(1e4)), (None, None)]
            elif m =="3PL":
                p0 = _pack_params_3pl(
                    float(items[j]["params"]["a"]), 
                    float(items[j]["params"]["b"]), 
                    float(items[j]["params"]["c"])
                )
                obj = lambda pv: _q_objective_3pl(pv, theta_q, s_qk, D)
                bounds = [
                    (np.log(1e-4), np.log(1e4)),  # log(a)
                    (None, None),                 # b
                    (_inv_logit(1e-6), _inv_logit(0.5))   # logit(c)
                ]
            elif m == "GPC":
                a0 = float(items[j]["params"]["a"])
                tau0 = np.asarray(items[j]["params"]["b"], dtype=float)
                p0 = _pack_params_gpcm(a0, tau0)
                obj = lambda pv: _q_objective_gpcm(pv, theta_q, s_qk, D)
                bounds = [(np.log(1e-4), np.log(1e4))] + [(None, None)] * (p0.size - 1)
            else:
                raise ValueError(m)

            res = minimize(obj, p0, method="L-BFGS-B", bounds=bounds)
            if not res.success:
                # mild fallback: perturb and retry once
                res = minimize(obj, p0 + rng.normal(scale=0.05, size=p0.size), method="L-BFGS-B", bounds=bounds)

            # unpack & sanitize
            if m == "2PL":
                a_new, b_new = _unpack_params_2pl(res.x)
                params = {"a": float(a_new), "b": float(b_new)}
            elif m == "3PL":
                a_new, b_new, c_new = _unpack_params_3pl(res.x)
                params = {"a": float(a_new), "b": float(b_new), "c": float(c_new)}
            else:  # GPC
                a_new, tau_new = _unpack_params_gpcm(res.x)
                params = {"a": float(a_new), "b": _center_gpcm_steps(tau_new)}

            # track change
            old = items[j]["params"]
            diffs = []
            for k in params:
                v_old = np.asarray(old[k])
                v_new = np.asarray(params[k])
                diffs.append(np.max(np.abs(v_new - v_old)))
            max_param_change = max(max_param_change, float(np.max(diffs)))
            new_params.append(params)

        # commit new params
        for j in range(J):
            items[j]["params"] = new_params[j]
            items[j]["history"].append(new_params[j])

        # compute observed log-likelihood (marginal)
        loglik = float(np.sum(loglike_i))

        # check convergence
        if (abs(loglik - last_loglik) < tol) and (max_param_change < 1e-4):
            converged = True
            break

        last_loglik = loglik
    else:
        converged = False
        loglik = float(np.sum(loglike_i))

    n_iter = it if converged else max_iter

    # ---------------- SEs via numeric Hessian of Q_j at final params ----------------
    if compute_se:
        for j, model_name in enumerate(item_models):
            # recompute s_qk at final w_iq (from last E-step) - create IRF object once
            irf_obj = IRF(params=items[j]["params"], model=model_name, D=D)
            prob_df = irf_obj.prob(theta_q)
            P_qk = prob_df.values  # Shape: (Q, n_categories)
            K = P_qk.shape[1] - 1
            xj = X[:, j]
            valid = ~np.isnan(xj)
            kj = np.zeros(N, dtype=int)
            kj[valid] = xj[valid].astype(int)
            onehot = np.zeros((valid.sum(), K + 1), dtype=float)
            onehot[np.arange(valid.sum()), kj[valid]] = 1.0
            s_qk = w_iq[valid, :].T @ onehot

            if model_name == "2PL":
                p_hat = _pack_params_2pl(items[j]["params"]["a"], items[j]["params"]["b"])
                f = lambda pv: _q_objective_2pl(pv, theta_q, s_qk, D)
                H = _numeric_hessian(f, p_hat)
                try:
                    cov = np.linalg.inv(H)
                    se = {
                        "a": float(np.sqrt(cov[0, 0]) * np.exp(p_hat[0])),
                        "b": float(np.sqrt(cov[1, 1]))
                    }
                except (np.linalg.LinAlgError, ValueError):
                    se = {"a": np.nan, "b": np.nan}
            elif model_name == "3PL":
                p_hat = _pack_params_3pl(items[j]["params"]["a"], items[j]["params"]["b"], items[j]["params"]["c"])
                f = lambda pv: _q_objective_3pl(pv, theta_q, s_qk, D)
                H = _numeric_hessian(f, p_hat)
                try:
                    cov = np.linalg.inv(H)
                    # SE for c via delta method: se(c) = se(logit(c)) * c * (1-c)
                    c_hat = expit(p_hat[2])
                    se_logit_c = np.sqrt(cov[2, 2])
                    se = {
                        "a": float(np.sqrt(cov[0, 0]) * np.exp(p_hat[0])),
                        "b": float(np.sqrt(cov[1, 1])),
                        "c": float(se_logit_c * c_hat * (1.0 - c_hat))
                    }
                except (np.linalg.LinAlgError, ValueError):
                    se = {"a": np.nan, "b": np.nan, "c": np.nan}
            else:  # GPC
                p_hat = _pack_params_gpcm(items[j]["params"]["a"], np.asarray(items[j]["params"]["b"]))
                f = lambda pv: _q_objective_gpcm(pv, theta_q, s_qk, D)
                H = _numeric_hessian(f, p_hat)
                try:
                    cov = np.linalg.inv(H)
                    se = {
                        "a": float(np.sqrt(cov[0, 0]) * np.exp(p_hat[0])),
                        # step params reported on unconstrained scale
                        "b_internal": np.sqrt(np.diag(cov)[1:]).tolist()
                    }
                except (np.linalg.LinAlgError, ValueError):
                    se = {"a": np.nan, "b_internal": [np.nan] * (p_hat.size - 1)}

            items[j]["SE"] = se

    return MMLEEMResult(
        loglik=loglik,
        converged=converged,
        n_iter=n_iter,
        theta_nodes=theta_q,
        theta_weights=pi_q,
        items=items,
    )

if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    N = 1000  # number of examinees
    J = 5     # number of items

    # Create mixed-format responses
    responses = np.zeros((N, J))

    # Item 1-2: 2PL dichotomous (0 or 1)
    for j in range(2):
        theta = np.random.normal(0, 1, N)
        a, b = 0.8, np.random.normal(0, 0.5)
        prob = 1 / (1 + np.exp(-1.7 * a * (theta - b)))
        responses[:, j] = np.random.binomial(1, prob, N)

    # Item 3-4: 3PL dichotomous (0 or 1)
    for j in range(2, 4):
        theta = np.random.normal(0, 1, N)
        a, b, c = 1.0, np.random.normal(0, 0.5), 0.2  # Fixed: scalar c, higher a
        prob = c + (1 - c) / (1 + np.exp(-1.7 * a * (theta - b)))  # Correct 3PL formula
        responses[:, j] = np.random.binomial(1, prob, N)

    # Item 5: GPCM polytomous (0, 1, 2)
    j = 4
    theta = np.random.normal(0, 1, N)
    a = 1.0
    tau = np.array([-0.5, 0.5])  # step parameters
    for i in range(N):
        scores = [0, a * (theta[i] - tau[0]), a * (2 * theta[i] - sum(tau))]
        scores = np.array(scores) - max(scores)
        probs = np.exp(scores) / np.sum(np.exp(scores))
        responses[i, j] = np.random.choice(3, p=probs)

    # Add some missing data
    missing_mask = np.random.random((N, J)) < 0.05
    responses[missing_mask] = np.nan

    # Define item models
    item_models = ["2PL", "2PL", "3PL", "3PL", "GPC"]

    # Run MMLE-EM estimation
    print("Running MMLE-EM estimation...")
    result = mmle_em(
        responses=responses,
        item_models=item_models,
        Q=41,
        D=1.7,
        tol=1e-6,
        max_iter=500,
        compute_se=True,
        random_state=42
    )

    # Display results
    print(f"\nEstimation Results:")
    print(f"Log-likelihood: {result.loglik:.2f}")
    print(f"Converged: {result.converged}")
    print(f"Number of iterations: {result.n_iter}")
    print(f"Number of quadrature nodes: {len(result.theta_nodes)}")

    print(f"\nItem Parameters:")
    for j, item in enumerate(result.items):
        print(f"\nItem {j+1} ({item['model']}):")
        params = item['params']
        se = item['SE']
        
        print(f"  Discrimination (a): {params['a']:.3f} (SE: {se['a']:.3f})")
        
        if item['model'] == '2PL':
            print(f"  Difficulty (b): {params['b']:.3f} (SE: {se['b']:.3f})")
        elif item['model'] == '3PL':
            if "c" not in se:
                print(f"c is not found in se: {se}")
                raise KeyError
            print(f"  Difficulty (b): {params['b']:.3f} (SE: {se['b']:.3f})")
            print(f"  Guessing (c): {params['c']:.3f} (SE: {se['c']:.3f})")
        elif item['model'] == 'GPC':
            b_vals = params['b']
            print(f"  Step parameters (b): {[f'{b:.3f}' for b in b_vals]}")
            print(f"  SE (internal): {[f'{s:.3f}' for s in se['b_internal']]}")

    # Test individual IRFs
    print(f"\nSample IRF evaluations at theta = 0:")
    for j, item in enumerate(result.items):
        irf_obj = IRF(params=item['params'], model=item['model'], D=1.7)
        probs = irf_obj.prob(theta=0.0)
        print(f"Item {j+1}: {probs.values.flatten()}")

    import matplotlib.pyplot as plt
    
    # Visualize theta nodes and their weights
    plt.figure(figsize=(12, 8))
    
    # Plot 1: Theta nodes and weights
    plt.subplot(2, 2, 1)
    plt.plot(result.theta_nodes, result.theta_weights, 'bo-', markersize=4)
    plt.xlabel('Theta (θ)')
    plt.ylabel('Quadrature Weight')
    plt.title('Gaussian-Hermite Quadrature Nodes and Weights')
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Item Response Functions for dichotomous items
    plt.subplot(2, 2, 2)
    theta_range = np.linspace(-4, 4, 200)
    for j, item in enumerate(result.items):
        if item['model'] in ['2PL', '3PL']:
            # Create IRF object and compute probabilities for all theta values at once
            irf_obj = IRF(params=item['params'], model=item['model'], D=1.7)
            prob_df = irf_obj.prob(theta_range)
            probs_array = prob_df.values
            # Plot P(X=1) for dichotomous items (column index 1, not 'cat_1')
            plt.plot(theta_range, probs_array[:, 1], label=f"Item {j+1} ({item['model']})")
    
    plt.xlabel('Theta (θ)')
    plt.ylabel('P(X=1)')
    plt.title('Item Response Functions - Dichotomous Items')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Item Response Functions for polytomous items
    plt.subplot(2, 2, 3)
    for j, item in enumerate(result.items):
        if item['model'] == 'GPC':
            # Create IRF object and compute probabilities for all theta values at once
            irf_obj = IRF(params=item['params'], model=item['model'], D=1.7)
            prob_df = irf_obj.prob(theta_range)
            probs_array = prob_df.values
            for k in range(probs_array.shape[1]):
                plt.plot(theta_range, probs_array[:, k], 
                        label=f"Item {j+1} Cat {k}", linestyle='--')
    
    plt.xlabel('Theta (θ)')
    plt.ylabel('Category Probability')
    plt.title('Item Response Functions - Polytomous Items')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 4: Theta distribution approximation
    plt.subplot(2, 2, 4)
    plt.bar(result.theta_nodes, result.theta_weights, width=0.1, alpha=0.7, 
            label='Quadrature approximation')
    
    # Overlay true standard normal for comparison
    theta_fine = np.linspace(-4, 4, 1000)
    normal_density = (1/np.sqrt(2*np.pi)) * np.exp(-0.5 * theta_fine**2)
    plt.plot(theta_fine, normal_density, 'r-', label='N(0,1) density')
    
    plt.xlabel('Theta (θ)')
    plt.ylabel('Density/Weight')
    plt.title('Theta Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()