from decimal import Decimal

import pytest

from spot_planner.main import _is_valid_combination, get_cheapest_periods

def test_performance():
    prices = [Decimal(f"{i}") for i in range(24)]
    get_cheapest_periods(
        prices=prices,
        low_price_threshold=Decimal("10"),
        min_selections=12,
        min_consecutive_selections=1,
            max_consecutive_selections=8,
        max_gap_between_periods=1,
        max_gap_from_start=1,
    )


@pytest.mark.slow
def test_maximum_range():
    prices = [Decimal(f"{i}") for i in range(29)]
    get_cheapest_periods(
        prices=prices,
        low_price_threshold=Decimal("10"),
        min_selections=12,
        min_consecutive_selections=1,
            max_consecutive_selections=8,
        max_gap_between_periods=1,
        max_gap_from_start=1,
    )
