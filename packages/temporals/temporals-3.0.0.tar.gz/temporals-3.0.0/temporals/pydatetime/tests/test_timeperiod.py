from zoneinfo import ZoneInfo
import pytest
from datetime import time, date, datetime
from temporals.pydatetime.periods import TimePeriod, DatePeriod, WallClockPeriod, AbsolutePeriod


class TestTimePeriod:

    def test_constructor_valid(self):
        # Valid objects
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)
        assert isinstance(self.period, TimePeriod)

    def test_constructor_invalid(self):
        # Date
        self.start = date(2024, 1, 1)
        self.end = date(2024, 1, 2)
        with pytest.raises(ValueError):
            TimePeriod(start=self.start, end=self.end)

        # Datetime
        self.start = datetime(2024, 1, 1, 8, 0, 0)
        self.end = datetime(2024, 1, 1, 10, 0, 0)
        with pytest.raises(ValueError):
            TimePeriod(start=self.start, end=self.end)

    def test_timeperiod_eq(self):
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period1 = TimePeriod(start=self.start, end=self.end)
        self.period2 = TimePeriod(start=self.start, end=self.end)
        assert self.period1 == self.period2

        self.different_end = time(11, 0, 0)
        self.period2 = TimePeriod(start=self.start, end=self.different_end)
        assert self.period1 != self.period2

    def test_eq_wallclock(self):
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)
        self.start_dt = datetime(2024, 1, 1, 8, 0, 0)
        self.end_dt = datetime(2024, 1, 1, 10, 0, 0)
        self.period_dt = WallClockPeriod(start=self.start_dt, end=self.end_dt)
        assert self.period == self.period_dt

    def test_eq_absolute(self):
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)
        self.start_dt = datetime(2024, 1, 1, 8, 0, 0)
        self.end_dt = datetime(2024, 1, 1, 10, 0, 0)
        self.period_dt = AbsolutePeriod(start=self.start_dt, end=self.end_dt)
        assert self.period == self.period_dt

    def test_invalid_eq(self):
        self.random_time = time(9, 0, 0)
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)
        assert self.random_time != self.period

    def test_membership_time(self):
        self.random_time = time(9, 0, 0)
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)
        assert self.random_time in self.period

    def test_membership_timeperiod(self):
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        self.start = time(8, 30, 0)
        self.end = time(9, 0, 0)
        self.inner_period = TimePeriod(start=self.start, end=self.end)
        assert self.inner_period in self.period

        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.eq_period = TimePeriod(start=self.start, end=self.end)
        assert self.eq_period in self.period

    def test_membership_datetime(self):
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        self.random_dt = datetime(2024, 1, 1, 10, 0, 0)
        assert self.random_dt in self.period

    def test_membership_wallclock(self):
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        self.start_dt = datetime(2024, 1, 1, 8, 30, 0)
        self.end_dt = datetime(2024, 1, 1, 9, 0, 0)
        self.period_dt = WallClockPeriod(start=self.start_dt, end=self.end_dt)
        assert self.period_dt in self.period

    def test_membership_absolute(self):
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        self.start_dt = datetime(2024, 1, 1, 8, 30, 0)
        self.end_dt = datetime(2024, 1, 1, 9, 0, 0)
        self.period_dt = AbsolutePeriod(start=self.start_dt, end=self.end_dt)
        assert self.period_dt in self.period

    def test_is_before(self):
        self.start = time(10, 0, 0)
        self.end = time(12, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        assert self.period.is_before(time(13, 0)) is True
        assert self.period.is_before(time(10, 0)) is False

        self.other_start = time(12, 0, 0)
        self.other_end = time(13, 0, 0)
        self.other_period = TimePeriod(start=self.other_start, end=self.other_end)
        assert self.period.is_before(self.other_period) is True

        self.other_start = time(8, 0, 0)
        self.other_end = time(10, 0, 0)
        self.other_period = TimePeriod(start=self.other_start, end=self.other_end)
        assert self.period.is_before(self.other_period) is False

    def test_is_after(self):
        self.start = time(10, 0, 0)
        self.end = time(12, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        assert self.period.is_after(time(13, 0)) is False
        assert self.period.is_after(time(10, 0)) is True

        self.other_start = time(12, 0, 0)
        self.other_end = time(13, 0, 0)
        self.other_period = TimePeriod(start=self.other_start, end=self.other_end)
        assert self.period.is_after(self.other_period) is False

        self.other_start = time(8, 0, 0)
        self.other_end = time(10, 0, 0)
        self.other_period = TimePeriod(start=self.other_start, end=self.other_end)
        assert self.period.is_after(self.other_period) is True

    def test_to_wallclock_date(self):
        self.start = time(8, 0)
        self.end = time(12, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        wc_period = self.period.to_wallclock(specific_date=date(2024, 1, 1))
        assert wc_period == WallClockPeriod(
            start=datetime(2024, 1, 1, 8, 0),
            end=datetime(2024, 1, 1, 12, 0)
        )

    def test_to_wallclock_period(self):
        self.start = time(8, 0)
        self.end = time(12, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        self.other_start = date(2024, 1, 10)
        self.other_end = date(2024, 1, 20)
        self.other_period = DatePeriod(start=self.other_start, end=self.other_end)

        wc_period = self.period.to_wallclock(specific_date=self.other_period)
        assert wc_period == WallClockPeriod(
            start=datetime(2024, 1, 10, 8, 0),
            end=datetime(2024, 1, 20, 12, 0)
        )

    def test_to_absolute_date(self):
        self.start = time(8, 0)
        self.end = time(12, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        abs_period = self.period.to_absolute(specific_date=date(2024, 1, 1),
                                             timezone=ZoneInfo("Europe/Paris"))
        assert abs_period == AbsolutePeriod(
            start=datetime(2024, 1, 1, 8, 0, tzinfo=ZoneInfo("Europe/Paris")),
            end=datetime(2024, 1, 1, 12, 0, tzinfo=ZoneInfo("Europe/Paris"))
        )

    def test_to_absolute_period(self):
        self.start = time(8, 0)
        self.end = time(12, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        self.other_start = date(2024, 1, 10)
        self.other_end = date(2024, 1, 20)
        self.other_period = DatePeriod(start=self.other_start, end=self.other_end)

        abs_period = self.period.to_absolute(specific_date=self.other_period,
                                             timezone=ZoneInfo("Europe/Paris"))
        assert abs_period == AbsolutePeriod(
            start=datetime(2024, 1, 10, 8, 0, tzinfo=ZoneInfo("Europe/Paris")),
            end=datetime(2024, 1, 20, 12, 0, tzinfo=ZoneInfo("Europe/Paris"))
        )

    def test_get_interim(self):
        self.start = time(8, 0)
        self.end = time(12, 0)
        self.period = TimePeriod(start=self.start, end=self.end)
        assert self.period.get_interim(time(3, 0)) == TimePeriod(time(3, 0),
                                                                 time(8, 0))
        assert self.period.get_interim(time(17, 0)) == TimePeriod(time(12, 0),
                                                                  time(17, 0))

        self.other_start = time(0, 0, 0)
        self.other_end = time(3, 0, 0)
        self.other_period = TimePeriod(start=self.other_start, end=self.other_end)
        assert self.period.get_interim(self.other_period) == TimePeriod(time(3, 0), time(8, 0))

        self.other_start = time(14, 0, 0)
        self.other_end = time(17, 0, 0)
        self.other_period = TimePeriod(start=self.other_start, end=self.other_end)
        assert self.period.get_interim(self.other_period) == TimePeriod(time(12, 0), time(14, 0))

    def test_overlaps(self):
        """
           0800     Period 1    1000
            |=====================|
                                |===================|
                               0945   Period 2   1200

            Period 1 is overlapped by Period 2
            Period 2 overlaps Period 1
            Period 1 does not overlap Period 2
            Period 2 is not overlapped by Period 1
        """
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        self.other_start = time(9, 45, 0)
        self.other_end = time(12, 0, 0)
        self.other_period = TimePeriod(start=self.other_start, end=self.other_end)
        assert self.period.overlapped_by(self.other_period) is True
        assert self.other_period.overlaps_with(self.period) is True
        assert self.period.overlaps_with(self.other_period) is False
        assert self.other_period.overlapped_by(self.period) is False

    def test_disconnects(self):
        """
           0800     Period 1    1000
            |=====================|
                                |===================|
                               0945   Period 2   1200

            Period 1 disconnect - 0800:0945
            Period 2 disconnect - 1000:1200

        """
        self.start = time(8, 0, 0)
        self.end = time(10, 0, 0)
        self.period = TimePeriod(start=self.start, end=self.end)

        self.other_start = time(9, 45, 0)
        self.other_end = time(12, 0, 0)
        self.other_period = TimePeriod(start=self.other_start, end=self.other_end)

        self.first_disconnect = self.period.get_disconnect(self.other_period)
        assert self.first_disconnect.start == time(8, 0)
        assert self.first_disconnect.end == time(9, 45)

        self.second_disconnect = self.other_period.get_disconnect(self.period)
        assert self.second_disconnect.start == time(10, 0)
        assert self.second_disconnect.end == time(12, 0)

        # Non-overlapping periods
        self.other_start = time(11, 45, 0)
        self.other_end = time(12, 0, 0)
        self.other_period = TimePeriod(start=self.other_start, end=self.other_end)

        self.first_disconnect = self.period.get_disconnect(self.other_period)
        assert self.first_disconnect is None

        self.second_disconnect = self.other_period.get_disconnect(self.period)
        assert self.second_disconnect is None
