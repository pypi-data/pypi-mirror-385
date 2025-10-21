import numbers
import re

import fakeitmakeit as fm


def test_version():
    # Check that the version is a string.
    assert isinstance(fm.__version__, str)
    assert re.fullmatch(r"20[0-9]{2}\.[0-9]{1,2}\.[0-9]{1,2}", fm.__version__)


class TestGENDERS:
    def test_type(self):
        # Check that GENDERS is a dictionary.
        assert isinstance(fm.util.GENDERS, dict)

    def test_length(self):
        # Check there are 3 genders.
        assert len(fm.util.GENDERS) == 3

    def test_keys(self):
        # Check that the keys are genders.
        assert "male" in fm.util.GENDERS

    def test_values(self):
        # Check that the values are all numbers.
        assert all(
            isinstance(value, numbers.Real) for value in fm.util.GENDERS.values()
        )


class TestTITLES:
    def test_type(self):
        # Check that TITLES is a set.
        assert isinstance(fm.util.TITLES, list)

    def test_length(self):
        # Check that TITLES has 5 titles.
        assert len(fm.util.TITLES) == 5

    def test_elements(self):
        # Check correct elements are in the set.
        assert "Mr" in fm.util.TITLES

    def test_values(self):
        # Check that the values are all strings.
        assert all(isinstance(value, str) for value in fm.util.TITLES)


class TestCOURSES:
    def test_type(self):
        # Check that COURSES is a dictionary.
        assert isinstance(fm.util.COURSES, dict)

    def test_length(self):
        # Check that COURSES has 3 courses.
        assert len(fm.util.COURSES) == 3

    def test_keys(self):
        # Check that the keys are course names.
        assert {"acse", "edsml", "gems"} <= set(fm.util.COURSES.keys())

    def test_values(self):
        # Check that the values are all numbers.
        assert all(
            isinstance(value, numbers.Real) for value in fm.util.COURSES.values()
        )


class TestCOUNTRIES:
    def test_type(self):
        # Check that COUNTRIES is a dictionary.
        assert isinstance(fm.util.COUNTRIES, dict)

    def test_length(self):
        # Check that COUNTRIES has sufficient items.
        assert len(fm.util.COUNTRIES) >= 245

    def test_keys(self):
        # Check that the keys are country names.
        assert {"Serbia", "Malta"} < set(fm.util.COUNTRIES.keys())

    def test_values(self):
        # Check that the values are all 1 (relative probabilities).
        assert all(
            isinstance(value, numbers.Real) for value in fm.util.COUNTRIES.values()
        )


class TestCOUNTRYLOCALE:
    def test_type(self):
        # Check that COUNTRY_LOCALE is a dictionary.
        assert isinstance(fm.util.COUNTRY_LOCALE, dict)

    def test_length(self):
        # Check that COUNTRY_LOCALE has sufficient items.
        assert len(fm.util.COUNTRY_LOCALE) >= 10

    def test_keys(self):
        # Check that the keys are country names.
        assert {"Argentina", "United States"} < set(fm.util.COUNTRY_LOCALE.keys())

    def test_values(self):
        # Check that the values contain an underscore.
        assert all("_" in value for value in fm.util.COUNTRY_LOCALE.values())

    def test_entries(self):
        # Check that the entries are valid locales.
        assert fm.util.COUNTRY_LOCALE["China"] == "zh_CN"
        assert fm.util.COUNTRY_LOCALE["United Kingdom"] == "en_GB"


class TestDiscreteDraw:
    def test_output(self):
        # Check that the output is one of the expected ones.
        assert fm.util.discrete_draw({"a": 0.5, "b": 0.5}) in {"a", "b"}

    def test_certain(self):
        # Check that the output is always the same if probability is 1.
        assert fm.util.discrete_draw({"a": 0, "b": 1}) == "b"
