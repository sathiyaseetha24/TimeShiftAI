import numpy as np

def simulate_path(base_salary, growth_rate, volatility, risk_tolerance, years=10, seed=42):
    rng = np.random.default_rng(seed)
    salary = [base_salary]
    for _ in range(years - 1):
        change = growth_rate + rng.normal(0, volatility)
        salary.append(salary[-1] * (1 + change * risk_tolerance))
    return salary
