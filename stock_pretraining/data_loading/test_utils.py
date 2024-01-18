from utils import update_domain, subtract_continuous_intervals, subtract_domain

currentDomain = "/2023-01-01|2023-01-20/2023-02-01|2023-03-20/2023-03-24|2024-01-01"
subtraction_domain = "/2023-02-01|2023-03-25"

start_date = "2023-01-20"
end_date = "2023-03-26"

print(update_domain("/", start_date, end_date))

# interval1 = "2022-01-04|2023-01-04"
# interval2 = "2022-04-04|2022-05-04"

# print(subtract_continuous_intervals(interval1, interval1))

# print(subtract_domain(currentDomain, subtraction_domain))