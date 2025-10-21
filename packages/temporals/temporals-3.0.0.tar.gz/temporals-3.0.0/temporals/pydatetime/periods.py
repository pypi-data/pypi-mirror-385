# TODO: fix membership evaluations
from . import interface
import calendar
from typing import Union
from zoneinfo import ZoneInfo
from datetime import time, date, datetime, timedelta
from temporals.interfaces import AbstractDuration
from temporals.duration import Duration
from .utils import check_existence
from temporals.exceptions import TimeAmbiguityError


class TimePeriod(interface.PyTimePeriod):
    """ The TimePeriod class is responsible for time periods within a 24-hour day. Instances of this class offer the
    'equal' comparison (see __eq__ below), as well as the membership (is, is not) test operators (see __contains__)
    below.
    """

    def __init__(self,
                 start: time,
                 end: time,
                 ):
        if not isinstance(start, time):
            raise ValueError(f"Provided value '{start}' for parameter 'start' is not an instance of time")
        if not isinstance(end, time):
            raise ValueError(f"Provided value '{end}' for parameter 'end' is not an instance of time")
        if start >= end:
            raise ValueError(f"The start of a period cannot be equal or after its end; values provided: start={start}, "
                             f"end={end}")
        self._start = start
        self._end = end
        # OOTB datetime.time does not support operations, so we'll turn it into a timedelta
        _start = timedelta(hours=start.hour,
                           minutes=start.minute,
                           seconds=start.second)
        _end = timedelta(hours=end.hour,
                         minutes=end.minute,
                         seconds=end.second)
        td: timedelta = _end - _start
        total = int(td.total_seconds())
        seconds = end.second - start.second
        minutes = end.minute - start.minute
        hours = end.hour - start.hour
        if seconds < 0:
            minutes -= 1
            seconds = 60 + seconds
        if minutes < 0:
            hours -= 1
            minutes = 60 + minutes
        if hours < 0:
            hours = 0
        self._duration = Duration(total_seconds=total, years=0, months=0, days=0, hours=hours, minutes=minutes,
                                  seconds=seconds)

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def duration(self) -> 'AbstractDuration':
        return self._duration

    def __str__(self):
        return f"{self.start.isoformat()}/{self.end.isoformat()}"

    def __eq__(self, other):
        """ Equality can only be determined between instances of this class, as well as the wallclock or absolute
        periods classes, since only these two classes contain information about the actual time in a day. In both cases,
        the instances will be tested for exactly equal start and end times.

        This method does not account for overlaps between the start and end times of the periods, to get this
        functionality, look at the following methods:
            overlaps_with
            overlapped_by
            get_overlap
            get_disconnect
        """
        if isinstance(other, interface.PyAbsolutePeriod) or isinstance(other, interface.PyWallClockPeriod):
            return (self.start == other.start.time()
                    and self.end == other.end.time())
        if isinstance(other, interface.PyTimePeriod):
            return (self.start == other.start
                    and self.end == other.end)
        return False

    def __contains__(self, item):
        """ Membership test can be done with instances of this class, the wallclock or absolute periods classes,
        datetime.datetime and datetime.time objects; When membership test is done for a period, it assumes that the
        request is to check if the tested period exists WITHIN the temporal borders of this period, that is to say,
        whether the start and end times of the other period are after and before, respectively, of the same of this period.

        0800       Your period:          1700
        |==================================|
             1200 |=============| 1300
                         ^ The period you are testing

        If you have an instance of this period, for example:
        >>> start = time(8, 0, 0)  # 8 o'clock in the morning
        >>> end = time(17, 0, 0)  # 5 o'clock in the afternoon
        >>> workday = TimePeriod(start=start, end=end)

        and then another TimePeriod:
        >>> lunch_start = time(12, 0, 0)  # 12 o'clock at lunch
        >>> lunch_end = time(13, 0, 0)  # 1 o'clock in the afternoon
        >>> lunch_break = TimePeriod(start=lunch_start, end=lunch_end)

        Then you can check if the lunch_break period is within your workday period:
        >>> lunch_break in workday

        For more in-depth comparisons and functionality, see:
            is_part_of
            has_as_part
            overlap
            disconnect
        """
        if isinstance(item, interface.PyTimePeriod):
            """ Only return True if the start and end times of `item` are within the actual time duration of this 
            period.
            """
            return self.start <= item.start and item.end <= self.end
        if isinstance(item, interface.PyAbsolutePeriod) or isinstance(item, interface.PyWallClockPeriod):
            return item.start.time() >= self.start and item.end.time() <= self.end
        if isinstance(item, datetime):
            item = item.time()
        if isinstance(item, time):
            return self.start <= item <= self.end
        return False

    def is_before(self, other: Union['interface.PyTimePeriod', time]) -> bool:
        """ Test if this period ends before the provided `other` value. This check will evaluate as True in the
        following scenario:

        time object:
        1000 This period:   1400
        |====================|
                                |
                              1500

        TimePeriod object:
        1000 This period:   1400
        |====================|
                                |====|
                              1500  1700
        """
        if isinstance(other, time):
            return self.end <= other
        elif isinstance(other, interface.PyTimePeriod):
            return self.end <= other.start
        return False

    def is_after(self, other: Union['interface.PyTimePeriod', time]) -> bool:
        """ Test if this period starts after the provided `other` value. This check will evaluate as True in the
        following scenario:

        time object:
                        1000       This period:          1700
                        |==================================|
                    |
                  0900

        TimePeriod object:
                        1000       This period:          1700
                        |==================================|
            |=======|
          0700    0900

        """
        if isinstance(other, time):
            return other <= self.start
        elif isinstance(other, interface.PyTimePeriod):
            return other.end <= self.start
        return False

    def get_interim(self,
                    other: Union['interface.PyTimePeriod', time]) -> Union['interface.PyTimePeriod', None]:
        """ Method returns the TimePeriod between the start/end of the provided period, if `other` is a TimePeriod,
        or the TimePeriod between the point in time and the start/end of this period, depending on whether the same is
        occurring before the start of this period or after the end of it.

        This method is intended to be used when the provided `other` does not exist within and does not overlap (or is
        being overlapped) by this period.

        For example, in the case of a point of in time:
        1000       This period:          1700
        |==================================|
                                                | 2000
                                            Point in time

        The returned TimePeriod will be from 1700 to 2000
        """
        _start = None
        _end = None
        if isinstance(other, time):
            if self.is_before(other):
                _start = self.end
                _end = other
            elif self.is_after(other):
                _start = other
                _end = self.start
        elif isinstance(other, TimePeriod):
            if self.is_before(other):
                _start = self.end
                _end = other.start
            elif self.is_after(other):
                _start = other.end
                _end = self.start
        if _start and _end:
            return TimePeriod(start=_start, end=_end)

    def overlaps_with(self,
                      other: Union['interface.PyTimePeriod', 'interface.PyAbsolutePeriod', 'interface.PyWallClockPeriod']
                      ) -> bool:
        """ Test if this period overlaps with another period that has begun before this one. This check will evaluate
        as True in the following scenario:
                        1000       This period:          1700
                        |==================================|
             0800 |=============| 1300
                         ^ The other period

        >>> this_start = time(10, 0, 0)
        >>> this_end = time(17, 0, 0)
        >>> other_start = time(8, 0, 0)
        >>> other_end = time(13, 0, 0)
        >>> this_period = TimePeriod(start=this_start, end=this_end)
        >>> other_period = TimePeriod(start=other_start, end=other_end)
        >>> this_period.overlaps_with(other_period)
        True

        The period that has begun first is considered the "main" period, even if it finishes before the end of this
        period, since it occupies an earlier point in time. Therefore, the current period, which has begun at a later
        point in time, is considered to be the overlapping one. Hence, the opposite check (overlapped_by) is True for
        the other_period:
        >>> other_period.overlapped_by(this_period)
        True

        Note that both of these checks will only work for partially overlapping periods - for fully overlapping periods,
        use the `in` membership test:
        >>> this_period in other_period
        """
        other_start: time = None  # type: ignore
        other_end: time = None  # type: ignore
        if isinstance(other, interface.PyTimePeriod):
            other_start = other.start
            other_end = other.end
        if isinstance(other, interface.PyAbsolutePeriod) or isinstance(other, interface.PyWallClockPeriod):
            other_start = other.start.time()
            other_end = other.end.time()
        if not other_end < self.start and other_start < self.start and other_end < self.end:
            return True
        return False

    def overlapped_by(self,
                      other: Union['interface.PyTimePeriod', 'interface.PyAbsolutePeriod', 'interface.PyWallClockPeriod']
                      ) -> bool:
        """ Test if this period is overlapped by the other period. This check will evaluate True in the following
        scenario:
           1000       This period:          1700
            |==================================|
                                1500 |=============| 1800
                                            ^ The other period

        >>> this_start = time(10, 0, 0)
        >>> this_end = time(17, 0, 0)
        >>> other_start = time(15, 0, 0)
        >>> other_end = time(18, 0, 0)
        >>> this_period = TimePeriod(start=this_start, end=this_end)
        >>> other_period = TimePeriod(start=other_start, end=other_end)
        >>> this_period.overlapped_by(other_period)
        True

        Since this period has begun first, it is considered the "main" one, and all other periods that begin after this
        one, are considered to be overlapping it. Therefore, the opposite check, `overlaps_with`, will evaluate True
        if the opposite check is being made:
        >>> other_period.overlaps_with(this_period)
        True

        Note that both of these checks will only work for partially overlapping periods - for fully overlapping periods,
        use the `in` membership test:
        >>> this_period in other_period
        """
        other_start: time = None  # type: ignore
        other_end: time = None  # type: ignore
        if isinstance(other, interface.PyTimePeriod):
            other_start = other.start
            other_end = other.end
        if isinstance(other, interface.PyAbsolutePeriod) or isinstance(other, interface.PyWallClockPeriod):
            other_start = other.start.time()
            other_end = other.end.time()
        if not self.end < other_start and self.start < other_start and self.end < other_end:
            return True
        return False

    def get_overlap(self,
                    other: Union['interface.PyTimePeriod', 'interface.PyAbsolutePeriod', 'interface.PyWallClockPeriod']
                    ) -> Union['interface.PyTimePeriod', None]:
        """ Method returns the overlapping interval between the two periods as a new TimePeriod instance

        >>> period1_start = time(8, 0, 0)
        >>> period1_end = time(12, 0, 0)
        >>> period1 = TimePeriod(start=period1_start, end=period1_end)
        >>> period2_start = time(10, 0, 0)
        >>> period2_end = time(13, 0, 0)
        >>> period2 = TimePeriod(start=period2_start, end=period2_end)
        >>> period1
        TimePeriod(start=datetime.time(8, 0), end=datetime.time(12, 0))
        >>> period2
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(13, 0))

        On a timeline, the two periods can be illustrated as:
           0800              Period 1                1200
            |=========================================|
                               |============================|
                              1000       Period 2          1300

        As expected, attempting a membership test would return False:
        >>> period2 in period1
        False
        however, testing overlaps does return True:
        >>> period1.overlapped_by(period2)
        True
        and the opposite:
        >>> period2.overlaps_with(period1)
        True

        Therefore, we can use the `get_overlap` method to obtain the precise length of the overlapping interval:
        >>> period1.get_overlap(period2)
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(12, 0))
        And since the overlap is always the same, regardless of the observer, the opposite action would have the same
        result:
        >>> period2.get_overlap(period1)
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(12, 0))
        """
        if (not isinstance(other, interface.PyTimePeriod)
                and (not isinstance(other, interface.PyAbsolutePeriod)
                     and not isinstance(other, interface.PyWallClockPeriod))
                ):
            raise TypeError(f"Cannot perform temporal operations with instances of type '{type(other)}'")
        if isinstance(other, interface.PyTimePeriod):
            return other.get_overlap(self)
        if self.overlaps_with(other):
            end_time = other.end if isinstance(other, interface.PyTimePeriod) else other.end.time()
            return TimePeriod(start=self.start, end=end_time)
        elif self.overlapped_by(other):
            start_time = other.start if isinstance(other, interface.PyTimePeriod) else other.start.time()
            return TimePeriod(start=start_time, end=self.end)
        return None

    def get_disconnect(self,
                       other: Union['interface.PyTimePeriod', 'interface.PyAbsolutePeriod', 'interface.PyWallClockPeriod']
                       ) -> Union['interface.PyTimePeriod', None]:
        """ Method returns the disconnect interval from the point of view of the invoking period. This means the time
        disconnect from the start of this period until the start of the period to which this period is being compared
        to. Since the span of time is relative to each of the two periods, this method will always return different
        intervals.

        Take, for example, the following two periods:
        >>> period1_start = time(8, 0, 0)
        >>> period1_end = time(12, 0, 0)
        >>> period1 = TimePeriod(start=period1_start, end=period1_end)
        >>> period2_start = time(10, 0, 0)
        >>> period2_end = time(13, 0, 0)
        >>> period2 = TimePeriod(start=period2_start, end=period2_end)
        >>> period1
        TimePeriod(start=datetime.time(8, 0), end=datetime.time(12, 0))
        >>> period2
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(13, 0))

        On a timeline, the two periods can be illustrated as:
           0800              Period 1                1200
            |=========================================|
                               |============================|
                              1000       Period 2          1300

        From the point of view of Period 1, the disconnect between the two periods is between the time 0800 and 1000;
        however, from the point of view of Period 2, the disconnect between them is between the time 1200 and 1300.

        Therefore, if you want to obtain the amount of time when the periods do NOT overlap as relative to Period 1,
        you should use:
        >>> period1.get_disconnect(period2)
        TimePeriod(start=datetime.time(8, 0), end=datetime.time(10, 0))

        But if you want to obtain the same as relative to Period 2 instead:
        >>> period2.get_disconnect(period1)
        TimePeriod(start=datetime.time(12, 0), end=datetime.time(13, 0))
        """
        if (not isinstance(other, interface.PyTimePeriod)
                and (not isinstance(other, interface.PyAbsolutePeriod)
                     and not isinstance(other, interface.PyWallClockPeriod))
        ):
            raise TypeError(f"Cannot perform temporal operations with instances of type '{type(other)}'")
        if self.overlapped_by(other):
            end_time = other.start if isinstance(other, interface.PyTimePeriod) else other.start.time()
            return TimePeriod(start=self.start, end=end_time)
        elif self.overlaps_with(other):
            start_time = other.end if isinstance(other, interface.PyTimePeriod) else other.end.time()
            return TimePeriod(start=start_time, end=self.end)
        return None

    def to_wallclock(self, specific_date: Union['interface.PyDatePeriod', date]) -> 'interface.PyWallClockPeriod':
        """ This method allows you to combine the TimePeriod with either a datetime.date or a DatePeriod object and
        create a wall clock period where:
            - the start of the period is set to the start of this period as time and the start of the provided period,
                or datetime.date, object as date;
            - the end of the period is set to the end of this period as time and the end of the provided period,
                or datetime.date, object as date;
        """
        _start = None
        _end = None
        if isinstance(specific_date, date):
            _start = datetime.combine(specific_date, self.start)
            _end = datetime.combine(specific_date, self.end)
        elif isinstance(specific_date, DatePeriod):
            _start = datetime.combine(specific_date.start, self.start)
            _end = datetime.combine(specific_date.end, self.end,)
        else:
            raise ValueError(f"Provided object '{specific_date}' is not an instance of datetime.date or DatePeriod")
        return WallClockPeriod(start=_start, end=_end)

    def to_absolute(self, specific_date: Union['interface.PyDatePeriod', date], timezone: ZoneInfo
                    ) -> 'interface.PyAbsolutePeriod':
        """ This method allows you to combine the TimePeriod with either a datetime.date or a DatePeriod object and
        create an absolute period where:
            - the start of the period is set to the start of this period as time and the start of the provided period,
                or datetime.date, object as date;
            - the end of the period is set to the end of this period as time and the end of the provided period,
                or datetime.date, object as date;

        Since absolute periods require timezone information, you need to pass a ZoneInfo instance via the `timezone`
        parameter which will be used for the start and end datetime objects created.
        """
        _start = None
        _end = None
        if isinstance(specific_date, date):
            _start = datetime.combine(specific_date, self.start, tzinfo=timezone)
            _end = datetime.combine(specific_date, self.end, tzinfo=timezone)
        elif isinstance(specific_date, DatePeriod):
            _start = datetime.combine(specific_date.start, self.start, tzinfo=timezone)
            _end = datetime.combine(specific_date.end, self.end, tzinfo=timezone)
        else:
            raise ValueError(f"Provided object '{specific_date}' is not an instance of datetime.date or DatePeriod")
        return AbsolutePeriod(start=_start, end=_end)


class DatePeriod(interface.PyDatePeriod):
    """ The DatePeriod class is responsible for date periods containing a year, month and day. Instances of this class
    offer the 'equal' comparison (see __eq__ below), as well as the membership (is, is not) test operators
    (see __contains__) below.
    """

    def __init__(self,
                 start: date,
                 end: date,
                 ):
        if not isinstance(start, date) or isinstance(start, datetime):
            raise ValueError(f"Provided value '{start}' for parameter 'start' is not an instance of datetime.date")
        if not isinstance(end, date) or isinstance(end, datetime):
            raise ValueError(f"Provided value '{end}' for parameter 'end' is not an instance of datetime.date")
        if start >= end:
            raise ValueError(f"The start of a period cannot be equal or after its end; values provided: start={start}, "
                             f"end={end}")
        self._start = start
        self._end = end
        # The total duration in seconds
        _total: int = 0
        # First calculate the years difference, collect the days and subtract them from the total amount of days
        _years: int = end.year - start.year
        # If the month of the end date is before the month of the start date, remove 1 year from the total count as it
        # wasn't one full year
        if end.month < start.month:
            _years = _years - 1
        leap_days = calendar.leapdays(start.year, end.year)
        total_days = (end - start).days
        # Turn all the days into seconds and store them in the self._total attr
        _total += total_days * 24 * 60 * 60
        # Remove the total amount of years from the days pool
        days_left = (total_days - (_years * 365)) - leap_days
        _months: int = 0
        _year = start.year
        next_month = start.month + _months
        days_to_go = abs(days_left)
        while days_to_go > 0:
            if next_month > 12:
                next_month = 1
                _year += 1
            days_in_month = calendar.monthrange(_year, next_month)[1]
            if days_to_go - days_in_month >= 0:
                _months += 1
                next_month += 1
                days_to_go -= days_in_month
            else:
                break
        _days: int = days_to_go
        self._duration = Duration(total_seconds=_total, years=_years, months=_months, days=_days, hours=0, minutes=0,
                                  seconds=0)

    @property
    def start(self) -> date:
        return self._start

    @property
    def end(self) -> date:
        return self._end

    @property
    def duration(self) -> 'AbstractDuration':
        return self._duration

    def __str__(self):
        return f"{self.start.isoformat()}/{self.end.isoformat()}"

    def __eq__(self, other):
        """ Equality can only be determined between instances of this class, as well as the wallclock or absolute
        periods classes, since only these two classes contain information about the actual date. In both cases,
        the instances will be tested for exactly equal start and end dates.

        This method does not account for overlaps between the start and end dates of the periods, to get this
        functionality, look at the following methods:
            overlaps_with
            overlapped_by
            get_overlap
            get_disconnect
        """
        if isinstance(other, interface.PyAbsolutePeriod) or isinstance(other, interface.PyWallClockPeriod):
            return (self.start == other.start.date()
                    and self.end == other.end.date())
        if isinstance(other, interface.PyDatePeriod):
            return (self.start == other.start
                    and self.end == other.end)
        return False

    def __contains__(self, item):
        """ Membership test can be done with instances of this class, wallclock or absolute periods classes,
        datetime.datetime and datetime.date objects; When membership test is done for a period, it assumes that the
        request is to check if the tested period exists WITHIN the temporal borders of this period, that is to say,
        whether the start and end date of the other period are after and before, respectively, of the same of this period.

        2024-01-01 Your period:        2024-03-01
        |==================================|
                |=============|     <---- The period you are testing
           2024-02-01     2024-02-10

        If you have an instance of this period, for example:
        >>> start = date(2024, 7, 1)  # 1st of July 2024
        >>> end = date(2024, 9, 1)  # 1st of September 2024
        >>> holiday = DatePeriod(start=start, end=end)

        and then another DatePeriod:
        >>> departure = date(2024, 7, 10)  # 10th of July 2024
        >>> arrival = date(2024, 7, 20)  # 20th of July 2024
        >>> paris_visit = DatePeriod(start=departure, end=arrival)

        Then you can check if the lunch_break period is within your workday period:
        >>> paris_visit in holiday

        For more in-depth comparisons and functionality, see:
            overlaps_with
            overlapped_by
            get_overlap
            get_disconnect
        """
        if isinstance(item, interface.PyDatePeriod):
            """ Only return True if the start and end times of `item` are within the actual time duration of this 
            period.
            """
            return self.start <= item.start and item.end <= self.end
        if isinstance(item, interface.PyAbsolutePeriod) or isinstance(item, interface.PyWallClockPeriod):
            return item.start.date() >= self.start and item.end.date() <= self.end
        if isinstance(item, datetime):
            item = item.date()
        if isinstance(item, date):
            return self.start <= item <= self.end
        return False

    def is_before(self,
                  other: Union['interface.PyDatePeriod', 'interface.PyAbsolutePeriod', 'interface.PyWallClockPeriod', datetime, date]
                  ) -> bool:
        """ Test if this period is ending before another one begins. This check will evaluate as True in the
        following scenario:
        2024-01-01        2024-01-05
            |================|   <------ This period
                                |================|
                            2024-01-06        2024-01-10

        Since dates do not distinguish between specific hours, periods sharing the same start-end date, or vice versa,
        are considered overlapping.
        """
        if isinstance(other, interface.PyDatePeriod):
            _value = other.start
        elif isinstance(other, interface.PyAbsolutePeriod) or isinstance(other, interface.PyWallClockPeriod):
            _value = other.start.date()
        elif isinstance(other, datetime):
            _value = other.date()
        else:
            _value = other
        return self.end < _value

    def get_interim(self,
                    other: Union['interface.PyDatePeriod', date]
                    ) -> Union['interface.PyDatePeriod', None]:
        """ Method returns the DatePeriod between the start/end of the provided period, if `other` is a DatePeriod,
        or the DatePeriod between the point in time and the start/end of this period, depending on whether the same is
        occurring before the start of this period or after the end of it.

        This method is intended to be used when the provided `other` does not exist within and does not overlap (or is
        being overlapped) by this period.
        """
        _start = None
        _end = None
        if isinstance(other, interface.PyDatePeriod):
            if self.is_before(other):
                _start = self.end
                _end = other.start
            elif self.is_after(other):
                _start = other.end
                _end = self.start
        elif isinstance(other, date):
            if self.is_before(other):
                _start = self.end
                _end = other
            elif self.is_after(other):
                _start = other
                _end = self.start
        if _start and _end:
            return DatePeriod(start=_start, end=_end)
        return None

    def is_after(self,
                 other: Union['interface.PyDatePeriod', 'interface.PyAbsolutePeriod', 'interface.PyWallClockPeriod', datetime, date]
                 ) -> bool:
        """ Test if this period is starting after another one ends. This check will evaluate as True in the
        following scenario:
        2024-01-01        2024-01-05
            |================|
                                |================| <----- This period
                            2024-01-06        2024-01-10

        Since dates do not distinguish between specific hours, periods sharing the same start-end date, or vice versa,
        are considered overlapping.
        """
        if isinstance(other, interface.PyDatePeriod):
            _value = other.end
        elif isinstance(other, interface.PyAbsolutePeriod) or isinstance(other, interface.PyWallClockPeriod):
            _value = other.end.date()
        elif isinstance(other, datetime):
            _value = other.date()
        else:
            _value = other
        return _value < self.start

    def overlaps_with(self,
                      other: Union['interface.PyDatePeriod', 'interface.PyAbsolutePeriod', 'interface.PyWallClockPeriod']
                      ) -> bool:
        """ Test if this period overlaps with another period that has begun before this one. This check will evaluate
        as True in the following scenario:
                    2024-02-01      This period:      2024-03-01
                        |==================================|
                 |=============|   <------ The other period
            2024-01-15    2024-02-05

        >>> this_start = date(2024, 2, 1)  # 2nd of Feb 2024
        >>> this_end = date(2024, 3, 1)  # 1st of Mar 2024
        >>> other_start = date(2024, 1, 15)  # 15th of Jan 2024
        >>> other_end = date(2024, 2, 5)  # 5th of Feb 2024
        >>> this_period = DatePeriod(start=this_start, end=this_end)
        >>> other_period = DatePeriod(start=other_start, end=other_end)
        >>> this_period.overlaps_with(other_period)
        True

        The period that has begun first is considered the "main" period, even if it finishes before the end of this
        period, since it occupies an earlier point in time. Therefore, the current period, which has begun at a later
        point in time, is considered to be the overlapping one. Hence, the opposite check (overlapped_by) is True for
        the other_period:
        >>> other_period.overlapped_by(this_period)
        True

        Note that both of these checks will only work for partially overlapping periods - for fully overlapping periods,
        use the `in` membership test:
        >>> this_period in other_period
        """
        other_start: date = None  # type: ignore
        other_end: date = None  # type: ignore
        if isinstance(other, interface.PyDatePeriod):
            other_start = other.start
            other_end = other.end
        if isinstance(other, interface.PyAbsolutePeriod) or isinstance(other, interface.PyWallClockPeriod):
            other_start = other.start.date()
            other_end = other.end.date()
        if other_start is None or other_end is None:
            return False
        if not other_end < self.start and other_start < self.start and other_end < self.end:
            return True
        return False

    def overlapped_by(self,
                      other: Union['interface.PyDatePeriod', 'interface.PyAbsolutePeriod', 'interface.PyWallClockPeriod']
                      ) -> bool:
        """ Test if this period is overlapped by the other period. This check will evaluate True in the following
        scenario:
           2024-01-01      This period:      2024-01-31
                |==================================|
                                            |=============|   <------ The other period
                                        2024-01-20    2024-03-10

        >>> this_start = date(2024, 1, 1)
        >>> this_end = date(2024, 1, 31)
        >>> other_start = date(2024, 1, 20)
        >>> other_end = date(2024, 3, 10)
        >>> this_period = DatePeriod(start=this_start, end=this_end)
        >>> other_period = DatePeriod(start=other_start, end=other_end)
        >>> this_period.overlapped_by(other_period)
        True

        Since this period has begun first, it is considered the "main" one, and all other periods that begin after this
        one, are considered to be overlapping it. Therefore, the opposite check, `overlaps_with`, will evaluate True
        if the opposite check is being made:
        >>> other_period.overlaps_with(this_period)
        True

        Note that both of these checks will only work for partially overlapping periods - for fully overlapping periods,
        use the `in` membership test:
        >>> this_period in other_period
        """
        other_start: date = None  # type: ignore
        other_end: date = None  # type: ignore
        if isinstance(other, interface.PyDatePeriod):
            other_start = other.start
            other_end = other.end
        if isinstance(other, interface.PyAbsolutePeriod) or isinstance(other, interface.PyWallClockPeriod):
            other_start = other.start.date()
            other_end = other.end.date()
        if other_start is None or other_end is None:
            return False
        if not self.end < other_start and self.start < other_start and self.end < other_end:
            return True
        return False

    def get_overlap(self,
                    other: Union['interface.PyDatePeriod', 'interface.PyAbsolutePeriod', 'interface.PyWallClockPeriod']
                    ) -> Union['interface.PyDatePeriod', None]:
        """ Method returns the overlapping interval between the two periods as a new DatePeriod instance

        >>> period1_start = date(2024, 1, 1)
        >>> period1_end = date(2024, 1, 10)
        >>> period1 = DatePeriod(start=period1_start, end=period1_end)
        >>> period2_start = date(2024, 1, 5)
        >>> period2_end = date(2024, 1, 15)
        >>> period2 = DatePeriod(start=period2_start, end=period2_end)
        >>> period1
        DatePeriod(start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10))
        >>> period2
        DatePeriod(start=datetime.date(2024, 1, 5), end=datetime.date(2024, 1, 15))

        On a timeline, the two periods can be illustrated as:
        2024-01-01      Period 1                2024-01-10
            |=========================================|
                               |============================================|
                         2024-01-05             Period 2              2024-01-15

        As expected, attempting a membership test would return False:
        >>> period2 in period1
        False
        however, testing overlaps does return True:
        >>> period1.overlapped_by(period2)
        True
        and the opposite:
        >>> period2.overlaps_with(period1)
        True

        Therefore, we can use the `get_overlap` method to obtain the precise length of the overlapping interval:
        >>> period1.get_overlap(period2)
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(12, 0))
        And since the overlap is always the same, regardless of the observer, the opposite action would have the same
        result:
        >>> period2.get_overlap(period1)
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(12, 0))
        """
        if (not isinstance(other, interface.PyDatePeriod) and
                (not isinstance(other, interface.PyAbsolutePeriod)
                 and not isinstance(other, interface.PyWallClockPeriod)
                )
        ):
            raise TypeError(f"Cannot perform temporal operations with instances of type '{type(other)}'")
        if self.overlaps_with(other):
            end_date = other.end if isinstance(other, interface.PyDatePeriod) else other.end.date()
            return DatePeriod(start=self.start, end=end_date)
        elif self.overlapped_by(other):
            start_date = other.start if isinstance(other, interface.PyDatePeriod) else other.start.date()
            return DatePeriod(start=start_date, end=self.end)
        return None

    def get_disconnect(self,
                       other: Union['interface.PyDatePeriod', 'interface.PyAbsolutePeriod', 'interface.PyWallClockPeriod']
                       ) -> Union['interface.PyDatePeriod', None]:
        """ Method returns the disconnect interval from the point of view of the invoking period. This means the time
        disconnect from the start of this period until the start of the period to which this period is being compared
        to. Since the span of time is relative to each of the two periods, this method will always return different
        intervals.

        Take, for example, the following two periods:
        >>> period1_start = date(2024, 1, 1)
        >>> period1_end = date(2024, 1, 10)
        >>> period1 = DatePeriod(start=period1_start, end=period1_end)
        >>> period2_start = date(2024, 1, 5)
        >>> period2_end = date(2024, 1, 15)
        >>> period2 = DatePeriod(start=period2_start, end=period2_end)
        >>> period1
        DatePeriod(start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10))
        >>> period2
        DatePeriod(start=datetime.date(2024, 1, 5), end=datetime.date(2024, 1, 15))

        On a timeline, the two periods can be illustrated as:
        2024-01-01      Period 1                2024-01-10
            |=========================================|
                               |============================================|
                         2024-01-05             Period 2              2024-01-15

        From the point of view of Period 1, the disconnect between the two periods is between the 1st and the 5th;
        however, from the point of view of Period 2, the disconnect between them is between the 10th and the 15th.

        Therefore, if you want to obtain the amount of time when the periods do NOT overlap as relative to Period 1,
        you should use:
        >>> period1.get_disconnect(period2)
        DatePeriod(start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 5))

        But if you want to obtain the same as relative to Period 2 instead:
        >>> period2.get_disconnect(period1)
        DatePeriod(start=datetime.date(2024, 1, 10), end=datetime.date(2024, 1, 15))
        """
        if (not isinstance(other, interface.PyDatePeriod) and
                (not isinstance(other, interface.PyAbsolutePeriod)
                 and not isinstance(other, interface.PyWallClockPeriod)
                )
        ):
            raise TypeError(f"Cannot perform temporal operations with instances of type '{type(other)}'")
        if self.overlapped_by(other):
            end_date = other.start if isinstance(other, interface.PyDatePeriod) else other.start.date()
            return DatePeriod(start=self.start, end=end_date)
        elif self.overlaps_with(other):
            start_date = other.end if isinstance(other, interface.PyDatePeriod) else other.end.date()
            return DatePeriod(start=start_date, end=self.end)
        return None

    def to_wallclock(self,
                     specific_time: Union['interface.PyTimePeriod', time]
                     ) -> 'interface.PyWallClockPeriod':
        """ This method allows you to combine the DatePeriod with either a datetime.time or a TimePeriod object and
        create a wall clock period where:
            - the start of the period is set to the start of this period as date and the start of the provided period,
                or datetime.time, object as time;
            - the end of the period is set to the end of this period as date and the end of the provided period,
                or datetime.time, object as time;
        """
        _start = None
        _end = None
        if isinstance(specific_time, time):
            _start = datetime.combine(self.start, specific_time)
            _end = datetime.combine(self.end, specific_time)
        elif isinstance(specific_time, interface.PyTimePeriod):
            _start = datetime.combine(self.start, specific_time.start)
            _end = datetime.combine(self.end, specific_time.end)
        else:
            raise ValueError(f"Provided object '{specific_time}' is not an instance of datetime.time or TimePeriod")
        return WallClockPeriod(start=_start, end=_end)

    def to_absolute(self,
                    specific_time: Union['interface.PyTimePeriod', time], timezone: ZoneInfo
                    ) -> 'interface.PyAbsolutePeriod':
        """ This method allows you to combine the DatePeriod with either a datetime.time or a TimePeriod object and
        create an absolute period where:
            - the start of the period is set to the start of this period as date and the start of the provided period,
                or datetime.time, object as time;
            - the end of the period is set to the end of this period as date and the end of the provided period,
                or datetime.time, object as time;

        Since absolute periods require timezone information, you need to pass a ZoneInfo instance via the `timezone`
        parameter which will be used for the start and end datetime objects created.
        """
        _start = None
        _end = None
        if isinstance(specific_time, time):
            _start = datetime.combine(self.start, specific_time, tzinfo=timezone)
            _end = datetime.combine(self.end, specific_time, tzinfo=timezone)
        elif isinstance(specific_time, interface.PyTimePeriod):
            _start = datetime.combine(self.start, specific_time.start, tzinfo=timezone)
            _end = datetime.combine(self.end, specific_time.end, tzinfo=timezone)
        else:
            raise ValueError(f"Provided object '{specific_time}' is not an instance of datetime.time or TimePeriod")
        return AbsolutePeriod(start=_start, end=_end)


class WallClockPeriod(interface.PyWallClockPeriod):

    def __init__(self,
                 start: datetime,
                 end: datetime,
                 ):
        if not isinstance(start, datetime):
            raise ValueError(f"Provided value '{start}' for parameter 'start' is not an instance of "
                             f"datetime.datetime")
        if not isinstance(end, datetime):
            raise ValueError(f"Provided value '{end}' for parameter 'end' is not an instance of "
                             f"datetime.datetime")
        if start >= end:
            raise ValueError(f"The start of a period cannot be equal or after its end; values provided: start={start}, "
                             f"end={end}")
        self._start = check_existence(start)
        self._end = check_existence(end)
        # The total duration in seconds
        self._total: int = 0
        self._seconds = end.second - start.second
        self._minutes = end.minute - start.minute
        self._hours = end.hour - start.hour
        if self._seconds < 0:
            self._minutes -= 1
            self._seconds = 60 - abs(self._seconds)
        elif self._seconds >= 60:
            self._minutes += 1
            self._seconds = 60 - self._seconds
        self._total += self._seconds
        if self._minutes < 0:
            self._hours -= 1
            self._minutes = 60 - abs(self._minutes)
        elif self._minutes >= 60:
            self._hours += 1
            self._minutes = 60 - self._minutes
        self._total += self._minutes * 60
        adjustment_days = 0
        if self._hours < 0:
            self._hours = 24 - abs(self._hours)
            adjustment_days = -1
        elif self._hours >= 24:
            self._hours = 24 - self._hours
            adjustment_days = 1
        self._total += self._hours * 60
        # First calculate the years difference, collect the days and subtract them from the total amount of days
        self._years: int = end.year - start.year
        # If the month of the end date is before the month of the start date, remove 1 year from the total count as it
        # wasn't one full year
        if end.month < start.month:
            self._years = self._years - 1
        leap_days = calendar.leapdays(start.year, end.year)
        total_days = (end - start).days + adjustment_days
        # Remove the total amount of years from the days pool
        days_left = (total_days - (self._years * 365)) - leap_days
        self._months: int = 0
        _year = start.year
        next_month = start.month + self._months
        while days_left > 0:
            if next_month > 12:
                next_month = 1
                _year += 1
            days_in_month = calendar.monthrange(_year, next_month)[1]
            if days_left - days_in_month >= 0:
                self._months += 1
                next_month += 1
                days_left -= days_in_month
                self._total += days_in_month * 86400
            else:
                break
        self._days: int = days_left
        if self._days < 0:
            self._days = 0
        self._total += self._days * 86400

    @property
    def start(self) -> datetime:
        return self._start

    @property
    def end(self) -> datetime:
        return self._end

    @property
    def duration(self) -> 'AbstractDuration':
        return Duration(total_seconds=self._total, years=self._years, months=self._months, days=self._days,
                        hours=self._hours, minutes=self._minutes, seconds=self._seconds)

    def __str__(self):
        return f"{self.start.isoformat()}/{self.end.isoformat()}"

    def _time_repeats(self,
                      _t: Union[time, TimePeriod]) -> bool:
        """ Internal method that checks if the provided time or TimePeriod will repeat within the duration of this
         period.

         for datetime.time objects:
         In all cases where this period is equal to or longer than 2 days (48h), this method will return True;
         For 1 day long periods (24h) or shorter, if the time is within the start and end of this period,
         it will return True;

         for periods.TimePeriod objects:
         In all cases where this period is longer than 2 days (over 72h), it will return True;
         In cases where the period is 2 days long (up to 72h), it will only return True if the TimePeriod does NOT start
         AND end before and after, respectively, this period.
         In cases of 1 day long (up to 48h) periods, it will only return True if the TimePeriod does not either start
         before this period, or end after it.

         It is important to remember that this method only checks FULL repetition, meaning this:
           0800               1700           Midnight        0800                   1700
            /========================================================================/ <- This Period
               /======/                                            /======/            <- TimePeriod
             0900    1200                                        0900    1200

         Cases of partially overlapping, but not fully, will return Fase:
           0800               1700           Midnight        0800                   1700
            /========================================================================/         <- This Period
         /=============================/                   /=============================/     <- TimePeriod
        0700                         2000                0700                           2000

         """
        if isinstance(_t, time):
            if self.duration.days >= 2:
                return True
            elif self.duration.days == 1:
                if self.start.time() <= _t <= self.end.time():
                    return True
        if isinstance(_t, TimePeriod):
            if self.duration.days > 2:
                # No situation in which the period won't repeat when the period is over 2 days long
                return True
            if self.duration.days == 2:
                # If the period is 2 days long, the TimePeriod must start before it and end after it in order not to
                # repeat, otherwise, it will repeat
                if not _t.start < self.start.time() or not self.end.time() < _t.end:
                    return True
            elif self.duration.days == 1:
                # If the period is (at least) 1 day long, it must either start before it or end after it not to repeat
                if self.start.time() <= _t.start and _t.end <= self.end.time():
                    # The other period starts at the same time or later and ends either before or at the same time as
                    # this one - it will exist twice within it
                    return True
        return False

    def __eq__(self, other):
        """ Equality can be determined between this class and any other of the Period classes, since this class contains
        the most complete information of a period in time.

        For instances of TimePeriod, equality will be measured in terms of hours;
        For instances of DatePeriod, equality will be measured in terms of dates;
        For instances of this class, equality will be measured for both.

        This method does not account for overlaps between the start and end times and/or dates of the periods, to get
        this functionality, look at the following methods:
            overlaps_with
            overlapped_by
            get_overlap
            get_disconnect
        """
        if isinstance(other, WallClockPeriod):
            return (self.start == other.start
                    and self.end == other.end)
        if isinstance(other, DatePeriod):
            return (self.start.date() == other.start
                    and self.end.date() == other.end)
        if isinstance(other, TimePeriod):
            return (self.start.time() == other.start
                    and self.end.time() == other.end)
        return False

    def __contains__(self, item):
        """ Membership test can be done with instances of this class, the DatePeriod and TimePeriod classes,
        datetime.datetime and datetime.date objects; When membership test is done for a period, it assumes that the
        request is to check if the tested period exists WITHIN the temporal borders of this period, that is to say,
        whether the start and end time and/or date of the other period are after and before, respectively, of the same
        of this period.

        2024-01-01 08:00 Your period: 2024-03-01 08:00
            |==================================|
                    |=============|     <---- The period you are testing
        2024-02-01 08:00   2024-02-15 08:00

        If you have an instance of this period, for example:
        >>> start = datetime(2024, 1, 1, 8, 0)  # 0800, 1st of Jan 2024
        >>> end = datetime(2024, 3, 1, 8, 0)  # 0800, 1st of Mar 2024
        >>> quarter = WallClockPeriod(start=start, end=end)

        and then another WallClockPeriod:
        >>> pto_start = datetime(2024, 2, 1, 8, 0)  # 0800, 1st of Feb 2024
        >>> pto_end = datetime(2024, 2, 15, 8, 0)  # 0800, 15th of Feb 2024
        >>> pto = WallClockPeriod(start=pto_start, end=pto_end)

        Then you can check if the pto period is within your quarter period:
        >>> pto in quarter

        For more in-depth comparisons and functionality, see:
            overlaps_with
            overlapped_by
            get_overlap
            get_disconnect

        Raises:
            TimeAmbiguityError - raised if the duration of this period is longer than a day and either a TimePeriod is
                tested, or an instance of datetime.time that falls within the start and end of this period. Also see:
                <url to doc>
                for more information.
        """
        if isinstance(item, WallClockPeriod):
            return self.start <= item.start and item.end <= self.end
        if isinstance(item, DatePeriod):
            return self.start.date() <= item.start and item.end <= self.end.date()
        if isinstance(item, TimePeriod):
            if self._time_repeats(item):
                raise TimeAmbiguityError(f"The provided TimePeriod '{item}' exist within this period "
                                         f"('{self}') more than once. For more information on this error, "
                                         f"see https://github.com/dimitarOnGithub/temporals/wiki/Misc")
            if self.duration.days == 1:
                if item.start < self.start.time():
                    if item.end <= self.end.time():
                        # Period starts before this once but ends before or at the same time as this once, hence
                        # existing only once
                        return True
                    else:
                        # Period never fully exists within this one as it starts before it and ends after it
                        return False
                if item.start >= self.start.time():
                    if self.end.time() < item.end:
                        # Starts equal or later but ends later too - existing only once
                        return True
            return self.start.time() <= item.start and item.end <= self.end.time()
        if isinstance(item, datetime):
            return self.start <= item <= self.end
        if isinstance(item, date):
            return self.start.date() <= item <= self.end.date()
        if isinstance(item, time):
            if self._time_repeats(item):
                raise TimeAmbiguityError(f"The provided unit of time ('{item}') exist within this period "
                                         f"('{self}')  more than once. For more information on this error, "
                                         f"see https://github.com/dimitarOnGithub/temporals/wiki/Misc")
            if self.duration.days == 1:
                return True
            return self.start.time() <= item <= self.end.time()
        return False

    def is_before(self,
                  other: Union['DatePeriod', 'WallClockPeriod', date, datetime]
                  ) -> bool:
        """ Test if this period ends before the provided `other` value. In the cases when a date or a DatePeriod is
        provided, the check will be done based on at least a 24 hour difference (ie, this period ends on the 2024-01-01
        and the provided date/DatePeriod begins on the 2024-01-02). In all other cases (datetime and wallclock or
        absolute periods), objects are allowed to share the same end-start datetime.
        """
        if isinstance(other, DatePeriod):
            return self.end.date() < other.start
        elif isinstance(other, datetime):
            return self.end <= other
        elif isinstance(other, date):
            return self.end.date() < other
        return self.end <= other.start

    def is_after(self,
                 other: Union['DatePeriod', 'WallClockPeriod', date, datetime]
                 ) -> bool:
        """ Test if this period begins after the provided `other` value. In the cases when a date or a DatePeriod is
        provided, the check will be done based on at least a 24 hour difference (ie, this period begins on the
        2024-01-02 and the provided date/DatePeriod ends on the 2024-01-01). In all other cases (datetime and
        wallclock or absolute periods), objects are allowed to share the same end-start datetime.
        """
        if isinstance(other, DatePeriod):
            return other.end < self.start.date()
        elif isinstance(other, datetime):
            return other <= self.start
        elif isinstance(other, date):
            return other < self.start.date()
        return other.end <= self.start

    def get_interim(self,
                    other: Union['WallClockPeriod', datetime]
                    ) -> Union['WallClockPeriod', None]:
        """ Method returns the WallClockPeriod between the start/end of the provided period, if `other` is a
        WallClockPeriod, or the WallClockPeriod between the point in time and the start/end of this period, depending on
        whether the same is occurring before the start of this period or after the end of it.

        This method is intended to be used when the provided `other` does not exist within and does not overlap (or is
        being overlapped) by this period.
        """
        _start = None
        _end = None
        if isinstance(other, WallClockPeriod):
            if self.is_before(other):
                _start = self.end
                _end = other.start
            elif self.is_after(other):
                _start = other.end
                _end = self.start
        elif isinstance(other, datetime):
            if self.is_before(other):
                _start = self.end
                _end = other
            elif self.is_after(other):
                _start = other
                _end = self.start
        if  _start and _end:
            return WallClockPeriod(start=_start, end=_end)

    def overlaps_with(self,
                      other: Union['TimePeriod', 'DatePeriod', 'WallClockPeriod']
                      ) -> bool:
        """ Test if this period overlaps with another period that has begun before this one. This check will evaluate
        as True in the following scenario:
                    2024-02-01 0800  This period:   2024-03-01 1700
                            |==================================|
                     |============================|   <------ The other period
            2024-02-01 0600             2024-02-01 1300

        >>> this_start = datetime(2024, 2, 1, 8, 0)  # 0800, 2nd of Feb 2024
        >>> this_end = datetime(2024, 2, 1, 17, 0)  # 1700, 2nd of Feb 2024
        >>> other_start = datetime(2024, 2, 1, 6, 0)  # 0600, 2nd of Feb 2024
        >>> other_end = datetime(2024, 2, 1, 13, 0)  # 1300, 2nd of Feb 2024
        >>> this_period = WallClockPeriod(start=this_start, end=this_end)
        >>> other_period = WallClockPeriod(start=other_start, end=other_end)
        >>> this_period.overlaps_with(other_period)
        True

        The period that has begun first is considered the "main" period, even if it finishes before the end of this
        period, since it occupies an earlier point in time. Therefore, the current period, which has begun at a later
        point in time, is considered to be the overlapping one. Hence, the opposite check (overlapped_by) is True for
        the other_period:
        >>> other_period.overlapped_by(this_period)
        True

        Note that both of these checks will only work for partially overlapping periods - for fully overlapping periods,
        use the `in` membership test:
        >>> this_period in other_period
        """
        if isinstance(other, TimePeriod):
            if self._time_repeats(other):
                raise TimeAmbiguityError(f"The provided TimePeriod '{other}' exist within this period "
                                         f"('{self}') more than once. For more information on this error, "
                                         f"see https://github.com/dimitarOnGithub/temporals/wiki/Misc")
            if self.start.date() < self.end.date():
                # Day stretches overnight - the start time must be before the start of this period but also after the
                # end of it
                if other.start < self.start.time() and other.start < self.end.time():
                    raise TimeAmbiguityError(f"The provided TimePeriod ('{other}') is ambiguous compared to this "
                                             f"WallClockPeriod ('{self}'); it's overlapped by (starts before) this "
                                             f"period on {self.start.date().isoformat()} but this period continues "
                                             f"until after it's start on {self.end.date().isoformat()}")
                else:
                    if not other.end < self.start.time():
                        return other.start <= self.start.time()
            else:
                if not other.end < self.start.time():
                    return other.start < self.start.time() and other.end < self.end.time()
        if isinstance(other, DatePeriod):
            if not other.end < self.start.date():
                return other.start < self.start.date() and other.end < self.end.date()
        if isinstance(other, WallClockPeriod):
            if not other.end < self.start:
                return other.start < self.start and other.end < self.end
        return False

    def overlapped_by(self,
                      other: Union['TimePeriod', 'DatePeriod', 'WallClockPeriod']
                      ) -> bool:
        """ Test if this period is overlapped by the other period. This check will evaluate True in the following
        scenario:
        2024-01-01 0800   This period:  2024-01-01 1700
                |==================================|
                        |=====================================|   <------ The other period
                2024-01-01 1200                    2024-01-01 2300

        >>> this_start = datetime(2024, 1, 1, 8, 0)  # 0800, 1st of Jan 2024
        >>> this_end = datetime(2024, 1, 1, 17, 0)  # 1700, 1st of Jan 2024
        >>> other_start = datetime(2024, 1, 1, 12, 0)  # 1200, 1st of Jan 2024
        >>> other_end = datetime(2024, 1, 1, 23, 0)  # 2300, 1st of Jan 2024
        >>> this_period = DatePeriod(start=this_start, end=this_end)
        >>> other_period = DatePeriod(start=other_start, end=other_end)
        >>> this_period.overlapped_by(other_period)
        True

        Since this period has begun first, it is considered the "main" one, and all other periods that begin after this
        one, are considered to be overlapping it. Therefore, the opposite check, `overlaps_with`, will evaluate True
        if the opposite check is being made:
        >>> other_period.overlaps_with(this_period)
        True

        Note that both of these checks will only work for partially overlapping periods - for fully overlapping periods,
        use the `in` membership test:
        >>> this_period in other_period
        """
        if isinstance(other, TimePeriod):
            if self._time_repeats(other):
                raise TimeAmbiguityError(f"The provided TimePeriod '{other}' exist within this WallClockPeriod "
                                         f"('{self}') more than once. For more information on this error, "
                                         f"see https://github.com/dimitarOnGithub/temporals/wiki/Misc")
            if self.start.date() < self.end.date():
                # Day stretches overnight - the start time must be after the start of this period but also after the
                # end of it
                if self.start.time() < other.start and self.end.time() < other.end:
                    raise TimeAmbiguityError(f"The provided TimePeriod ('{other}') is ambiguous compared to this "
                                             f"WallClockPeriod ('{self}'); it overlaps with (starts after) this "
                                             f"period on {self.start.date().isoformat()} but this period continues "
                                             f"until after it's start on {self.end.date().isoformat()}")
                else:
                    if not self.end.time() < other.start:
                        return self.start.time() <= other.start
            else:
                if not self.end.time() < other.start:
                    return self.start.time() < other.start and self.end.time() < other.end
        if isinstance(other, DatePeriod):
            if not self.end.date() < other.start:
                return self.start.date() < other.start and self.end.date() < other.end
        if isinstance(other, WallClockPeriod):
            if not self.end < other.start:
                return self.start < other.start and self.end < other.end
        return False

    def get_overlap(self,
                    other: Union['TimePeriod', 'DatePeriod', 'WallClockPeriod']
                    ) -> Union['TimePeriod', 'DatePeriod', 'WallClockPeriod', None]:
        """ Method returns the overlapping interval between the two periods as a new period instance. Returned object
        will be an instance of the class that's being tested.

        >>> period1_start = datetime(2024, 1, 1, 8, 0, 0)
        >>> period1_end = datetime(2024, 1, 1, 12, 0, 0)
        >>> period1 = WallClockPeriod(start=period1_start, end=period1_end)
        >>> period2_start = time(10, 0, 0)
        >>> period2_end = time(13, 0, 0)
        >>> period2 = TimePeriod(start=period2_start, end=period2_end)
        >>> period1
        WallClockPeriod(start=datetime.datetime(2024, 1, 1, 8, 0), end=datetime.datetime(2024, 1, 1, 12, 0))
        >>> period2
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(13, 0))

        On a timeline, the two periods can be illustrated as:
           0800              Period 1                1200
            |=========================================|
                               |============================|
                              1000       Period 2          1300

        As expected, attempting a membership test would return False:
        >>> period2 in period1
        False
        however, testing overlaps does return True:
        >>> period1.overlapped_by(period2)
        True
        and the opposite:
        >>> period2.overlaps_with(period1)
        True

        Therefore, we can use the `get_overlap` method to obtain the precise length of the overlapping interval:
        >>> period1.get_overlap(period2)
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(12, 0))
        And since the overlap is always the same, regardless of the observer, the opposite action would have the same
        result:
        >>> period2.get_overlap(period1)
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(12, 0))
        """
        if (not isinstance(other, TimePeriod)
                and not isinstance(other, DatePeriod)
                and not isinstance(other, WallClockPeriod)):
            raise TypeError(f"Cannot perform temporal operations with instances of type '{type(other)}'")
        period_to_use = None
        _start = None
        _end = None
        if self.overlaps_with(other) or self.overlapped_by(other):
            if isinstance(other, TimePeriod):
                period_to_use = TimePeriod
                _start = self.start.time() if self.overlaps_with(other) else other.start
                _end = other.end if self.overlaps_with(other) else self.end.time()
            elif isinstance(other, DatePeriod):
                period_to_use = DatePeriod
                _start = self.start.date() if self.overlaps_with(other) else other.start
                _end = other.end if self.overlaps_with(other) else self.end.date()
            else:
                period_to_use = WallClockPeriod
                _start = self.start if self.overlaps_with(other) else other.start
                _end = other.end if self.overlaps_with(other) else self.end
            return period_to_use(start=_start, end=_end)
        else:
            return None

    def get_disconnect(self,
                       other: Union['TimePeriod', 'DatePeriod', 'WallClockPeriod']
                       ) -> Union['TimePeriod', 'DatePeriod', 'WallClockPeriod', None]:
        """ Method returns the disconnect interval from the point of view of the invoking period. This means the time
        disconnect from the start of this period until the start of the period to which this period is being compared
        to. Since the span of time is relative to each of the two periods, this method will always return different
        intervals.

        Take, for example, the following two periods:
        >>> period1_start = datetime(2024, 1, 1, 8, 0, 0)
        >>> period1_end = datetime(2024, 1, 1, 12, 0, 0)
        >>> period1 = WallClockPeriod(start=period1_start, end=period1_end)
        >>> period2_start = datetime(2024, 1, 1, 10, 0, 0)
        >>> period2_end = datetime(2024, 1, 1, 13, 0, 0)
        >>> period2 = WallClockPeriod(start=period2_start, end=period2_end)
        >>> period1
        WallClockPeriod(start=datetime.datetime(2024, 1, 1, 8, 0), end=datetime.datetime(2024, 1, 1, 12, 0))
        >>> period2
        WallClockPeriod(start=datetime.datetime(2024, 1, 1, 10, 0), end=datetime.datetime(2024, 1, 1, 13, 0))

        On a timeline, the two periods can be illustrated as:
           0800              Period 1                1200
            |=========================================|
                               |============================|
                              1000       Period 2          1300

        From the point of view of Period 1, the disconnect between the two periods is between the time 0800 and 1000;
        however, from the point of view of Period 2, the disconnect between them is between the time 1200 and 1300.

        Therefore, if you want to obtain the amount of time when the periods do NOT overlap as relative to Period 1,
        you should use:
        >>> period1.get_disconnect(period2)
        WallClockPeriod(start=datetime.datetime(2024, 1, 1, 8, 0), end=datetime.datetime(2024, 1, 1, 10, 0))

        But if you want to obtain the same as relative to Period 2 instead:
        >>> period2.get_disconnect(period1)
        WallClockPeriod(start=datetime.datetime(2024, 1, 1, 12, 0), end=datetime.datetime(2024, 1, 1, 13, 0))
        """
        if (not isinstance(other, TimePeriod)
                and not isinstance(other, DatePeriod)
                and not isinstance(other, WallClockPeriod)):
            raise TypeError(f"Cannot perform temporal operations with instances of type '{type(other)}'")
        period_to_use = None
        _start = None
        _end = None
        if isinstance(other, TimePeriod):
            period_to_use = TimePeriod
            if self.overlapped_by(other):
                _start = self.start.time()
                _end = other.start
            elif self.overlaps_with(other):
                _start = other.end
                _end = self.end.time()
        elif isinstance(other, DatePeriod):
            period_to_use = DatePeriod
            if self.overlapped_by(other):
                _start = self.start.date()
                _end = other.start
            elif self.overlaps_with(other):
                _start = other.end
                _end = self.end.date()
        else:
            period_to_use = WallClockPeriod
            if self.overlapped_by(other):
                _start = self.start
                _end = other.start
            elif self.overlaps_with(other):
                _start = other.end
                _end = self.end
        if period_to_use and _start and _end:
            return period_to_use(start=_start, end=_end)
        return None


class AbsolutePeriod(interface.PyAbsolutePeriod):

    def __init__(self,
                 start: datetime,
                 end: datetime,
                 account_dst: bool = False
                 ):
        if not isinstance(start, datetime):
            raise ValueError(f"Provided value '{start}' for parameter 'start' is not an instance of "
                             f"datetime.datetime")
        if not isinstance(end, datetime):
            raise ValueError(f"Provided value '{end}' for parameter 'end' is not an instance of "
                             f"datetime.datetime")
        if start >= end:
            raise ValueError(f"The start of a period cannot be equal or after its end; values provided: start={start}, "
                             f"end={end}")
        self._start = check_existence(start)
        self._end = check_existence(end)
        # The total duration in seconds
        self._total: int = 0
        self._seconds = end.second - start.second
        self._minutes = end.minute - start.minute
        self._hours = end.hour - start.hour
        start_dst = 0
        if self.start.dst() is not None:
            start_dst = int(self.start.dst().total_seconds())
        end_dst = 0
        if self.end.dst() is not None:
            end_dst = int(self.end.dst().total_seconds())
        if start_dst != 0 and end_dst != 0:
            # Both start and end times are in DST, we can stop here
            pass
        else:
            if start_dst != 0:
                offset_duration = Duration.from_seconds(start_dst)
                self._hours += offset_duration.hours
                self._minutes += offset_duration.minutes
                self._seconds += offset_duration.seconds
            elif end_dst != 0:
                offset_duration = Duration.from_seconds(end_dst)
                self._hours -= offset_duration.hours
                self._minutes -= offset_duration.minutes
                self._seconds -= offset_duration.seconds
        if self._seconds < 0:
            self._minutes -= 1
            self._seconds = 60 - abs(self._seconds)
        elif self._seconds >= 60:
            self._minutes += 1
            self._seconds = 60 - self._seconds
        self._total += self._seconds
        if self._minutes < 0:
            self._hours -= 1
            self._minutes = 60 - abs(self._minutes)
        elif self._minutes >= 60:
            self._hours += 1
            self._minutes = 60 - self._minutes
        self._total += self._minutes * 60
        adjustment_days = 0
        if self._hours < 0:
            self._hours = 24 - abs(self._hours)
            adjustment_days = -1
        elif self._hours >= 24:
            self._hours = 24 - self._hours
            adjustment_days = 1
        self._total += self._hours * 60
        # First calculate the years difference, collect the days and subtract them from the total amount of days
        self._years: int = end.year - start.year
        # If the month of the end date is before the month of the start date, remove 1 year from the total count as it
        # wasn't one full year
        if end.month < start.month:
            self._years = self._years - 1
        leap_days = calendar.leapdays(start.year, end.year)
        total_days = (end - start).days + adjustment_days
        # Remove the total amount of years from the days pool
        days_left = (total_days - (self._years * 365)) - leap_days
        self._months: int = 0
        _year = start.year
        next_month = start.month + self._months
        while days_left > 0:
            if next_month > 12:
                next_month = 1
                _year += 1
            days_in_month = calendar.monthrange(_year, next_month)[1]
            if days_left - days_in_month >= 0:
                self._months += 1
                next_month += 1
                days_left -= days_in_month
                self._total += days_in_month * 86400
            else:
                break
        self._days: int = days_left
        if self._days < 0:
            self._days = 0
        self._total += self._days * 86400

    @property
    def start(self) -> datetime:
        return self._start

    @property
    def end(self) -> datetime:
        return self._end

    @property
    def duration(self) -> 'AbstractDuration':
        return Duration(total_seconds=self._total, years=self._years, months=self._months, days=self._days,
                        hours=self._hours, minutes=self._minutes, seconds=self._seconds)

    def __str__(self):
        return f"{self.start.isoformat()}/{self.end.isoformat()}"

    def _time_repeats(self,
                      _t: Union[time, TimePeriod]) -> bool:
        """ Internal method that checks if the provided time or TimePeriod will repeat within the duration of this
         period.

         for datetime.time objects:
         In all cases where this period is equal to or longer than 2 days (48h), this method will return True;
         For 1 day long periods (24h) or shorter, if the time is within the start and end of this period,
         it will return True;

         for periods.TimePeriod objects:
         In all cases where this period is longer than 2 days (over 72h), it will return True;
         In cases where the period is 2 days long (up to 72h), it will only return True if the TimePeriod does NOT start
         AND end before and after, respectively, this period.
         In cases of 1 day long (up to 48h) periods, it will only return True if the TimePeriod does not either start
         before this period, or end after it.

         It is important to remember that this method only checks FULL repetition, meaning this:
           0800               1700           Midnight        0800                   1700
            /========================================================================/ <- This Period
               /======/                                            /======/            <- TimePeriod
             0900    1200                                        0900    1200

         Cases of partially overlapping, but not fully, will return Fase:
           0800               1700           Midnight        0800                   1700
            /========================================================================/         <- This Period
         /=============================/                   /=============================/     <- TimePeriod
        0700                         2000                0700                           2000

         """
        if isinstance(_t, time):
            if self.duration.days >= 2:
                return True
            elif self.duration.days == 1:
                if self.start.time() <= _t <= self.end.time():
                    return True
        if isinstance(_t, TimePeriod):
            if self.duration.days > 2:
                # No situation in which the period won't repeat when the period is over 2 days long
                return True
            if self.duration.days == 2:
                # If the period is 2 days long, the TimePeriod must start before it and end after it in order not to
                # repeat, otherwise, it will repeat
                if not _t.start < self.start.time() or not self.end.time() < _t.end:
                    return True
            elif self.duration.days == 1:
                # If the period is (at least) 1 day long, it must either start before it or end after it not to repeat
                if self.start.time() <= _t.start and _t.end <= self.end.time():
                    # The other period starts at the same time or later and ends either before or at the same time as
                    # this one - it will exist twice within it
                    return True
        return False

    def __eq__(self, other):
        """ Equality can be determined between this class and any other of the Period classes, since this class contains
        the most complete information of a period in time.

        For instances of TimePeriod, equality will be measured in terms of hours;
        For instances of DatePeriod, equality will be measured in terms of dates;
        For instances of this class, equality will be measured for both.

        This method does not account for overlaps between the start and end times and/or dates of the periods, to get
        this functionality, look at the following methods:
            overlaps_with
            overlapped_by
            get_overlap
            get_disconnect
        """
        if isinstance(other, AbsolutePeriod):
            return (self.start == other.start
                    and self.end == other.end)
        if isinstance(other, DatePeriod):
            return (self.start.date() == other.start
                    and self.end.date() == other.end)
        if isinstance(other, TimePeriod):
            return (self.start.time() == other.start
                    and self.end.time() == other.end)
        return False

    def __contains__(self, item):
        """ Membership test can be done with instances of this class, the DatePeriod and TimePeriod classes,
        datetime.datetime and datetime.date objects; When membership test is done for a period, it assumes that the
        request is to check if the tested period exists WITHIN the temporal borders of this period, that is to say,
        whether the start and end time and/or date of the other period are after and before, respectively, of the same
        of this period.

        2024-01-01 08:00 Your period: 2024-03-01 08:00
            |==================================|
                    |=============|     <---- The period you are testing
        2024-02-01 08:00   2024-02-15 08:00

        If you have an instance of this period, for example:
        >>> start = datetime(2024, 1, 1, 8, 0)  # 0800, 1st of Jan 2024
        >>> end = datetime(2024, 3, 1, 8, 0)  # 0800, 1st of Mar 2024
        >>> quarter = AbsolutePeriod(start=start, end=end)

        and then another AbsolutePeriod:
        >>> pto_start = datetime(2024, 2, 1, 8, 0)  # 0800, 1st of Feb 2024
        >>> pto_end = datetime(2024, 2, 15, 8, 0)  # 0800, 15th of Feb 2024
        >>> pto = AbsolutePeriod(start=pto_start, end=pto_end)

        Then you can check if the pto period is within your quarter period:
        >>> pto in quarter

        For more in-depth comparisons and functionality, see:
            overlaps_with
            overlapped_by
            get_overlap
            get_disconnect

        Raises:
            TimeAmbiguityError - raised if the duration of this period is longer than a day and either a TimePeriod is
                tested, or an instance of datetime.time that falls within the start and end of this period. Also see:
                <url to doc>
                for more information.
        """
        if isinstance(item, AbsolutePeriod):
            return self.start <= item.start and item.end <= self.end
        if isinstance(item, DatePeriod):
            return self.start.date() <= item.start and item.end <= self.end.date()
        if isinstance(item, TimePeriod):
            if self._time_repeats(item):
                raise TimeAmbiguityError(f"The provided TimePeriod '{item}' exist within this AbsolutePeriod "
                                         f"('{self}') more than once. For more information on this error, "
                                         f"see https://github.com/dimitarOnGithub/temporals/wiki/Misc")
            if self.duration.days == 1:
                if item.start < self.start.time():
                    if item.end <= self.end.time():
                        # Period starts before this once but ends before or at the same time as this once, hence
                        # existing only once
                        return True
                    else:
                        # Period never fully exists within this one as it starts before it and ends after it
                        return False
                if item.start >= self.start.time():
                    if self.end.time() < item.end:
                        # Starts equal or later but ends later too - existing only once
                        return True
            return self.start.time() <= item.start and item.end <= self.end.time()
        if isinstance(item, datetime):
            return self.start <= item <= self.end
        if isinstance(item, date):
            return self.start.date() <= item <= self.end.date()
        if isinstance(item, time):
            if self._time_repeats(item):
                raise TimeAmbiguityError(f"The provided unit of time ('{item}') exist within this AbsolutePeriod "
                                         f"('{self}')  more than once. For more information on this error, "
                                         f"see https://github.com/dimitarOnGithub/temporals/wiki/Misc")
            if self.duration.days == 1:
                return True
            return self.start.time() <= item <= self.end.time()
        return False

    def is_before(self,
                  other: Union['DatePeriod', 'AbsolutePeriod', date, datetime]
                  ) -> bool:
        """ Test if this period ends before the provided `other` value. In the cases when a date or a DatePeriod is
        provided, the check will be done based on at least a 24 hour difference (ie, this period ends on the 2024-01-01
        and the provided date/DatePeriod begins on the 2024-01-02). In all other cases (datetime and AbsolutePeriod),
        objects are allowed to share the same end-start datetime.
        """
        if isinstance(other, DatePeriod):
            return self.end.date() < other.start
        elif isinstance(other, datetime):
            return self.end <= other
        elif isinstance(other, date):
            return self.end.date() < other
        return self.end <= other.start

    def is_after(self,
                 other: Union['DatePeriod', 'AbsolutePeriod', date, datetime]
                 ) -> bool:
        """ Test if this period begins after the provided `other` value. In the cases when a date or a DatePeriod is
        provided, the check will be done based on at least a 24 hour difference (ie, this period begins on the
        2024-01-02 and the provided date/DatePeriod ends on the 2024-01-01). In all other cases (datetime and
        AbsolutePeriod), objects are allowed to share the same end-start datetime.
        """
        if isinstance(other, DatePeriod):
            return other.end < self.start.date()
        elif isinstance(other, datetime):
            return other <= self.start
        elif isinstance(other, date):
            return other < self.start.date()
        return other.end <= self.start

    def get_interim(self,
                    other: Union['AbsolutePeriod', datetime]
                    ) -> Union['AbsolutePeriod', None]:
        """ Method returns the AbsolutePeriod between the start/end of the provided period, if `other` is a
        AbsolutePeriod, or the AbsolutePeriod between the point in time and the start/end of this period, depending on
        whether the same is occurring before the start of this period or after the end of it.

        This method is intended to be used when the provided `other` does not exist within and does not overlap (or is
        being overlapped) by this period.
        """
        _start = None
        _end = None
        if isinstance(other, AbsolutePeriod):
            if self.is_before(other):
                _start = self.end
                _end = other.start
            elif self.is_after(other):
                _start = other.end
                _end = self.start
        elif isinstance(other, datetime):
            if self.is_before(other):
                _start = self.end
                _end = other
            elif self.is_after(other):
                _start = other
                _end = self.start
        if  _start and _end:
            return AbsolutePeriod(start=_start, end=_end)

    def overlaps_with(self,
                      other: Union['TimePeriod', 'DatePeriod', 'AbsolutePeriod']
                      ) -> bool:
        """ Test if this period overlaps with another period that has begun before this one. This check will evaluate
        as True in the following scenario:
                    2024-02-01 0800  This period:   2024-03-01 1700
                            |==================================|
                     |============================|   <------ The other period
            2024-02-01 0600             2024-02-01 1300

        >>> this_start = datetime(2024, 2, 1, 8, 0)  # 0800, 2nd of Feb 2024
        >>> this_end = datetime(2024, 2, 1, 17, 0)  # 1700, 2nd of Feb 2024
        >>> other_start = datetime(2024, 2, 1, 6, 0)  # 0600, 2nd of Feb 2024
        >>> other_end = datetime(2024, 2, 1, 13, 0)  # 1300, 2nd of Feb 2024
        >>> this_period = AbsolutePeriod(start=this_start, end=this_end)
        >>> other_period = AbsolutePeriod(start=other_start, end=other_end)
        >>> this_period.overlaps_with(other_period)
        True

        The period that has begun first is considered the "main" period, even if it finishes before the end of this
        period, since it occupies an earlier point in time. Therefore, the current period, which has begun at a later
        point in time, is considered to be the overlapping one. Hence, the opposite check (overlapped_by) is True for
        the other_period:
        >>> other_period.overlapped_by(this_period)
        True

        Note that both of these checks will only work for partially overlapping periods - for fully overlapping periods,
        use the `in` membership test:
        >>> this_period in other_period
        """
        if isinstance(other, TimePeriod):
            if self._time_repeats(other):
                raise TimeAmbiguityError(f"The provided TimePeriod '{other}' exist within this AbsolutePeriod "
                                         f"('{self}') more than once. For more information on this error, "
                                         f"see https://github.com/dimitarOnGithub/temporals/wiki/Misc")
            if self.start.date() < self.end.date():
                # Day stretches overnight - the start time must be before the start of this period but also after the
                # end of it
                if other.start < self.start.time() and other.start < self.end.time():
                    raise TimeAmbiguityError(f"The provided TimePeriod ('{other}') is ambiguous compared to this "
                                             f"AbsolutePeriod ('{self}'); it's overlapped by (starts before) this "
                                             f"period on {self.start.date().isoformat()} but this period continues "
                                             f"until after it's start on {self.end.date().isoformat()}")
                else:
                    if not other.end < self.start.time():
                        return other.start <= self.start.time()
            else:
                if not other.end < self.start.time():
                    return other.start < self.start.time() and other.end < self.end.time()
        if isinstance(other, DatePeriod):
            if not other.end < self.start.date():
                return other.start < self.start.date() and other.end < self.end.date()
        if isinstance(other, AbsolutePeriod):
            if not other.end < self.start:
                return other.start < self.start and other.end < self.end
        return False

    def overlapped_by(self,
                      other: Union['TimePeriod', 'DatePeriod', 'AbsolutePeriod']
                      ) -> bool:
        """ Test if this period is overlapped by the other period. This check will evaluate True in the following
        scenario:
        2024-01-01 0800   This period:  2024-01-01 1700
                |==================================|
                        |=====================================|   <------ The other period
                2024-01-01 1200                    2024-01-01 2300

        >>> this_start = datetime(2024, 1, 1, 8, 0)  # 0800, 1st of Jan 2024
        >>> this_end = datetime(2024, 1, 1, 17, 0)  # 1700, 1st of Jan 2024
        >>> other_start = datetime(2024, 1, 1, 12, 0)  # 1200, 1st of Jan 2024
        >>> other_end = datetime(2024, 1, 1, 23, 0)  # 2300, 1st of Jan 2024
        >>> this_period = DatePeriod(start=this_start, end=this_end)
        >>> other_period = DatePeriod(start=other_start, end=other_end)
        >>> this_period.overlapped_by(other_period)
        True

        Since this period has begun first, it is considered the "main" one, and all other periods that begin after this
        one, are considered to be overlapping it. Therefore, the opposite check, `overlaps_with`, will evaluate True
        if the opposite check is being made:
        >>> other_period.overlaps_with(this_period)
        True

        Note that both of these checks will only work for partially overlapping periods - for fully overlapping periods,
        use the `in` membership test:
        >>> this_period in other_period
        """
        if isinstance(other, TimePeriod):
            if self._time_repeats(other):
                raise TimeAmbiguityError(f"The provided TimePeriod '{other}' exist within this AbsolutePeriod "
                                         f"('{self}') more than once. For more information on this error, "
                                         f"see https://github.com/dimitarOnGithub/temporals/wiki/Misc")
            if self.start.date() < self.end.date():
                # Day stretches overnight - the start time must be after the start of this period but also after the
                # end of it
                if self.start.time() < other.start and self.end.time() < other.end:
                    raise TimeAmbiguityError(f"The provided TimePeriod ('{other}') is ambiguous compared to this "
                                             f"AbsolutePeriod ('{self}'); it overlaps with (starts after) this "
                                             f"period on {self.start.date().isoformat()} but this period continues "
                                             f"until after it's start on {self.end.date().isoformat()}")
                else:
                    if not self.end.time() < other.start:
                        return self.start.time() <= other.start
            else:
                if not self.end.time() < other.start:
                    return self.start.time() < other.start and self.end.time() < other.end
        if isinstance(other, DatePeriod):
            if not self.end.date() < other.start:
                return self.start.date() < other.start and self.end.date() < other.end
        if isinstance(other, AbsolutePeriod):
            if not self.end < other.start:
                return self.start < other.start and self.end < other.end
        return False

    def get_overlap(self,
                    other: Union['TimePeriod', 'DatePeriod', 'AbsolutePeriod']
                    ) -> Union['TimePeriod', 'DatePeriod', 'AbsolutePeriod', None]:
        """ Method returns the overlapping interval between the two periods as a new period instance. Returned object
        will be an instance of the class that's being tested.

        >>> period1_start = datetime(2024, 1, 1, 8, 0, 0)
        >>> period1_end = datetime(2024, 1, 1, 12, 0, 0)
        >>> period1 = AbsolutePeriod(start=period1_start, end=period1_end)
        >>> period2_start = time(10, 0, 0)
        >>> period2_end = time(13, 0, 0)
        >>> period2 = TimePeriod(start=period2_start, end=period2_end)
        >>> period1
        AbsolutePeriod(start=datetime.datetime(2024, 1, 1, 8, 0), end=datetime.datetime(2024, 1, 1, 12, 0))
        >>> period2
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(13, 0))

        On a timeline, the two periods can be illustrated as:
           0800              Period 1                1200
            |=========================================|
                               |============================|
                              1000       Period 2          1300

        As expected, attempting a membership test would return False:
        >>> period2 in period1
        False
        however, testing overlaps does return True:
        >>> period1.overlapped_by(period2)
        True
        and the opposite:
        >>> period2.overlaps_with(period1)
        True

        Therefore, we can use the `get_overlap` method to obtain the precise length of the overlapping interval:
        >>> period1.get_overlap(period2)
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(12, 0))
        And since the overlap is always the same, regardless of the observer, the opposite action would have the same
        result:
        >>> period2.get_overlap(period1)
        TimePeriod(start=datetime.time(10, 0), end=datetime.time(12, 0))
        """
        if (not isinstance(other, TimePeriod)
                and not isinstance(other, DatePeriod)
                and not isinstance(other, AbsolutePeriod)):
            raise TypeError(f"Cannot perform temporal operations with instances of type '{type(other)}'")
        period_to_use = None
        _start = None
        _end = None
        if self.overlaps_with(other) or self.overlapped_by(other):
            if isinstance(other, TimePeriod):
                period_to_use = TimePeriod
                _start = self.start.time() if self.overlaps_with(other) else other.start
                _end = other.end if self.overlaps_with(other) else self.end.time()
            elif isinstance(other, DatePeriod):
                period_to_use = DatePeriod
                _start = self.start.date() if self.overlaps_with(other) else other.start
                _end = other.end if self.overlaps_with(other) else self.end.date()
            else:
                period_to_use = AbsolutePeriod
                _start = self.start if self.overlaps_with(other) else other.start
                _end = other.end if self.overlaps_with(other) else self.end
            return period_to_use(start=_start, end=_end)
        else:
            return None

    def get_disconnect(self,
                       other: Union['TimePeriod', 'DatePeriod', 'AbsolutePeriod']
                       ) -> Union['TimePeriod', 'DatePeriod', 'AbsolutePeriod', None]:
        """ Method returns the disconnect interval from the point of view of the invoking period. This means the time
        disconnect from the start of this period until the start of the period to which this period is being compared
        to. Since the span of time is relative to each of the two periods, this method will always return different
        intervals.

        Take, for example, the following two periods:
        >>> period1_start = datetime(2024, 1, 1, 8, 0, 0)
        >>> period1_end = datetime(2024, 1, 1, 12, 0, 0)
        >>> period1 = AbsolutePeriod(start=period1_start, end=period1_end)
        >>> period2_start = datetime(2024, 1, 1, 10, 0, 0)
        >>> period2_end = datetime(2024, 1, 1, 13, 0, 0)
        >>> period2 = AbsolutePeriod(start=period2_start, end=period2_end)
        >>> period1
        AbsolutePeriod(start=datetime.datetime(2024, 1, 1, 8, 0), end=datetime.datetime(2024, 1, 1, 12, 0))
        >>> period2
        AbsolutePeriod(start=datetime.datetime(2024, 1, 1, 10, 0), end=datetime.datetime(2024, 1, 1, 13, 0))

        On a timeline, the two periods can be illustrated as:
           0800              Period 1                1200
            |=========================================|
                               |============================|
                              1000       Period 2          1300

        From the point of view of Period 1, the disconnect between the two periods is between the time 0800 and 1000;
        however, from the point of view of Period 2, the disconnect between them is between the time 1200 and 1300.

        Therefore, if you want to obtain the amount of time when the periods do NOT overlap as relative to Period 1,
        you should use:
        >>> period1.get_disconnect(period2)
        AbsolutePeriod(start=datetime.datetime(2024, 1, 1, 8, 0), end=datetime.datetime(2024, 1, 1, 10, 0))

        But if you want to obtain the same as relative to Period 2 instead:
        >>> period2.get_disconnect(period1)
        AbsolutePeriod(start=datetime.datetime(2024, 1, 1, 12, 0), end=datetime.datetime(2024, 1, 1, 13, 0))
        """
        if (not isinstance(other, TimePeriod)
                and not isinstance(other, DatePeriod)
                and not isinstance(other, AbsolutePeriod)):
            raise TypeError(f"Cannot perform temporal operations with instances of type '{type(other)}'")
        period_to_use = None
        _start = None
        _end = None
        if isinstance(other, TimePeriod):
            period_to_use = TimePeriod
            if self.overlapped_by(other):
                _start = self.start.time()
                _end = other.start
            elif self.overlaps_with(other):
                _start = other.end
                _end = self.end.time()
        elif isinstance(other, DatePeriod):
            period_to_use = DatePeriod
            if self.overlapped_by(other):
                _start = self.start.date()
                _end = other.start
            elif self.overlaps_with(other):
                _start = other.end
                _end = self.end.date()
        else:
            period_to_use = AbsolutePeriod
            if self.overlapped_by(other):
                _start = self.start
                _end = other.start
            elif self.overlaps_with(other):
                _start = other.end
                _end = self.end
        if period_to_use and _start and _end:
            return period_to_use(start=_start, end=_end)
        return None
