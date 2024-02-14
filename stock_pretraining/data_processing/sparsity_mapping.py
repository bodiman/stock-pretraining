from stock_pretraining.data_processing.utils import increment, intervals_intersect
from datetime import datetime, timedelta

class SparsityMappingString():
    def __init__(self, resample_freq, string=None, date_to_str=None, str_to_date=None):
        if string is None:
            string = "/"

        if date_to_str is None:
            date_to_str = lambda date: date.strftime("%Y-%m-%d")

        if str_to_date is None:
            str_to_date = lambda string: datetime.strptime(string, "%Y-%m-%d")

        now = datetime.now()
        assert date_to_str(str_to_date(date_to_str(now))) == date_to_str(now), "str_to_date and date_to_str must provide valid back and forth conversions between date and string formats"
        assert not ("/" in date_to_str(now)), "string representation of datetime must not contain forward slash character '/'."
        assert not ("|" in date_to_str(now)), "string representation of datetime must not contain pipe character '|'."

        self.validate(string)
        self.string = string

        self.resample_freq = resample_freq

    @property
    def is_null(self):
        return self.string != "/"

    def get_str_intervals(self):
        string_intervals = self.string.split("/")
        string_intervals = [i.split("|") for i in string_intervals if i != ""]

        return string_intervals
    
    
    def get_intervals(self):
        string_intervals = self.get_str_intervals()

        date_intervals = []
        for string_interval in string_intervals:
            start, end = string_interval.split("|")
            date_intervals.append([self.str_to_date(start), self.str_to_date(end)])

        return date_intervals


    def validate(self, mapstr):
        try:
            running_date = None

            assert mapstr[0] == '/'
            mapstr = mapstr[1:]
            continuous_intervals = mapstr.split('/')
            continuous_intervals = [i for i in continuous_intervals if i != ""]

            for continuous_interval_string in continuous_intervals:
                continuous_interval = continuous_interval_string.split("|")
                assert len(continuous_interval) == 2

                start_date = self.str_to_date(continuous_interval[0])
                stop_date = self.str_to_date(continuous_interval[1])

                assert running_date == None or start_date > running_date
                assert stop_date >= start_date
                
                running_date = stop_date


        except Exception:
            raise ValueError(f"Improperly formatted sparsity mapping string /{mapstr}")

        return "/" + mapstr

    def __add__(self, other):
        return self.add_domain(self, other.string)
    
    def __sub__(self, other):
        return self.subtract_domain(self, other.string)

    def add_domain(self, sparsity_mapping_2):
        sparsity_mapping_1 = self.string[1:]

        sparsity_mapping_2 = sparsity_mapping_2[1:].split("/")
        sparsity_mapping_2 = [i for i in sparsity_mapping_2 if i != ""]

        for subtract_interval in sparsity_mapping_2:
            sparsity_mapping_1 = self.add_continuos_interval_to_domain(sparsity_mapping_1, subtract_interval)
        
        self.string = "/" + sparsity_mapping_1

        return self


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
    def add_continuos_interval_to_domain(self, domain, continuous_interval):
        start, stop = continuous_interval

        sparsity_mapping_array = domain[1:].split("/")
        sparsity_mapping_array = [i for i in sparsity_mapping_array if i != ""]
        sparsity_mapping_array = [[self.str_to_date(i) for i in interval_string.split("|")] for interval_string in sparsity_mapping_array]

        new_sparsity_mapping_array = []
        for interval in sparsity_mapping_array:
            if intervals_intersect(interval, [start, stop], unit=self.resample_freq):
                start = min(start, interval[0])
                stop = max(stop, interval[1])

                continue
            
            new_sparsity_mapping_array.append(interval)

        new_sparsity_mapping_array.append([start, stop])
        new_sparsity_mapping_array = sorted(new_sparsity_mapping_array, key=lambda x: x[0])

        return "".join([f'/{self.date_to_str(interval[0])}|{self.date_to_str(interval[1])}' for interval in new_sparsity_mapping_array])

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
    def subtract_domain(self, sparsity_mapping_2, resample_freq=None):
        sparsity_mapping_1 = self.string[1:]

        sparsity_mapping_2 = sparsity_mapping_2[1:].split("/")
        sparsity_mapping_2 = [i for i in sparsity_mapping_2 if i != ""]

        for subtract_interval in sparsity_mapping_2:
            sparsity_mapping_1 = self.subtract_continuous_interval_from_domain(sparsity_mapping_1, subtract_interval)
        
        self.string = "/" + sparsity_mapping_1

        return self

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
    def subtract_continuous_interval_from_domain(self, domain, subtraction_interval):
        domain = domain.split("/")
        domain = [i for i in domain if i != ""]

        subtraction_interval = subtraction_interval.split("|")
        subtraction_interval = [self.str_to_date(subtraction_interval[0]), self.str_to_date(subtraction_interval[1])]

        all_intervals = []

        for continuous_interval_str in domain:
            continuous_interval = continuous_interval_str.split("|")
            continuous_interval = [self.str_to_date(continuous_interval[0]), self.str_to_date(continuous_interval[1])]

            difference = self.subtract_continuous_intervals(continuous_interval, subtraction_interval)
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
    def subtract_continuous_intervals(self, interval1, interval2):
        if not intervals_intersect(interval1, interval2, self.resample_freq):
            interval1[0] = self.date_to_str(interval1[0])
            interval1[1] = self.date_to_str(interval1[1])

            return  f"{interval1[0]}|{interval1[1]}"
        
        if interval2[0] <= interval1[0] and interval1[1] <= interval2[1]:
            return ""

        #1 is proper subset
        if interval1[0] < interval2[0] and interval2[1] < interval1[1]:
            interval1[0] = self.date_to_str(interval1[0])
            interval1[1] = self.date_to_str(interval1[1])
            return f"{interval1[0]}|{increment(interval2[0], self.resample_freq, decrement=True)}/{increment(interval2[1], self.resample_freq)}|{interval1[1]}"
        
        #one starts in front of the other
        if interval1[0] >= interval2[0]:
            interval1[0] = self.date_to_str(interval1[0])
            interval1[1] = self.date_to_str(interval1[1])
            return f"{increment(interval2[1], self.resample_freq, decrement=True)}|{interval1[1]}"
        
        interval1[0] = self.date_to_str(interval1[0])
        interval1[1] = self.date_to_str(interval1[1])
        return f"{interval1[0]}|{increment(interval2[0], self.resample_freq)}"

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