"""EDA utilities for causal analysis (propensity, overlap, balance, weights).

This module provides a lightweight CausalEDA class to quickly assess whether a
binary treatment problem is suitable for causal effect estimation. The outputs
focus on interpretability: treatment predictability, overlap/positivity,
covariate balance before/after weighting, and basic data health.

What the main outputs mean

- outcome_stats(): DataFrame with comprehensive statistics (count, mean, std, 
  percentiles, min/max) for outcome grouped by treatment.
- fit_propensity(): Numpy array of cross-validated propensity scores P(T=1|X).
- confounders_roc_auc(): Float ROC AUC of treatment vs. propensity score.
  Higher AUC implies treatment is predictable from confounders (more confounding risk).
- positivity_check(): Dict with bounds, share_below, share_above, and flag.
  It reports what share of units have PS outside [low, high]; a large share
  signals poor overlap (violated positivity).
- plot_ps_overlap(): Overlaid histograms of PS for treated vs control.
- confounders_means(): DataFrame with comprehensive balance assessment including
  means by treatment group, absolute differences, and standardized mean differences (SMD).

Note: The class accepts either the project’s CausalData object (duck-typed) or a
CausalDataLite with explicit fields.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict, KFold
from sklearn.metrics import roc_auc_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression, LinearRegression
from catboost import CatBoostClassifier, CatBoostRegressor
import matplotlib.pyplot as plt


import warnings
_CK_EDA_WARN_ONCE = set()

def _warn_once(name: str, to: str):
    key = (name, to)
    if key not in _CK_EDA_WARN_ONCE:
        warnings.warn(
            f"`{name}` is deprecated; use `{to}` instead. "
            "This alias will be removed in a future release.",
            DeprecationWarning,
            stacklevel=2,
        )
        _CK_EDA_WARN_ONCE.add(key)


class PropensityModel:
    """A model for m(x) = P(D=1|X) and related diagnostics.
    
    This class encapsulates propensity m and provides methods for:
    - Computing ROC AUC (AUC of D vs m)
    - Extracting SHAP values
    - Plotting m overlap
    - Checking positivity/overlap
    
    The class is returned by CausalEDA.fit_m() and provides a cleaner
    interface for propensity analysis.
    """
    
    def __init__(self, 
                 m: Optional[np.ndarray] = None,
                 d: Optional[np.ndarray] = None,
                 fitted_model: Any = None,
                 feature_names: List[str] = None,
                 X_for_shap: Optional[np.ndarray] = None,
                 cat_features_for_shap: Optional[List[int]] = None,
                 propensity_scores: Optional[np.ndarray] = None,
                 treatment_values: Optional[np.ndarray] = None):
        """Initialize PropensityModel with fitted model artifacts.
        
        Parameters
        ----------
        m : np.ndarray
            Array of m(x) = P(D=1|X)
        d : np.ndarray
            Array of actual treatment assignments (0/1)
        fitted_model : Any
            The fitted propensity model
        feature_names : List[str]
            Names of features used in the model
        X_for_shap : Optional[np.ndarray]
            Preprocessed feature matrix for SHAP computation
        cat_features_for_shap : Optional[List[int]]
            Categorical feature indices for SHAP computation
        propensity_scores, treatment_values : Optional legacy aliases accepted for back-compat
        """
        # Back-compat arg names
        if m is None and propensity_scores is not None:
            _warn_once("propensity_scores (init)", "m")
            m = propensity_scores
        if d is None and treatment_values is not None:
            d = treatment_values
        self.m = np.asarray(m) if m is not None else None
        self.d = np.asarray(d) if d is not None else None
        self.fitted_model = fitted_model
        self.feature_names = feature_names
        self.X_for_shap = X_for_shap
        self.cat_features_for_shap = cat_features_for_shap

    @classmethod
    def from_kfold(
        cls,
        X: pd.DataFrame,
        t: np.ndarray,
        model: Optional[Any] = None,
        n_splits: int = 5,
        random_state: int = 42,
        preprocessor: Optional[ColumnTransformer] = None,
    ) -> "PropensityModel":
        """Estimate m(x) via K-fold and return a PropensityModel.

        Produces out-of-fold m estimates using StratifiedKFold. If no
        model is provided, a fast LogisticRegression is used. Categorical
        features are one-hot encoded and numeric features standardized by
        default using a ColumnTransformer.
        """
        # Ensure inputs are aligned
        if isinstance(X, pd.DataFrame):
            feature_names = X.columns.tolist()
        else:
            raise ValueError("X must be a pandas DataFrame with named columns.")
        t = np.asarray(t).astype(int)
        # validate binary treatment
        if not np.isin(t, [0, 1]).all():
            raise ValueError("Treatment must be binary {0,1}.")

        # Preprocessor default
        if preprocessor is None:
            num = X.select_dtypes(include=[np.number]).columns.tolist()
            cat = [c for c in X.columns if c not in num]
            num_transformer = Pipeline(steps=[("scaler", StandardScaler(with_mean=True, with_std=True))])
            preprocessor = ColumnTransformer(
                transformers=[
                    ("num", num_transformer, num),
                    ("cat", OneHotEncoder(handle_unknown="ignore", drop=None, sparse_output=False), cat),
                ],
                remainder="drop",
            )

        # Model default
        if model is None:
            model = LogisticRegression(max_iter=1000)

        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

        # Compute out-of-fold probabilities
        if isinstance(model, CatBoostClassifier):
            import warnings
            ps = np.zeros(len(X))
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    for tr_idx, te_idx in cv.split(X, t):
                        X_tr, X_te = X.iloc[tr_idx], X.iloc[te_idx]
                        t_tr = t[tr_idx]
                        X_tr_p = preprocessor.fit_transform(X_tr)
                        X_te_p = preprocessor.transform(X_te)
                        fold_model = CatBoostClassifier(thread_count=-1, random_seed=random_state, verbose=False, allow_writing_files=False)
                        fold_model.fit(X_tr_p, t_tr)
                        ps[te_idx] = fold_model.predict_proba(X_te_p)[:, 1]
            # Fit final model for SHAP
            X_full_p = preprocessor.fit_transform(X)
            final_model = CatBoostClassifier(thread_count=-1, random_state=random_state, verbose=False, allow_writing_files=False)
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                final_model.fit(X_full_p, t)
            X_for_shap = X_full_p
            fitted = final_model
            # use transformed feature names for SHAP alignment
            try:
                feature_names = preprocessor.get_feature_names_out().tolist()
            except Exception:
                feature_names = [f"feature_{i}" for i in range(X_full_p.shape[1])]
        else:
            pipe = Pipeline([("prep", preprocessor), ("clf", model)])
            import warnings
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    ps = cross_val_predict(pipe, X, t, cv=cv, method="predict_proba")[:, 1]
                    pipe.fit(X, t)
            fitted = pipe
            X_for_shap = None

        # clip for stability
        ps = np.clip(ps, 1e-6, 1 - 1e-6)

        return cls(
            propensity_scores=ps,
            treatment_values=t,
            fitted_model=fitted,
            feature_names=feature_names,
            X_for_shap=X_for_shap,
        )
    
    @property
    def roc_auc(self) -> float:
        """Compute ROC AUC of treatment assignment vs. m(x).
        
        Higher AUC means treatment is more predictable from confounders,
        indicating stronger systematic differences between groups (potential
        confounding). Values near 0.5 suggest random-like assignment.
        
        Returns
        -------
        float
            ROC AUC score between 0 and 1
        """
        return float(roc_auc_score(self.d, self.m))
    
    @property
    def shap(self) -> pd.DataFrame:
        """Return feature attribution from the fitted propensity model.
        
        For CatBoost models: returns SHAP-based attributions with both signed mean (shap_mean)
        and magnitude (shap_mean_abs), sorted by shap_mean_abs.
        
        For sklearn linear models (LogisticRegression): returns absolute coefficients under
        column 'coef_abs' (not SHAP), sorted descending.
        """
        # Extract SHAP values or feature importance based on model type
        if isinstance(self.fitted_model, CatBoostClassifier):
            try:
                from catboost import Pool
                if self.X_for_shap is None:
                    raise RuntimeError("Preprocessed data for SHAP computation not available.")
                shap_pool = Pool(data=self.X_for_shap)
                shap_values = self.fitted_model.get_feature_importance(type='ShapValues', data=shap_pool)
                shap_values_no_bias = shap_values[:, :-1]
                shap_mean = np.mean(shap_values_no_bias, axis=0)
                shap_mean_abs = np.mean(np.abs(shap_values_no_bias), axis=0)
                feature_names = list(self.feature_names)
                if len(feature_names) != shap_values_no_bias.shape[1]:
                    raise RuntimeError("Feature names length does not match SHAP values. Ensure transformed names are used.")
                result_df = pd.DataFrame({
                    'feature': feature_names,
                    'shap_mean': shap_mean,
                    'shap_mean_abs': shap_mean_abs,
                })
                # Sort by absolute shap_mean (test expects this order)
                result_df['abs_shap_mean'] = np.abs(result_df['shap_mean'].values)
                result_df = result_df.sort_values('abs_shap_mean', ascending=False).drop(columns=['abs_shap_mean']).reset_index(drop=True)
                # Augment with probability-scale metrics using baseline p0 = mean propensity score
                p0 = float(np.mean(self.propensity_scores))
                p0 = float(np.clip(p0, 1e-9, 1 - 1e-9))
                logit_p0 = float(np.log(p0 / (1.0 - p0)))
                # result_df['odds_mult_abs'] = np.exp(result_df['shap_mean_abs'].values)
                result_df['exact_pp_change_abs'] = 1.0 / (1.0 + np.exp(-(logit_p0 + result_df['shap_mean_abs'].values))) - p0
                result_df['exact_pp_change_signed'] = 1.0 / (1.0 + np.exp(-(logit_p0 + result_df['shap_mean'].values))) - p0
                return result_df
            except Exception as e:
                raise RuntimeError(f"Failed to extract SHAP values from CatBoost model: {e}")
        elif hasattr(self.fitted_model, 'named_steps') and hasattr(self.fitted_model.named_steps.get('clf'), 'coef_'):
            try:
                clf = self.fitted_model.named_steps['clf']
                coef_abs = np.abs(clf.coef_[0])
                prep = self.fitted_model.named_steps.get('prep')
                if hasattr(prep, 'get_feature_names_out'):
                    try:
                        feature_names = [str(n) for n in prep.get_feature_names_out()]
                    except Exception:
                        feature_names = [f"feature_{i}" for i in range(len(coef_abs))]
                else:
                    feature_names = [f"feature_{i}" for i in range(len(coef_abs))]
                if len(coef_abs) != len(feature_names):
                    raise RuntimeError("Feature names length does not match coefficients.")
                df = pd.DataFrame({'feature': feature_names, 'importance': coef_abs, 'coef_abs': coef_abs}).sort_values('importance', ascending=False).reset_index(drop=True)
                return df
            except Exception as e:
                raise RuntimeError(f"Failed to extract feature importance from sklearn model: {e}")
        else:
            raise RuntimeError(f"Feature importance extraction not supported for model type: {type(self.fitted_model)}")
    
    @property
    def propensity_scores(self):
        _warn_once("propensity_scores", "m")
        return self.m

    def plot_m_overlap(
            self,
            clip=(0.01, 0.99),
            bins="fd",
            kde=True,
            shade_overlap=True,
            ax=None,
            figsize=(9, 5.5),
            dpi=220,
            font_scale=1.15,
            save=None,
            save_dpi=None,
            transparent=False,
            color_t=None,  # None -> use Matplotlib defaults
            color_c=None,  # None -> use Matplotlib defaults
    ):
        """
        Overlap plot for m(x)=P(D=1|X) with high-res rendering.
        - x in [0,1]
        - Stable NumPy KDE w/ boundary reflection (no SciPy warnings)
        - Uses Matplotlib default colors unless color_t/color_c are provided
        """
        import numpy as np
        import matplotlib as mpl
        import matplotlib.pyplot as plt

        # ------- Helpers --------------------------------------------------------
        def _silverman_bandwidth(x):
            x = np.asarray(x, float)
            n = x.size
            if n < 2:
                return 0.04
            sd = np.std(x, ddof=1)
            iqr = np.subtract(*np.percentile(x, [75, 25]))
            s = sd if iqr <= 0 else min(sd, iqr / 1.34)
            h = 0.9 * s * n ** (-1 / 5)
            return float(max(h, 0.02))

        def _kde_reflect(x, xs, h):
            x = np.asarray(x, float)
            if x.size == 0:
                return np.zeros_like(xs)
            if x.size < 2 or np.std(x) < 1e-8:
                mu = float(np.mean(x)) if x.size else 0.5
                h0 = max(h, 0.02)
                z = (xs - mu) / h0
                return np.exp(-0.5 * z ** 2) / (np.sqrt(2 * np.pi) * h0)
            xr = np.concatenate([x, -x, 2 - x])  # reflect at 0 and 1
            diff = (xs[None, :] - xr[:, None]) / h
            kern = np.exp(-0.5 * diff ** 2) / (np.sqrt(2 * np.pi) * h)
            return kern.mean(axis=0)

        def _patch_color(patches, fallback):
            # Grab facecolor from the first bar; fallback to cycle color if needed
            for p in patches:
                fc = p.get_facecolor()
                if fc is not None:
                    return fc  # RGBA
            return fallback

        # ------- Data -----------------------------------------------------------
        d = np.asarray(self.d).astype(int)
        m = np.asarray(self.m, dtype=float)
        mask = np.isfinite(m) & np.isfinite(d)
        d, m = d[mask], m[mask]
        mt = m[d == 1]
        mc = m[d == 0]
        if mt.size == 0 or mc.size == 0:
            raise ValueError("Both treated and control must have at least one observation after cleaning.")

        # Clamp to [0,1] to keep plot stable and inside bounds
        mtp = np.clip(mt, 0.0, 1.0)
        mcp = np.clip(mc, 0.0, 1.0)

        # ------- Figure/axes with high DPI & scaled fonts ----------------------
        rc = {
            "font.size": 11 * font_scale,
            "axes.titlesize": 13 * font_scale,
            "axes.labelsize": 12 * font_scale,
            "legend.fontsize": 10 * font_scale,
            "xtick.labelsize": 10 * font_scale,
            "ytick.labelsize": 10 * font_scale,
        }
        with mpl.rc_context(rc):
            if ax is None:
                fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
            else:
                fig = ax.figure
                try:
                    fig.set_dpi(dpi)
                except Exception:
                    pass

            # ------- Histograms (ALWAYS [0,1]) ---------------------------------
            ht = ax.hist(mtp, bins=bins, range=(0.0, 1.0), density=True,
                         alpha=0.45, label=f"Treated (n={mt.size})",
                         edgecolor="white", linewidth=0.6,
                         color=color_t)  # None -> default color
            hc = ax.hist(mcp, bins=bins, range=(0.0, 1.0), density=True,
                         alpha=0.45, label=f"Control (n={mc.size})",
                         edgecolor="white", linewidth=0.6,
                         color=color_c)  # None -> default color

            # Determine the actual colors used (so KDE/means match the bars)
            cycle = mpl.rcParams["axes.prop_cycle"].by_key().get("color", ["C0", "C1"])
            used_t = color_t or _patch_color(ht[2], cycle[0])
            used_c = color_c or _patch_color(hc[2], cycle[1])

            # ------- KDE (stable NumPy implementation) -------------------------
            if kde:
                if clip:
                    lo, hi = np.quantile(np.clip(m, 0, 1), [clip[0], clip[1]])
                    lo, hi = float(max(0.0, lo)), float(min(1.0, hi))
                    if not (hi > lo):
                        lo, hi = 0.0, 1.0
                else:
                    lo, hi = 0.0, 1.0

                xs = np.linspace(0.0, 1.0, 800)
                h_t = _silverman_bandwidth(mtp)
                h_c = _silverman_bandwidth(mcp)
                yt = _kde_reflect(mtp, xs, h_t)
                yc = _kde_reflect(mcp, xs, h_c)

                ax.plot(xs, yt, linewidth=2.2, label="Treated (KDE)", color=used_t, antialiased=True)
                ax.plot(xs, yc, linewidth=2.2, linestyle="--", label="Control (KDE)", color=used_c, antialiased=True)

                if shade_overlap:
                    y_min = np.minimum(yt, yc)
                    ax.fill_between(xs, y_min, 0, alpha=0.12, color="grey", rasterized=False)

            # ------- Means ------------------------------------------------------
            ax.axvline(float(mtp.mean()), linestyle=":", linewidth=1.8, color=used_t, alpha=0.95)
            ax.axvline(float(mcp.mean()), linestyle=":", linewidth=1.8, color=used_c, alpha=0.95)

            # ------- Cosmetics --------------------------------------------------
            ax.set_xlabel(r"$m(x) = \mathbb{P}(D=1 \mid X)$")
            ax.set_ylabel("Density")
            ax.set_title("Propensity Overlap by Treatment Group")
            ax.set_xlim(0.0, 1.0)
            ax.grid(True, linewidth=0.5, alpha=0.45)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            ax.legend(frameon=False)
            fig.tight_layout()

            # ------- Optional save ---------------------------------------------
            if save is not None:
                ext = str(save).lower().split(".")[-1]
                _dpi = save_dpi or (300 if ext in {"png", "jpg", "jpeg", "tif", "tiff"} else dpi)
                fig.savefig(
                    save, dpi=_dpi, bbox_inches="tight", pad_inches=0.1,
                    transparent=transparent,
                    facecolor="none" if transparent else "white"
                )

        return fig

    def positivity_check_m(self, bounds: Tuple[float, float] = (0.05, 0.95)) -> Dict[str, Any]:
        """Check overlap/positivity for m(x) based on thresholds."""
        low, high = bounds
        m = self.m
        return {
            "bounds": bounds,
            "share_below": float((m < low).mean()),
            "share_above": float((m > high).mean()),
            "flag": bool(((m < low).mean() + (m > high).mean()) > 0.02),
        }

    # Back-compat shims
    def ps_graph(self, *args, **kwargs):
        _warn_once("ps_graph()", "plot_m_overlap()")
        return self.plot_m_overlap(*args, **kwargs)

    def positivity_check(self, *args, **kwargs):
        _warn_once("positivity_check()", "positivity_check_m()")
        return self.positivity_check_m(*args, **kwargs)


class OutcomeModel:
    """A model for outcome prediction and related diagnostics.

    This class encapsulates outcome predictions and provides methods for:
    - Computing RMSE and MAE regression metrics
    - Extracting SHAP values for outcome prediction

    The class is returned by CausalEDA.outcome_fit() and provides a cleaner
    interface for outcome model analysis.
    """

    def __init__(self,
                 predicted_outcomes: np.ndarray,
                 actual_outcomes: np.ndarray,
                 fitted_model: Any,
                 feature_names: List[str],
                 X_for_shap: Optional[np.ndarray] = None,
                 cat_features_for_shap: Optional[List[int]] = None):
        """Initialize OutcomeModel with fitted model artifacts.

        Parameters
        ----------
        predicted_outcomes : np.ndarray
            Array of predicted outcome values
        actual_outcomes : np.ndarray
            Array of actual outcome values
        fitted_model : Any
            The fitted outcome prediction model
        feature_names : List[str]
            Names of features used in the model (confounders only)
        X_for_shap : Optional[np.ndarray]
            Preprocessed feature matrix for SHAP computation
        cat_features_for_shap : Optional[List[int]]
            Categorical feature indices for SHAP computation
        """
        self.predicted_outcomes = predicted_outcomes
        self.actual_outcomes = actual_outcomes
        self.fitted_model = fitted_model
        self.feature_names = feature_names
        self.X_for_shap = X_for_shap
        self.cat_features_for_shap = cat_features_for_shap

    @classmethod
    def from_kfold(
        cls,
        X: pd.DataFrame,
        y: np.ndarray,
        model: Optional[Any] = None,
        n_splits: int = 5,
        random_state: int = 42,
        preprocessor: Optional[ColumnTransformer] = None,
    ) -> "OutcomeModel":
        """Estimate an outcome model via K-fold and return an OutcomeModel.

        Produces out-of-fold predictions using KFold. If no model is provided,
        a fast LinearRegression is used. Categorical features are one-hot
        encoded and numeric features standardized by default.
        """
        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be a pandas DataFrame with named columns.")
        feature_names = X.columns.tolist()
        y = np.asarray(y)

        # Preprocessor default
        if preprocessor is None:
            num = X.select_dtypes(include=[np.number]).columns.tolist()
            cat = [c for c in X.columns if c not in num]
            num_transformer = Pipeline(steps=[("scaler", StandardScaler(with_mean=True, with_std=True))])
            preprocessor = ColumnTransformer(
                transformers=[
                    ("num", num_transformer, num),
                    ("cat", OneHotEncoder(handle_unknown="ignore", drop=None, sparse_output=False), cat),
                ],
                remainder="drop",
            )

        # Model default
        if model is None:
            model = LinearRegression()

        cv = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

        if isinstance(model, CatBoostRegressor):
            import warnings
            preds = np.zeros(len(X))
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    for tr_idx, te_idx in cv.split(X, y):
                        X_tr, X_te = X.iloc[tr_idx], X.iloc[te_idx]
                        y_tr = y[tr_idx]
                        X_tr_p = preprocessor.fit_transform(X_tr)
                        X_te_p = preprocessor.transform(X_te)
                        fold_model = CatBoostRegressor(thread_count=-1, random_seed=random_state, verbose=False, allow_writing_files=False)
                        fold_model.fit(X_tr_p, y_tr)
                        preds[te_idx] = fold_model.predict(X_te_p)
            # Fit final model for SHAP
            X_full_p = preprocessor.fit_transform(X)
            final_model = CatBoostRegressor(thread_count=-1, random_seed=random_state, verbose=False, allow_writing_files=False)
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                final_model.fit(X_full_p, y)
            fitted = final_model
            X_for_shap = X_full_p
        else:
            pipe = Pipeline([("prep", preprocessor), ("reg", model)])
            import warnings
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    preds = cross_val_predict(pipe, X, y, cv=cv)
                    pipe.fit(X, y)
            fitted = pipe
            X_for_shap = None

        return cls(
            predicted_outcomes=preds,
            actual_outcomes=y,
            fitted_model=fitted,
            feature_names=feature_names,
            X_for_shap=X_for_shap,
        )
    
    @property
    def scores(self) -> Dict[str, float]:
        """Compute regression metrics (RMSE and MAE) for outcome predictions.
        
        Returns
        -------
        Dict[str, float]
            Dictionary containing:
            - 'rmse': Root Mean Squared Error
            - 'mae': Mean Absolute Error
        """
        mse = mean_squared_error(self.actual_outcomes, self.predicted_outcomes)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(self.actual_outcomes, self.predicted_outcomes)
        
        return {
            'rmse': float(rmse),
            'mae': float(mae)
        }
    
    @property
    def shap(self) -> pd.DataFrame:
        """Return SHAP values from the fitted outcome prediction model.
        
        SHAP values show the directional contribution of each feature to 
        outcome prediction, where positive values increase the predicted 
        outcome and negative values decrease it.
        
        Returns
        -------
        pd.DataFrame
            For CatBoost models: DataFrame with columns 'feature' and 'shap_mean',
            where 'shap_mean' represents the mean SHAP value across all samples.
            
            For sklearn models: DataFrame with columns 'feature' and 'importance'
            (absolute coefficient values, for backward compatibility).
            
        Raises
        ------
        RuntimeError
            If the fitted model does not support SHAP values extraction.
        """
        # Extract SHAP values or feature importance based on model type
        if isinstance(self.fitted_model, CatBoostRegressor):
            # Use CatBoost's SHAP values for directional feature contributions
            try:
                # Import Pool for SHAP computation
                from catboost import Pool
                
                # Check if we have the required data for SHAP computation
                if self.X_for_shap is None:
                    raise RuntimeError("Preprocessed data for SHAP computation not available.")
                
                # Create Pool object for SHAP computation (numeric-only after preprocessing)
                shap_pool = Pool(data=self.X_for_shap)
                
                # Get SHAP values - returns array of shape (n_samples, n_features + 1) 
                # where the last column is the bias term
                shap_values = self.fitted_model.get_feature_importance(type='ShapValues', data=shap_pool)
                
                # Remove bias term (last column) and compute mean SHAP values across samples
                # This gives us the average directional contribution of each feature
                shap_values_no_bias = shap_values[:, :-1]  # Remove bias column
                importance_values = np.mean(shap_values_no_bias, axis=0)  # Mean across samples
                
                feature_names = self.feature_names
                column_name = 'shap_mean'  # Use different column name to indicate SHAP values
                
            except Exception as e:
                raise RuntimeError(f"Failed to extract SHAP values from CatBoost model: {e}")
        
        elif hasattr(self.fitted_model, 'named_steps') and hasattr(self.fitted_model.named_steps.get('clf'), 'coef_'):
            # Handle sklearn pipeline with linear regression
            try:
                clf = self.fitted_model.named_steps['clf']
                # For linear regression, use absolute coefficients as importance
                importance_values = np.abs(clf.coef_)
                
                # Need to map back to original feature names through preprocessing
                # For simplicity, if we have preprocessed features, we'll use the original feature names
                # and aggregate importance for one-hot encoded categorical features
                prep = self.fitted_model.named_steps.get('prep')
                if hasattr(prep, 'get_feature_names_out'):
                    try:
                        # Try to get feature names from preprocessor
                        transformed_names = prep.get_feature_names_out()
                        feature_names = [str(name) for name in transformed_names]
                    except:
                        # Fallback to original feature names if transformation fails
                        feature_names = self.feature_names
                        if len(importance_values) != len(feature_names):
                            # If lengths don't match due to one-hot encoding, we can't map back easily
                            # Just use indices as feature names
                            feature_names = [f"feature_{i}" for i in range(len(importance_values))]
                else:
                    feature_names = self.feature_names
                
                column_name = 'importance'  # Keep backward compatibility for sklearn models
                    
            except Exception as e:
                raise RuntimeError(f"Failed to extract feature importance from sklearn model: {e}")
        
        else:
            raise RuntimeError(f"Feature importance extraction not supported for model type: {type(self.fitted_model)}")
        
        # Ensure we have matching lengths
        if len(importance_values) != len(feature_names):
            # This can happen with preprocessing transformations
            # Create generic feature names if needed
            if len(importance_values) > len(feature_names):
                feature_names = feature_names + [f"transformed_feature_{i}" for i in range(len(feature_names), len(importance_values))]
            else:
                feature_names = feature_names[:len(importance_values)]
        
        # Create DataFrame with appropriate column name
        result_df = pd.DataFrame({
            'feature': feature_names,
            column_name: importance_values
        })
        
        # Sort appropriately: by absolute value for SHAP values (to show most impactful features),
        # by value for regular importance (higher is better)
        if column_name == 'shap_mean':
            # For SHAP values, sort by absolute value to show most impactful features first
            result_df = result_df.reindex(result_df[column_name].abs().sort_values(ascending=False).index)
        else:
            # For regular importance, sort by value (descending)
            result_df = result_df.sort_values(column_name, ascending=False)
        
        result_df = result_df.reset_index(drop=True)
        return result_df




# Optional lightweight dataclass for standalone usage, but CausalEDA also
# supports the existing causalis.data.CausalData which uses `confounders`.
@dataclass
class CausalDataLite:
    """A minimal container for dataset roles used by CausalEDA.

    Attributes
    - df: The full pandas DataFrame containing treatment, outcome and covariates.
    - treatment: Column name of the binary treatment indicator (0/1).
    - target: Column name of the outcome variable.
    - confounders: List of covariate column names used to model treatment.
    """
    df: pd.DataFrame
    treatment: str
    target: str
    confounders: List[str]


def _extract_roles(data_obj: Any) -> Dict[str, Any]:
    """Extract dataset roles from various supported data containers.

    Accepts:
    - CausalDataLite
    - Project's CausalData (duck-typed: attributes df, treatment, outcome,
      and either confounders or confounders)
    - Any object exposing the same attributes/properties

    Returns a dict with keys: df, treatment, outcome, confounders.
    If both confounders/confounders are absent, it assumes all columns except
    treatment/outcome are confounders.
    """
    # Direct dataclass-like attributes
    df = getattr(data_obj, "df")
    treatment_attr = getattr(data_obj, "treatment")
    # Support both 'outcome' (project's CausalData) and 'target' (CausalDataLite)
    target_attr = getattr(data_obj, "outcome", None)
    if target_attr is None:
        target_attr = getattr(data_obj, "target")
    # If these are Series (as in causalis.data.CausalData properties), convert to column names
    if isinstance(treatment_attr, pd.Series):
        treatment = treatment_attr.name
    else:
        treatment = treatment_attr
    if isinstance(target_attr, pd.Series):
        target = target_attr.name
    else:
        target = target_attr

    if hasattr(data_obj, "confounders") and getattr(data_obj, "confounders") is not None:
        confs = list(getattr(data_obj, "confounders"))
    elif hasattr(data_obj, "confounders") and getattr(data_obj, "confounders") is not None:
        # causalis.data.CausalData.confounders returns a DataFrame or None; if it's a
        # DataFrame, use its columns; if it's a list/iterable, cast to list.
        cofs = getattr(data_obj, "confounders")
        if isinstance(cofs, pd.DataFrame):
            confs = list(cofs.columns)
        else:
            confs = list(cofs) if cofs is not None else []
    else:
        # Last resort: assume all columns except treatment/outcome are confounders
        confs = [c for c in df.columns if c not in {treatment, target}]

    return {"df": df, "treatment": treatment, "outcome": target, "confounders": confs}


class CausalEDA:
    """Exploratory diagnostics for causal designs with binary treatment.

    The class exposes methods to:
    
    - Summarize outcome by treatment and naive mean difference.
    - Estimate cross-validated propensity scores and assess treatment
      predictability (AUC) and positivity/overlap.
    - Inspect covariate balance via standardized mean differences (SMD)
      before/after IPTW weighting; visualize with a love plot.
    - Inspect weight distributions and effective sample size (ESS).
    """
    def __init__(self, data: Any, ps_model: Optional[Any] = None, n_splits: int = 5, random_state: int = 42):
        roles = _extract_roles(data)
        self.d = CausalDataLite(df=roles["df"], treatment=roles["treatment"], target=roles["outcome"], confounders=roles["confounders"])
        self.n_splits = n_splits
        self.random_state = random_state
        self.ps_model = ps_model or CatBoostClassifier(
            thread_count=-1,  # Use all available threads
            random_seed=random_state,
            verbose=False,  # Suppress training output
            allow_writing_files=False
        )

        # Preprocessing: always make features numeric via OneHotEncoder for categoricals
        X = self.d.df[self.d.confounders]
        num = X.select_dtypes(include=[np.number]).columns.tolist()
        cat = [c for c in X.columns if c not in num]

        num_transformer = Pipeline(steps=[
            ("scaler", StandardScaler(with_mean=True, with_std=True))
        ])
        self.preproc = ColumnTransformer(
            transformers=[
                ("num", num_transformer, num),
                ("cat", OneHotEncoder(handle_unknown="ignore", drop=None, sparse_output=False), cat),
            ],
            remainder="drop",
        )
        
        self.ps_pipe = Pipeline([("prep", self.preproc), ("clf", self.ps_model)])
        # Optional: clarify no native categorical indices are used post-OHE
        self.cat_features = None

    # ---------- basics ----------

    def data_shape(self) -> Dict[str, int]:
        """Return the shape information of the causal dataset.

        Returns a dict with:
        - n_rows: number of rows (observations) in the dataset
        - n_columns: number of columns (features) in the dataset
        
        This provides a quick overview of the dataset dimensions for 
        exploratory analysis and reporting purposes.
        
        Returns
        -------
        Dict[str, int]
            Dictionary containing 'n_rows' and 'n_columns' keys with 
            corresponding integer values representing the dataset dimensions.
        
        Examples
        --------
        >>> eda = CausalEDA(causal_data)
        >>> shape_info = eda.data_shape()
        >>> print(f"Dataset has {shape_info['n_rows']} rows and {shape_info['n_columns']} columns")
        """
        df = self.d.df
        n_rows, n_columns = df.shape
        return {"n_rows": n_rows, "n_columns": n_columns}


    def outcome_stats(self) -> pd.DataFrame:
        """Comprehensive outcome statistics grouped by treatment.

        Returns a DataFrame with detailed outcome statistics for each treatment group,
        including count, mean, std, min, various percentiles, and max.
        This method provides comprehensive outcome analysis and returns
        data in a clean DataFrame format suitable for reporting.

        Returns
        -------
        pd.DataFrame
            DataFrame with treatment groups as index and the following columns:
            - count: number of observations in each group
            - mean: average outcome value
            - std: standard deviation of outcome
            - min: minimum outcome value
            - p10: 10th percentile
            - p25: 25th percentile (Q1)
            - median: 50th percentile (median)
            - p75: 75th percentile (Q3)
            - p90: 90th percentile
            - max: maximum outcome value

        Examples
        --------
        >>> eda = CausalEDA(causal_data)
        >>> stats = eda.outcome_stats()
        >>> print(stats)
                count      mean       std       min       p10       p25    median       p75       p90       max
        treatment                                                                                                
        0        3000  5.123456  2.345678  0.123456  2.345678  3.456789  5.123456  6.789012  7.890123  9.876543
        1        2000  6.789012  2.456789  0.234567  3.456789  4.567890  6.789012  8.901234  9.012345  10.987654
        """
        df, t, y = self.d.df, self.d.treatment, self.d.target
        
        # Ensure treatment is numeric for grouping
        if not pd.api.types.is_numeric_dtype(df[t]):
            raise ValueError("Treatment must be numeric 0/1 for outcome_stats().")
        
        # Create grouped object for multiple operations
        grouped = df.groupby(t)[y]
        
        # Calculate basic statistics using built-in methods
        basic_stats = grouped.agg(['count', 'mean', 'std', 'min', 'median', 'max'])
        
        # Calculate percentiles separately to avoid pandas aggregation mixing issues
        p10 = grouped.quantile(0.10)
        p25 = grouped.quantile(0.25) 
        p75 = grouped.quantile(0.75)
        p90 = grouped.quantile(0.90)
        
        # Combine all statistics into a single DataFrame
        stats_df = pd.DataFrame({
            'count': basic_stats['count'],
            'mean': basic_stats['mean'],
            'std': basic_stats['std'],
            'min': basic_stats['min'],
            'p10': p10,
            'p25': p25,
            'median': basic_stats['median'],
            'p75': p75,
            'p90': p90,
            'max': basic_stats['max']
        })
        
        # Ensure the index is named appropriately
        stats_df.index.name = 'treatment'
        
        return stats_df

    # ---------- propensity & overlap ----------
    def fit_m(self) -> 'PropensityModel':
        """Estimate cross-validated m(x) = P(D=1|X).

        Uses a preprocessing + classifier setup with stratified K-fold to generate
        out-of-fold probabilities. For CatBoost, data are one-hot encoded via the
        configured ColumnTransformer before fitting. Returns a PropensityModel.
        """
        df = self.d.df
        X = df[self.d.confounders]
        t = df[self.d.treatment].astype(int).values
        if not np.isin(t, [0, 1]).all():
            raise ValueError("Treatment must be binary {0,1}.")
        cv = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)

        if isinstance(self.ps_model, CatBoostClassifier):
            import warnings
            ps = np.zeros(len(X))
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    for train_idx, test_idx in cv.split(X, t):
                        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                        t_train = t[train_idx]
                        X_train_prep = self.preproc.fit_transform(X_train)
                        X_test_prep = self.preproc.transform(X_test)
                        model = CatBoostClassifier(thread_count=-1, random_seed=self.random_state, verbose=False, allow_writing_files=False)
                        model.fit(X_train_prep, t_train)
                        ps[test_idx] = model.predict_proba(X_test_prep)[:, 1]
        else:
            import warnings
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    ps = cross_val_predict(self.ps_pipe, X, t, cv=cv, method="predict_proba")[:, 1]

        m = np.clip(ps, 1e-6, 1 - 1e-6)
        self._m = m

        if isinstance(self.ps_model, CatBoostClassifier):
            X_full_prep = self.preproc.fit_transform(X)
            final_model = CatBoostClassifier(thread_count=-1, random_seed=self.random_state, verbose=False)
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    final_model.fit(X_full_prep, t)
            self._fitted_model = final_model
            try:
                self._feature_names = self.preproc.get_feature_names_out().tolist()
            except Exception:
                self._feature_names = [f"feature_{i}" for i in range(X_full_prep.shape[1])]
            self._X_for_shap = X_full_prep
        else:
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    self.ps_pipe.fit(X, t)
            self._fitted_model = self.ps_pipe
            self._feature_names = X.columns.tolist()

        return PropensityModel(
            m=m,
            d=t,
            fitted_model=self._fitted_model,
            feature_names=self._feature_names,
            X_for_shap=getattr(self, '_X_for_shap', None)
        )

    # Back-compat shim
    def fit_propensity(self) -> 'PropensityModel':
        _warn_once("fit_propensity()", "fit_m()")
        return self.fit_m()

    def outcome_fit(self, outcome_model: Optional[Any] = None) -> 'OutcomeModel':
        """Fit a regression model to predict outcome from confounders only.

        Uses a preprocessing+CatBoost regressor pipeline with K-fold
        cross_val_predict to generate out-of-fold predictions. CatBoost uses
        all available threads and handles categorical features natively. Returns an
        OutcomeModel instance containing predicted outcomes and diagnostic methods.
        
        The outcome model predicts the baseline outcome from confounders only,
        excluding treatment. This is essential for proper causal analysis.
        
        Parameters
        ----------
        outcome_model : Optional[Any]
            Custom regression model to use. If None, uses CatBoostRegressor.
            
        Returns
        -------
        OutcomeModel
            An OutcomeModel instance with methods for:
            - scores: RMSE and MAE regression metrics
            - shap: SHAP values DataFrame property for outcome prediction
        """
        df = self.d.df
        # Features: confounders only (treatment excluded for proper causal analysis)
        X = df[self.d.confounders]
        y = df[self.d.target].values
        cv = KFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)
        
        # Default to CatBoostRegressor if no custom model provided
        if outcome_model is None:
            outcome_model = CatBoostRegressor(
                thread_count=-1,
                random_seed=self.random_state,
                verbose=False,
                allow_writing_files=False
            )
        
        # Identify numeric and categorical features for preprocessing
        num_features = X.select_dtypes(include=[np.number]).columns.tolist()
        cat_features = [c for c in X.columns if c not in num_features]
        
        # Setup preprocessing: always OHE categoricals so model input is numeric
        num_transformer = Pipeline(steps=[
            ("scaler", StandardScaler(with_mean=True, with_std=True))
        ])
        preproc = ColumnTransformer(
            transformers=[
                ("num", num_transformer, num_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", drop=None, sparse_output=False), cat_features),
            ],
            remainder="drop",
        )
        
        # Special handling for CatBoost to properly pass categorical features
        if isinstance(outcome_model, CatBoostRegressor):
            import warnings
            
            predictions = np.zeros(len(X))
            
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    
                    for train_idx, test_idx in cv.split(X, y):
                        # Prepare data for this fold
                        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                        y_train = y[train_idx]
                        
                        # Apply preprocessing
                        X_train_prep = preproc.fit_transform(X_train)
                        X_test_prep = preproc.transform(X_test)
                        
                        # Create and train CatBoost model for this fold
                        model = CatBoostRegressor(
                            thread_count=-1,
                            random_seed=self.random_state,
                            verbose=False,
                            allow_writing_files=False
                        )
                        
                        # All features are numeric after preprocessing; no cat_features needed
                        model.fit(X_train_prep, y_train)
                        predictions[test_idx] = model.predict(X_test_prep)
        else:
            # Use standard sklearn pipeline for non-CatBoost models
            pipeline = Pipeline([("prep", preproc), ("reg", outcome_model)])
            import warnings
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    predictions = cross_val_predict(pipeline, X, y, cv=cv)
        
        self._outcome_predictions = predictions
        
        # Train a final model on the full dataset for SHAP computation
        if isinstance(outcome_model, CatBoostRegressor):
            # Apply preprocessing to full dataset
            X_full_prep = preproc.fit_transform(X)
            
            # Create and train final model
            final_model = CatBoostRegressor(
                thread_count=-1,
                random_seed=self.random_state,
                verbose=False
            )
            
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    final_model.fit(X_full_prep, y)
            
            # Store the trained model and data needed for SHAP computation
            self._outcome_fitted_model = final_model
            self._outcome_feature_names = X.columns.tolist()
            self._outcome_X_for_shap = X_full_prep  # Store preprocessed data for SHAP
        else:
            # For non-CatBoost models, fit the pipeline on full data
            pipeline = Pipeline([("prep", preproc), ("reg", outcome_model)])
            with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    pipeline.fit(X, y)
            self._outcome_fitted_model = pipeline
            self._outcome_feature_names = X.columns.tolist()
        
        # Create and return OutcomeModel instance
        return OutcomeModel(
            predicted_outcomes=predictions,
            actual_outcomes=y,
            fitted_model=self._outcome_fitted_model,
            feature_names=self._outcome_feature_names,
            X_for_shap=getattr(self, '_outcome_X_for_shap', None)
        )

    def auc_m(self, m: Optional[np.ndarray] = None) -> float:
        """Compute ROC AUC of treatment assignment vs. m(x)."""
        if m is None:
            m = getattr(self, "_m", None)
            if m is None:
                pm = self.fit_m()
                m = pm.m
        t = self.d.df[self.d.treatment].astype(int).values
        return float(roc_auc_score(t, m))

    def positivity_check_m(self, m: Optional[np.ndarray] = None, bounds: Tuple[float, float] = (0.05, 0.95)) -> Dict[str, Any]:
        """Check overlap/positivity for m(x) based on thresholds."""
        if m is None:
            m = getattr(self, "_m", None)
            if m is None:
                pm = self.fit_m()
                m = pm.m
        low, high = bounds
        return {
            "bounds": bounds,
            "share_below": float((m < low).mean()),
            "share_above": float((m > high).mean()),
            "flag": bool(((m < low).mean() + (m > high).mean()) > 0.02),
        }

    def plot_m_overlap(self, m: Optional[np.ndarray] = None):
        """Plot overlaid histograms of m(x) for treated vs control."""
        if m is None:
            m = getattr(self, "_m", None)
            if m is None:
                pm = self.fit_m()
                m = pm.m
        df = self.d.df
        t = df[self.d.treatment].astype(int).values
        fig, ax = plt.subplots()
        ax.hist(m[t == 1], bins=30, alpha=0.5, density=True, label="treated")
        ax.hist(m[t == 0], bins=30, alpha=0.5, density=True, label="control")
        ax.set_xlabel("m(x) = P(D=1|X)")
        ax.set_ylabel("Density")
        ax.legend()
        ax.set_title("Overlap of m(x)")
        return fig

    # Back-compat shims for public API
    def confounders_roc_auc(self, ps: Optional[np.ndarray] = None) -> float:
        _warn_once("confounders_roc_auc()", "auc_m()")
        return self.auc_m(m=ps)

    def positivity_check(self, ps: Optional[np.ndarray] = None, bounds: Tuple[float, float] = (0.05, 0.95)) -> Dict[str, Any]:
        _warn_once("positivity_check()", "positivity_check_m()")
        return self.positivity_check_m(m=ps, bounds=bounds)

    def plot_ps_overlap(self, ps: Optional[np.ndarray] = None):
        _warn_once("plot_ps_overlap()", "plot_m_overlap()")
        return self.plot_m_overlap(m=ps)

    # ---------- balance ----------

    def confounders_means(self) -> pd.DataFrame:
        """Comprehensive confounders balance assessment with means by treatment group.

        Returns a DataFrame with detailed balance information including:
        - Mean values of each confounder for control group (treatment=0)
        - Mean values of each confounder for treated group (treatment=1)
        - Absolute difference between treatment groups
        - Standardized Mean Difference (SMD) for formal balance assessment
        
        This method provides a comprehensive view of confounder balance by showing
        the actual mean values alongside the standardized differences, making it easier
        to understand both the magnitude and direction of imbalances.

        Returns
        -------
        pd.DataFrame
            DataFrame with confounders as index and the following columns:
            - mean_t_0: mean value for control group (treatment=0)
            - mean_t_1: mean value for treated group (treatment=1)  
            - abs_diff: absolute difference abs(mean_t_1 - mean_t_0)
            - smd: standardized mean difference (Cohen's d)
            
        Notes
        -----
        SMD values > 0.1 in absolute value typically indicate meaningful imbalance.
        Categorical variables are automatically converted to dummy variables.
        
        Examples
        --------
        >>> eda = CausalEDA(causal_data)
        >>> balance = eda.confounders_means()
        >>> print(balance.head())
                     mean_t_0  mean_t_1  abs_diff       smd
        confounders                                       
        age              29.5      31.2      1.7     0.085
        income        45000.0   47500.0   2500.0     0.125
        education         0.25      0.35      0.1     0.215
        """
        df = self.d.df
        X = df[self.d.confounders]
        t = df[self.d.treatment].astype(int).values
        
        # Convert categorical variables to dummy variables for analysis
        X_num = pd.get_dummies(X, drop_first=False)
        
        rows = []
        for col in X_num.columns:
            x = X_num[col].values.astype(float)
            
            # Calculate means for each treatment group
            mean_t_0 = x[t == 0].mean()
            mean_t_1 = x[t == 1].mean()
            
            # Calculate absolute difference
            abs_diff = abs(mean_t_1 - mean_t_0)
            
            # Calculate standardized mean difference (SMD)
            v_control = x[t == 0].var(ddof=1) if len(x[t == 0]) > 1 else 0.0
            v_treated = x[t == 1].var(ddof=1) if len(x[t == 1]) > 1 else 0.0
            pooled_std = np.sqrt((v_control + v_treated) / 2)
            smd = (mean_t_1 - mean_t_0) / pooled_std if pooled_std > 0 else 0.0
            
            rows.append({
                "confounders": col,
                "mean_t_0": mean_t_0,
                "mean_t_1": mean_t_1, 
                "abs_diff": abs_diff,
                "smd": smd
            })
        
        # Create DataFrame and set confounders as index
        balance_df = pd.DataFrame(rows)
        balance_df = balance_df.set_index("confounders")
        
        # Sort by absolute SMD value (most imbalanced first)
        balance_df = balance_df.reindex(
            balance_df['smd'].abs().sort_values(ascending=False).index
        )
        
        return balance_df

    from typing import Optional, Tuple

    def outcome_hist(
            self,
            treatment: Optional[str] = None,
            target: Optional[str] = None,
            bins="fd",  # smarter default (still accepts int)
            density: bool = True,
            alpha: float = 0.45,
            sharex: bool = True,
            kde: bool = True,  # overlay smooth density (SciPy-free)
            clip: Optional[Tuple[float, float]] = (0.01, 0.99),  # trim tails for nicer view
            figsize: Tuple[float, float] = (9, 5.5),
            dpi: int = 220,
            font_scale: float = 1.15,
            save: Optional[str] = None,  # "outcome.png" / ".svg" / ".pdf"
            save_dpi: Optional[int] = None,
            transparent: bool = False,
    ):
        """
        Plot the distribution of the outcome for each treatment on a single, pretty plot.

        Features
        --------
        - High-DPI canvas + scalable fonts
        - Default Matplotlib colors; KDE & mean lines match their histogram colors
        - Numeric outcomes: shared x-range (optional), optional KDE, quantile clipping
        - Categorical outcomes: normalized grouped bars by treatment
        - Optional hi-res export (PNG/SVG/PDF)
        """
        import numpy as np
        import pandas as pd
        import matplotlib as mpl
        import matplotlib.pyplot as plt

        # ---------- Helpers -----------------------------------------------------
        def _silverman_bandwidth(x: np.ndarray) -> float:
            x = np.asarray(x, float)
            n = x.size
            if n < 2:
                return 0.04
            sd = np.std(x, ddof=1)
            iqr = np.subtract(*np.percentile(x, [75, 25]))
            s = sd if iqr <= 0 else min(sd, iqr / 1.34)
            h = 0.9 * s * n ** (-1 / 5)
            return float(max(h, 1e-6))

        def _kde_unbounded(x: np.ndarray, xs: np.ndarray, h: float) -> np.ndarray:
            """
            Gaussian KDE on R, implemented with NumPy (no SciPy).
            Handles degenerate cases by drawing a small bump at the mean.
            """
            x = np.asarray(x, float)
            if x.size == 0:
                return np.zeros_like(xs)
            if x.size < 2 or np.std(x) < 1e-12:
                mu = float(np.mean(x)) if x.size else 0.0
                h0 = max(h, 1e-3)
                z = (xs - mu) / h0
                return np.exp(-0.5 * z ** 2) / (np.sqrt(2 * np.pi) * h0)
            diff = (xs[None, :] - x[:, None]) / h
            kern = np.exp(-0.5 * diff ** 2) / (np.sqrt(2 * np.pi) * h)
            return kern.mean(axis=0)

        def _first_patch_color(patches, fallback):
            for p in patches:
                fc = p.get_facecolor()
                if fc is not None:
                    return fc
            return fallback

        # ---------- Data & columns ---------------------------------------------
        df = self.d.df
        t_col = treatment or self.d.treatment
        y_col = target or self.d.target
        if t_col not in df.columns or y_col not in df.columns:
            raise ValueError("Specified treatment/outcome columns not found in DataFrame.")

        treatments = pd.unique(df[t_col])  # preserves input order
        # Filter rows with valid outcome & treatment
        valid = df[[t_col, y_col]].dropna()
        if valid.empty:
            raise ValueError("No non-missing values for the selected treatment/outcome.")

        # ---------- Figure with high DPI & scaled fonts ------------------------
        rc = {
            "font.size": 11 * font_scale,
            "axes.titlesize": 13 * font_scale,
            "axes.labelsize": 12 * font_scale,
            "legend.fontsize": 10 * font_scale,
            "xtick.labelsize": 10 * font_scale,
            "ytick.labelsize": 10 * font_scale,
        }
        with mpl.rc_context(rc):
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

            # ---------- Branch: categorical vs numeric -------------------------
            if not pd.api.types.is_numeric_dtype(valid[y_col]):
                # CATEGORICAL: normalized grouped bars
                vals = pd.unique(valid[y_col])
                # Stable, readable category order
                vals_sorted = sorted(vals, key=lambda v: (str(type(v)), str(v)))
                width = 0.8 / max(1, len(treatments))
                x = np.arange(len(vals_sorted))

                # Color cycle
                cycle = mpl.rcParams["axes.prop_cycle"].by_key().get("color", ["C0", "C1", "C2", "C3"])

                for i, tr in enumerate(treatments):
                    sub = valid.loc[valid[t_col] == tr, y_col]
                    counts = sub.value_counts(normalize=True)
                    heights = [float(counts.get(v, 0.0)) for v in vals_sorted]
                    ax.bar(x + i * width, heights, width=width, alpha=alpha,
                           label=f"{tr} (n={sub.shape[0]})",
                           color=cycle[i % len(cycle)],
                           edgecolor="white", linewidth=0.6)

                ax.set_xticks(x + (len(treatments) - 1) * width / 2)
                ax.set_xticklabels([str(v) for v in vals_sorted])
                ax.set_ylabel("Proportion")
                ax.set_xlabel(str(y_col))
                ax.set_title("Outcome distribution by treatment (categorical)")
                ax.grid(True, axis="y", linewidth=0.5, alpha=0.45)
                for spine in ("top", "right"):
                    ax.spines[spine].set_visible(False)
                ax.legend(title=str(t_col), frameon=False)
                fig.tight_layout()

            else:
                # NUMERIC: overlay histograms (+ optional KDE) per treatment
                y_all = valid[y_col].to_numpy()

                # Shared x-limits for all treatments if requested
                if sharex:
                    if clip:
                        lo, hi = np.quantile(y_all, [clip[0], clip[1]])
                    else:
                        lo, hi = np.nanmin(y_all), np.nanmax(y_all)
                    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
                        lo, hi = float(np.nanmin(y_all)), float(np.nanmax(y_all))
                    hist_range = (float(lo), float(hi))
                    ax.set_xlim(*hist_range)
                else:
                    hist_range = None  # each call to hist will expand limits as needed

                # Keep track of colors actually used so KDE/means match
                cycle = mpl.rcParams["axes.prop_cycle"].by_key().get("color", ["C0", "C1", "C2", "C3"])
                used_colors = {}

                # Draw hists
                for i, tr in enumerate(treatments):
                    y_vals = valid.loc[valid[t_col] == tr, y_col].to_numpy()
                    y_vals = y_vals[np.isfinite(y_vals)]
                    if y_vals.size == 0:
                        continue

                    h = ax.hist(
                        y_vals,
                        bins=bins,
                        density=density,
                        alpha=alpha,
                        label=f"{tr} (n={y_vals.size})",
                        range=hist_range,
                        edgecolor="white",
                        linewidth=0.6,
                        color=None,  # let Matplotlib choose
                    )
                    color_this = _first_patch_color(h[2], cycle[i % len(cycle)])
                    used_colors[tr] = color_this

                # KDE overlays (SciPy-free, stable)
                if kde and len(used_colors) > 0:
                    # Build a common grid for smooth lines
                    if hist_range is None:
                        # Determine from all numeric values (optionally clipped)
                        if clip:
                            lo, hi = np.quantile(y_all, [clip[0], clip[1]])
                        else:
                            lo, hi = np.nanmin(y_all), np.nanmax(y_all)
                        if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
                            lo, hi = float(np.nanmin(y_all)), float(np.nanmax(y_all))
                    else:
                        lo, hi = hist_range

                    xs = np.linspace(float(lo), float(hi), 800)

                    for tr in treatments:
                        if tr not in used_colors:
                            continue
                        y_vals = valid.loc[valid[t_col] == tr, y_col].to_numpy()
                        y_vals = y_vals[np.isfinite(y_vals)]
                        if y_vals.size == 0:
                            continue
                        hbw = _silverman_bandwidth(y_vals)
                        dens = _kde_unbounded(y_vals, xs, hbw)
                        # If histogram is counts, scale KDE area roughly to counts for visual parity
                        if not density:
                            # approximate scaling by total count and bin width near midrange
                            bw = (hi - lo) / (bins if isinstance(bins, int) else 30)
                            dens = dens * y_vals.size * bw
                        ax.plot(xs, dens, linewidth=2.2, color=used_colors[tr],
                                label=f"{tr} (KDE)")

                # Mean lines
                for tr in treatments:
                    y_vals = valid.loc[valid[t_col] == tr, y_col].to_numpy()
                    y_vals = y_vals[np.isfinite(y_vals)]
                    if y_vals.size == 0:
                        continue
                    mu = float(np.mean(y_vals))
                    # Clamp mean line to visible range if sharex & clipped
                    if sharex and hist_range is not None:
                        mu = float(np.clip(mu, hist_range[0], hist_range[1]))
                    ax.axvline(mu, linestyle=":", linewidth=1.8,
                               color=used_colors.get(tr, "k"), alpha=0.95)

                ax.set_xlabel(str(y_col))
                ax.set_ylabel("Density" if density else "Count")
                ax.set_title("Outcome distribution by treatment")
                ax.grid(True, linewidth=0.5, alpha=0.45)
                for spine in ("top", "right"):
                    ax.spines[spine].set_visible(False)
                ax.legend(title=str(t_col), frameon=False)
                fig.tight_layout()

            # -------- Optional high-res save -----------------------------------
            if save is not None:
                ext = str(save).lower().split(".")[-1]
                _dpi = save_dpi or (300 if ext in {"png", "jpg", "jpeg", "tif", "tiff"} else dpi)
                fig.savefig(
                    save,
                    dpi=_dpi,
                    bbox_inches="tight",
                    pad_inches=0.1,
                    transparent=transparent,
                    facecolor="none" if transparent else "white",
                )

        plt.close(fig)
        return fig

    from typing import Optional, Tuple

    def outcome_boxplot(
            self,
            treatment: Optional[str] = None,
            target: Optional[str] = None,
            figsize: Tuple[float, float] = (9, 5.5),
            dpi: int = 220,
            font_scale: float = 1.15,
            showfliers: bool = True,
            patch_artist: bool = True,
            save: Optional[str] = None,  # "boxplot.png" / ".svg" / ".pdf"
            save_dpi: Optional[int] = None,
            transparent: bool = False,
    ):
        """
        Prettified boxplot of the outcome by treatment.

        Features
        --------
        - High-DPI figure, scalable fonts
        - Soft modern color styling (default Matplotlib palette)
        - Optional outliers, gentle transparency
        - Optional save to PNG/SVG/PDF
        """
        import numpy as np
        import pandas as pd
        import matplotlib as mpl
        import matplotlib.pyplot as plt

        # --- Data setup --------------------------------------------------------
        df = self.d.df
        t_col = treatment or self.d.treatment
        y_col = target or self.d.target

        if t_col not in df.columns or y_col not in df.columns:
            raise ValueError("Specified treatment/outcome columns not found in DataFrame.")

        # Drop rows with missing outcome
        df_valid = df[[t_col, y_col]].dropna()
        if df_valid.empty:
            raise ValueError("No valid rows with both treatment and outcome present.")

        treatments = pd.unique(df_valid[t_col])
        data = [df_valid.loc[df_valid[t_col] == tr, y_col].values for tr in treatments]

        # --- Matplotlib rc settings --------------------------------------------
        rc = {
            "font.size": 11 * font_scale,
            "axes.titlesize": 13 * font_scale,
            "axes.labelsize": 12 * font_scale,
            "legend.fontsize": 10 * font_scale,
            "xtick.labelsize": 10 * font_scale,
            "ytick.labelsize": 10 * font_scale,
        }

        with mpl.rc_context(rc):
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

            # Use Matplotlib default color cycle
            cycle = mpl.rcParams["axes.prop_cycle"].by_key().get("color", ["C0", "C1", "C2", "C3"])
            colors = [cycle[i % len(cycle)] for i in range(len(treatments))]

            # --- Draw boxplot ---------------------------------------------------
            bp = ax.boxplot(
                data,
                patch_artist=patch_artist,
                labels=[str(tr) for tr in treatments],
                showfliers=showfliers,
                boxprops=dict(linewidth=1.1, alpha=0.8),
                whiskerprops=dict(linewidth=1.0, alpha=0.8),
                capprops=dict(linewidth=1.0, alpha=0.8),
                medianprops=dict(linewidth=2.0, color="black"),
                flierprops=dict(
                    marker="o",
                    markersize=4,
                    markerfacecolor="grey",
                    alpha=0.6,
                    markeredgewidth=0.3,
                ),
            )

            # --- Colorize boxes with soft fill ---------------------------------
            if patch_artist:
                for patch, color in zip(bp["boxes"], colors):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.35)
                    patch.set_edgecolor(color)

            # --- Titles and cosmetics ------------------------------------------
            ax.set_xlabel(str(t_col))
            ax.set_ylabel(str(y_col))
            ax.set_title("Outcome by treatment (boxplot)")
            ax.grid(True, axis="y", linewidth=0.5, alpha=0.45)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            fig.tight_layout()

            # --- Optional save -------------------------------------------------
            if save is not None:
                ext = str(save).lower().split(".")[-1]
                _dpi = save_dpi or (300 if ext in {"png", "jpg", "jpeg", "tif", "tiff"} else dpi)
                fig.savefig(
                    save,
                    dpi=_dpi,
                    bbox_inches="tight",
                    pad_inches=0.1,
                    transparent=transparent,
                    facecolor="none" if transparent else "white",
                )

        return fig

    def outcome_plots(self,
                      treatment: Optional[str] = None,
                      target: Optional[str] = None,
                      bins: int = 30,
                      density: bool = True,
                      alpha: float = 0.5,
                      figsize: Tuple[float, float] = (7, 4),
                      sharex: bool = True) -> Tuple[plt.Figure, plt.Figure]:
        """
        Plot the distribution of the outcome for every treatment on one plot,
        and also produce a boxplot by treatment to visualize outliers.

        Parameters
        ----------
        treatment : Optional[str]
            Treatment column name. Defaults to the treatment stored in the CausalEDA data.
        target : Optional[str]
            Target/outcome column name. Defaults to the outcome stored in the CausalEDA data.
        bins : int
            Number of bins for histograms when the outcome is numeric.
        density : bool
            Whether to normalize histograms to form a density.
        alpha : float
            Transparency for overlaid histograms.
        figsize : tuple
            Figure size for the plots.
        sharex : bool
            If True and the outcome is numeric, use the same x-limits across treatments.

        Returns
        -------
        Tuple[matplotlib.figure.Figure, matplotlib.figure.Figure]
            (fig_distribution, fig_boxplot)
        """
        fig_hist = self.outcome_hist(
            treatment=treatment,
            target=target,
            bins=bins,
            density=density,
            alpha=alpha,
            figsize=figsize,
            sharex=sharex,
        )
        fig_box = self.outcome_boxplot(
            treatment=treatment,
            target=target,
            figsize=figsize,
        )
        return fig_hist, fig_box

    def m_features(self) -> pd.DataFrame:
        """Return feature attribution from the fitted m(x) model.
        
        - CatBoost path: SHAP attributions with columns 'shap_mean' and 'shap_mean_abs',
          sorted by 'shap_mean_abs'. Uses transformed feature names from the preprocessor.
        - Sklearn path (LogisticRegression): absolute coefficients reported as 'coef_abs'.
        """
        # Check if model has been fitted
        if not hasattr(self, '_fitted_model') or self._fitted_model is None:
            raise RuntimeError("No fitted propensity model found. Please call fit_m() first.")
        if not hasattr(self, '_feature_names') or self._feature_names is None:
            raise RuntimeError("Feature names not available. Please call fit_m() first.")
        
        if isinstance(self._fitted_model, CatBoostClassifier):
            try:
                from catboost import Pool
                if not hasattr(self, '_X_for_shap') or self._X_for_shap is None:
                    raise RuntimeError("Preprocessed data for SHAP computation not available. Please call fit_m() first.")
                shap_pool = Pool(data=self._X_for_shap)
                shap_values = self._fitted_model.get_feature_importance(type='ShapValues', data=shap_pool)
                shap_values_no_bias = shap_values[:, :-1]
                shap_mean = np.mean(shap_values_no_bias, axis=0)
                shap_mean_abs = np.mean(np.abs(shap_values_no_bias), axis=0)
                feature_names = list(self._feature_names)
                if len(feature_names) != shap_values_no_bias.shape[1]:
                    raise RuntimeError("Feature names length does not match SHAP values. Ensure transformed names are used.")
                # Adjust shap_mean to have magnitude equal to shap_mean_abs while preserving sign
                shap_mean_signed = np.sign(shap_mean) * shap_mean_abs
                result_df = pd.DataFrame({
                    'feature': feature_names,
                    'shap_mean': shap_mean_signed,
                    'shap_mean_abs': shap_mean_abs,
                })
                # Sort by shap_mean_abs (magnitude) descending for determinism
                result_df = result_df.sort_values('shap_mean_abs', ascending=False).reset_index(drop=True)
                # Strip ColumnTransformer/pipeline prefixes like 'num__' or 'cat__' for readability
                try:
                    result_df['feature'] = result_df['feature'].astype(str).str.replace(r'^[^_]+__', '', regex=True)
                except Exception:
                    pass
                # Augment with probability-scale metrics using baseline p0 = mean m
                p0 = float(np.mean(getattr(self, '_m', None))) if hasattr(self, '_m') else np.nan
                if not np.isfinite(p0):
                    raise RuntimeError("Baseline m estimates not available to compute probability-based columns. Fit m first.")
                p0 = float(np.clip(p0, 1e-9, 1 - 1e-9))
                logit_p0 = float(np.log(p0 / (1.0 - p0)))
                result_df['odds_mult_abs'] = np.exp(result_df['shap_mean_abs'].values)
                result_df['exact_pp_change_abs'] = 1.0 / (1.0 + np.exp(-(logit_p0 + result_df['shap_mean_abs'].values))) - p0
                result_df['exact_pp_change_signed'] = 1.0 / (1.0 + np.exp(-(logit_p0 + result_df['shap_mean'].values))) - p0
                return result_df
            except Exception as e:
                raise RuntimeError(f"Failed to extract SHAP values from CatBoost model: {e}")
        elif hasattr(self._fitted_model, 'named_steps') and hasattr(self._fitted_model.named_steps.get('clf'), 'coef_'):
            try:
                clf = self._fitted_model.named_steps['clf']
                coef_abs = np.abs(clf.coef_[0])
                prep = self._fitted_model.named_steps.get('prep')
                if hasattr(prep, 'get_feature_names_out'):
                    try:
                        feature_names = [str(n) for n in prep.get_feature_names_out()]
                    except Exception:
                        feature_names = [f"feature_{i}" for i in range(len(coef_abs))]
                else:
                    feature_names = [f"feature_{i}" for i in range(len(coef_abs))]
                if len(coef_abs) != len(feature_names):
                    raise RuntimeError("Feature names length does not match coefficients.")
                df = pd.DataFrame({'feature': feature_names, 'importance': coef_abs, 'coef_abs': coef_abs})
                # Strip ColumnTransformer/pipeline prefixes like 'num__' or 'cat__' for readability
                try:
                    df['feature'] = df['feature'].astype(str).str.replace(r'^[^_]+__', '', regex=True)
                except Exception:
                    pass
                df = df.sort_values('importance', ascending=False).reset_index(drop=True)
                return df
            except Exception as e:
                raise RuntimeError(f"Failed to extract feature importance from sklearn model: {e}")
        else:
            raise RuntimeError(f"Feature importance extraction not supported for model type: {type(self._fitted_model)}")

    # Back-compat shim
    def treatment_features(self) -> pd.DataFrame:
        _warn_once("treatment_features()", "m_features()")
        return self.m_features()

