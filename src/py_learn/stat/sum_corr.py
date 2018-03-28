'''
Created on Feb 4, 2018

@author: jj
'''
import numpy as np

def rv_gen_with_corr(size, corr_coef):
    """
    Generate random variables samples with `size` and correlation coefficient
    equal to `corr_coef`
    """
    rv_1 = np.random.normal(size=size)
    rv_2 = np.random.normal(size=size)
    corr_mat = np.array([[1.0, corr_coef],
                         [corr_coef, 1.0]])
    L = np.linalg.cholesky(corr_mat)
    rv = L @ np.array([rv_1, rv_2])
#     print(f'Correlation between the two variables:\n{np.corrcoef(rv[0], rv[1])}')
    return rv[0], rv[1]

def calc_mean_corr(x, y, p):
    """
    Calculate the correlation between aggregation of `x` and `y` with period length `p`.
    """
    assert len(x) == len(y)
    assert len(x) % p == 0
    new_dim = len(x) // p
    A = np.zeros((new_dim, len(x)))
    for i in range(new_dim):
        A[i, (i*p):(i*p+p)] = 1.0/p
    return np.corrcoef(A @ x, A @ y)[0,1]

def sim(num_sim=100, num_months=100, p=22, corr_coef=0.2):
    size=num_months * p
    A = np.zeros((num_months, size))
    for i in range(num_months):
        A[i, (i*p):(i*p+p)] = 1.0/p
    new_corr_arr = [0] * num_sim
    for i in range(num_sim):
        x, y = rv_gen_with_corr(size, corr_coef)
        new_corr_arr[i] = np.corrcoef(A @ x, A @ y)[0,1]
    return new_corr_arr

def sim_stop(num_sim=100, num_months=100, p=22, corr_coef=0.2):
    size=num_months * p
    A = np.zeros((num_months, size))
    for i in range(num_months):
        A[i, (i*p):(i*p+p)] = 1.0/p
    for i in range(num_sim):
        x, y = rv_gen_with_corr(size, corr_coef)
        corr = np.corrcoef(A @ x, A @ y)[0,1]
        if corr < 0.02:
            print(f'correlation of the sums: {corr}')
            break
    corr_arr = np.zeros(num_months)
    for j in range(num_months):
        corr_arr[j] = np.corrcoef(x[(j*p):(j*p+p)], y[(j*p):(j*p+p)])[0,1]
    return (x, y), (A @ x, A @ y), corr_arr

