# Linear Drift Detector

A lightweight, explainable **concept drift detection** library based on **linear coefficient analysis** using OLS (Ordinary Least Squares).  
This package is designed for both **regression** and **classification** models to detect when the underlying data relationship between features and targets has changed over time — i.e., when **concept drift** occurs.

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Core Idea](#core-idea)
3. [Mathematical Foundation](#mathematical-foundation)
4. [Algorithm Overview](#algorithm-overview)
5. [Installation](#installation)
6. [Quick Start Example (Regression)](#quick-start-example-regression)
7. [Example (Classification)](#example-classification)
8. [Output Details](#output-details)
9. [Interpretation](#interpretation)
10. [When to Use](#when-to-use)
11. [Limitations](#limitations)
12. [License](#license)

---

## Introduction

In many deployed ML systems, the relationship between inputs (`X`) and target (`y`) evolves over time.  
This evolution — often subtle — causes **concept drift**, where a model trained on historical data no longer reflects the true structure of incoming (production) data.

Instead of retraining blindly, it’s essential to **detect** when this drift occurs.  
That’s where the `linear-drift-detector` helps: it quantifies the **change in feature relationships** using **OLS regression coefficients**.

---

## Core Idea

Even if your production model is nonlinear (like Random Forest or XGBoost),  
we can still *proxy* the structural relationship between features and targets using a **simple linear fit**.

We fit an **OLS model** on:
- The training dataset (`X_train`, `y_train`)
- The production dataset (`X_prod`, `y_prod_prediction` — actual labels or predicted outputs)

Then, we compare the learned coefficients.

If the coefficients shift significantly between the two datasets,  
it indicates a **potential concept drift** in the data-generating process.

---

## Mathematical Foundation

Let the relationship between target `y` and features `X` be modeled as:

$$
y = X\beta + \epsilon
$$

Where:
- $X$: Feature matrix  
- $\beta$: Coefficient vector  
- $\epsilon$: Random noise term

We fit two models:

$$
\hat{\beta}_{train} = (X_{train}^T X_{train})^{-1} X_{train}^T y_{train}
$$

$$
\hat{\beta}_{prod} = (X_{prod}^T X_{prod})^{-1} X_{prod}^T y_{prod}
$$

Then compute:

$$
\Delta \beta = \hat{\beta}_{prod} - \hat{\beta}_{train}
$$

To statistically test if the difference is significant:

$$
Z_i = \frac{\hat{\beta}_{prod,i} - \hat{\beta}_{train,i}}{\sqrt{SE_{train,i}^2 + SE_{prod,i}^2}}
$$

Where $SE$ is the standard error of each coefficient.

The two-tailed p-value is computed as:

$$
p_i = 2(1 - \Phi(|Z_i|))
$$

---

## Algorithm Overview

1. **Input:**
   - `X_train`, `y_train`: historical (training) data
   - `X_prod`, `y_prod_prediction`: production data and outputs (actual or predicted)
2. **Fit two OLS models:**
   - `model_train = OLS(y_train, X_train)`
   - `model_prod = OLS(y_prod_prediction, X_prod)`
3. **Extract coefficients and standard errors**
4. **Compute difference metrics:**
   - Δβ (coefficient shift)
   - L2 norm distance
   - Z-test and p-values for statistical significance
5. **Return diagnostic report**

---

## Installation 

```bash
pip install linear-drift-detector
```

## Quick Start Example (Regression)
```bash
import numpy as np
from linear_drift_detector import linear_coefficient_shift

# Generate training data
np.random.seed(42)
X_train = np.random.randn(200, 3)
y_train = 3*X_train[:,0] - 2.5*X_train[:,1] + 4*X_train[:,2] + np.random.randn(200)*0.5

# Generate production data (shifted relationships)
X_prod = np.random.randn(200, 3)
y_prod_pred = 4*X_prod[:,0] - 1.5*X_prod[:,1] + 5*X_prod[:,2] + np.random.randn(200)*0.5

# Run drift detection
result = linear_coefficient_shift(X_train, y_train, X_prod, y_prod_pred)

# Print diagnostic outputs
print(result["z_test"])
print("L2 Distance:", result["l2_distance"])
```
### Example Output 

| | coef_train | coef_prod | diff    | z_value | p_value |
|----------|------------|-----------|---------|---------|---------|
| const    | 0.01234    | 0.02345   | 0.01111 | 0.28    | 0.776   |
| x1       | 2.98456    | 3.99123   | 1.00667 | 5.12    | 0.000   |
| x2       | -2.48721   | -1.49834  | 0.98887 | 4.97    | 0.000   |
| x3       | 4.01245    | 4.98678   | 0.97433 | 4.54    | 0.000   |

**L2 Distance: 1.71**

**Interpretation**: Significant p-values (< 0.05) and large L2 distance indicate a strong concept drift.

--- 

## Example (Classification)
Even for classification tasks, OLS can be used as a proxy detector for internal data structure shifts.

``` bash
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from linear_drift_detector import linear_coefficient_shift

# Training data
X_train, y_train = make_classification(
    n_samples=200, n_features=3, n_informative=3, n_redundant=0, random_state=42
)

# Production data with changed separation
X_prod, y_prod = make_classification(
    n_samples=200, n_features=3, n_informative=3, n_redundant=0, class_sep=1.5, random_state=99
)

# Simulate model predictions
clf = LogisticRegression()
clf.fit(X_train, y_train)
y_prod_pred = clf.predict_proba(X_prod)[:, 1]

# Detect drift
result = linear_coefficient_shift(X_train, y_train, X_prod, y_prod_pred)
print(result["z_test"])
print("L2 Distance:", result["l2_distance"])
```
Here, the production dataset has a different internal structure, and the drift detector highlights this through coefficient divergence. The output is similar to regression. 

---
## Output Details

The function returns a dictionary:

| Key | Description |
|-----|-------------|
| `coef_train` | Coefficients from training OLS |
| `coef_prod` | Coefficients from production OLS |
| `coef_diff` | Difference vector (production - training) |
| `l2_distance` | Magnitude of coefficient drift |
| `z_test` | DataFrame with z-values and p-values for each coefficient |

## Interpretation

High L2 Distance: overall structural shift in data

Low p-values (< 0.05): statistically significant coefficient drift

Large Δβ: feature relationship changed

Stable coefficients: no significant drift

---
## When to Use

Monitor deployed regression or classification models

Detect data drift when retraining is expensive

Quantify how much internal data relationship has changed

Build interpretability into data drift detection pipelines

---
## Limitations

OLS assumes a linear relationship — may not match nonlinear models

Requires same feature dimensionality (`X_train.shape == X_prod.shape`)

Sensitive to scaling (consider standardizing features)

Works best as a proxy detector, may not as a perfect substitute for full statistical drift tests

---
## License

MIT License © 2025
Developed for the open-source data science community.
