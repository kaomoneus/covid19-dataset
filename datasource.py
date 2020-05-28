from typing import List

import cached_property


class Region:
    def __init__(self, region_id: int, name: str):
        self.id = region_id
        self.name = name

    def __repr__(self):
        return self.name


class ValuesItem:
    def __init__(self, x: int, dx: int):
        self.x = x
        self.dx = dx


class DailyStats:
    def __init__(self, cases: ValuesItem, cured: ValuesItem, deaths: ValuesItem):
        self.cases = cases
        self.cured = cured
        self.deaths = deaths


class RegionsCollection:
    def __init__(self, stat_struct_json: dict, default_region_name: str):
        self._stat = sorted(
            [
                value for _, value in stat_struct_json['data'].items()
            ],
            key=lambda s: s['info']['name']
        )

        self._dates = stat_struct_json['dates']

        self._default_region_name = default_region_name

    @cached_property
    def regions(self) -> List[Region]:

        regions = [
            Region(i, self._stat[i]['info']['name'])
            for i in range(0, len(self._stat))
        ]

        return regions

    @cached_property
    def default_region(self):
        regions = self.regions
        for r in regions:
            if r.name == self._default_region_name:
                return r.id
        return 0

    @property
    def dates(self):
        return self._dates

    @staticmethod
    def _create_values_item(values: List[int], i: int) -> ValuesItem:
        return ValuesItem(values[i], values[i] - values[i - 1] if i > 0 else 0)

    def daily_stats(self, region_id: int):
        cases = self._stat[region_id]['cases']
        deaths = self._stat[region_id]['deaths']
        cured = self._stat[region_id]['cured']

        stats = [
            DailyStats(
                cases=RegionsCollection._create_values_item(cases, i),
                deaths=RegionsCollection._create_values_item(deaths, i),
                cured=RegionsCollection._create_values_item(cured, i)
            )
            for i in range(0, len(cases))
        ]

        return stats
