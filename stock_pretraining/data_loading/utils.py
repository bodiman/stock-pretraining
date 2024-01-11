"""
Updates the sparsity mapping string of a stock domain based on a new 

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

    Intersection

    No Intersection

    s1e1 s2e2
    s2e2 s1e1

    """


"""
Note
----

This function operates on strings
"""
def intervals_intersect(interval1, interval2):
    s1, e1 = interval1
    s2, e2 = interval2

    return not (e1 < s2 or s1 > e2)

