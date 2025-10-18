# Bayesian A/B Testing

## Overview

This repository implements Bayesian A/B testing for both **proportion** and **mean** metrics. The project supports:

- **Conjugate inference** (closed-form posterior sampling)
- **MCMC inference** (Metropolis-Hastings sampling)

**Note:** MCMC inference for **proportion metrics** is experimental and may require further tuning for proper convergence. Conjugate inference works reliably for both means and proportions.

## Installation

Clone the repository directly:

```bash
git clone https://github.com/thiagogsdsa/ab-bayes-test.git
cd ab-bayes-test
```

## Usage

Check the `examples/` folder for demonstration scripts:

- `1.3_mean_compare.py`: compares treatment vs. control for mean metrics
- `1.x_proportion_compare.py`: (planned) examples for proportion metrics

Example usage:

```python
from ab_bayes_test import ABBayesTest
import pandas as pd

df = pd.read_csv("data/example.csv")
ab_test = ABBayesTest(df, group_col="group", value_col="value", metric_type="mean")
ab_test.fit()
print(ab_test.results(ci=0.95))
```

## Methodology

For detailed methodology and theory, see [Bayesian A/B Testing Notes (PDF)](docs/pdf/theory.pdf).

**Proportion Metrics:**

1. **Prior Definition** – Beta prior
2. **Posterior Inference**
   - **Conjugacy** – Beta-Binomial closed-form
   - **MCMC** – Binomial likelihood with Metropolis-Hastings (experimental)

**Mean Metrics:**

1. **Prior Definition** – Normal prior
2. **Posterior Inference**
   - **Conjugacy** – Normal-Normal closed-form
   - **MCMC** – Normal likelihood with sample normalization for numerical stability

**Posterior Summary:**

- Posterior mean
- Posterior standard deviation
- Credible interval (e.g., 95%)
- Lift:

```
Lift = (theta_treatment / theta_control) - 1
```

- Probability of treatment superiority: fraction of posterior samples where treatment > control

**Note:** Although MCMC uses normalized data for numerical stability, all reported posterior summaries are converted back to the original scale for interpretability.

## References

1. Gelman, A., Carlin, J. B., Stern, H. S., & Rubin, D. B. (2013). *Bayesian Data Analysis (3rd ed.)*. CRC Press. [Link](https://www.stat.columbia.edu/~gelman/book/)
2. PyMC Documentation (2024). *Bayesian A/B Testing Example*. [Link](https://www.pymc.io/projects/docs/en/stable/)
3. Stan Development Team (2024). *Stan User’s Guide*. [Link](https://mc-stan.org/users/documentation/)

## Contribution & Feedback

If you notice bugs, issues, or have suggestions for improvement, feel free to open an issue or contact me via email.

**Author:** Thiago Guimarães
**Email:** [thiago.guimaraes.sto@gmail.com](mailto:thiago.guimaraes.sto@gmail.com)
**LinkedIn:** [thiagogsdsa](https://www.linkedin.com/in/thiagogsdsa)
**GitHub:** [thiagogsdsa](https://github.com/thiagogsdsa)
**Repository:** [ab-bayes-test](https://github.com/thiagogsdsa/ab-bayes-test)
