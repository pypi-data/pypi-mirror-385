import random
from dataclasses import dataclass

import faker
import pycountry

# Distributions.
GENDERS = {"male": 0.49, "female": 0.5, "nonbinary": 0.01}
TITLES = ["Mr", "Ms", "Mrs", "Miss", "Mx"]
COURSES = {"acse": 0.4, "edsml": 0.4, "gems": 0.2}
COUNTRIES = {country.name: 1 for country in pycountry.countries}


# Country-locale mapping.
# Exposed as mapping instead of a function for performance reasons.
COUNTRY_LOCALE = {}
for country in COUNTRIES:
    for locale in faker.config.AVAILABLE_LOCALES:
        if pycountry.countries.get(name=country).alpha_2 in locale:
            COUNTRY_LOCALE[country] = locale
            break


def discrete_draw(distribution):
    """Draw a value from a discrete distribution.

    Parameters
    ----------
    distribution: dict

        Dictionary with keys being possible outputs and values their probabilities.

    Returns
    -------
    str

        Randomly selected value.

    Examples
    --------
    >>> import fakeitmakeit as fm
    >>> fm.util.discrete_draw({"a": 0.5, "b": 0.5})  # doctest: +SKIP
    'a'

    """
    values = list(distribution.keys())
    probabilities = list(distribution.values())
    return random.choices(values, weights=probabilities, k=1)[0]


@dataclass
class Student:
    """A dataclass to be populated in student function."""

    cid: str
    gender: str
    nationality: str
    first_name: str
    last_name: str
    title: str
    course: str
    username: str
    email: str
    personal_email: str
    github: str
    fee_status: str
    enrollment_status: str
    tutor: str


@dataclass
class CohortBias:
    """A dataclass for grouping cohort-specific distributions."""

    gender: dict
    course: dict
    country_bias: dict


cohort_bias = CohortBias(
    gender={"male": 0.65, "female": 0.34, "nonbinary": 0.01},
    course={"acse": 0.4, "edsml": 0.4, "gems": 0.2},
    country_bias={
        "China": 1800,
        "United Kingdom": 350,
        "India": 150,
        "United States": 100,
        "Germany": 100,
        "France": 100,
        "Hong Kong": 100,
        "Spain": 100,
        "Italy": 100,
        "Netherlands": 80,
        "Canada": 80,
    },
)
