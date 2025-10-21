from typing import Optional

import autofit as af
import autoarray as aa

from autolens import exc


class SubhaloAgg:
    def __init__(
        self,
        aggregator_grid_search: af.GridSearchAggregator,
        settings_inversion: Optional[aa.SettingsInversion] = None,
    ):
        """
        Wraps a PyAutoFit aggregator in order to create generators of fits to imaging data, corresponding to the
        results of a non-linear search model-fit.
        """

        self.aggregator_grid_search = aggregator_grid_search
        self.settings_inversion = settings_inversion

        if len(aggregator_grid_search) == 0:
            raise exc.AggregatorException(
                "There is no grid search of results in the aggregator."
            )
        elif len(aggregator_grid_search) > 1:
            raise exc.AggregatorException(
                "There is more than one grid search of results in the aggregator - please filter the"
                "aggregator."
            )

    @property
    def grid_search_result(self) -> af.GridSearchResult:
        return self.aggregator_grid_search[0]["result"]
