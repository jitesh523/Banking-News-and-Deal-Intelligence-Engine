"""Regression coverage for ingestion-order-independent trend analysis."""

from datetime import datetime

import pytest

from app.services.trend_analyzer import TrendAnalyzer


METHODS = [
    "get_deal_volume_trend",
    "get_deal_value_trend",
    "get_sentiment_trend",
    "company_sentiment",
]


def populated_analyzer(day_order):
    analyzer = TrendAnalyzer()
    for day in day_order:
        date = datetime(2026, 10, day)
        for _ in range(day):
            analyzer.add_deal_event(date, "merger", deal_amount=100)
        analyzer.add_sentiment_event(date, day / 5, company="Example Bank")
    return analyzer


def analyze(analyzer, method, **kwargs):
    if method == "company_sentiment":
        return analyzer.get_sentiment_trend(company="Example Bank", **kwargs)
    return getattr(analyzer, method)(**kwargs)


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("bounded", [False, True], ids=["all-dates", "date-range"])
def test_newest_first_ingestion_still_reports_rising_trend(method, bounded):
    analyzer = populated_analyzer([5, 4, 3, 2, 1])
    bounds = {}
    expected_days = [1, 2, 3, 4, 5]
    if bounded:
        bounds = {"start_date": datetime(2026, 10, 2), "end_date": datetime(2026, 10, 4)}
        expected_days = [2, 3, 4]

    result = analyze(analyzer, method, **bounds)

    assert result["trend_direction"] == "increasing"
    assert list(result["timeline"]) == [f"2026-10-{day:02d}" for day in expected_days]
    if method == "get_deal_volume_trend":
        assert result["total_deals"] == sum(expected_days)
    elif method == "get_deal_value_trend":
        assert result["total_value"] == 100 * sum(expected_days)
    else:
        assert result["average_sentiment"] == pytest.approx(0.6)


@pytest.mark.parametrize("method", METHODS)
def test_shuffled_ingestion_matches_chronological_results(method):
    chronological = populated_analyzer([1, 2, 3, 4, 5])
    shuffled = populated_analyzer([3, 5, 1, 4, 2])
    result = analyze(shuffled, method)

    assert result == analyze(chronological, method)
    assert list(result["timeline"]) == list(analyze(chronological, method)["timeline"])
    # Reading a trend must not rearrange the source event collections.
    assert list(shuffled.deal_timeline) == [
        "2026-10-03", "2026-10-05", "2026-10-01", "2026-10-04", "2026-10-02"
    ]


@pytest.mark.parametrize("day_order", [[], [1]], ids=["empty", "one-day"])
def test_empty_and_single_day_trends_remain_stable(day_order):
    analyzer = populated_analyzer(day_order)
    for method in METHODS:
        assert analyze(analyzer, method)["trend_direction"] == "stable"
