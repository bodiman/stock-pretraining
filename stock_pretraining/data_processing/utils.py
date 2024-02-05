from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from ..models import resample_options

"""
Increments datetime by 1 unit

Parameters
----------

datestr: str
    A string that can be parsed as a datetime in the form YYYY-MM-DD H:M:S

unit: resample_options.member
    The unit

Returns
-------

new_datestr: str
    Incremented string

"""

def increment(datestr, unit, decrement = False):
    parsed = parse(datestr)

    kwargs = {}

    for key, value in resample_options.items():
        kwargs[key] = (unit == value) * (-1 if decrement else 1)

    parsed = parsed + relativedelta(**kwargs)

    if parsed.hour == 0 and parsed.minute == 0:
        return str(parsed.date())

    return f"{str(parsed.date())} {str(parsed.time())}"

"""
Updates the sparsity mapping string of a stock domain by adding a new time interval

Parameters
----------

sparsity_mapping: str
    The sparsity mapping string representing the current domain

start: string 'YYYY-MM-DD'
    The start date of the new domain entry

stop: string 'YYYY-MM-DD'
    The stop date of the new domain entry

resample_freq: string
    The resample frequency of the input intervals

Returns
-------

updated_sparsity_mapping: string
    The updated sparsity mapping string


"""
def update_domain(sparsity_mapping, start, stop, resample_freq=resample_options["days"]):
    sparsity_mapping_array = sparsity_mapping[1:].split("/")
    sparsity_mapping_array = [i for i in sparsity_mapping_array if i != ""]
    new_sparsity_mapping_array = []

    for interval in [interval_string.split("|") for interval_string in sparsity_mapping_array]:
        if intervals_intersect(interval, [start, stop], resample_freq):
            start = min(start, interval[0])
            stop = max(stop, interval[1])

            continue
        
        new_sparsity_mapping_array.append(interval)
    
    new_sparsity_mapping_array.append([start, stop])
    new_sparsity_mapping_array = sorted(new_sparsity_mapping_array, key=lambda x: x[0])

    return "".join([f'/{interval[0]}|{interval[1]}' for interval in new_sparsity_mapping_array])

    """
    1. Collect ordered list of partial domains.
    2. Loop through current pairs and check if start and stop intersect the partial domain
        3. To check intersection, sort them by start, then see if end1 > start2 or end2 > start1
        4. If there is an intersection, absorb the domain into the start and stop and remove it from the list

    5. Sort the list by starting date and combine into sparsity mapping string
    6. Loop through final result. If the difference between and end and a start is less than a time unit, combine the two
    """


"""
Calculates the relative complement of two sparsity mapping strings

Parameters
----------

sparsity_mapping_1: string
    Base sparsity mapping string

sparsity_mapping_2: string
    Sparsity mapping string to be subtracted

resample_freq: string
    The resample frequency of the input intervals

return_closed: boolean
    Weather to automatically convert the subtracted intervals into closed intervals

Returns
-------

difference: string
    Sparsity mapping string representing the difference between the two domains

"""
def subtract_domain(sparsity_mapping_1, sparsity_mapping_2, resample_freq=None, return_closed=True):
    if return_closed:
        assert resample_freq is not None, "resample_freq must be provided if return closed is set to True"

    sparsity_mapping_1 = sparsity_mapping_1[1:]

    sparsity_mapping_2 = sparsity_mapping_2[1:].split("/")
    sparsity_mapping_2 = [i for i in sparsity_mapping_2 if i != ""]

    for subtract_interval in sparsity_mapping_2:
        sparsity_mapping_1 = subtract_continuous_interval_from_domain(sparsity_mapping_1, subtract_interval, resample_freq, return_closed)
    
    return "/" + sparsity_mapping_1

    """
    1. Loop through continuous intervals in sparsity mapping 2
        2. Subtract from sparsity mapping 1
    3. Return sparsity mapping 1
    """


"""
A helper function for subtract_domain.
Takes the difference between a domain and a continuous interval

Parameters
----------

domain: string 
    A sparsity mapping string

subtraction_interval: string
    An interval string of the form YYYY-MM-DD|YYYY-MM-DD

resample_freq: string
    The resample frequency of the input intervals

return_closed: boolean
    Weather to automatically convert the subtracted intervals into closed intervals

Returns
-------
difference: string
    Sparsity mapping string representing the difference between the domain and subtraction_interval

"""
def subtract_continuous_interval_from_domain(domain, subtraction_interval, resample_freq, return_closed):
    domain = domain.split("/")
    domain = [i for i in domain if i != ""]

    all_intervals = []

    for continuous_interval in domain:
        difference = subtract_continuous_intervals(continuous_interval, subtraction_interval, resample_freq, return_closed)
        all_intervals.append(difference)

    all_intervals = [i for i in all_intervals if i != ""]
    return "/".join(all_intervals)

    """
    1. Loop through domain
    2. Get continous interval difference
    3. append to list
    4. combine everything back into string
    """



"""
A helper function of subtract_continuous_interval_from_domain. 
Applies to single continuous intervals rather than complete, possibly sparse domains.


Parameters
----------

interval1: string
    Base continuous interval in sparsity mapping string notation

interval2: string
    Continuous interval to be subtracted in sparsity mapping string notation

resample_freq: string
    The resample frequency of the input intervals

return_closed: boolean
    Weather to automatically convert the subtracted intervals into closed intervals
    
Returns
-------

updated_interval: string
    A new interval in sparsity mapping string format


Notes
-----
The resample frequency is included to prevent the creation of open intervals.
Subtracting a closed interval from a closed interval results in an open interval.
However, since the datapoints are discrete, we can easily convert between open and closed
intervals by adding / subtracting one resample_freq.

Also, it should be noted that subtract_continuous intervals may return an interval


"""
def subtract_continuous_intervals(interval1, interval2, resample_freq, return_closed):
    interval1 = interval1.split("|")
    interval2 = interval2.split("|")

    if not intervals_intersect(interval1, interval2, resample_freq):
        return  f"{interval1[0]}|{interval1[1]}"
    
    if interval2[0] <= interval1[0] and interval1[1] <= interval2[1]:
        return ""

    #1 is proper subset
    if interval1[0] < interval2[0] and interval2[1] < interval1[1]:
        if return_closed:
            return f"{interval1[0]}|{increment(interval2[0], resample_freq, decrement=True)}/{increment(interval2[1], resample_freq)}|{interval1[1]}"
        return f"{interval1[0]}|{interval2[0]}/{interval2[1]}|{interval1[1]}"
    
    #one starts in front of the other
    if interval1[0] >= interval2[0]:
        if return_closed:
            return f"{increment(interval2[1], resample_freq, decrement=True)}|{interval1[1]}"
        return f"{interval2[1]}|{interval1[1]}"
    
    if return_closed:
        return f"{interval1[0]}|{increment(interval2[0], resample_freq)}"
    return f"{interval1[0]}|{interval2[0]}"

    """
    Here are the cases:

    1. interval 1 and interval 2 do not intersect:
        return interval 1

    2. Interval 1 is a subset of interval 2
        Return ""

    3. Interval 2 is a proper subset of interval 1
        Produce two new intervals, (interval1[0], interval2[0]) and (interval2[1], interval1[1])

    4. Interval 1 and interval 2 overlap, but neither properly contains the other:
        Check which end of interval 1 lies within interval 2 and update that end
    """



"""
Determines weather two continuous intervals intersect

Parameters
----------

interval1: tuple(string, string)
    A continuous interval in YYYY-MM-DD format

interval2: tuple(string, string)
    A continuous interval in YYYY-MM-DD format

unit: resample_options.member
    The minimum descrete unit for intervals

Returns
-------

intersects: bool
    Weather the intervals intersect
"""
def intervals_intersect(interval1, interval2, unit):
    s1, e1 = interval1
    s2, e2 = interval2

    return not (e1 < increment(s2, unit=unit, decrement=True) or increment(s1, unit=unit, decrement=True) > e2)


"""
s1 s2 e1 e1 e2
"""