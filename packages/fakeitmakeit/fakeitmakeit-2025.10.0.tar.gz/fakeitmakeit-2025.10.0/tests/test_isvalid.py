import numpy as np
import pandas as pd
import pytest

import fakeitmakeit as fm


@pytest.fixture(scope="function")
def valid_assignment():
    return pd.Series(
        data=[23.0, 56.8, 72.5],
        index=pd.Index(["abc123", "def4561", "g789"], name="username"),
    )


@pytest.fixture(scope="function")
def invalid_assignment():
    return pd.Series(
        data=[23.0, -56.8, 72.5],
        index=pd.Index(["abc123", "def4561", "g789"], name="username"),
    )


@pytest.fixture(scope="function")
def valid_cohort():
    cohort = pd.DataFrame(
        {
            "cid": ["01079210", "02747269", "02605421"],
            "username": ["jsg8052", "tf97", "mk4717"],
            "github": ["acse-jsg8052", "edsml-tf97", "edsml-mk4717"],
            "course": ["acse", "edsml", "edsml"],
            "title": ["Miss", "Miss", "Mr"],
            "first_name": ["Jie", "Tracy", "Mahika"],
            "last_name": ["Gong", "Fry", "Kapur"],
            "gender": ["female", "female", "male"],
            "email": [
                "james13@imperial.ac.uk",
                "tchurch@imperial.ac.uk",
                "angela05@imperial.ac.uk",
            ],
            "tutor": ["Anne Spencer", "Theresa Jones", "Joseph Wells"],
            "fee_status": ["overseas", "home", "overseas"],
            "nationality": ["China", "United Kingdom", "India"],
            "enrollment_status": ["enrolled", "enrolled", "enrolled"],
            "personal_email": [
                "nathanolson@lindsey.biz",
                "ruizsally@smith.com",
                "willissandy@cline.com",
            ],
        }
    )
    return cohort.set_index("username")


@pytest.fixture(scope="module")
def invalid_cohort():
    # Duplicate username
    cohort = pd.DataFrame(
        {
            "cid": ["01079210", "02747269", "02605421"],
            "username": ["jsg8052", "tf97", "tf97"],
            "github": ["acse-jsg8052", "edsml-tf97", "edsml-mk4717"],
            "course": ["acse", "edsml", "edsml"],
            "title": ["Miss", "Miss", "Mr"],
            "first_name": ["Jie", "Tracy", "Mahika"],
            "last_name": ["Gong", "Fry", "Kapur"],
            "gender": ["female", "female", "male"],
            "email": [
                "james13@imperial.ac.uk",
                "tchurch@imperial.ac.uk",
                "angela05@imperial.ac.uk",
            ],
            "tutor": ["Anne Spencer", "Theresa Jones", "Joseph Wells"],
            "fee_status": ["overseas", "home", "overseas"],
            "nationality": ["China", "United Kingdom", "India"],
            "enrollment_status": ["enrolled", "enrolled", "enrolled"],
            "personal_email": [
                "nathanolson@lindsey.biz",
                "ruizsally@smith.com",
                "willissandy@cline.com",
            ],
        }
    )
    return cohort.set_index("username")


class TestEmail:
    def test_valid(self):
        # Check that valid emails are valid.
        assert fm.isvalid.email("username@domain.com")
        assert fm.isvalid.email("user.name@domain.com")
        assert fm.isvalid.email("user_name@domain.ac.uk")

    def test_invalid(self):
        # Check that invalid emails are invalid.
        assert not fm.isvalid.email("username@domain")
        assert not fm.isvalid.email("user_name@domain.")
        assert not fm.isvalid.email("user name@domain.com")
        assert not fm.isvalid.email("username@domain.com ")
        assert not fm.isvalid.email(" username@domain.com ")


class TestUsername:
    def test_valid(self):
        # Test cases with valid usernames
        assert fm.isvalid.username("s12")  # we allow one letter in username
        assert fm.isvalid.username("ab12")
        assert fm.isvalid.username("ab123")
        assert fm.isvalid.username("abc1234")
        assert fm.isvalid.username("xy9999")
        assert fm.isvalid.username("x99999")  # we allow 5 digits in username

    def test_invalid_start_digit(self):
        # Test case with a username starting with a digit
        assert not fm.isvalid.username("1ab123")

    def test_invalid_wrong_first_digit(self):
        # Test case with a username having '0' as the first digit after letters
        assert not fm.isvalid.username("ab0234")

    def test_invalid_too_few_digits(self):
        # Test case with too few digits
        assert not fm.isvalid.username("abc1")

    def test_invalid_too_many_digits(self):
        # Test case with too many digits
        assert not fm.isvalid.username("ab123456")

    def test_invalid_uppercase_letters(self):
        # Test case with uppercase letters
        assert not fm.isvalid.username("aBc123")

    def test_invalid_special_characters(self):
        # Test case with special characters
        assert not fm.isvalid.username("ab#123")

    def test_invalid_too_many_letters(self):
        # Test case with too many letters
        assert not fm.isvalid.username("abcd1234")

    def test_invalid_empty_string(self):
        # Test case with an empty string
        assert not fm.isvalid.username("")

    def test_invalid_whitespace(self):
        # Test case with whitespace
        assert not fm.isvalid.username("ab 1234")

    def test_invalid_trailing_whitespace(self):
        # Test case with whitespace
        assert not fm.isvalid.username("ab1234 ")
        assert not fm.isvalid.username(" ab1234")


class TestCID:
    def test_valid(self):
        # Test valid CIDs that meet all the criteria
        assert fm.isvalid.cid("01234567")
        assert fm.isvalid.cid("02123456")
        assert fm.isvalid.cid("05123456")
        assert fm.isvalid.cid("00123456")  # we allow two leading zeros

    def test_invalid_length(self):
        # Test CIDs with incorrect length (should be exactly 8 digits)
        assert not fm.isvalid.cid("0123456")  # Too short
        assert not fm.isvalid.cid("012345678")  # Too long

    def test_invalid_starting_digit(self):
        # Test a CID that does not start with a digit
        assert not fm.isvalid.cid("51234567")

    def test_invalid_contains_non_digit(self):
        # Test CIDs that contain non-digit characters
        assert not fm.isvalid.cid("01234a67")

    def test_invalid_empty_string(self):
        # Test an empty string (should be invalid)
        assert not fm.isvalid.cid("")

    def test_invalid_special_characters(self):
        # Test CIDs that contain special characters
        assert not fm.isvalid.cid("0123-567")

    def test_invalid_trailing_whitespace(self):
        # Test a CID with trailing whitespace
        assert not fm.isvalid.cid("01234567 ")
        assert not fm.isvalid.cid(" 01234567")


class TestName:
    def test_valid_single_word(self):
        # Test valid single word names (each word must start with a capital letter)
        assert fm.isvalid.name("John")
        assert fm.isvalid.name("Mary")

    def test_valid_multiple_words(self):
        # Test valid multiple word names (names with more than one word, each starting
        # with a capital letter)
        assert fm.isvalid.name("John Smith")
        assert fm.isvalid.name("Jean-Luc Picard")
        assert fm.isvalid.name("Jean-Luc (Peter) Picard")

    def test_valid_hyphenated_names(self):
        # Test valid hyphenated names (names with hyphens, each part starting with a
        # capital letter)
        assert fm.isvalid.name("Mary-Ann")
        assert fm.isvalid.name("Jean-Paul")

    def test_valid_accented_characters(self):
        # Test valid names with accented characters
        assert fm.isvalid.name("Željko Petrović")
        assert fm.isvalid.name("Jürgen Müller")
        assert fm.isvalid.name("Émilie Durand")
        assert fm.isvalid.name("José García")
        assert fm.isvalid.name("Łukasz Kowalski")
        assert fm.isvalid.name("Márquez López")
        assert fm.isvalid.name("François Dupont")
        assert fm.isvalid.name("Anaïs Fournier")
        assert fm.isvalid.name("Mesut Özil")
        assert fm.isvalid.name("Šimon Novak")

    def test_invalid_capitalization(self):
        # Test names with invalid capitalization (names must start each word with a
        # capital letter)
        assert not fm.isvalid.name("john")  # Not capitalized
        assert not fm.isvalid.name("JOHN")  # All uppercase

    def test_invalid_contains_digits_or_characters(self):
        # Test names containing digits or special characters (names should only contain
        # letters, spaces, or hyphens)
        assert not fm.isvalid.name("John123")  # Contains digits
        assert not fm.isvalid.name("John@Doe")  # Contains special characters
        assert not fm.isvalid.name("John_Doe")  # Contains special characters

    def test_invalid_use_of_hyphen_or_space(self):
        # Test names with incorrect use of hyphen or space (hyphens should replace
        # spaces, not be used alongside them)
        assert not fm.isvalid.name("John - Smith")  # Hyphen not used correctly
        assert not fm.isvalid.name("John  Smith")  # Double space

    def test_invalid_empty_or_whitespace(self):
        # Test empty string or names with leading/trailing whitespace (names should not
        # have extra whitespace)
        assert not fm.isvalid.name("")  # Empty string
        assert not fm.isvalid.name(" John")  # Leading space
        assert not fm.isvalid.name("John ")  # Trailing space

    def test_parenthesis(self):
        # Test names with parenthesis.
        assert fm.isvalid.name("John (Daniel) Smith")
        assert fm.isvalid.name("John (Daniel)")


class TestTitle:
    @pytest.mark.parametrize(
        "title, expected",
        [
            ("Mr", True),
            ("Ms", True),
            ("Mrs", True),
            ("Mx", True),
            ("Miss", True),
            ("Dr", True),
            ("mr", False),  # Not correctly capitalized
            ("Doctor", False),  # Not an exact match
            ("Lord", False),  # Not in the list
            ("Mx ", False),  # Trailing whitespace
            ("", False),  # Empty string
        ],
    )
    def test_valid(self, title, expected):
        assert fm.isvalid.title(title) == expected


class TestCourse:
    @pytest.mark.parametrize(
        "course, expected",
        [
            ("acse", True),
            ("edsml", True),
            ("gems", True),
            ("ACSE", False),  # Not lowercase
            ("Edsml", False),  # Not lowercase
            ("gEmS", False),  # Not lowercase
            ("math", False),  # Not in the list
            ("acse ", False),  # Trailing whitespace
            ("", False),  # Empty string
        ],
    )
    def test_valid(self, course, expected):
        assert fm.isvalid.course(course) == expected


class TestGender:
    @pytest.mark.parametrize(
        "gender, expected",
        [
            ("male", True),
            ("female", True),
            ("nonbinary", True),
            ("Male", False),  # Not lowercase
            ("FEMALE", False),  # Not lowercase
            ("NonBinary", False),  # Not lowercase
            ("man", False),  # Not in the list
            ("woman", False),  # Not in the list
            ("male ", False),  # Trailing whitespace
            ("", False),  # Empty string
        ],
    )
    def test_valid(self, gender, expected):
        assert fm.isvalid.gender(gender) == expected


class TestFeeStatus:
    @pytest.mark.parametrize(
        "fee_status, expected",
        [
            ("home", True),  # Valid fee status
            ("overseas", True),  # Valid fee status
            ("home - elq", True),  # Valid fee status
            ("Home", False),  # Not lowercase
            ("OVERSEAS", False),  # Not lowercase
            ("local", False),  # Not in the list
            ("international", False),  # Not in the list
            ("overseas ", False),  # Trailing whitespace
            ("", False),  # Empty string
        ],
    )
    def test_valid(self, fee_status, expected):
        assert fm.isvalid.fee_status(fee_status) == expected


class TestCountry:
    @pytest.mark.parametrize(
        "country, expected",
        [
            ("United Kingdom", True),  # Valid country
            ("United States", True),  # Valid country
            ("Croatia", True),  # Valid country
            ("United Kingdom ", False),  # Trailing whitespace
            ("", False),  # Empty string
            ("UK", False),  # Not in the list
            ("England", False),  # Not in the list
        ],
    )
    def test_valid(self, country, expected):
        assert fm.isvalid.country(country) == expected


class TestMark:
    @pytest.mark.parametrize(
        "mark, expected",
        [
            (0, True),  # Lower bound
            (100, True),  # Upper bound
            (50.0, True),  # Middle value
            (65.12, True),  # Middle value
            (101, False),  # Above upper bound
            (np.nan, True),  # Missing value
            (-1, False),  # Below lower bound
            ("50", False),  # Not a number
        ],
    )
    def test_valid(self, mark, expected):
        assert fm.isvalid.mark(mark) == expected


class TestAssignment:
    def test_valid(self, valid_assignment):
        # Check that valid assignments are valid
        assert fm.isvalid.assignment(valid_assignment)

    def test_with_valid_usernames(self, valid_assignment):
        assert fm.isvalid.assignment(
            valid_assignment, valid_usernames=["abc123", "def4561", "g789"]
        )

    def test_with_wrong_valid_usernames1(self, valid_assignment):
        # One username is missing.
        assert not fm.isvalid.assignment(
            valid_assignment, valid_usernames=["def4561", "g789"]
        )

    def test_with_wrong_valid_usernames2(self, valid_assignment):
        # One username is missing.
        with pytest.raises(ValueError):
            fm.isvalid.assignment(
                valid_assignment, valid_usernames=["def4561", "wrong_username"]
            )

    def test_wrong_index(self, valid_assignment):
        valid_assignment.index = ["1", "2", "3"]
        assert not fm.isvalid.assignment(valid_assignment)

    def test_index_name(self, valid_assignment):
        valid_assignment.index.name = "wrong_name"
        assert not fm.isvalid.assignment(valid_assignment)

    def test_index_not_unique(self, valid_assignment):
        valid_assignment.index = ["abc123", "abc123", "gr789"]
        valid_assignment.index.name = "username"
        assert not fm.isvalid.assignment(valid_assignment)

    def test_invalid(self, invalid_assignment):
        # Check that invalid assignments are invalid
        assert not fm.isvalid.assignment(invalid_assignment)


class TestCohort:
    def test_valid(self, valid_cohort):
        # Check that valid cohorts are valid
        assert fm.isvalid.cohort(valid_cohort)

    def test_invalid(self, invalid_cohort):
        assert not fm.isvalid.cohort(invalid_cohort)

    def test_wrong_index(self, valid_cohort):
        valid_cohort.index = ["1", "2", "3"]
        assert not fm.isvalid.cohort(valid_cohort)

    def test_wrong_index_name(self, valid_cohort):
        valid_cohort.index.name = "wrong_name"
        assert not fm.isvalid.cohort(valid_cohort)

    def test_wrong_data(self, valid_cohort):
        valid_cohort.loc["tf97", "first_name"] = "WRONG NAME"
        assert not fm.isvalid.cohort(valid_cohort)

    def test_github(self, valid_cohort):
        course = valid_cohort.github.str.extract(r"(^.*?)\-", expand=False)
        username = valid_cohort.github.str.extract(r"\-(.*?$)", expand=False)
        assert course.map(fm.isvalid.course).all()
        assert username.map(fm.isvalid.username).all()
