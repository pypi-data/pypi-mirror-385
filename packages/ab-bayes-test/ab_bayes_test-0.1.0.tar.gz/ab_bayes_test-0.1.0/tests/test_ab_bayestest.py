import pytest
import pandas as pd
import numpy as np
from ab_bayes_test import ABBayesTest

def test_lift_proportion():
    np.random.seed(42)
    group_a = np.random.binomial(1, 0.3, size=20)
    group_b = np.random.binomial(1, 0.5, size=20)
    df = pd.DataFrame({"group": ["A"]*20 + ["B"]*20,
                       "value": np.concatenate([group_a, group_b])})
    
    ab_test = ABBayesTest(df, "group", "value", metric_type="proportion")
    ab_test.run()
    lift = ab_test.lift()
    
    assert len(lift) == ab_test.sampling_size
    assert np.mean(lift) > 0  # ensure B > A
