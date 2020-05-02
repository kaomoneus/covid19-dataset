from typing import List, Callable

import requests
import matplotlib.pyplot as plt
from cached_property import cached_property


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


def infection_factors_percent(total_cases: List[int]):
    base = total_cases[0]
    return [
        (infection_factor(total_cases[i], base, i) - 1.) * 100
        for i in range(1, len(total_cases))
    ]


def plot_factors(
    offset: int,
    cases: List[int],
    new_cases: List[int],
    compare_with_new: bool,
    factors_function: Callable[[List[int]], List[float]]
):

    # exclude base from indices
    indices = range(offset + 1, offset + len(new_cases))

    fig, ax1 = plt.subplots()

    color = '#ff0000'
    ax1.set_xlabel('day')
    ax1.set_ylabel('new', color=color)
    ax1.plot(
        indices,
        new_cases[1:] if compare_with_new else cases[1:],
        color=color
    )
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('factor %', color=color)  # we already handled the x-label with ax1
    ax2.plot(indices, factors_function(cases), color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()


class Covid19Dataset:

    def __init__(
            self,
            url: str = 'https://yastat.net/s3/milab/2020/covid19-stat/data/data_struct_1.json'
    ):
        self.json_data = requests.get(url).json()
        self.dates = self.json_data['russia_stat_struct']['dates']
        self.russia_stat = [
            value for _, value in self.json_data['russia_stat_struct']['data'].items()
        ]

    class Region:
        def __init__(self, region_id: int, name: str):
            self.id = region_id
            self.name = name

        def __repr__(self):
            return self.name

    @cached_property
    def regions(self) -> List[Region]:

        sorted_stat = sorted(
            self.russia_stat,
            key=lambda s: s['info']['name']
        )

        regions = [
            Covid19Dataset.Region(i, sorted_stat[i]['info']['name'])
            for i in range(0, len(sorted_stat))
        ]

        return regions

    @cached_property
    def whole_russia_id(self) -> int:
        regions = self.regions
        for r in regions:
            if r.name == 'Россия':
                return r.id
        return 0

    def plot(self, base: int, region_id: int, show_new: bool):
        total = self.russia_stat[region_id]['cases']
        new_cases = self.russia_stat[region_id]['cases_delta']
        plot_factors(
            offset=base,
            cases=total[base:],
            new_cases=new_cases[base:],
            factors_function=infection_factors_percent,
            compare_with_new=show_new
        )





