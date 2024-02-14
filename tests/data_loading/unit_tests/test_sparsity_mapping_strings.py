import pytest
from stock_pretraining import SparsityMappingString


resample_map = {
    "days": "daily",
    "months": "monthly",
    "years": "annually"
}

def test_sms():
    x = SparsityMappingString("/")
    print(x)


# @pytest.mark.parametrize("sparsity_mapping, start, stop, datestrformat, resample_freq, expected", [
#     ("/", "2020-01-01", "2021-01-01", "%Y-%m-%d", "days", "/2020-01-01|2021-01-01"),
#     ("/2020-01-01|2021-01-01", "2020-01-01", "2021-01-01", "%Y-%m-%d", "days", "/2020-01-01|2021-01-01"),
#     ("/2020-01-01|2021-01-01", "2020-01-01", "2021-01-02", "%Y-%m-%d", "days", "/2020-01-01|2021-01-02"),
#     ("/2020-01-01|2021-01-01", "2019-12-31", "2021-01-01", "%Y-%m-%d", "days", "/2019-12-31|2021-01-01"),
#     ("/2020-01-01|2021-01-01", "2019-12-31", "2021-01-02", "%Y-%m-%d", "days", "/2019-12-31|2021-01-02"),
#     ("/2020-01-01|2021-01-01", "2021-01-01", "2021-01-02", "%Y-%m-%d", "days", "/2020-01-01|2021-01-02"),
#     ("/2020-01-01|2021-01-01", "2021-01-02", "2021-01-02", "%Y-%m-%d", "days", "/2020-01-01|2021-01-02"),
#     ("/2020-01-01|2021-01-01", "2021-01-03", "2021-01-03", "%Y-%m-%d", "days", "/2020-01-01|2021-01-01/2021-01-03|2021-01-03"),
#     ("/2020-01-01|2021-01-01/2021-01-03|2021-01-03", "2021-01-02", "2021-01-02", "%Y-%m-%d", "days", "/2020-01-01|2021-01-03"),
#     ("/", "2020-01-01", "2021-01-01", "%Y-%m-%d", "months", "/2020-01-01|2021-01-01"),
# ])
# def test_update_domain(sparsity_mapping, start, stop, datestrformat, resample_freq, expected):
#     assert update_domain(sparsity_mapping=sparsity_mapping, start=start, stop=stop, datestrformat=datestrformat, resample_freq=resample_freq) == expected


# @pytest.mark.parametrize("sparsity_mapping, start, stop, datestrformat, resample_freq", [
#     ("/", "", "", "YYYY-MM-DD", "day"),
# ])
# def test_update_domain_invalid(sparsity_mapping, start, stop, datestrformat, resample_freq):
#     with pytest.raises(ValueError, match="time data"):
#         update_domain(sparsity_mapping=sparsity_mapping, start=start, stop=stop, datestrformat=datestrformat, resample_freq=resample_freq)

# @pytest.mark.parametrize("sparsity_mapping, start, stop, datestrformat, resample_freq", [
#     ("/", "", "", "YYYY-MM-DD", "day"),
# ])
# def test_update_domain_invalid(sparsity_mapping, start, stop, datestrformat, resample_freq):
#     with pytest.raises(AssertionError, match=f"invalid resample_freq"):
#         update_domain(sparsity_mapping=sparsity_mapping, start=start, stop=stop, datestrformat=datestrformat, resample_freq=resample_freq)