'''
Created on Aug 25, 2015

@author: Aaron Klein
'''

import scipy
import numpy as np

from base_maximizer import BaseMaximizer


class GradientAscent(BaseMaximizer):
    '''
    Performs a gradient ascent based on the LBFGS algorithm. It draws N configurations uniformly and start a local search from the M best random point.
    For the resulting M points that were obtain via local search it returns the point with the highest function value.
    '''

    def __init__(self, objective_function, X_lower, X_upper, n_random=1000, n_restarts=10):
        self.n_restarts = n_restarts
        self.n_random = n_random
        super(GradientAscent, self).__init__(objective_function, X_lower, X_upper)

    def _acquisition_fkt_wrapper(self, x):
        # LFBGS minimizes that's why we have to add a minus here
        fx, gx = self.objective_func(x, derivative=True)
        return -fx[0], -gx[0, 0]

    def maximize(self):
        # Draw N random configurations uniformly
        random_points = np.random.uniform(self.X_lower, self.X_upper, (self.n_random, self.X_lower.shape[0]))
        fvals = np.zeros([self.n_random])
        for i in range(self.n_random):
            fvals[i] = self.objective_func(random_points[i])

        # Use the M best random configurations as start points for a gradient ascent
        best = fvals.argsort()[-self.n_restarts:]

        x_opt = np.zeros([self.n_restarts, self.X_lower.shape[0]])
        fval = np.zeros([self.n_restarts])
        for i in range(self.n_restarts):
            start_point = random_points[best[i]]
            res = scipy.optimize.fmin_l_bfgs_b(self._acquisition_fkt_wrapper, start_point, bounds=zip(self.X_lower, self.X_upper))
            x_opt[i] = res[0]
            fval[i] = res[1]
        # Return the point with the highest function value
        best = np.argmax(fval)
        return np.array([x_opt[best]])
