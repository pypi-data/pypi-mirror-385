import copy
import datetime
import functools
import os
import pickle
import shutil
import warnings
from collections import defaultdict, namedtuple
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import varwg
from varwg import helpers as my
from varwg.core import base, plotting
from varwg.meteo import avrwind, meteox2y

# from varwg.meteo.meteox2y_cy import pot_s_rad
from varwg.meteo.meteox2y import pot_s_rad, sunshine_riseset

# from varwg.time_series_analysis import (
#     conditional_sim as csim,
# )
from varwg.time_series_analysis import (
    cresample,
    distributions,
    models,
)
from varwg.time_series_analysis import (
    resample as resampler,
)
from varwg.time_series_analysis import seasonal_distributions as sd
from varwg.time_series_analysis import (
    time_series as ts,
)

read_met = base.read_met

try:
    from varwg import config as conf
except ImportError:
    from varwg import config_template as conf

    conf_filepath = conf.__file__
    if conf_filepath.endswith(".pyc"):
        conf_filepath = conf_filepath[:-1]


def delete_cache():
    shutil.rmtree(conf.cache_dir)


def dump_data(
    times_,
    data,
    var_names,
    p,
    q,
    extra="",
    random_state=None,
    out_dir=None,
    conversions=None,
):
    """Dumps the given datetimes and data in an ascii file and random state in
    a pickle file."""
    if out_dir is None:
        out_dir = conf.out_dir
    if p is None:
        p = 0
    if conversions:
        data = np.copy(data)
        for conversion in list(conversions):
            times_, data, var_names = conversion(times_, data, var_names)
    outfilename = "VARMA_p%d_q%d_sim%s.dat" % (p, q, extra)
    outfilepath = os.path.join(out_dir, outfilename)
    with open(outfilepath, "w") as txt_file:
        txt_file.write("time\t" + "\t".join(var_names) + os.linesep)
        for time, values in zip(times_, data.T):
            txt_file.write(
                "%s\t%s%s"
                % (
                    time.isoformat(),
                    "\t".join(
                        conf.out_format[var_name] % val
                        for var_name, val in zip(var_names, values)
                    ),
                    os.linesep,
                )
            )

    if random_state is not None:
        with open(outfilepath + ".random_state", "wb") as pi_file:
            pickle.dump(random_state, pi_file)

    return outfilepath


def metfile2df(met_file):
    try:
        pd_kwds = dict(
            skiprows=5,
            index_col=0,
            parse_dates=True,
            sep="\t",
            date_parser=varwg.times.cwr2datetime,
        )
        met_df = pd.read_csv(met_file, **pd_kwds).astype(float)
    except TypeError:

        def date_hour2datetime(date_str, hour_str):
            return varwg.times.str2datetime(
                "%s %s" % (date_str, hour_str), "%d. %m %y %H"
            )

        pd_kwds = dict(
            index_col=0, parse_dates=[[0, 1]], date_parser=date_hour2datetime
        )
        met_df = pd.read_csv(met_file, **pd_kwds).astype(float)
    return met_df


def outfile2df(outfile):
    pd_kwds = dict(index_col=0, parse_dates=[0], sep="\t")
    return pd.read_csv(outfile, **pd_kwds).astype(float)


def metfile2hdf5(met_file, h5_filename=None, key="met"):
    if h5_filename is None:
        h5_filename = os.path.splitext(met_file)[0] + ".h5"
    met_df = metfile2df(met_file)
    met_df.to_hdf(h5_filename, key)


def seasonal_back(
    dist_sol,
    norm_data,
    var_names,
    doys=None,
    solution_template="%s",
    pass_doys=True,
    var_names_back=None,
    mean_shifts=None,
):
    """Transform variables from normal to real-world marginals.

    Parameters
    ----------
    dist_sol : mapping like dict or shelve object
        Distribution fitting parameters.
    norm_data : (K, T) array
        Normally distributed data.
    var_names : (K,) sequence of str
        Variable names used as dist_sol[solution_template % var_name].
    doys : None or (T,) float array, optional
        Only needed for different doys than the calibration dataset.
    solution_template : str, optional
        Used in the form dist_sol[solution_template % var_name]

    Returns
    -------
    data : (K, T) array
        Re-transformed data
    """
    data = np.empty_like(norm_data)
    if mean_shifts is None:
        mean_shifts = defaultdict(lambda: None)
    if var_names_back is None:
        var_names_back = var_names
    for var_name in var_names_back:
        var_i = var_names.index(var_name)
        var = norm_data[var_i]
        # for var_i, (var_name, var) in enumerate(zip(var_names, norm_data)):
        distribution, solution = dist_sol[solution_template % var_name]
        if hasattr(distribution, "dist") and isinstance(
            distribution.dist, distributions.Normal
        ):
            # in this case, we do not need a qenuine qq-transform, the normal
            # inverse Z transform suffices, AND is immune to producing nans
            # for "extreme" values in the standard-normal world!
            if doys is not None:
                _T = (2 * np.pi / 365 * doys)[np.newaxis, :]
            else:
                _T = None
            mus, sigmas = distribution.trig2pars(solution, _T)
            data[var_i] = var * sigmas + mus
        else:
            quantiles = distributions.norm.cdf(var)
            doys_ = doys if pass_doys else None
            data[var_i] = distribution.ppf(
                solution,
                quantiles,
                doys=doys_,
                mean_shift=(mean_shifts.get(var_name, None)),
            )
    return data


def sim_byvariable(values, times, p=2, aggregation="%w"):
    aggr_values, aggr_times = ts.time_part_average(
        values, times, aggregation, expand=False, return_times=True
    )
    dist = sd.SeasonalDist(distributions.norm, aggr_values, aggr_times)
    solution = dist.fit(T0=50)
    trans = distributions.norm.ppf(dist.cdf(solution), 0, 1)
    B, sigma_u = models.VAR_LS(trans, p=p)
    T = len(aggr_values)
    sim = models.VAR_LS_sim(B, sigma_u, T - p)
    retrans = dist.ppf(solution, distributions.norm.cdf(sim, 0, 1))
    retrans = np.repeat(retrans, varwg.times.time_part_average.repeats)
    return retrans


def interannual_variability(T, mean_arrival=30, disturbance_std=0.1):
    """Generate a time series used as a disturbance within the std-norm world.
    Disturbances are simulated as gaussian changes occuring after t timesteps,
    where t is drawn from an exponential distribution.
    """

    def arrival():
        return distributions.expon.ppf(
            varwg.rng.random(),
            lambd=1.0 / mean_arrival,
            # loc=1 weil wir taegliche Werte
            # berechnen und daher 1 Tag die
            # kuerzest moegliche Dauer ist
            x0=1,
        )

    def disturbance():
        return abs(
            distributions.norm.ppf(
                varwg.rng.random(),
                sigma=float(disturbance_std),
            )
        )

    m_t = np.zeros(T)
    breaks_ii = [t] = [int(round(arrival()))]
    while t < T:
        breaks_ii += [breaks_ii[-1] + int(round(arrival()))]
        t = breaks_ii[-1]
    sign = 1
    for break_, next_break in zip(breaks_ii[:-1], breaks_ii[1:]):
        period_length = min(int(round(next_break - break_)), len(m_t) - break_)
        window = np.bartlett(period_length + 1)[:-1]
        if window.mean() <= 0:
            window = np.ones(period_length) / period_length
        else:
            window /= window.mean()
        m_t[break_:next_break] = sign * disturbance() * window
        sign *= -1
    return m_t


def sw_diurnal(date, daily_sw_data, del_t=3600):
    """add standard daily cycle to daily mean sw data
    Parameters
    ----------
    date: array
        date in unix timestamps
    daily_sw_data: array
    del_t: int
        timestep of output data in seconds, default = 3600s

    Returns
    -------
    date_: array
        output date in unix timestamps
    data_: array
        sw data in del_t-steps"""
    nn = 86400.0 / del_t
    date_ = np.arange(date[0], date[-1] + 86400, del_t)
    swmax = pot_s_rad(
        varwg.times.unix2str(date_, "%Y-%m-%dT%H:%M"),
        lat=conf.latitude,
        longt=conf.longitude,
    )
    swmax_daily = np.average(swmax.reshape(-1, nn), axis=1).repeat(nn)
    fkt = swmax / swmax_daily
    data_ = daily_sw_data.repeat(nn) * fkt
    return date_, data_


class VarWG(plotting.Plotting):
    """A Vector-Autoregressive weather generator.

    >>> my_vg = VG(("theta", "Qsw", "ILWR", "rh", "u", "v"))
    >>> my_vg.fit()
    >>> times_out, sim_data = my_vg.simulate()
    """

    def __init__(
        self,
        var_names,
        met_file=None,
        sum_interval=24,
        max_nans=12,
        plot=False,
        separator="\t",
        refit=None,
        detrend_vars=None,
        verbose=True,
        data_dir=None,
        cache_dir=None,
        dump_data=True,
        non_rain=None,
        rain_method="regression",
        conf_update=None,
        station_name=None,
        infill=False,
        fit_kwds=None,
        **met_kwds,
    ):
        """A vector autoregressive moving average (VARMA) weather generator.
        Initializing a VG-object does the following:
            - read input data from a met-file
            - aggregate it according to sum_interval
            - convert the data using seasonal distributions

        To fit the VARMA process call fit(). Afterwards
        simulated time series can be obtained with simulate().

        Parameters
        ----------
        var_names : sequence containing strings
        met_file : string, dict, pandas DataFrame or None, optional
            If None, value will be read from config.py.
            Data can also be supplied directly with a dict, mapping variable
            names to ndarrays containing the data. The dictionary has to
            contain an item with the key "datetimes" which has to contain an
            ndarray of datetime objects.
            If data is supplied as a pandas DataFrame, time information will be
            taken from its index.
        sum_inverval : int or sequence of ints, optional
            Number of timesteps to aggregate. If a sequence is given, its
            elements are used variable - specific. In this case the sequence
            has to have the same length as var_names.
            Default 24 corresponds to the case of hourly input data and daily
            simulation
        plot : boolean, optional
            Plot all kinds of information. Warning: a lot of windows will
            appear.
        separator : str or None, optional
            String that separates columns in the met_file. It is fed to the
            split method of str, so None corresponds to any whitespace.
        refit : None, 'all' or sequence of strings from var_names, optional
            Instead of using cached solutions for the seasonal distribution
            fit, run the fit again and cache it.
        detrend_vars : sequence containing strings or None, optional
            Remove a linear trend from the variables.
        verbose : boolean, optional
            Be more verbose if True.
        data_dir : str, optional
            Overwrites the data_dir variable from the config-file.
        cache_dir : str, optional
            Overwrites the cache_dir variable from the config-file.
        dump_data : boolean, optional
            Write simulation and disaggregation results (filename can be
            infered by the outfilepath attribute).
        non_rain : None or sequence of str, optional
            Variables used for rain gap filling.
        rain_method : 'distance' or 'regression', optional
            Which method to use for rain gap filling. 'distance' uses
            euclidean distance to wet states. 'regression' uses a
            regression to extrapolate from wet do dry amounts.
        conf_update : dict or None, optional
            Replaces variables in the config file.
        station_name : str or None, optional
            Name of the station. Usefull in combination with
            weathercop multisite generation.
        infill : boolean, optional
            VAR-based infilling of missing values.
        """
        # external_var_names=None,
        # "fix" unicode problems
        var_names = [str(var_name) for var_name in var_names]
        self.station_name = station_name
        if conf_update is not None:
            self._conf_update(conf_update)
        super(VarWG, self).__init__(
            var_names,
            met_file=met_file,
            sum_interval=sum_interval,
            plot=plot,
            separator=separator,
            refit=refit,
            detrend_vars=detrend_vars,
            verbose=verbose,
            data_dir=data_dir,
            cache_dir=cache_dir,
            seasonal_fitting=True,
            dump_data=dump_data,
            non_rain=non_rain,
            rain_method=rain_method,
            max_nans=max_nans,
            infill=infill,
            fit_kwds=fit_kwds,
            **met_kwds,
        )
        # simulated residuals
        self.ut = None

    def _conf_update(self, conf_update):
        for name, value in conf_update.items():
            setattr(conf, name, value)
            setattr(base.conf, name, value)
            setattr(plotting.conf, name, value)
            if hasattr(self, name):
                setattr(self, name, value)

    def __getattribute__(self, name):
        # Plotting overwrites __getattribute__ to do a seasonal fitting
        # only if it is (implicitly) requested. That behaviour is only usefull
        # when creating a Plotting instance
        return base.Base.__getattribute__(self, name)

    def __str__(self):
        return f"VG({self.station_name}, {self.rain_method})"

    def fit(
        self,
        p=None,
        q=0,
        p_max=10,
        seasonal=True,
        ex=None,
        ex_kwds=None,
        extro=False,
        doy_width=60,
        fft_order=2,
        *args,
        **kwds,
    ):
        """p is the order of autoregressive process.
        q the order of the moving average process
        If p is not given, it is selected using the Schwartz Information
        Criterion."""
        self.p, self.q, self.seasonal = p, q, seasonal
        self.ex_in = ex
        if q == 0:
            if p is None:
                if self.verbose:
                    print("Perfoming VAR order selection: ", end=" ")
                try:
                    if ex is None:
                        p = models.VAR_order_selection(self.data_trans, p_max)
                    else:
                        est_kwds = {} if ex_kwds is None else ex_kwds
                        est_kwds["ex"] = ex
                        o_select = models.VAR_order_selection
                        p = o_select(
                            self.data_trans,
                            p_max,
                            estimator=models.VAREX_LS,
                            est_kwds=est_kwds,
                        )
                    self.p = p
                except ValueError:
                    warnings.warn(
                        "Could not fit the VAR process. Trying to "
                        "remove extreme values."
                    )
                    mi, ma = np.min(self.data_trans), np.max(self.data_trans)
                    if ma > -mi:
                        self.data_trans.ravel()[
                            np.argmax(self.data_trans)
                        ] = np.nan
                    else:
                        self.data_trans.ravel()[
                            np.argmin(self.data_trans)
                        ] = np.nan
                    if not self.infill:
                        self.data_trans = my.interp_nonfin(self.data_trans)
                    self.fit(p, q, p_max, seasonal, ex, ex_kwds)
                if self.verbose:
                    print("p=%d seems parsimonious to me" % self.p)
                    if p == 0:
                        print(
                            "Wow, you should not do any autoregressive "
                            "modeling."
                        )
            # fit a VAR-model
            if self.seasonal:
                if self.verbose:
                    print("Fitting the seasonal VAR model.")
                self.svar_doy_width = doy_width
                self.svar_fft_order = fft_order
                self.Bs, self.sigma_us = models.SVAR_LS(
                    self.data_trans,
                    self.data_doys,
                    self.p,
                    var_names=self.var_names,
                    verbose=self.verbose,
                    doy_width=doy_width,
                    fft_order=fft_order,
                    *args,
                    **kwds,
                )
                self.residuals = models.SVAR_residuals(
                    self.data_trans, self.data_doys, self.Bs, self.p
                )
            else:
                if self.verbose:
                    print("Fitting the VAR model.")
                if extro:

                    def transforms(x):
                        sim_sea = seasonal_back(
                            self.dist_sol, x, self.var_names, self.data_doys
                        )
                        return sim_sea / self.sum_interval

                    def backtransforms(x):
                        return self._fit_seasonal(values=x, filter_nans=False)[
                            0
                        ]

                    B, self.sigma_u = models.VAR_LS_extro(
                        self.data_trans,
                        (self.data_raw / self.sum_interval),
                        transforms,
                        backtransforms,
                        p=self.p,
                        *args,
                        **kwds,
                    )
                    self.residuals = models.VAR_LS_extro.residuals
                elif ex is None:
                    B, self.sigma_u = models.VAR_LS(
                        self.data_trans, self.p, *args, **kwds
                    )
                    self.residuals = models.VAR_residuals(
                        self.data_trans, B, self.p
                    )
                else:
                    B, self.sigma_u = models.VAREX_LS(
                        self.data_trans, p, ex, *args, **kwds
                    )
                # we call it AM to have one place for VARMA parameters
                self.AM = B
            self.p = p

        else:
            if (p is None) and (q is None):
                if self.verbose:
                    print("Perfoming VARMA order selection: ", end=" ")
                self.p, self.q = p, q = models.VARMA_order_selection(
                    self.data_trans, p_max, plot_table=self.plot, *args, **kwds
                )
                if self.verbose:
                    print("p=%d and q=%d seems parsimonious to me" % (p, q))
            else:
                self.p, self.q = p, q
            # fit a VARMA-model
            if self.verbose:
                print("Fitting the VARMA model")
            # the VARMA implementation is for mean-adjusted data. the data
            # should have zero mean, asuming the fit for the qq-transformation
            # was perfect.
            # ... and nothing is perfect. so we subtract the mean here
            self.means = self.data_trans.mean(axis=1)[:, np.newaxis]
            self.data_trans -= self.means

            AM, sigma_u, residuals = models.VARMA_LS_prelim(
                self.data_trans, p, q, *args, **kwds
            )

            self.data_trans += self.means
            self.AM, self.sigma_u, self.residuals = AM, sigma_u, residuals

    def _gen_online_transform(self, dist_sol, solution_template="%s"):
        """Generates the callables for time_series_analysis.models.VAR_LS_sim
        that enforce the factor-change in precipitation."""
        r_index = self.var_names.index("R")
        r_dist, solution = dist_sol[solution_template % "R"]

        def transform(value_vector, t):
            # back-transform precipitation, apply the real-world
            # factor and transform back to standard-normal
            r_stdn = value_vector[r_index]
            doy = self.sim_doys[t]
            quantile = distributions.norm.cdf(r_stdn, 0, 1)
            r_real = r_dist.ppf(solution, quantile, doys=doy)
            value_vector[r_index] = r_real * self.r_fact
            return value_vector

        return transform

    def simulate(
        self,
        T=None,
        *,
        mean_arrival=None,
        disturbance_std=None,
        theta_incr=None,
        r_fact=None,
        theta_grad=None,
        fixed_variables=None,
        primary_var="theta",
        scale_prim=True,
        climate_signal=None,
        start_str=None,
        stop_str=None,
        random_state=None,
        ex=None,
        ex_kwds=None,
        seed_before_sim=None,
        # loc_shift=False,
        resample=False,
        res_kwds=None,
        asy=False,
        residuals=None,
        sim_func=None,
        sim_func_kwds=None,
        phase_randomize=False,
        phase_randomize_vary_mean=True,
        return_rphases=False,
        rphases=None,
        p_kwds=None,
        taboo_period_min=None,
        taboo_period_max=None,
        conversions=None,
    ):
        """Simulate based on data from __init__ and the fit from calling
        self.fit().
        To choose a specific order of AR and MA call fit(p, q) before calling
        simulate. Otherwise fit will be called without parameters, so p and q
        will be guessed by applying an information criterion.

        Parameters
        ----------
        T : None or int, optional
            Number of timesteps to simulate. T=None produces as many simulation
            timesteps as there were in the data used for fitting the VARMA
            process.
        mean_arrival : float, optional
            average length of warm/cold periods [d]
        disturbance_std : float, optional
            standard deviation of deviation of warm/cold periods from mean
        theta_incr : float, optional
            increase in average of temperature [deg C]
        r_fact : float, optional
            factor to increase precipitation
        theta_grad : float, optional
            gradient increase in average of temperature [deg C / (T)]
        fixed_variables : dictionary mapping var_names to None or (T,) ndarrays
            Keeps the provided time - series fixed. Mappings to None indicate
            that the input data should be used as a fixed variable.
            Can be used to simulate hierarchically.
        primary_var : str, one of var_names from __init__ or sequence of those,
                optional
            All disturbances (mean_arrival, distrubance_std, theta_incr,
            theta_grad and climate_signal) correspond to changes in this
            variable.
        scale_prim : boolean, optional
            Allow primary variables to influence each other.
            Only effective when using multiple primary variables!
        climate_signal : (T,) ndarray
            A time series of the 'primary_var'. Differences between
            'climate_signal' and the seasonal mean are used to perturb the
            VAR process.
        start_str : str of format '%m-%d %H', optional
            String representation of the start date of the simulation.
        stop_str : str of format '%m-%d %H', optional
            String representation of the end date of the simulation.
        random_state : str, tuple as returned by numpy.random.get_state() or
                       None, optional
            Sets the random state before simulating.
            *str* is interpreted as a pickle file containing the random state.
            *tuple* is interpreted as the random state itself.
        ex : (T,) ndarray or function
            External variable. If given as a function, ex_t will be generated
            by calling ex(Y[:t], **ex_kwds), with Y being the simulated values.
        ex_kwds : None or dict
            Keyword arguments to be passed to ex.
        seed_before_sim : None or int, optional
            Seed the Random Generator before simulating. The integer
            passed will be used as seed (also if it is a 0).
            (_scenario_parameters also draws random numbers).
        loc_shift : bool, optional
            Change on the primary variables will be removed after simulation
            and added to the backtransformed variables.
        res_kwds : dict or None, optional
            Keywords for the resampler, if not None, use resampling.
            See `time_series_analysis.resample.resample` for allowed
            parameters.
        residuals : (K, T+) ndarray
            Residuals with which to run the time series model. If more
            than T columns are supplied the additional time steps (at
            the beginning) will be used for spin-up.
        sim_func : None or callable, optional
            Callback to replace the time series model.
        sim_func_kwds : None or dict
            Extra keyword arguments for sim_func
        conversions : iterable of callables

        Returns
        -------
        sim_times : (T,) ndarray of datetime objects
        sim_sea : (K, T) float ndarray

        """
        if sim_func_kwds is None:
            sim_func_kwds = dict()
        if isinstance(random_state, str):
            with open(random_state, "rb") as pi_file:
                random_state = pickle.load(pi_file)
        if random_state is not None:
            varwg.rng.bit_generator.state = random_state
        # we record the random state to later dump it
        pre_sim_random_state = varwg.rng.bit_generator.state

        if mean_arrival is None and disturbance_std is not None:
            raise RuntimeError(
                "Must specify mean_arrival if disturbance_std is given."
            )
        if disturbance_std is None and mean_arrival is not None:
            raise RuntimeError(
                "Must specify disturbance_std if mean_arrival is given."
            )
        (
            self.disturbance_std,
            self.theta_incr,
            self.r_fact,
            self.theta_grad,
            self.mean_arrival,
        ) = [
            None if x is None else np.atleast_1d(x).astype(float)
            for x in (
                disturbance_std,
                theta_incr,
                r_fact,
                theta_grad,
                mean_arrival,
            )
        ]
        self.fixed_variables = fixed_variables
        if primary_var is None:
            # we got to have one
            self.primary_var = primary_var = self.var_names[0]
        if isinstance(primary_var, str):
            self.primary_var = (primary_var,)
            self.climate_signal = np.atleast_1d(climate_signal)
            # self.climate_signal = np.atleast_2d(climate_signal)
        else:
            self.primary_var = primary_var
            self.climate_signal = (
                np.array([None] * len(primary_var))
                if climate_signal is None
                else climate_signal
            )
        # if self.climate_signal.dtype == object:
        #     # we have to back up, this has not worked
        #     self.climate_signal = tuple(self.climate_signal[0])
        for var_name in self.primary_var:
            if var_name not in self.var_names:
                raise ValueError(f"{primary_var=} not in {self.var_names=}")
        if return_rphases and not phase_randomize:
            warnings.warn(
                "Phases were requested, yet phase randomization is not enabled.\n"
                "Setting phase_randomize=True now"
            )
            phase_randomize = True
        if rphases and not phase_randomize:
            warnings.warn(
                "Phases were supplied, yet phase randomization is not enabled.\n"
                "Setting phase_randomize=True now"
            )
            phase_randomize = True
        self.phase_randomize = phase_randomize
        self.phase_randomize_vary_mean = phase_randomize_vary_mean

        if T is None:
            if climate_signal is not None:
                # if we have multiple primary variables, elements of climate
                # signal can be None. we also have to be careful, because the
                # number of primary variables could be interpreted as T
                # climate_signal = np.atleast_2d(climate_signal)
                _signal = np.array(
                    [_ for _ in self.climate_signal if _ is not None]
                )
                self.T_sim = np.atleast_2d(_signal).shape[1]
            else:
                self.T_sim = self.T_summed
        else:
            self.T_sim = T

        # we depend on order selection if self.fit was not called
        if self.p is None and sim_func is None:
            self.fit(**self.fit_kwds)

        # if this is True, we still call self._gen_sim_times because
        # of expected side-effects
        self.sim_times_is_times = start_str is None and stop_str is None
        self.sim_times = self._gen_sim_times(
            start_str=start_str, stop_str=stop_str
        )
        # self.T_sim has to be reset when self._gen_sim_times is
        # called, but not inside self.disaggregate
        self.T_sim = len(self.sim_times)

        if self.phase_randomize:
            if self.theta_incr is None:
                self.theta_incr = np.zeros(len(self.primary_var))
            if residuals is None:
                residuals = self.residuals

        # converts the given parameters so they are understood in the
        # std-normal world
        # to store effect of scenario parameters by primary variable
        self._m_single, self._m_t_single, self._m_trend_single = [], [], []
        m, m_t, m_trend = sc_pars = self._scenario_parameters(
            theta_incr,
            theta_grad,
            disturbance_std,
            climate_signal,
            phase_randomize,
            scale_prim,
            primary_var_sim=sim_func_kwds.get("primary_var_sim", None),
        )
        # store to be able to play outside with it later
        self.m, self.m_t, self.m_trend = m, m_t, m_trend

        fixed_data = self._prepare_fixed_data()

        # relative changes have to be dealt with differently: the
        # factor is dependent on the distribution and therefore can
        # only be done when we now the value of the to-be-transformed
        # variable.
        if r_fact:
            transform = self._gen_online_transform(self.dist_sol)
        else:
            transform = None

        if self.verbose:
            print("Simulating a time-series.")
        if type(seed_before_sim) is int:
            varwg.reseed(seed_before_sim)
        var_names_back = None
        if sim_func is not None:
            if sim_func_kwds is None:
                sim_func_kwds = {}
            sim = sim_func(self, sc_pars, **sim_func_kwds)
            # this is weathercop-specific
            if (stop_at := sim_func_kwds.get("stop_at", None)) is not None:
                vine = sim_func_kwds["wcop"].vine
                var_names_back = vine.varnames[: stop_at + 1]
            if return_rphases := sim_func_kwds.get("return_rphases", False):
                sim, ranks_sim, rphases = sim
            else:
                sim, ranks_sim = sim
        elif resample or res_kwds is not None:
            # in contrast to the parametric models, we do not
            # transform anything
            # here we combine any change in theta_incr
            m_resampler = (m + m_t + m_trend[:, None])[self.primary_var_ii]
            # m_resampler = m[:, 0]
            try:
                res_kwds = my.ADict(res_kwds)
            except TypeError:
                res_kwds = my.ADict()
            cy = "cy" in res_kwds and res_kwds["cy"]
            resample_raw = res_kwds.pop("resample_raw", False)
            if cy:
                sim, self.res_indices, self.candidates = cresample.resample(
                    (
                        self.data_raw / self.sum_interval
                        if resample_raw
                        else self.data_trans
                    ),
                    self.times,
                    self.p,
                    n_sim_steps=self.T_sim,
                    theta_incr=theta_incr if resample_raw else m_resampler,
                    theta_i=self.primary_var_ii,
                    # cache_dir=conf.cache_dir,
                    cache_dir=self.cache_dir,
                    verbose=self.verbose,
                    return_candidates=True,
                    z_transform=resample_raw,
                    **(res_kwds - "cy"),
                )
            else:
                sim, self.res_indices, self.candidates = resampler.resample(
                    data=(
                        self.data_raw / self.sum_interval
                        if resample_raw
                        else self.data_trans
                    ),
                    dtimes=self.times,
                    p=self.p,
                    n_sim_steps=self.T_sim,
                    theta_incr=theta_incr if resample_raw else m_resampler,
                    bias=None,
                    theta_i=self.primary_var_ii,
                    # cache_dir=conf.cache_dir,
                    cache_dir=self.cache_dir,
                    verbose=self.verbose,
                    # verbose=True,
                    return_candidates=True,
                    z_transform=resample_raw,
                    **res_kwds,
                )
        elif self.q in (0, None):
            # simulate VAR-time-series
            if self.seasonal:
                # scale u to not get too much variance
                # n_unique_doys = len(np.unique(self.data_doys))
                # uu = self.svar_doy_width / n_unique_doys * residuals
                uu = residuals
                sim = models.SVAR_LS_sim(
                    self.Bs,
                    self.sigma_us,
                    self.sim_doys,
                    m,
                    ia=m_t,
                    m_trend=m_trend,
                    fixed_data=fixed_data,
                    u=uu,
                    phase_randomize=phase_randomize,
                    return_rphases=return_rphases,
                    rphases=rphases,
                    p_kwds=p_kwds,
                    taboo_period_min=taboo_period_min,
                    taboo_period_max=taboo_period_max,
                )
                if return_rphases:
                    sim, rphases = sim
                self.ut = models.SVAR_LS_sim.ut
            else:
                if asy:
                    if isinstance(asy, str):
                        asy = [self.var_names.index(asy)]
                    elif asy:
                        asy = self.var_names
                    sim = models.VAR_LS_sim_asy(
                        self.AM,
                        self.sigma_u,
                        self.T_sim,
                        self.data_trans,
                        self.p,
                        skewed_i=asy,
                        verbose=self.verbose,
                        var_names=self.var_names,
                        u=residuals,
                    )
                    self.ut = models.VAR_LS_sim_asy.ut
                elif ex is None:
                    sim = models.VAR_LS_sim(
                        self.AM,
                        self.sigma_u,
                        self.T_sim,
                        m,
                        ia=m_t,
                        m_trend=m_trend,
                        fixed_data=fixed_data,
                        transform=transform,
                        u=residuals,
                        phase_randomize=phase_randomize,
                        rphases=rphases,
                        return_rphases=return_rphases,
                        p_kwds=p_kwds,
                        taboo_period_min=taboo_period_min,
                        taboo_period_max=taboo_period_max,
                    )
                    if return_rphases:
                        sim, rphases = sim
                else:
                    sim, self.ex_out = models.VAREX_LS_sim(
                        self.AM,
                        self.sigma_u,
                        self.T_sim,
                        ex,
                        m,
                        ia=m_t,
                        m_trend=m_trend,
                        ex_kwds=ex_kwds,
                        u=residuals,
                    )
        else:
            sim = models.VARMA_LS_sim(
                self.AM,
                self.p,
                self.q,
                self.sigma_u,
                # process means that are used as
                # starting values there is some
                # confusion here...
                self.means,
                self.T_sim,
                m,
                ia=m_t,
                m_trend=m_trend,
                fixed_data=fixed_data,
                u=residuals,
            )

        if self.plot and self.sigma_u is not None:
            ts.matr_img(
                self.sigma_u,
                "Noise Covariance matrix",
                self.var_names,
                self.var_names,
            )

        # # location shifting
        # # DO NOT USE
        # if loc_shift:
        #     __import__("pdb").set_trace()
        #     sim = self._location_shift_normal(sim)

        # transform back
        if resample or res_kwds is not None:

            # use the indices to map back, we do not want any new
            # values to occur here!

            sim_sea = np.array(
                [
                    self.data_raw[
                        self.var_names.index(var_name), self.res_indices
                    ]
                    for var_name in self.var_names
                ]
            )
            sim_sea /= self.sum_interval

            # data_raw = self.data_raw / self.sum_interval
            # sim_sea = (
            #     sim * data_raw.std(axis=1)[:, None]
            #     + data_raw.mean(axis=1)[:, None]
            # )

            # sim_sea = seasonal_back(
            #     self.dist_sol, sim, self.var_names, doys=self.sim_doys
            # )
            # sim_sea /= self.sum_interval

            # if theta_incr > 0:
            #     plt.scatter(self.times, self.data_raw[0] / 24)
            #     plt.scatter(self.times[self.res_indices],
            #                 self.data_raw[0, self.res_indices] / 24)
            #     plt.show()
        else:
            # sim_sea = seasonal_back(self.dist_sol, sim, self.var_names,
            #                         doys=self.sim_doys)
            # sim_sea /= self.sum_interval
            # if "R" in self.var_names:
            #     r_index = self.var_names.index("R")
            #     sim_sea[r_index] *= self.sum_interval[r_index]

            if self.theta_incr is not None:
                mean_shifts = dict(
                    theta=self.theta_incr
                    * self.sum_interval.ravel()[self.primary_var_ii]
                )
            else:
                mean_shifts = None
            sim_sea = seasonal_back(
                self.dist_sol,
                sim,
                self.var_names,
                doys=self.sim_doys,
                var_names_back=var_names_back,
                mean_shifts=mean_shifts,
                # pass_doys=(not self.sim_times_is_times)
            )
            sim_sea /= self.sum_interval

        # spicyness can lead to infs
        sim_sea[~np.isfinite(sim_sea)] = np.nan
        sim_sea = my.interp_nonfin(sim_sea, max_interp=3)

        # if loc_shift:
        #     sim_sea = self._location_shift_back(sim_sea)

        if conversions:
            for conversion in list(conversions):
                self.sim_times, sim_sea, self.var_names_conv = conversion(
                    self.sim_times, np.copy(sim_sea), self.var_names
                )

        # lets store this so we can play with it from the outside
        self.sim, self.sim_sea = sim, sim_sea

        if self.verbose:
            self.print_means()

        if self.dump:
            extra = "" if self.station_name is None else self.station_name
            self.outfilepath = dump_data(
                self.sim_times,
                self.sim_sea,
                self.var_names,
                self.p,
                0 if self.q is None else self.q,
                extra=extra,
                random_state=pre_sim_random_state,
                out_dir=self.data_dir,
                conversions=conversions if conversions else conf.conversions,
            )

        if sim_func is not None:
            if return_rphases:
                return self.sim_times, sim_sea, ranks_sim, rphases
            return self.sim_times, sim_sea, ranks_sim

        if return_rphases:
            return self.sim_times, sim_sea, rphases
        return self.sim_times, sim_sea

    def print_means(self):
        obs = self.to_df("daily input").mean(axis=0)
        obs.name = "obs"
        sim = self.to_df("daily output", with_conversions=False).mean(axis=0)
        sim.name = "sim"
        diff = pd.DataFrame(
            sim.values - obs.values, index=obs.index, columns=["diff"]
        )
        diff_perc = pd.DataFrame(
            100 * (sim.values - obs.values) / obs.values,
            index=obs.index,
            columns=["diff [%]"],
        )
        print(pd.concat([obs, sim, diff, diff_perc], axis=1).round(3))

    # def disaggregate_rm(self, refit=None):
    #     """Random Mixing variant of disaggregation."""
    #     if self.sim is None:
    #         raise RuntimeError("Call simulate first.")

    #     if self.verbose:
    #         print("Disaggregating selected variables.")

    #     data_hourly_trans = self._fit_seasonal_hourly(refit=refit)

    #     # infer the target covariance and autocovariance structure
    #     # from the hourly untransformed data
    #     data_hourly = base.met_as_array(self.met, var_names=self.var_names)
    #     # the nans mess up the calculation of the covariance matrix
    #     data_hourly = data_hourly[:, np.all(np.isfinite(data_hourly), axis=0)]
    #     if isinstance(self.sum_interval, abc.Iterable):
    #         warnings.warn(
    #             "Per-variable sum_interval is not supported " "anymore."
    #         )
    #         disagg_len = self.sum_interval[0]
    #     else:
    #         disagg_len = self.sum_interval

    #     # disaggregate
    #     dht = np.array(data_hourly_trans)
    #     if "R" in self.var_names:
    #         if self.verbose:
    #             print("Transforming 'negative rain'")
    #         # rain_old = np.copy(dht[0])
    #         dht = self._negative_rain(
    #             dht,
    #             self.met["R"],
    #             self.data_doys_raw,
    #             # var_names=("theta", "ILWR", "u", "v")
    #         )

    #         # fig, axs = plt.subplots(self.K, sharex=True)
    #         # for val, ax in zip(dht, axs):
    #         #     ax.plot(dtimes, val)
    #         # axs[0].plot(dtimes, rain_old)
    #         # plt.show()
    #         sum_vars = self.var_names.index("R")
    #     else:
    #         sum_vars = None
    #     cov = np.cov(dht[:, np.all(np.isfinite(dht), axis=0)])
    #     self.data_hourly_trans = dht

    #     # self.plot_transformed_hourly()
    #     # plt.show()

    #     # generate the datetime information of the disaggregated time series.
    #     # how many timesteps are there per day in the input data?
    #     # we assume that the data is not finer than hours
    #     hours_unique = np.unique([dtime.hour for dtime in self.times_orig])
    #     # read timesteps per day (abbreviation, because it is used a lot as an
    #     # index modifier below
    #     tpd = len(hours_unique)
    #     self.dis_times = self._gen_sim_times(
    #         self.T_sim * tpd, output_resolution=1.0
    #     )

    #     def trans(data, doys):
    #         return seasonal_back(
    #             self.dist_sol,
    #             data,
    #             self.var_names,
    #             doys,
    #             solution_template="%s_hourly",
    #         )

    #     t_kwds = dict(doys=times.datetime2doy(self.dis_times))
    #     self.sim_dis = csim.disaggregate_piecewice(
    #         self.sim,
    #         autocov=data_hourly_trans,
    #         disagg_len=disagg_len,
    #         cov=cov,
    #         pool_size=25,
    #         trans=trans,
    #         t_kwds=t_kwds,
    #         verbose=True,
    #         sum_vars=sum_vars,
    #     )

    #     # retransform disaggregated variables
    #     sim_sea_dis = seasonal_back(
    #         self.dist_sol,
    #         self.sim_dis,
    #         self.var_names,
    #         doys=times.datetime2doy(self.dis_times),
    #         solution_template="%s_hourly",
    #     )
    #     # housekeeping
    #     self.sim_sea_dis = sim_sea_dis
    #     # some of the plotting routines depend on the availability of
    #     # the variable names we disaggregated
    #     self.var_names_dis = self.var_names
    #     return self.dis_times, sim_sea_dis

    def disaggregate(
        self,
        var_names_dis=None,
        event_dt=None,
        factors=None,
        doy_tolerance=15,
        latitude=None,
        longitude=None,
    ):
        """Disaggregate variables to hourly time steps by drawing from the
        residuals of the measured data

        Parameters
        ----------
        var_names_dis : list of str, optional
            names of variables to be disaggregated. if None all variables are
            disaggregated
        event_dt : array of datetimes, optional
            days on which factors will be applied to change daily cycle
            amplitudes.
        factors : sequence of length K
            see event_dt

        Returns
        -------
        times_out : array of datetime objects
        sim_sea_dis : array
            simulated variables in hourly time steps. the last day gets lost
        """
        if self.sim is None:
            raise RuntimeError("Call simulate first.")

        # disaggregate selected variables to hourly values, all the others
        # will be repeated 24 times a day. The last day gets lost
        if var_names_dis is None:
            if self.verbose:
                print("Disaggregating all variables")
            var_names_dis = self.var_names
        elif isinstance(var_names_dis, str):
            if self.verbose:
                print("Disaggregating selected variables.")
            var_names_dis = (var_names_dis,)

        if latitude is None:
            latitude = conf.latitude
        if longitude is None:
            longitude = conf.longitude

        # how many timesteps are there per day in the input data?
        # we assume that the data is not finer than hours
        hours_unique = np.unique([dtime.hour for dtime in self.times_orig])
        # read timesteps per day (abbreviation, because it is used a
        # lot as an index modifier below)
        tpd = len(hours_unique)

        self.dis_times = self._gen_sim_times(
            (self.T_sim - 1) * tpd, output_resolution=1.0
        )
        # reset cache
        self._dis_doys = None

        if factors is not None:
            factors = np.asarray(factors)[:, None]

        deltas_input, sim_interps = self._gen_deltas_input(
            var_names_dis,
            tpd,
            longitude=longitude,
            latitude=latitude,
        )
        deltas_drawn, sim_sea_dis = self._add_deltas(
            deltas_input,
            sim_interps,
            var_names_dis,
            tpd,
            event_dt=event_dt,
            factors=factors,
            doy_tolerance=doy_tolerance,
        )

        #  check for variables with limits
        for var_name in var_names_dis:
            var_i = self.var_names.index(var_name)
            limits = copy.copy(conf.par_known[var_name])
            u_kwds = dict()
            if var_name.startswith("Qsw"):

                def pot_s(doys, longitude, latitude):
                    hourly = pot_s_rad(
                        doys,
                        lat=latitude,
                        longt=longitude,
                        tz_mer=None,
                    )
                    return hourly * self.sum_interval[var_i]

                u_kwds = dict(longitude=longitude, latitude=latitude)
                limits["u"] = pot_s
            elif var_name.startswith("sun"):

                def sun_hours(doys):
                    dtimes = varwg.times.doy2datetime(doys)
                    sunrise, sunset = sunshine_riseset(
                        dtimes, longitude, latitude, tz_offset=None
                    )
                    doy_hours = (doys - doys.astype(int)) * 24
                    max_hours = np.full_like(doys, 60)
                    max_hours[(doy_hours < sunrise) & (doy_hours > sunset)] = 0
                    sunrise_dist = 60 * (sunrise - doy_hours)
                    sunset_dist = 60 * (sunset - doy_hours)
                    sunrise_mask = (sunrise_dist > 0) & (sunrise_dist < 60)
                    sunset_mask = (sunset_dist < 0) & (sunset_dist > -60)
                    max_hours[sunrise_mask] = sunrise_dist[sunrise_mask]
                    max_hours[sunset_mask] = 60 + sunset_dist[sunset_mask]
                    return max_hours * self.sum_interval[var_i]

                limits["u"] = sun_hours

            sim_interp = sim_interps[var_i]
            pos_mask = deltas_drawn[var_i] > 0
            neg_mask = ~pos_mask

            # we have to interpret a threshold as a lower limit (no negative
            # rain, please)
            seas_dist, _ = self.dist_sol[var_name]
            if hasattr(seas_dist, "dist") and hasattr(
                seas_dist.dist, "thresh"
            ):
                if limits is None:
                    limits = {}
                # limits["l"] = conf.array_gen(seas_dist.dist.thresh)
                limits["l"] = conf.array_gen(conf.threshold)
                # limits["l"] = conf.array_gen(0.)
                # limits["u"] = conf.array_gen(1.e12)

            if limits is not None and ("u" in limits or "uc" in limits):
                upper_func = limits["u"] if "u" in limits else limits["uc"]
                upper = (
                    upper_func(self.dis_doys[pos_mask], **u_kwds)
                    / self.sum_interval[var_i]
                )
                upper_perc = deltas_drawn[var_i, pos_mask]
                interps = sim_interp[pos_mask]
                upper_dis = interps + upper_perc * (upper - interps)
                sim_sea_dis[var_i, pos_mask] = upper_dis

            if limits is not None and ("l" in limits or "lc" in limits):
                lower_func = limits["l"] if "l" in limits else limits["lc"]
                lower = (
                    lower_func(self.dis_doys[neg_mask])
                    / self.sum_interval[var_i]
                )
                lower_perc = deltas_drawn[var_i, neg_mask]
                interps = sim_interp[neg_mask]
                lower_dis = interps + lower_perc * (interps - lower)
                lower_dis = np.where(lower_dis < lower, lower, lower_dis)
                sim_sea_dis[var_i, neg_mask] = lower_dis

        # sim_sea_dis = np.roll(sim_sea_dis, -1, axis=1)

        # fig, ax = plt.subplots()
        # ax.plot(sim_sea_dis[0], "-o", label="sim_sea_dis")
        # ax.plot(sim_interps[0], "-x", label="sim_interps")
        # daily_rain_out = self.sim_sea[self.var_names.index("R")]
        # m = self.T_sim * tpd - tpd
        # rain_mask_out = (daily_rain_out > 0).repeat(tpd)[:m]
        # for start_i, end_i in my.gaps(rain_mask_out):
        #     ax.axvspan(start_i, end_i, alpha=.5)
        # ax.legend(loc="best")
        # plt.show()

        self.var_names_dis = var_names_dis
        self.sim_sea_dis = sim_sea_dis

        if self.dump:
            # if varnames_dis==None, daily values are returned and dumped:
            self.outfilepath = dump_data(
                self.dis_times,
                sim_sea_dis,
                self.var_names,
                self.p,
                0 if self.q is None else self.q,
                "_disaggregated",
                out_dir=self.data_dir,
                conversions=conf.conversions,
            )

        return self.dis_times, sim_sea_dis

    def _prepare_output(self):
        """Makes the requested conversions defined in the config file and
        returns a dictionary for methods like to_dyresm or to_glm."""
        if self.sim_sea_dis is None:
            raise RuntimeError("Call disaggregate first.")

        dtimes, data, var_names = (
            self.dis_times,
            self.sim_sea_dis,
            self.var_names,
        )
        if conf.conversions:
            for conversion in list(conf.conversions):
                times, data, var_names = conversion(dtimes, data, var_names)
        met = {var_name: vals for var_name, vals in zip(var_names, data)}
        return dtimes, met

    def to_dyresm(
        self, outfilepath, ts=3600, info=None, wind_fct=1.0, output_rh=False
    ):
        """Converts output to a DYRESM input file.

        Parameters
        ----------
        outfilepath : str
            dyresm meteorological bc file
        ts : int
            timestep in dyresm-met-file in seconds, should be divisor of 86400
        info : information text string in file header
        wind_fct : float
            factor for wind speed. Default: 1.0 (for Konstanz wind data: 1.3)

        """
        times_, met_dict = self._prepare_output()

        # the now string! ready cut, easy to handle, simpson's individual
        # emperor stringettes - just the right length!
        now_str = datetime.datetime.now().isoformat(" ")
        moist_varname = "rh" if output_rh else "e"
        template_filepath = os.path.join(
            os.path.dirname(__file__), "dyresm_header_template"
        )
        with open(template_filepath) as template_file:
            template = template_file.read()
        dyresm_header = template.format(
            now_str=now_str, info=info, ts=ts, moist_varname=moist_varname
        )

        if not output_rh:
            if "e" not in met_dict:
                met_dict["e"] = meteox2y.rel2vap_p(
                    met_dict["rh"], met_dict["theta"]
                )
        if "U" not in met_dict:
            met_dict["U"] = avrwind.component2angle(
                met_dict["u"], met_dict["v"]
            )[1]
        met_dict["U"] *= wind_fct
        if "R" not in met_dict:
            met_dict["R"] = np.zeros_like(met_dict["theta"])
        data = np.array(
            [varwg.times.datetime2cwr(times_)]
            + [
                met_dict[var_name]
                for var_name in (
                    "Qsw",
                    "ILWR",
                    "theta",
                    "rh" if output_rh else "e",
                    "U",
                    "R",
                )
            ]
        ).T

        with open(outfilepath, "w") as outfile:
            outfile.write(dyresm_header)
        with open(outfilepath, "ab") as outfile:
            np.savetxt(
                outfile,
                data,
                fmt=(
                    b"%10.5f\t%7.3f\t%7.3f\t%6.2f\t"
                    + (b"%.3f" if output_rh else b"%4.1f")
                    + b"\t%5.2f\t%.6f"
                ),
            )

    def to_glm(self, outfilepath):
        """Converts output to a GLM input file.

        Parameters
        ----------
        outfilepath : path/filename
            glm meteorological bc file
        """
        dtimes, met = self._prepare_output()

        header = (
            "time,ShortWave,LongWave, AirTemp,RelHum, WindSpeed,Rain,"
            "Snow" + os.linesep
        )
        if "U" not in met:
            try:
                met["U"] = avrwind.component2angle(met["u"], met["v"])[1]
            except KeyError:
                warnings.warn("No wind information found. Filling in 0's!!")
                met["U"] = np.zeros_like(met[list(met.keys())[0]])
        if "R" not in met:
            warnings.warn(
                "No precipitation information available. Filling "
                " in with 0's!!"
            )
            met["R"] = np.zeros_like(met[list(met.keys())[0]])
        times_str = varwg.times.datetime2str(dtimes, "%Y-%m-%d %H:%M")
        lines = [
            ",".join(
                [time_str]
                + [
                    "%.6f" % met[key][i]
                    for key in ("Qsw", "ILWR", "theta", "rh", "U", "R")
                ]
                + ["0.0" + os.linesep]  # snow
            )
            for i, time_str in enumerate(times_str)
        ]
        with open(outfilepath, "w") as glm_file:
            glm_file.write(header)
            glm_file.writelines(lines)

    def to_gotm(self, outfilepath, sw_outfilepath=None, rain_outfilepath=None):
        """Converts output to a GOTM input file set (met and separate
        short-wave file).

        Parameters
        ----------
        outfilepath : path/filename
            GOTM meteorological bc file
        sw_outfilepath : path/filename
            GOTM short-wave bc file
        rain_outfilepath : path/filename
            GOTM precipitation bc file
        """
        if sw_outfilepath is None:
            sw_outfilepath = outfilepath[: -len(".dat")] + "_swr.dat"
        if rain_outfilepath is None:
            rain_outfilepath = outfilepath[: -len(".dat")] + "_precip_file.dat"
        dtimes, met = self._prepare_output()

        if "U" not in met:
            try:
                met["wdir"], met["U"] = avrwind.component2angle(
                    met["u"], met["v"]
                )
                # gideon: "I think the cloud cover and wind direction
                # should both be 0 (for the time being...)"
                met["wdir"][:] = 0
            except KeyError:
                warnings.warn("No wind information found. Filling in 0's!!")
                met["wdir"] = met["U"] = np.zeros_like(
                    met[list(met.keys())[0]]
                )
        if "R" not in met:
            warnings.warn(
                "No precipitation information available. Filling "
                " in with 0's!!"
            )
            met["R"] = np.zeros_like(met[list(met.keys())[0]])
        if "air_pressure" not in met:
            met["air_pressure"] = np.full_like(met[list(met.keys())[0]], 1000)
        if "cloud_cover" not in met:
            ilwr = meteox2y.temp2lw(met["theta"])
            met["cloud_cover"] = meteox2y.lw2clouds(
                ilwr, met["theta"], rh=met["rh"]
            )
            met["cloud_cover"][:] = 0

        # relative humidity has to be in %
        rh = met["rh"]
        if np.max(rh) <= 1.5:
            met["rh"] *= 100

        times_str = varwg.times.datetime2str(dtimes, "%Y-%m-%d %H:%M:%S")
        var_names = "U", "cloud_cover", "air_pressure", "theta", "rh", "wdir"
        # fmts = "%.2f", "%.6f", "%.0f", "%.3f", "%.6f"
        lines = [
            "\t".join(
                [time_str]
                + [conf.out_format[key] % met[key][i] for key in var_names]
                + [os.linesep]
            )
            for i, time_str in enumerate(times_str)
        ]

        with open(outfilepath, "w") as gotm_file:
            # gotm_file.write(header)
            gotm_file.writelines(lines)

        # separate short-wave file
        lines = [
            "%s\t%s%s"
            % (time_str, conf.out_format["Qsw"] % met["Qsw"][i], os.linesep)
            for i, time_str in enumerate(times_str)
        ]
        with open(sw_outfilepath, "w") as gotm_file:
            gotm_file.writelines(lines)

        # separate precipitation file
        lines = [
            "%s\t%s%s"
            % (time_str, conf.out_format["R"] % met["R"][i], os.linesep)
            for i, time_str in enumerate(times_str)
        ]
        with open(rain_outfilepath, "w") as gotm_file:
            gotm_file.writelines(lines)

    def to_df(
        self, kind="hourly input", var_names=None, *, with_conversions=True
    ):
        if var_names is None:
            var_names = self.var_names

        data = None
        if kind == "hourly input":
            if "e" in var_names and "e" not in self.met:
                self.met["e"] = meteox2y.rel2vap_p(
                    self.met["rh"], self.met["theta"]
                )
            data = np.array([self.met[var_name] for var_name in var_names])
            index = self.times_orig
        elif kind == "daily input":
            data = self.data_raw / self.sum_interval
            index = self.times
        elif kind == "daily input trans":
            data = self.data_trans
            index = self.times
        elif kind == "daily output trans":
            data = self.sim
            index = self.sim_times
        elif kind == "daily output":
            data = self.sim_sea
            index = self.sim_times
        elif kind == "hourly output":
            data = self.sim_sea_dis
            index = self.dis_times
        else:
            raise RuntimeError(f"kind={kind} not understood")
            return
        if data is None and "output" in kind:
            raise RuntimeError("Call simulate, before requesting output")
        if data.shape[0] != len(var_names):
            data = np.array(
                [data[self.var_names.index(name)] for name in var_names]
            )
        # do not trust that the conversions have any side-effects on
        # its parameters!
        index, data = map(np.copy, (index, data))
        var_names = [name for name in var_names]
        if with_conversions:
            if (
                "trans" not in kind
                and "input" not in kind
                and conf.conversions
            ):
                for conversion in conf.conversions:
                    index, data, var_names = conversion(index, data, var_names)
        df = pd.DataFrame(data=data.T, columns=var_names, index=index)
        df.name = kind
        df.index.name = "time"
        return df

    def infill_trans_nans(self):
        if self.p is None:
            if self.verbose:
                print("Fitting seasonal VAR for infilling.")
            self.fit(**self.fit_kwds)
        data_infilled = models.SVAR_LS_fill(
            self.Bs, self.sigma_us, self.data_doys, self.data_trans
        )
        n_nan_timesteps = (np.isnan(self.data_trans).sum(axis=0) > 0).sum()
        if self.verbose:
            nan_perc = n_nan_timesteps / self.T_summed * 100
            if n_nan_timesteps:
                print(
                    f"Filled in {n_nan_timesteps} time steps ({nan_perc:.1f}%)"
                )
            for var_i, values in enumerate(self.data_trans):
                n_nan_timesteps = np.isnan(values).sum()
                if n_nan_timesteps:
                    nan_perc = n_nan_timesteps / self.T_summed * 100
                    var_name = self.var_names[var_i]
                    print(f"\t{var_name}: {n_nan_timesteps} ({nan_perc:.1f}%)")

        # fig, axs = plt.subplots(nrows=self.K, ncols=1, sharex=True)
        # for var_i, var_name in enumerate(self.var_names):
        #     ax = axs[var_i]
        #     ax.plot(self.times, self.data_trans[var_i], color="k")
        #     ax.plot(self.times, data_infilled[var_i], "--", color="b")
        #     ax.set_title(var_name)
        # fig.suptitle(self.station_name)

        # fig, axs = self.plot_meteogram_hourly()
        # fig, axs = self.plot_meteogram_trans()

        self.data_trans = data_infilled

        # fig, axs = self.plot_meteogram_trans(figs=fig, axss=axs)
        # fig, axs = self.plot_meteogram_daily()

        self.data_raw = seasonal_back(
            self.dist_sol, self.data_trans, self.var_names, self.data_doys
        )

        if n_nan_timesteps:
            self.fit(**self.fit_kwds)
        # fig, axs = self.plot_meteogram_daily(figs=fig, axss=axs)
        # plt.show()

        return data_infilled

    def predict(self, dtimes=None, data_past=None, T=1, n_realizations=1):
        """Predict the next T steps given the past data.

        Parameters
        ----------
        dtimes : None or (p,) ndarray, optional
            datetimes of past timesteps, if None, the last p datetimes from
            the input data are used
        data_past : None or (K, p)) ndarray, optional
            Past on which to predict the future. p is the order of the VAR -
            process (it is stored in self.p after self.fit() is called).
            If None, data from the input is used.
        T : int, optional
            number of timesteps to predict.
        n_realizations : int, optional
            number of realizations of prediction

        Returns
        -------
        prediction : (K, T) or (K, T, n_realizations) ndarray
        """
        if self.p is None:
            self.fit(**self.fit_kwds)
        if dtimes is None:
            dtimes = self.times[-self.p :]
        if data_past is None:
            data_past = self.data_raw[:, -self.p :]
        past_doys = varwg.times.datetime2doy(dtimes)
        data_past_trans = self._fit_seasonal(values=data_past, doys=past_doys)[
            0
        ]
        prediction = models.VAR_LS_predict(
            data_past_trans, self.AM, self.sigma_u, T, n_realizations
        )
        prediction = prediction.reshape((-1, T, n_realizations))

        # calculate the output resolution in days
        first_doy, second_doy = varwg.times.datetime2doy(self.times[:2])
        delta_doy = second_doy - first_doy
        prediction_doys = past_doys[-1] + delta_doy * np.arange(1, T + 1)
        prediction_dtimes = varwg.times.doy2datetime(
            prediction_doys, year=dtimes[-1].year
        )
        prediction_doys = np.where(
            prediction_doys > 366, prediction_doys - 366, prediction_doys
        )
        prediction_sea = np.atleast_3d(np.empty_like(prediction))

        for r in range(n_realizations):
            prediction_sea[..., r] = seasonal_back(
                self.dist_sol,
                prediction[..., r],
                self.var_names,
                doys=prediction_doys,
            )
        prediction_sea /= self.sum_interval[:, np.newaxis, :]
        return prediction_dtimes, np.squeeze(prediction_sea)

    def plot_prediction(self, dtimes=None, data_past=None, T=1, hindcast=True):
        # don't be verbose for this part (we fetch previous fits all the time
        # which is rather boring)
        verbose = self.verbose
        self.verbose = False
        if self.p is None:
            self.fit(**self.fit_kwds)
        n_prev_steps = (4 if hindcast else 2) * self.p
        if dtimes is None:
            dtimes = self.times[-n_prev_steps:]
        if data_past is None:
            data_past = self.data_raw[:, -n_prev_steps:]

        prediction_dtimes, prediction = self.predict(
            dtimes[-self.p :], data_past[:, -self.p :], T
        )

        fig, axes = plt.subplots(nrows=self.K, sharex=True, squeeze=True)
        fig.suptitle(
            "Prediction made on %s"
            % varwg.times.datetime2str(varwg.times.datetime.now())
        )
        for var_i, (ax, var_name) in enumerate(zip(axes, self.var_names)):
            ax.plot(
                dtimes[self.p :],
                data_past[var_i, self.p :] / self.sum_interval[var_i],
                "k",
                linewidth=2,
            )
            ax.plot(prediction_dtimes, prediction[var_i], "b-x", linewidth=2)
            ax.grid()
            ax.set_ylabel(r"%s %s" % (var_name, conf.units[var_name]))
            ax.set_title(conf.long_var_names[var_name])

        if hindcast:
            for shift in range(self.p + 1, n_prev_steps):
                hindcast_dtimes, hindcast = self.predict(
                    dtimes[:shift],
                    data_past[:, :shift],
                    n_prev_steps - shift,
                    1,
                )
                col = plt.cm.jet(
                    1
                    - float(shift - self.p - 1) / (n_prev_steps - self.p - 1),
                    alpha=0.5,
                )
                for var_i, ax in enumerate(axes):
                    ax.plot(
                        hindcast_dtimes,
                        hindcast[var_i],
                        "-",
                        color=col,
                        linewidth=1,
                    )
                    # connect the hindcast with the end of its supporting data
                    ax.plot(
                        [dtimes[shift - 1], hindcast_dtimes[0]],
                        [
                            data_past[var_i, shift - 1]
                            / self.sum_interval[var_i],
                            np.atleast_1d(hindcast[var_i])[0],
                        ],
                        "-x",
                        color=col,
                        linewidth=1,
                    )
        ti = plt.xticks()[0]
        la_ = [
            varwg.times.datetime2str(
                varwg.times.ordinal2datetime(tii), "%d.%m. %H h"
            )
            for tii in ti
        ]
        plt.xticks(ti, la_, rotation=30)

        self.verbose = verbose

    def _gen_m_trend(
        self, prim_i, prim_index, prim_is_normal, sigma, scale, scale_nn
    ):
        theta_grad = self.theta_grad[prim_i]
        if np.isnan(theta_grad):
            self._m_trend_single += [np.zeros(self.K)]
            return self._m_trend_single[-1]
        # e.g. gradual temperature change
        primvar_trend = theta_grad * self.sum_interval[prim_index]
        # looking for the mean of the standard deviation
        if prim_is_normal:
            m_trend_primvar = primvar_trend / np.mean(sigma)
        else:
            # TODO: the following is most likely wrong!!!
            m_trend_primvar = np.mean(scale_nn(primvar_trend))
        self._m_trend_single += [m_trend_primvar * scale]
        return self._m_trend_single[-1]

    def _gen_m(
        self, prim_i, prim_index, prim_is_normal, sigma, scale, scale_nn
    ):
        if self.theta_incr is not None:
            theta_incr = self.theta_incr[prim_i]
            if np.isnan(theta_incr):
                self._m_single += [np.zeros((self.K, self.T_sim))]
                return self._m_single[-1]

        intercept = (
            # self.data_trans.mean(axis=1)
            np.nanmean(self.data_trans, axis=1)
            - scale * self.data_trans[prim_index].mean()
        ).reshape((self.K, 1))
        intercept[prim_index] = 0
        if self.theta_incr is not None:
            # change in mean in the real world
            delta_primvar = theta_incr * self.sum_interval[prim_index]
            if prim_is_normal:
                m_primvar = delta_primvar / sigma
            else:
                m_primvar = scale_nn(delta_primvar)
        else:
            m_primvar = 0
        if self.phase_randomize and self.phase_randomize_vary_mean:
            var_mean_scale = (
                self.phase_randomize_vary_mean
                if isinstance(self.phase_randomize_vary_mean, float)
                else 0.5
            )
            m_primvar += var_mean_scale * varwg.rng.normal()
            return m_primvar

        else:
            self._m_single += [
                m_primvar * scale.reshape((self.K, 1)) + intercept
            ]
            return self._m_single[-1]

    def _gen_m_t(
        self,
        prim_i,
        prim_index,
        prim_is_normal,
        sigma,
        scale,
        scale_nn,
        scale_nn_simple,
        _T,
    ):
        m_t = np.zeros((self.K, self.T_sim))
        # das war an der Tafel im Seminarraum 2:
        # mean_arrival: mittlere Zeit zwischen Aenderungen (kalte/warme
        # Perioden)
        # disturbance_std: Stabw der disturbances
        if self.disturbance_std is not None:
            disturbance_std = self.disturbance_std[prim_i]
            mean_arrival = self.mean_arrival[prim_i]
            disturbance_std = disturbance_std * self.sum_interval[prim_index]
            if prim_is_normal:
                disturbance_std /= np.mean(sigma)
            else:
                disturbance_std = np.mean(scale_nn(disturbance_std))
            m_t_primvar = interannual_variability(
                self.T_sim, mean_arrival, disturbance_std
            )
            m_t += m_t_primvar * scale.reshape((self.K, 1))

        if (
            self.climate_signal is not None
            and self.climate_signal[prim_i] is not None
        ):
            climate_diff = self._get_climate_diff(_T, prim_i)
            if prim_is_normal:
                climate_diff /= sigma
            else:
                climate_diff = scale_nn_simple(climate_diff)
            m_t += climate_diff * scale.reshape((self.K, 1))
        self._m_t_single += [m_t]
        return m_t

    @property
    def cov_trans(self):
        """The covariance matrix of the transformed data.
        If seasonal is True, this is of (365, K, K)-shape.
        """
        if self._cov_trans is None:
            if self.seasonal:
                covs = []
                for doy_ii, doy in enumerate(self.unique_doys):
                    ii = (self.data_doys > doy - self.doy_width) & (
                        self.data_doys <= doy + self.doy_width
                    )
                    if (doy - self.doy_width) < 0:
                        ii |= self.doys > (365.0 - self.doy_width + doy)
                    if (doy + self.doy_width) > 365:
                        ii |= self.doys < (doy + self.doy_width - 365.0)
                    covs += np.cov(self.data_trans[ii])
                covs = [
                    [
                        my.fourier_approx(covs[:, i, j], 4)
                        for i in range(self.K)
                    ]
                    for j in range(self.K)
                ]
                self._cov_trans = np.array(covs)
            else:
                self._cov_trans = np.cov(self.data_trans)
        return self._cov_trans

    def _scale_nn(self, x, seas_dist, trig_params):
        return my.pickle_cache(
            str(
                Path(self.seasonal_cache_file).parent
                / f"qq_shift_{self.station_name}_{x}_%s.pkl"
            ),
            warn=False,
            # clear_cache=True,
        )(seas_dist.qq_shift)(
            x,
            trig_params,
            # doys=self.sim_doys
        )

    def _scenario_parameters(
        self,
        theta_incr=None,
        theta_grad=None,
        disturbance_std=None,
        climate_signal=None,
        phase_randomize=False,
        scale_prim=True,
        primary_var_sim=None,
    ):
        """Prepares the scenario parameters, m and m_trend for the
        std.-normal world.

        Parameters
        ----------
        phase_randomize : boolean, optional
            Use phase randomization for VAR-residuals
        scale_prim : boolean, optional
            Allow primary variables to influence each other.
            Only effective when using multiple primary variables!
        """

        def str2tuple(thing):
            if isinstance(thing, str):
                return (thing,)
            return thing

        if primary_var_sim is None:
            prim_vars = str2tuple(self.primary_var)
            primary_var_ii = self.primary_var_ii
        else:
            prim_vars = str2tuple(primary_var_sim)
            primary_var_ii = [
                self.var_names.index(prim_var) for prim_var in prim_vars
            ]

        m = np.zeros((self.K, self.T_sim))
        m_t = np.zeros_like(m)
        m_trend = np.zeros(self.K)
        ScenParameters = namedtuple(
            "scenario_parameters", ("m", "m_t", "m_trend")
        )

        for prim_i, prim in enumerate(prim_vars):
            # prim_i is index inside sequence of primary variables.
            # prim_index is index inside sequence of all variables.
            # prim_index = self.primary_var_ii[prim_i]
            prim_index = primary_var_ii[prim_i]
            # scale other variables according to linear regression
            finite_row_mask = np.all(np.isfinite(self.data_trans), axis=0)
            data_trans = self.data_trans[:, finite_row_mask]
            scale = np.cov(data_trans)[prim_index] / np.var(
                data_trans[prim_index]
            )

            # do not change the primary variable by itself
            scale[prim_index] = 1
            if not scale_prim:
                # do not change the other primary variables
                scale[self.primary_var_ii] = 1
            if prim in self.var_names:
                seas_dist, trig_params = self.dist_sol[prim]
                if hasattr(seas_dist, "dist"):
                    prim_is_normal = isinstance(
                        seas_dist.dist, distributions.Normal
                    )
                else:
                    prim_is_normal = False

                if not prim_is_normal:
                    scale_nn = functools.partial(
                        self._scale_nn,
                        seas_dist=seas_dist,
                        trig_params=trig_params,
                    )

                    # means = seas_dist.mean(trig_params, self.sim_doys)

                    # we might exist in a loop and want to avoid
                    # calculating the medians all the time
                    if not hasattr(seas_dist, "medians"):
                        seas_dist.medians = seas_dist.median(
                            trig_params, self.sim_doys
                        )

                    def scale_nn_simple(x):
                        if seas_dist.medians.shape != x.shape:
                            seas_dist.medians = seas_dist.median(
                                trig_params, self.sim_doys
                            )
                        return distributions.norm.ppf(
                            seas_dist.cdf(
                                trig_params,
                                seas_dist.medians + x,
                                self.sim_doys,
                            )
                        )

                else:
                    scale_nn = None
                    scale_nn_simple = None

                # get the doy-specific distribution parameters
                _T = (2 * np.pi / 365 * self.sim_doys)[np.newaxis, :]
                if prim_is_normal:
                    sigma = seas_dist.trig2pars(trig_params, _T)[1]
                else:
                    sigma = None

                if theta_grad is not None:
                    m_trend += self._gen_m_trend(
                        prim_i,
                        prim_index,
                        prim_is_normal,
                        sigma,
                        scale,
                        scale_nn,
                    )
                else:
                    self._m_trend_single += [np.zeros(self.K)]

                if theta_incr is not None or self.phase_randomize_vary_mean:
                    m += self._gen_m(
                        prim_i,
                        prim_index,
                        prim_is_normal,
                        sigma,
                        scale,
                        scale_nn,
                    )
                else:
                    self._m_single += [np.zeros((self.K, self.T_sim))]

                if disturbance_std is not None or climate_signal is not None:
                    m_t += self._gen_m_t(
                        prim_i,
                        prim_index,
                        prim_is_normal,
                        sigma,
                        scale,
                        scale_nn,
                        scale_nn_simple,
                        _T,
                    )

        return ScenParameters(m, m_t, m_trend)

    def _get_climate_diff(self, _T, prim_i=0):
        """Calculates the difference between the seasonal mean of the primary
        variable and the given climate signal."""
        var_name = self.primary_var[prim_i]
        return (
            # np.atleast_2d(self.climate_signal)[prim_i]
            self.climate_signal[prim_i]
            - self.fitted_medians(var_name)
        ) * self.sum_interval_dict[var_name]

    def _location_shift_normal(self, sim):
        for prim_i, prim in enumerate(self.primary_var):
            prim_index = self.var_names.index(prim)
            dummy_time = np.arange(self.T_sim, dtype=float)
            m = self._m_single[prim_i][prim_index]
            m_t = mt[prim_i][prim_index] if (mt := self._m_t_single) else 0
            m_trend = self._m_trend_single[prim_i][prim_index]
            sim[prim_index] -= m + m_t + dummy_time / self.T_sim * m_trend
        return sim

    def _location_shift_back(self, sim_sea):
        for prim_i, prim in enumerate(self.primary_var):
            prim_index = self.var_names.index(prim)

            if self.theta_incr is not None:
                theta_incr = self.theta_incr[prim_i]
                if not np.isnan(theta_incr):
                    sim_sea[prim_index] += theta_incr

            if self.theta_grad is not None:
                theta_grad = self.theta_grad[prim_i]
                if not np.isnan(theta_grad):
                    dummy_time = np.arange(self.T_sim, dtype=float)
                    sim_sea[prim_index] += dummy_time / self.T_sim * theta_grad

            if self.climate_signal is not None:
                if self.climate_signal[prim_i] is not None:
                    # get the doy-specific distribution parameters
                    _T = (2 * np.pi / 365 * self.sim_doys)[np.newaxis, :]
                    climate_diff = self._get_climate_diff(_T, prim_i)
                    sim_sea[prim_index] += (
                        climate_diff / self.sum_interval[prim_index]
                    )
        return sim_sea

    def random_dryness(
        self,
        T=None,
        start_str=None,
        stop_str=None,
        n_events=None,
        duration_min=2,
        duration_max=7,
        month_start=6,
        month_end=9,
        event_dryness=0.4,
    ):
        """This is a very special method designed to generate dry hot events
        for Lake Kinneret.

        Parameters
        ----------
        T : None or int, optional
            Number of timesteps to simulate. T=None produces as many simulation
            timesteps as there were in the data used for fitting the VARMA
            process.
        start_str : str of format '%m-%d %H', optional
            String representation of the start date of the simulation.
        stop_str : str of format '%m-%d %H', optional
            String representation of the end date of the simulation.
        n_events : int or None
            Number of events to generate. If none there will be an average of 3
            events per year.
        duration_min : int
            Minimum length of events
        duration_max : int
            Maximum length of events
        month_start : int
            Month when the events can start to happen (january = 1)
        month_end : int
            Latest month in which the events can happen (january = 1)
        event_dryness : float
            The value of relative humidity that will be set during the events.

        Returns
        -------
        rh_signal : ndarray, dtype=float
            To be used as climate_signal in VG.simulate
        event_dt : ndarray, dtype=object (datetime)
            Datetimes of the events. Can be passed to VG.disaggregate later.
        """
        if T is None:
            self.T_sim = self.T_summed
        else:
            self.T_sim = T
        self.sim_times = self._gen_sim_times(T, start_str, stop_str)
        if n_events is None:
            n_events = 3 * int(len(self.sim_doys) / 365.0)

        rh_signal = np.copy(self.fitted_medians("rh", self.sim_doys))
        months = varwg.times.time_part(self.sim_times, "%m")
        summer_ii = np.where((months >= month_start) & (months <= month_end))[
            0
        ]
        durations = varwg.rng.integers(duration_min, duration_max + 1, n_events)
        for event_i in range(n_events):
            i = varwg.rng.choice(summer_ii)
            duration = durations[event_i]
            rh_signal[i : i + duration] = event_dryness

        event_mask = np.where(rh_signal <= event_dryness)[0]
        event_dt = self.sim_times[event_mask]

        return rh_signal, event_dt


if __name__ == "__main__":
    # warnings.simplefilter("error", RuntimeWarning)

    # import config_konstanz_disag as conf
    import config_konstanz as conf

    from varwg.core import plotting

    base.conf = plotting.conf = conf
    met_vg = VG(
        ("R", "theta", "ILWR", "Qsw", "rh", "u", "v"),
        # non_rain=("theta", "Qsw", "rh"),
        rain_method="regression",
        # rain_method="distance",
        neg_rain_doy_width=30,
        neg_rain_fft_order=2,
        # refit=True,
        # refit="R",
        verbose=True,
        dump_data=False,
        # plot=True
    )

    # met_vg.fit(seasonal=True)
    # # met_vg.fit(seasonal=False)
    # simt, sim = met_vg.simulate(T=100*365, phase_randomize=True)
    # # met_vg.disaggregate()
    # # simt, sim = met_vg.simulate(start_str="01.01.2000 00:00:00",
    # #                             stop_str="31.12.3000 00:00:00",
    # #                             resample=False)
    # # simt_dis, sim_dis = met_vg.disaggregate()
    # # met_vg.plot_all()
    # met_vg.plot_meteogramm_trans()
    # met_vg.plot_exceedance_daily()
    # # met_vg.plot_qq()
    # met_vg.plot_daily_fit("R")
    # met_vg.plot_monthly_hists("R")
    # fig, ax = plt.subplots(nrows=1, ncols=1)
    # rr, sol = met_vg.dist_sol["R"]
    # params = rr.all_parameters_dict(sol, doys=np.arange(365))
    # ax.plot(params["q_thresh"])
    # plt.show()
