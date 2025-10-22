"""
DoubleML implementation for estimating average treatment effects on the treated.

This module provides a function to estimate average treatment effects on the treated using DoubleML.
"""

import warnings
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Union, List, Tuple

import doubleml as doubleml

from causalis.data.causaldata import CausalData


def dml_atte_source(
    data: CausalData,
    ml_g: Optional[Any] = None,
    ml_m: Optional[Any] = None,
    n_folds: int = 5,
    n_rep: int = 1,
    confidence_level: float = 0.95,
) -> Dict[str, Any]:
    """
    Estimate average treatment effects on the treated using DoubleML's interactive regression model (IRM).
    
    Parameters
    ----------
    data : CausalData
        The causaldata object containing treatment, target, and confounders variables.
    ml_g : estimator, optional
        A machine learner implementing ``fit()`` and ``predict()`` methods for the nuisance function g_0(D,X) = E[Y|X,D].
        If None, a CatBoostRegressor configured to use all CPU cores is used.
    ml_m : classifier, optional
        A machine learner implementing ``fit()`` and ``predict_proba()`` methods for the nuisance function m_0(X) = E[D|X].
        If None, a CatBoostClassifier configured to use all CPU cores is used.
    n_folds : int, default 5
        Number of folds for cross-fitting.
    n_rep : int, default 1
        Number of repetitions for the sample splitting.
    confidence_level : float, default 0.95
        The confidence level for calculating confidence intervals (between 0 and 1).
        
    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
        - coefficient: The estimated average treatment effect on the treated
        - std_error: The standard error of the estimate
        - p_value: The p-value for the null hypothesis that the effect is zero
        - confidence_interval: Tuple of (lower, upper) bounds for the confidence interval
        - model: The fitted DoubleMLIRM object
        
    Raises
    ------
    ValueError
        If the causaldata object doesn't have treatment, target, and confounders variables defined,
        or if the treatment variable is not binary.
        
    Examples
    --------
    >>> from causalis.data import generate_rct_data
    >>> from causalis.data import CausalData
    >>> from causalis.inference.atte import dml_atte_source
    >>> 
    >>> # Generate data
    >>> df = generate_rct_data()
    >>> 
    >>> # Create causaldata object
    >>> ck = CausalData(
    ...     df=df,
    ...     outcome='outcome',
    ...     treatment='treatment',
    ...     confounders=['age', 'invited_friend']
    ... )
    >>> 
    >>> # Estimate ATT using DoubleML
    >>> results = dml_atte_source(ck)
    >>> print(f"ATT: {results['coefficient']:.4f}")
    >>> print(f"Standard Error: {results['std_error']:.4f}")
    >>> print(f"P-value: {results['p_value']:.4f}")
    >>> print(f"Confidence Interval: {results['confidence_interval']}")
    """
    # Validate inputs
    if data.treatment is None:
        raise ValueError("CausalData object must have a treatment variable defined")
    if data.target is None:
        raise ValueError("CausalData object must have a outcome variable defined")
    if not data.confounders:
        raise ValueError("CausalData object must have confounders variables defined")
    
    # Check confidence level
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be between 0 and 1 (exclusive)")
    
    # Set default ML models if not provided
    if ml_g is None or ml_m is None:
        # Lazy import CatBoost only if defaults are needed
        try:
            from catboost import CatBoostRegressor, CatBoostClassifier  # type: ignore
        except ImportError as e:
            raise ImportError(
                "CatBoost is required for default learners. Install 'catboost' or provide ml_g and ml_m."
            ) from e
        if ml_g is None:
            ml_g = CatBoostRegressor(iterations=100, depth=5, min_data_in_leaf=2, thread_count=-1, verbose=False, allow_writing_files=False)
        if ml_m is None:
            ml_m = CatBoostClassifier(iterations=100, depth=5, min_data_in_leaf=2, thread_count=-1, verbose=False, allow_writing_files=False)
    
    # Prepare DataFrame and normalize treatment
    df = data.get_df().copy()
    tname = data.treatment.name
    yname = data.target.name
    xnames = list(data.confounders)

    t = df[tname].values
    if df[tname].dtype == bool:
        df[tname] = t.astype(int)
    else:
        uniq = np.unique(t)
        if not np.array_equal(np.sort(uniq), np.array([0, 1])) and not np.array_equal(np.sort(uniq), np.array([0.0, 1.0])):
            raise ValueError(f"Treatment must be binary 0/1 or boolean; found {uniq}.")
        df[tname] = df[tname].astype(int)
    
    # Create DoubleMLData object using public names
    data_dml = doubleml.DoubleMLData(
        df,
        y_col=yname,
        d_cols=tname,
        x_cols=xnames
    )
    
    # Create and fit DoubleMLIRM object with score="ATTE" for ATT estimation
    dml_irm_obj = doubleml.DoubleMLIRM(
        data_dml,
        ml_g=ml_g,
        ml_m=ml_m,
        n_folds=n_folds,
        n_rep=n_rep,
        score="ATTE"  # Use ATTE score for ATT estimation
    )
    
    # Suppress scikit-learn FutureWarning about 'force_all_finite' rename during fit
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=".*'force_all_finite' was renamed to 'ensure_all_finite'.*",
            category=FutureWarning,
        )
        dml_irm_obj.fit()
    
    # Calculate confidence interval
    ci = dml_irm_obj.confint(level=confidence_level)
    
    # Extract confidence interval values robustly
    if isinstance(ci, pd.DataFrame):
        pct_cols = [c for c in ci.columns if "%" in c]
        if len(pct_cols) >= 2:
            ci_lower = float(ci.iloc[0][pct_cols[0]])
            ci_upper = float(ci.iloc[0][pct_cols[1]])
        else:
            ci_lower = float(ci.iloc[0, 0])
            ci_upper = float(ci.iloc[0, 1])
    else:
        ci_lower = float(ci[0, 0])
        ci_upper = float(ci[0, 1])
    
    # Return results as a dictionary
    return {
        "coefficient": float(dml_irm_obj.coef[0]),
        "std_error": float(dml_irm_obj.se[0]),
        "p_value": float(dml_irm_obj.pval[0]),
        "confidence_interval": (ci_lower, ci_upper),
        "model": dml_irm_obj
    }