from cvxopt import solvers, matrix
import collections
import numpy as np

solvers.options["show_progress"] = False

def downside_variance(returns, m, short_sales=False):
    # min (1/T)sum(y_t^2)
    # s.t. mu*x >= m
    # e'x = 1
    # y_t >= 0
    # y_t >= (mu-ret_t)*x
    # {x >= 0} - Shorting constraint
    
    returns = np.asmatrix(returns)
    means = np.mean(returns, axis=1)

    N, T = returns.shape
    
    P = (2.0/T)*np.concatenate((np.zeros((N, N+T)),
        np.concatenate((np.zeros((T, N)), np.eye(T)), axis=1)),axis=0)

    q = np.zeros((N+T, 1))
    
    A = np.zeros((1, T+N))
    A[0, 0:N] = 1.0
    
    b = [1.0]
    
    h = np.zeros((2*T + 1, 1))
    h[0, 0] = -m
    
    G_0 = np.zeros((1, N+T))
    G_0[0, 0:N] = -np.transpose(means)
    
    G_1 = np.concatenate((np.zeros((T, N)), -1.0*np.eye(T)), axis=1)
    G_2 = np.concatenate((np.transpose(-returns+(means*np.ones((1, T)))), -1.0*np.eye(T)), axis=1)
    G = np.concatenate((G_0, G_1, G_2), axis=0)
    
    if not short_sales:
        h = np.concatenate((h, np.zeros((N, 1))), axis=0)
        G = np.concatenate((G, np.concatenate((-1.0*np.eye(N), np.zeros((N, T))), axis=1)), axis=0)

    sol = solvers.qp(
        matrix(P),
        matrix(q),
        matrix(G),
        matrix(h),
        matrix(A),
        matrix(b)
    )

    return sol['x'][:N]

if __name__ == '__main__':
    rets = {
        'Stocks': [
            26.81, -8.78, 22.69, 16.36, 12.36, -10.10, 23.94, 11.00, -8.47, 3.94, 14.30, 18.99,
            -14.69, -26.47, 37.23, 23.93, -7.16, 6.57, 18.61, 32.50, -4.92, 21.55, 22.56, 6.27,
            31.17, 18.67, 5.25, 16.61, 31.69, -3.10, 30.46, 7.62, 10.08, 1.32, 37.58, 22.96,
            33.36, 28.58, 21.04, -9.10, -11.89, -22.10, 28.68
        ],
        'Bonds': [
            2.20, 5.72, 1.79, 3.71, 0.93, 5.12, -2.86, 2.25, -5.63, 18.92, 11.24, 2.39, 3.29,
            4.00, 5.52, 15.56, 0.38, -1.26, -1.26, -2.48, 4.04, 44.28, 1.29, 15.29, 32.27,
            22.39, -3.03, 6.84, 18.54, 7.74, 19.36, 7.34, 13.06, -7.32, 25.94, 0.13, 12.02,
            14.45, -7.51, 17.22, 5.51, 15.15, 0.54
        ],
        'MM': [
            2.33, 2.93, 3.38, 3.85, 4.32, 5.40, 4.51, 6.02, 8.97, 4.90, 4.14, 5.33, 9.95, 8.53,
            5.20, 4.65, 6.56, 10.03, 13.78, 18.90, 12.37, 8.95, 9.47, 8.38, 8.27, 6.91, 6.77,
            8.76, 8.45, 7.31, 4.43, 2.92, 2.96, 5.45, 5.60, 5.29, 5.50, 4.68, 5.30, 6.40, 1.82,
            1.24, 0.98
        ]
    }

    r = []
    for k in sorted(rets.keys()):
        r.append([1.0+i/100 for i in rets[k]])
    means = np.mean(r, axis=1)
    steps = np.linspace(min(means), max(means), num=100)
    print sorted(rets.keys()) 
    xs = map(lambda x: np.transpose(downside_variance(r, x))[0], steps)
    for i, row in enumerate(xs):
        print steps[i], map(lambda x: "%0.3f"%x, row), np.dot(means, row)

