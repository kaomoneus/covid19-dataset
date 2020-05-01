from typing import List, Callable

import requests
import matplotlib.pyplot as plt
from ipywidgets import interact, interact_manual


def infection_factor(current: int, base: int, days_count: int):
    if days_count == 0:
        raise ValueError("Days count should be at least 1")
    return (float(current) / base)**(1./days_count)


def infection_factors(new_cases: List[int]):
    base = new_cases[0]
    return [
        infection_factor(new_cases[i], base, i)
        for i in range(1, len(new_cases))
    ]


def infection_factors_percent(new_cases: List[int]):
    base = new_cases[0]
    return [
        (infection_factor(new_cases[i], base, i) - 1.) * 100
        for i in range(1, len(new_cases))
    ]


def plot_factors(
    data: List[int],
    factors_function: Callable[[List[int]], List[float]]
):

    # exclude base from indices
    indices = range(1, len(data))

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('day')
    ax1.set_ylabel('total', color=color)
    ax1.plot(indices, data[1:], color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('factor %', color=color)  # we already handled the x-label with ax1
    ax2.plot(indices, factors_function(data), color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()


def run_plot(base: int):
    json_data = requests.get('https://yastat.net/s3/milab/2020/covid19-stat/data/data_struct_1.json').json()
    russia_stat = json_data['russia_stat_struct']

    dates = russia_stat['dates']
    indices = range(0, len(dates))
    overall = None
    for _, value in russia_stat['data'].items():
        repr(value)
        info = value['info']
        if info['name'] == 'Россия':
            overall = value
            break

    new_cases = overall['cases_delta']

    stride = 10

    # plt.plot(indices, new_cases)
    plot_factors(new_cases[5:], infection_factors_percent)





