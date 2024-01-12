from utils import update_domain

currentDomain = "/2023-01-01|2023-01-20/2023-02-01|2023-03-20/2023-03-24|2024-01-01"

# start_date = "2023-01-20"
# end_date = "2023-03-26"

# print(update_domain(currentDomain, start_date, end_date))

from dateutil.parser import parse

def validate_sparsity_mapping(mapstr):
        try:
            running_date = None

            assert mapstr[0] == '/'
            mapstr = mapstr[1:]
            continuous_intervals = mapstr.split('/')

            for continuous_interval_string in continuous_intervals:
                continuous_interval = continuous_interval_string.split("|")
                assert len(continuous_interval) == 2

                start_date = parse(continuous_interval[0])
                stop_date = parse(continuous_interval[1])

                assert running_date == None or start_date > running_date
                assert stop_date > start_date
                
                running_date = stop_date


        except Exception:
            raise ValueError(f"Improperly formatted sparsity mapping string /{mapstr}")

        """
        1. Remove first character
        2. Track a running date
        3. split strings into stretches by `/`
            4. for each domain stretch, split it into 2 by '|'
                5. check that there are exactly 2 elements in the list
                6. check that the value is greater than the running date, then update the running date `/`
        """

        return "/" + mapstr

print(validate_sparsity_mapping(currentDomain))