import warnings
import numpy as np
from varwg import helpers as my, ecdf
import varwg


@my.cache(mask=None)
def _random_phases(
    K, T_sim, T_data, zero_phases=None, verbose=False, mask_fun=None
):
    T_total = 0
    phases_stacked = []
    _random_phases.clear_cache()
    while T_total < T_sim:
        # phase randomization with same random phases in all
        # variables and stations
        phases_len = T_data // 2 - 1 + T_data % 2
        phases_pos = varwg.rng.uniform(0, 2 * np.pi, phases_len)

        if mask_fun is not None:
            # e.g.: do not touch phases that are close to the annual
            # frequency
            periods = np.fft.rfftfreq(phases_len * 2)[1:] ** -1
            mask = mask_fun(periods)
            if verbose > 1:
                print(
                    f"Holding {mask.sum()} ({mask.mean() * 100:.3f}%)"
                    " of phases constant."
                )
            phases_pos[mask] = 0

        phases_pos = np.array(K * [phases_pos])
        phases_neg = -phases_pos[:, ::-1]
        nyquist = np.full(K, 0)[:, None]
        # zero_phases = phases[:, 0, None]
        if zero_phases is None:
            zero_phases = np.zeros(K)[:, None]
        elif zero_phases.ndim < 2:
            zero_phases = zero_phases[:, None]
        if T_data % 2 == 0:
            phases = np.hstack((zero_phases, phases_pos, nyquist, phases_neg))
            if mask_fun is not None:
                mask = np.hstack(([False], mask, [False], mask))
        else:
            phases = np.hstack((zero_phases, phases_pos, phases_neg))
            if mask_fun is not None:
                mask = np.hstack(([False], mask, mask))
        phases_stacked += [phases]
        T_total += T_data
        if mask_fun is not None:
            if _random_phases.mask is None:
                _random_phases.mask = mask
            else:
                _random_phases.mask = np.concatenate(
                    (_random_phases.mask, mask)
                )
    return phases_stacked


def randomize2d(
    data,
    T=None,
    taboo_period_min=None,
    taboo_period_max=None,
    return_rphases=False,
    rphases=None,
    qq=True,
):
    """
    assumes daily discretization and does not touch yearly cycles."""
    assert np.all(np.isfinite(data))
    K, T_data = data.shape
    if T is None:
        T_sim = T_data
    else:
        T_sim = T

    if taboo_period_min is not None and taboo_period_max is not None:

        def mask_fun(periods):
            return (np.abs(periods) > taboo_period_min) & (
                np.abs(periods) < taboo_period_max
            )

    else:
        mask_fun = None
    A = np.fft.fft(data)
    zero_phases = np.angle(A)[:, 0]
    if rphases is None:
        rphases = _random_phases(
            K, T_sim, T_data, zero_phases=zero_phases, mask_fun=mask_fun
        )
    fft_sim = np.concatenate(
        [np.fft.ifft(A * np.exp(1j * rphases_)).real for rphases_ in rphases],
        axis=1,
    )[:, :T_sim]
    assert np.all(np.isfinite(fft_sim))

    # data_means = np.mean(data, axis=1)
    # fft_sim += data_means[:, None] - fft_sim.mean(axis=1)[:, None]
    # fft_sim -= fft_sim.mean(axis=1)[:, None]
    # print(f"{np.std(data, axis=1)=}")
    # print(f"{np.std(fft_sim, axis=1)=}")
    # print(f"{np.mean(data, axis=1)=}")
    # print(f"{np.mean(fft_sim, axis=1)=}")
    # print(f"{A[:, 0]=}")
    # print(f"{A_new[:, 0]=}")

    if qq:
        data_dists = [ecdf.ECDF(data_row) for data_row in data]
        sim_dists = [ecdf.ECDF(fft_sim_row) for fft_sim_row in fft_sim]
        fft_sim = np.array(
            [
                data_dist.ppf(sim_dist.cdf())
                for data_dist, sim_dist in zip(data_dists, sim_dists)
            ]
        )

        # import matplotlib.pyplot as plt
        # fig, axs = plt.subplots(
        #     nrows=1, ncols=K, subplot_kw=dict(aspect="equal")
        # )
        # qq = np.linspace(1e-6, 1 - 1e-6, 500)
        # for ax, data_dist, sim_dist in zip(axs, data_dists, sim_dists):
        #     data_sample = data_dist.ppf(qq)
        #     sim_sample = sim_dist.ppf(qq)
        #     ax.plot(data_sample, sim_sample)
        #     min_ = min(data_sample[0], sim_sample[0])
        #     max_ = max(data_sample[-1], sim_sample[-1])
        #     ax.plot(
        #         [min_, max_],
        #         [min_, max_],
        #         linestyle="--",
        #         color="k",
        #         alpha=0.5,
        #     )
        # plt.show()

    if return_rphases:
        return fft_sim, rphases
    return fft_sim


def randomize2d_old(
    data,
    T=None,
    taboo_period_min=None,
    taboo_period_max=None,
    return_rphases=False,
):
    """
    assumes daily discretization and does not touch yearly cycles."""
    K, T_data = data.shape
    if T is None:
        T = T_data
    # if taboo_period_max is None:
    #     taboo_period_max = T
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        # we divide by zero here
        periods = 1 / np.fft.fftfreq(T_data)
    print(f"{taboo_period_min=}")
    print(f"{taboo_period_max=}")
    if taboo_period_min is not None and taboo_period_max is not None:
        taboo_freqs_ii = np.where(
            (np.abs(periods) > taboo_period_min)
            & (np.abs(periods) < taboo_period_max)
        )[0]
    else:
        taboo_freqs_ii = None
    A = np.fft.fft(data)
    phases_data = np.angle(A)
    T_total = 0
    randomized = []
    zero_phases = np.zeros(K)[:, None]
    while T_total < T:
        phases_lh = varwg.rng.uniform(
            0, 2 * np.pi, T_data // 2 if T_data % 2 == 1 else T_data // 2 - 1
        )
        phases_lh = np.array(K * [phases_lh])
        phases_rh = -phases_lh[:, ::-1]
        if T_data % 2 == 0:
            phases = np.hstack(
                (
                    zero_phases,
                    # phases_data[:, 0, None],
                    phases_lh,
                    phases_data[:, phases_data.shape[1] // 2, None],
                    phases_rh,
                )
            )
        else:
            phases = np.hstack(
                (
                    zero_phases,
                    # phases_data[:, 0, None],
                    phases_lh,
                    phases_rh,
                )
            )
        # phases[:, taboo_freqs_ii] = 0  # phases_data[:, taboo_freqs_ii]
        A_new = A * np.exp(1j * phases)
        if taboo_freqs_ii is not None:
            A_new[:, taboo_freqs_ii] = A[:, taboo_freqs_ii]
        randomized += [np.fft.ifft(A_new).real]
        # randomized += [np.fft.ifft(A).real]
        T_total += T_data
    randomized = np.concatenate(randomized, axis=1)[:, :T]
    # data_means = np.mean(data, axis=1)
    # randomized += data_means[:, None] - randomized.mean(axis=1)[:, None]
    # randomized -= randomized.mean(axis=1)[:, None]
    # print(f"{np.std(data, axis=1)=}")
    # print(f"{np.std(randomized, axis=1)=}")
    # print(f"{np.mean(data, axis=1)=}")
    # print(f"{np.mean(randomized, axis=1)=}")
    # print(f"{A[:, 0]=}")
    # print(f"{A_new[:, 0]=}")
    if return_rphases:
        return randomized, phases
    return randomized
