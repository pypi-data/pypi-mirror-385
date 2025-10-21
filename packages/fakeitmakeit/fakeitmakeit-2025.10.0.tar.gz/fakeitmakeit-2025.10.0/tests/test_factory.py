import collections
import re

import numpy as np
import pandas as pd
import pytest

import fakeitmakeit as fm

UINT_RE = re.compile(r"^[0-9]+$")  # unsigned integer regex


@pytest.fixture(scope="module")
def cohort():
    return fm.cohort(n=100)


@pytest.fixture(scope="module")
def assignment(cohort):
    return fm.assignment(usernames=cohort.index, mean=65, std=10, pfail=0.1, pnan=0.1)


class TestCID:
    def test_type(self):
        # Check that the CID is a string.
        assert isinstance(fm.cid(), str)

    def test_length(self):
        # Check that the CID is 8 digits long.
        assert len(fm.cid()) == 8

    def test_all_digits(self):
        # Check that the CID is all digits.
        assert UINT_RE.search(fm.cid())

    def test_first_digit(self):
        # Check that the first digit is always 0.
        assert int(fm.cid()[0]) == 0

    def test_second_digit(self):
        # Check that the second digit is always 1 or 2.
        assert int(fm.cid()[1]) in [1, 2]

    def test_remaining_digits(self):
        # Check that the remaining 6 digits are always between 0 and 9.
        assert UINT_RE.search(fm.cid()[2:])

    def test_all_digits_present(self):
        # Check that all digits (0-9) can be present in the CID.
        assert len(set("".join(fm.cid() for _ in range(50)))) == 10

    def test_convertible(self):
        # Check that the CID is convertible to an integer.
        assert isinstance(int(fm.cid()), int)

    def test_isvalid(self):
        # Check that the CID is valid.
        assert fm.isvalid.cid(fm.cid())


class TestGender:
    def test_type(self):
        # Check that gender is a string.
        assert isinstance(fm.gender(), str)

    def test_values(self):
        # Check the output is one of the expected ones.
        assert fm.gender() in fm.util.GENDERS

    def test_probability_certain_outcome(self):
        # Check that the probabilities are respected.
        assert fm.gender(distribution={"outcome1": 1, "outcome2": 0}) == "outcome1"

    def test_probabilities_uncertain_outcome(self):
        # Check that the probabilities are respected.
        distribution = {"male": 0.2, "female": 0.75, "nonbinary": 0.05}
        counts = collections.Counter(
            fm.gender(distribution=distribution) for _ in range(1000)
        )
        assert counts["nonbinary"] < counts["male"] < counts["female"]

    def test_isvalid(self):
        # Check that gender is valid.
        assert fm.isvalid.gender(fm.gender())


class TestTitle:
    def test_type(self):
        # Check that title is a string.
        assert isinstance(fm.title(), str)

    def test_startswith_upper(self):
        # Check that the title starts with an uppercase M.
        assert fm.title().startswith("M")

    def test_no_gender(self):
        # Check that the title is one of the expected ones.
        assert fm.title() in fm.util.TITLES

    def test_male(self):
        # Check that the title is one of the expected ones for a male.
        assert fm.title(genderval="male") == "Mr"

    def test_female(self):
        # Check that the title is one of the expected ones for a female.
        assert fm.title(genderval="female") in {"Ms", "Mrs", "Miss"}

    def test_nonbinary(self):
        # Check that the title is one of the expected ones for a nonbinary.
        assert fm.title(genderval="nonbinary") == "Mx"

    def test_wrong_gender(self):
        # Check the exception is raised.
        with pytest.raises(ValueError):
            fm.title(genderval="wrong_gender")

    def test_isvalid(self):
        # Check that title is valid.
        assert fm.isvalid.title(fm.title())


class TestCourse:
    def test_type(self):
        # Check that course is a string.
        assert isinstance(fm.course(), str)

    def test_values(self):
        # Check the output is one of the expected ones.
        assert fm.course() in fm.util.COURSES

    def test_probability_certain_outcome(self):
        # Check that the probabilities are respected.
        assert fm.course(distribution={"course1": 1, "course2": 0}) == "course1"

    def test_probabilities_uncertain_outcome(self):
        # Check that the probabilities are respected.
        distribution = {"c1": 0.2, "c2": 0.75, "c3": 0.05}
        counts = collections.Counter(
            fm.course(distribution=distribution) for _ in range(1000)
        )
        assert counts["c3"] < counts["c1"] < counts["c2"]

    def test_isvalid(self):
        # Check that course is valid.
        assert fm.isvalid.course(fm.course())


class TestCountry:
    def test_type(self):
        # Check that country is a string.
        assert isinstance(fm.country(), str)

    def test_defaults(self):
        # Check that the country is one of the expected ones.
        assert fm.country() in fm.util.COUNTRIES

    def test_probability_certain_outcome(self):
        # Check that the probabilities are respected.
        assert fm.country(distribution={"country1": 1, "country2": 0}) == "country1"

    def test_probabilities_uncertain_outcome(self):
        # Check that the probabilities are respected.
        distribution = {"c1": 0.2, "c2": 0.75, "c3": 0.05}
        counts = collections.Counter(
            fm.country(distribution=distribution) for _ in range(1000)
        )
        assert counts["c3"] < counts["c1"] < counts["c2"]

    def test_bias(self):
        # Check that the bias is respected.
        bias = {"China": 1000, "United Kingdom": 100}
        counts = collections.Counter(fm.country(bias=bias) for _ in range(100))
        assert counts["China"] > counts["United Kingdom"] > counts["Syria"]

    def test_isvalid(self):
        # Check that country is valid.
        assert fm.isvalid.country(fm.country())


class TestUsername:
    def test_type(self):
        # Check that username is a string.
        assert isinstance(fm.username(), str)

    def test_length(self):
        # Check that the username is between 4 and 7 characters long.
        assert 4 <= len(fm.username()) <= 7

    def test_lower(self):
        # Check that the username is lowercase.
        assert fm.username().islower()

    def test_no_space(self):
        # Check that the username does not contain spaces.
        assert " " not in fm.username()

    def test_first_letter(self):
        # Check that the first letter is the first letter of the first name.
        assert fm.username(nameval="John Smith").startswith("j")

    def test_last_letter(self):
        # Check that the last letter is the first letter of the last name.
        letters = [i for i in fm.username(nameval="John Doe") if i.isalpha()]
        assert letters[-1] == "d"

    def test_num_digits(self):
        # Check that the username contains 2 to 4 digits.
        assert 2 <= sum(i.isdigit() for i in fm.username()) <= 4

    def test_num_letters(self):
        # Check that the username contains 2 or 3 letters.
        assert 2 <= sum(i.isalpha() for i in fm.username()) <= 3

    def test_isvalid(self):
        # Check that username is valid.
        assert fm.isvalid.username(fm.username())


class TestEmail:
    def test_type(self):
        # Check that email is a string.
        assert isinstance(fm.email(), str)

    def test_at(self):
        # Check that the email contains an @.
        assert "@" in fm.email()

    def test_dot(self):
        # Check that the email contains a dot.
        assert "." in fm.email()

    def test_domain(self):
        # Check that the email contains domainval if specified.
        assert fm.email(domainval="gmail.com").endswith("@gmail.com")

    def test_valid(self):
        # Check that the email is valid.
        assert fm.isvalid.email(fm.email())


class TestName:
    def test_type(self):
        # Check that name is a string.
        assert isinstance(fm.name(), str)

    def test_space(self):
        # Check that the name contains a space.
        assert " " in fm.name()

    def test_china(self):
        # Check that Chinese names are generated as expected.
        for i in range(300):
            first_name, *_ = fm.name(countryval="China").split()
            if first_name in {
                "Jang",
                "Jing",
                "Wei",
                "Fang",
                "Lei",
                "Tao",
                "Qiang",
                "Ming",
                "Chao",
                "Li",
            }:
                assert True
                break
        else:
            assert False

    def test_gender(self):
        # Check expected female names are in the output.
        for i in range(300):
            first_name, *_ = fm.name(
                genderval="female", countryval="United Kingdom"
            ).split()
            if first_name in {
                "Ellie",
                "Jill",
                "Irene",
                "Jean",
                "Megan",
                "Fiona",
                "Sylvia",
                "Claire",
                "Kim",
                "Lydia",
                "Jane",
                "Karen",
                "Amy",
                "Paula",
            }:
                assert True
                break
        else:
            assert False

    def test_isvalid(self):
        # Check that name is valid.
        assert fm.isvalid.name(fm.name())


class TestMark:
    def test_type(self):
        # Check that mark is a float.
        # np.nan is an instance of float as well.
        assert isinstance(fm.mark(), float)

    def test_range(self):
        # Check that the mark is between 0 and 100.
        assert 0 <= fm.mark(pnan=0) <= 100

    def test_pfail_1(self):
        # Check pfail is respected.
        assert fm.mark(pfail=1, pnan=0) == 0.0

    def test_pfail_0_5(self):
        # Check pfail is respected.
        marks = np.array([fm.mark(pfail=0.5, pnan=0) for _ in range(100)])
        assert 35 <= (marks == 0).sum() <= 65

    def test_pfail_0(self):
        # Check pfail is respected.
        marks = np.array([fm.mark(pfail=0, pnan=0) for _ in range(100)])
        assert (marks == 0).sum() == 0

    def test_pnan_1(self):
        # Check pfail is respected.
        assert np.isnan(fm.mark(pfail=0, pnan=1))

    def test_pnan_0_5(self):
        # Check pfail is respected.
        marks = np.array([fm.mark(pfail=0, pnan=0.5) for _ in range(100)])
        assert 35 <= np.isnan(marks).sum() <= 65

    def test_pnan_0(self):
        # Check pfail is respected.
        marks = np.array([fm.mark(pfail=0, pnan=0) for _ in range(100)])
        assert np.isnan(marks).sum() == 0

    def test_mean(self):
        # Check that the mean is as expected.
        marks = np.array(
            [fm.mark(mean=65, std=10, pfail=0, pnan=0) for _ in range(100)]
        )
        assert 60 <= marks.mean() <= 70

    def test_std(self):
        # Check that the standard deviation is as expected.
        marks = np.array(
            [fm.mark(mean=65, std=10, pfail=0, pnan=0) for _ in range(100)]
        )
        assert 8 <= marks.std() <= 12

    def test_isvalid(self):
        # Check that mark is valid.
        assert fm.isvalid.mark(fm.mark())


class TestFeedback:
    def test_type(self):
        # Check that feedback is a string.
        assert isinstance(fm.feedback(), str)


class TestStudent:
    def test_type(self):
        # Check that the output is a Student dataclass.
        assert isinstance(fm.student(), fm.util.Student)

    def test_cid(self):
        # Check that the CID is a string.
        assert hasattr(fm.student(), "cid")

    def test_repr(self):
        # Check that the repr string makes sense.
        assert "Student" in repr(fm.student())


class TestCohort:
    def test_type(self, cohort):
        # Check that the output is a DataFrame.
        assert isinstance(cohort, pd.DataFrame)

    def test_course(self, cohort):
        # Check that the output is the right length.
        assert len(cohort["course"].unique()) == 3

    def test_tutor(self, cohort):
        # Check that the number of tutors is bounded.
        assert cohort["tutor"].map(fm.isvalid.name).all()

    def test_nationality(self, cohort):
        # Check that nationalities are as expected.
        counts = collections.Counter(cohort["nationality"])

        assert set(counts.keys()) <= set(fm.util.COUNTRIES.keys())
        assert counts["China"] > 40
        assert counts["United Kingdom"] > 4

    def test_username(self, cohort):
        # Check that usernames are as expected.
        assert cohort.index.name == "username"
        assert cohort.index.is_unique
        assert cohort.index.map(fm.isvalid.username).all()

    def test_cid(self, cohort):
        # Check that CIDs are as expected.
        assert cohort["cid"].map(fm.isvalid.cid).all()

    def test_email(self, cohort):
        # Check that emails are as expected.
        assert cohort["email"].map(fm.isvalid.email).all()

    def test_personal_email(self, cohort):
        # Check that emails are as expected.
        assert cohort["personal_email"].map(fm.isvalid.email).all()

    def test_title(self, cohort):
        # Check that titles are as expected.
        assert cohort["title"].map(fm.isvalid.title).all()

    def test_first_name(self, cohort):
        # Check that names are as expected.
        assert cohort["first_name"].map(fm.isvalid.name).all()

    def test_last_name(self, cohort):
        # Check that names are as expected.
        assert cohort["last_name"].map(fm.isvalid.name).all()

    def test_gender(self, cohort):
        # Check that genders are as expected.
        assert cohort["gender"].map(fm.isvalid.gender).all()

    def test_fee_status(self, cohort):
        # Check that genders are as expected.
        assert cohort["fee_status"].map(fm.isvalid.fee_status).all()

    def test_isvalid(self, cohort):
        # Check that the output is a DataFrame.
        assert fm.isvalid.cohort(cohort)


class TestAssignment:
    def test_type(self, assignment):
        # Check that the output is a DataFrame.
        assert isinstance(assignment, pd.Series)
        assert assignment.dtype == np.float64

    def test_index(self, assignment):
        # Check that usernames are as expected.
        assert assignment.index.is_unique
        assert assignment.index.name == "username"
        assert assignment.index.map(fm.isvalid.username).all()

    def test_mark(self, assignment):
        # Check that the marks are as expected.
        assert assignment.apply(fm.isvalid.mark).all()

    def test_wrong_username(self):
        # Check that the exception is raised.
        with pytest.raises(ValueError):
            fm.assignment(usernames=["wrong_username", "abc123"])

    def test_isvalid(self, cohort):
        assignment = fm.assignment(usernames=cohort.index, pnan=0.1)
        assert fm.isvalid.assignment(assignment, valid_usernames=cohort.index)

    def test_nan(self, assignment):
        # Ensure that there are np.nan values in the assignment.
        assert assignment.isna().sum() > 0
