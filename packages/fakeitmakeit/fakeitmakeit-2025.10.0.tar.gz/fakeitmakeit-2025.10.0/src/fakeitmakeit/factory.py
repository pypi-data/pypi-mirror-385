import random
import re
import string
from dataclasses import fields

import numpy as np
import pandas as pd
from faker import Faker

import fakeitmakeit.isvalid as fmiv
import fakeitmakeit.util as fmu


def cid():
    """Generate a random 8-digit CID.

    The first digit is always 0, whereas the second digit is 1 or 2. The remaining 6
    digits are randomly generated between 0 and 9.

    Returns
    -------
    str

        Randomly generated CID.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.cid()  # doctest: +SKIP
    "01234567"

    """
    # The first digit is always 0.
    number = "0"

    # The second digit is 1 or 2.
    number += str(random.choice([1, 2]))

    # Generate the remaining 6 digits randomly between 0 and 9.
    number += "".join(str(random.randint(0, 9)) for _ in range(6))

    return number


def gender(distribution=dict(fmu.GENDERS)):
    """Generate a random gender.

    Possible gender values and their relative probabilities are passed via
    ``distribution`` - a dictionary whose keys are possible outputs and values are
    relative probablilities. The values in ``distribution`` do not have to sum to 1
    because selections will be made according to the relative weights.

    Parameters
    ----------
    distribution: dict

        Keys are possible output values and values are relative probablilities. For
        instance, ``{"male": 0.5, "female": 0.5}``.

    Returns
    -------
    str

        Randomly generated gender.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.gender()  # doctest: +SKIP
    'male'

    """
    return fmu.discrete_draw(distribution)


def title(genderval=None):
    """Generate a random title.

    If gender is provided via ``genderval``, then the title is generated
    according to it. Otherwise, the gender and accordingly the title is
    generated randomly.

    For further details, refer to:
    - https://www.grammarly.com/blog/ms-mrs-miss-difference/
    - https://publishing.rcseng.ac.uk/doi/pdf/10.1308/rcsbull.2021.141

    Parameters
    ----------
    genderval: str

        Gender.

    Returns
    -------
    str

        Randomly generated title.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.title('male')
    'Mr'
    >>> fm.title('nonbinary')
    'Mx'
    >>> fm.title()  # doctest: +SKIP
    'Mx'

    """
    genderval = genderval or gender()
    if genderval == "male":
        return "Mr"
    elif genderval == "female":
        return random.choice(["Ms", "Mrs", "Miss"])
    elif genderval == "nonbinary":
        return "Mx"
    else:
        raise ValueError(f"Invalid gender: {genderval=}")


def course(distribution=dict(fmu.COURSES)):
    """Generate a random course.

    Possible courses and their relative probabilities are passed via ``distribution``.
    It is a dictionary whose keys are possible outputs and values are relative
    probablilities. The values in ``distribution`` do not have to sum to 1 because
    selections will be made according to the relative weights.

    Parameters
    ----------
    distribution: dict

        Keys are possible outputs and values are relative probablilities. For instance,
        ``{"course1": 0.5, "course2": 0.5}``.

    Returns
    -------
    str

        Randomly generated course.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.course()  # doctest: +SKIP
    'acse'

    """
    return fmu.discrete_draw(distribution)


def country(distribution=dict(fmu.COUNTRIES), bias=None):
    """Generate a random country.

    Distribution is passed via ``distribution``. It is a dictionary whose keys are
    possible outputs and values are relative probablilities. The values in
    ``distribution`` do not have to sum to 1 because selections will be made according
    to the relative weights.

    By default, all countries are equally likely and their relative probablility is 1.
    To modify the default probablilities, pass a dictionary of countries and their
    relative probabilities via ``bias``. Internally, ``distribution |= bias`` is
    calculated.

    Parameters
    ----------
    distribution: dict

        Keys are possible outputs and values are relative probablilities.

    Returns
    -------
    str

        Randomly generated country.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.country()  # doctest: +SKIP
    'United Kingdom'
    >>> fm.country(bias={'India': 0.5, 'United Kingdom': 0.2})  # doctest: +SKIP
    'India'
    >>> fm.country(distribution={}, bias={'France': 1})
    'France'

    """
    distribution |= bias or {}
    return fmu.discrete_draw(distribution)


def username(nameval=None):
    """Generate a random username.

    The username is the combination of 2-3 lowercase letters and a random number with 2
    to 4 digits. The first letter of the username is the first letter of the first name,
    whereas the the last letter of the username is the first letter of the last name.
    Letters are followed with a random integer between 2 and 4 digits. The first digit
    of the number is never zero.

    Parameters
    ----------
    nameval: str

        Name.

    Returns
    -------
    str

        Randomly generated username.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.username('John Smith')  # doctest: +SKIP
    'jws4122'

    """
    nameval = nameval or name()

    # Get the first letter of the first name.
    first_letter, *_ = nameval.casefold().split()[0]

    # Get the first letter of the last name.
    last_letter, *_ = nameval.casefold().split()[-1]

    # Randomly decide if the string will have 2 or 3 letters.
    if random.choice([2, 3]) == 3:
        # Generate a random middle lowercase letter (can be any lowercase letter).
        middle_letter = random.choice(string.ascii_lowercase)
        letters = first_letter + middle_letter + last_letter
    else:
        letters = first_letter + last_letter

    # Generate a random number between 2 and 4 digits where the first digit is not zero.
    num_digits = random.choice([2, 3, 4])
    numbers = str(random.randint(1, 9))  # First digit is never zero
    for _ in range(num_digits - 1):
        numbers += str(random.randint(0, 9))

    return letters + numbers


def email(domainval=None):
    """Generate a random email.

    If ``domainval`` is not provided, then an email with a random domain is generated.
    Otherwise, the email is generated with the provided domain.

    Parameters
    ----------
    domainval: str

        Domain.

    Returns
    -------
    str

        Randomly generated email.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.email()  # doctest: +SKIP
    'somerandomemail@domain.com'
    >>> fm.email(domainval='myuniversity.ac.uk')  # doctest: +SKIP
    'john.doe@myuniversity.ac.uk'

    """
    fake = Faker()
    domain = domainval or fake.domain_name()
    return f"{fake.user_name()}@{domain}"


def name(genderval=None, countryval=None):
    """Generate a random name.

    This function uses Faker to generate a random name. Depending on the ``countryval``
    and ``genderval`` parameters, the name is generated according to the locale and by
    calling the appropriate method from ``Faker``. Otherwise, the name with the default
    ``Faker`` locale is returned.

    Parameters
    ----------
    genderval: str

        Gender.

    countryval: str

        Country.

    Returns
    -------
    str

        Randomly generated name.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.name()  # doctest: +SKIP
    'John Smith'
    >>> fm.name(countryval='China')  # doctest: +SKIP
    'Zhang San'
    >>> fm.name(genderval='female', countryval='Germany')  # doctest: +SKIP
    'Anna Schmidt'

    """
    locale = fmu.COUNTRY_LOCALE.get(countryval, None)
    fake = Faker(locale)

    # Romanized is available only for some countries.
    if hasattr(fake, "romanized_name"):
        res = fake.romanized_name()
    else:
        # Depending on the gender, we call the appropriate method from Faker.
        method = f"name_{genderval}" if genderval is not None else "name"

        # Not all countries have names for different genders.
        try:
            res = getattr(fake, method)()
        except AttributeError:
            res = fake.name()

        # Remove suffixes and prefixes - Mr, PhD, words with dots and all caps.
        # This is not exhaustive and some names might still contain some of these.
        pattern = r"\b(?:[A-Z]+\b|PhD|Dr\(a\)|,|Dr|Mr|Mrs|Ms|Miss|\w*\.\w*)"
        res = re.sub(pattern, "", res).strip()

    if fmiv.name(res, allow_special_characters=False):
        return res
    else:
        # If the name is not valid, then we generate a new one with default faker until
        # it passes validation.
        while not fmiv.name(res, allow_special_characters=False):
            res = Faker().name()

        return res


def mark(mean=65.0, std=6.0, pfail=0.02, pnan=0.0):
    """Generate a random mark.

    A mark between 0 and 100 is generated from a normal distribution with the given
    ``mean`` and standard deviation ``std``. There is fail probability ``pfail`` that
    the mark will be 0. Similarly, the probability that mark will be ``np.nan`` is
    ``pnan. Resulting mark is rounded to two decimal places.

    Mark 0 can be interpreted as the student not submitting the assignment, whereas
    ``np.nan`` can be interpreted as the mark not being available, e.g. skipped exam due
    to mitigating circumstances.

    Parameters
    ----------
    mean: float

        Mean.

    std: float

        Standard deviation.

    pfail: float

        Probability that the mark will be 0.

    pnan: float

        Probability that the mark will be ``np.nan``.

    Returns
    -------
    float

        Randomly generated from [0, 100] range or ``np.nan``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.mark(mean=65, std=10)  # doctest: +SKIP
    71
    >>> fm.mark(mean=65, std=10, pfail=1, pnan=0)
    0.0
    >>> fm.mark(mean=65, std=10, pfail=0, pnan=1)
    nan

    """
    rng = np.random.default_rng()

    if rng.random() < pfail:
        # Return 0 with a probability of pfail.
        return 0.0
    elif rng.random() < pnan:
        # Return np.nan with a probability of pfail.
        return np.nan
    else:
        # Generate a random number from a normal distribution with the given
        # mean and standard deviation.
        number = rng.normal(loc=mean, scale=std)
        # Clip the number to be be between 0 and 100.
        number = np.clip(number, 0, 100)
        # Round the number to two decimal places
        return round(number, 2)


def feedback():
    """Generate a random feedback.

    The feedback is generated by Faker and consists of one paragraph.

    Returns
    -------
    str

        Randomly generated feedback.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.feedback()  # doctest: +SKIP
    ...

    """
    return "\n\n".join(Faker().paragraphs(nb=1))


def student():
    """Generate a random student.

    Returns
    -------
    Student

        Student dataclass.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.student()
    Student(cid=...)

    """
    # (Intermediate) values required for other fields.
    genderval = gender(distribution=fmu.cohort_bias.gender)
    courseval = course(distribution=fmu.cohort_bias.course)
    countryval = country(bias=fmu.cohort_bias.country_bias)
    first_name, *_, last_name = name(genderval=genderval, countryval=countryval).split()
    usernameval = username(nameval=f"{first_name} {last_name}")

    return fmu.Student(
        cid=cid(),
        gender=genderval,
        course=courseval,
        nationality=countryval,
        first_name=first_name,
        last_name=last_name,
        title=title(genderval=genderval),
        username=usernameval,
        email=email(domainval="imperial.ac.uk"),
        personal_email=email(),
        github=f"{courseval}-{usernameval}",
        fee_status="home" if countryval == "United Kingdom" else "overseas",
        enrollment_status="enrolled",
        tutor=name(),
    )


def cohort(n):
    """Generate a cohort of students.

    Parameters
    ----------
    n: int

        Number of students.

    Returns
    -------
    pd.DataFrame

        A cohort dataframe.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.cohort(n=30)  # doctest: +SKIP
    ...

    """
    students = [student() for _ in range(n)]
    return (
        pd.DataFrame(
            {
                col.name: [getattr(student, col.name) for student in students]
                for col in fields(fmu.Student)
            }
        )
        .set_index("username", verify_integrity=True)
        .astype(
            {
                "course": "category",
                "gender": "category",
                "title": "category",
                "nationality": "category",
                "fee_status": "category",
                "enrollment_status": "category",
            }
        )
    )


def assignment(usernames, mean=65, std=6, pfail=0.02, pnan=0.0):
    """Generate an assignment.

    For each username, a mark is generated using the ``mark`` function.

    Parameters
    ----------
    usernames: Iterable[str]

        Iterable of usernames.

    mean: float

        Mean.

    std: float

        Standard deviation.

    pfail: float

        Probability that the mark will be 0.

    pnan: float

        Probability that the mark will be ``np.nan``.

    Returns
    -------
    pd.Series

        An assignment.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.assignment(["abc123", "xyz321"])  # doctest: +SKIP
    username
    abc123     67.9
    xyz321    73.08
    Name: mark, dtype: Float64

    """
    usernames = list(usernames)
    invalid = [u for u in usernames if not fmiv.username(u)]
    if invalid:
        raise ValueError(f"Invalid usernames: {invalid}.")

    return pd.Series(
        data=[mark(mean=mean, std=std, pfail=pfail, pnan=pnan) for _ in usernames],
        index=pd.Index(usernames, name="username"),
        name="mark",
        dtype=np.float64,  # allow missing values
    )
