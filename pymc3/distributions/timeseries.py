import theano.tensor as T

from .continuous import Normal, Flat
from .distribution import Continuous

__all__ = ['AR1', 'GaussianRandomWalk']


class AR1(Continuous):
    """
    Autoregressive process with 1 lag.

    Parameters
    ----------
    k : tensor
       effect of lagged value on current value
    tau_e : tensor
       precision for innovations
    """
    def __init__(self, k, tau_e, *args, **kwargs):
        super(AR1, self).__init__(*args, **kwargs)
        self.k = k
        self.tau_e = tau_e
        self.tau = tau_e * (1 - k ** 2)
        self.mode = 0.

    def logp(self, x):
        k = self.k
        tau_e = self.tau_e

        x_im1 = x[:-1]
        x_i = x[1:]
        boundary = Normal.dist(0, tau_e).logp

        innov_like = Normal.dist(k * x_im1, tau_e).logp(x_i)
        return boundary(x[0]) + T.sum(innov_like) + boundary(x[-1])


class GaussianRandomWalk(Continuous):
    """
    Random Walk with Normal innovations

    Parameters
    ----------
    tau : tensor
        tau > 0, innovation precision
    sd : tensor
        sd > 0, innovation standard deviation (alternative to specifying tau)
    mu: tensor
        innovation drift, defaults to 0.0
    init : distribution
        distribution for initial value (Defaults to Flat())
    """
    def __init__(self, tau=None, init=Flat.dist(), sd=None, mu=0.,
                 *args, **kwargs):
        super(GaussianRandomWalk, self).__init__(*args, **kwargs)
        self.tau = tau
        self.sd = sd
        self.mu = mu
        self.init = init
        self.mean = 0.

    def logp(self, x):
        tau = self.tau
        sd = self.sd
        mu = self.mu
        init = self.init

        x_im1 = x[:-1]
        x_i = x[1:]

        innov_like = Normal.dist(mu=x_im1 + mu, tau=tau, sd=sd).logp(x_i)
        return init.logp(x[0]) + T.sum(innov_like)
