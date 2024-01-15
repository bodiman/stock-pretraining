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

Returns
-------

updated_sparsity_mapping: string
    The updated sparsity mapping string

new_domains: string ??? Note: May be better to do this in a separate function unless there is a way to do both efficiently
    A sparsity mapping string representing the difference between The updated string and the input string

"""
def update_domain(sparsity_mapping, start, stop):
    sparsity_mapping_array = sparsity_mapping[1:].split("/")
    new_sparsity_mapping_array = []
    

    for interval in [interval_string.split("|") for interval_string in sparsity_mapping_array]:
        if intervals_intersect(interval, [start, stop]):
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
    """


"""
Determines weather two continuous intervals intersect


Parameters
----------

interval1: string
    A continuous interval in sparsity mapping string notation

interval2: string
    A continuous interval in sparsity mapping string notation

Returns
-------

intersects: bool
    Weather the intervals intersect

Note
----

This function operates on strings
"""
def intervals_intersect(interval1, interval2):
    s1, e1 = interval1
    s2, e2 = interval2

    return not (e1 < s2 or s1 > e2)


"""
Calculates the relative complement of two sparsity mapping strings

Parameters
----------

sparsity_mapping_1: string
    Base sparsity mapping string

sparsity_mapping_2: string
    Sparsity mapping string to be subtracted

Returns
-------
"""
def subtract_domain(sparsity_mapping_1, sparisty_mapping_2):
    """
    1. Loop through the continuous intervals in sparsity mapping 1
        2. Loop through the continuous intervals in sparsity mapping 2
            3. subtract each continuous domain 2 from continuous domain 1, append continuous domain 1 to a list
    
    4. combine list of new, not necessarily continuous domains into a sparsity mapping string
    """


"""
A helper function of subtract_domain. 
Applies to single continuous intervals rather than complete, possibly sparse domains.


Parameters
----------

interval1: string
    Base continuous interval in sparsity mapping string notation

interval2: string
    Continuous interval to be subtracted in sparsity mapping string notation

    
Returns
-------



"""
def subtract_continuous_intervals(interval1, interval2):
    ...
    """
    Here are the cases:

    1. interval 1 and interval 2 do not intersect:
        return interval 1

    2. Interval 1 and interval 2 overlap, but interval 2 is not a proper subset of interval 1:
        Check which end of interval 1 lies within interval 2 and update that end

    3. Interval 2 is a proper subset of interval 1
        Produce two new intervals, (interval1[0], interval2[0]) and (interval2[1], interval1[1])
    """



