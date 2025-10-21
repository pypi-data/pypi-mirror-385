import logging
import numbers
import re

import numpy as np
import pandas as pd

import fakeitmakeit.util as fmu


def email(value):
    """Check if ``value`` is a valid email.

    Parameters
    ----------
    value: str

        Email.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.isvalid.email('nikola.tesla@gmail.com')
    True
    >>> fm.isvalid.email('nikola.tesla(at)gmail.com')
    False

    """
    email_re = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return bool(re.fullmatch(email_re, value))


def username(value):
    """Check if ``value`` is a valid username.

    Parameters
    ----------
    value: str

        Username.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.isvalid.username('johndoe')
    False
    >>> fm.isvalid.username('abc1234')
    True

    """
    # We allow 1-3 lowercase letters followed by 1-5 numbers - first number is never 0.
    username_re = r"[a-z]{1,3}[1-9][0-9]{1,4}"
    return bool(re.fullmatch(username_re, value))


def cid(value):
    """Check if ``value`` is a valid CID.

    Parameters
    ----------
    value: str

        CID.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.isvalid.cid('01234567')
    True
    >>> fm.isvalid.cid('012345678')  # 9 digits
    False

    """
    cid_re = r"0[0-9]{7}"
    return bool(re.fullmatch(cid_re, value))


def name(value, allow_special_characters=True):
    """Check if ``value`` is a valid name.

    Parameters
    ----------
    value: str

        Name.

    allow_special_characters: bool, optional

        If ``True``, allow special characters in names, e.g. umlauts.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.isvalid.name('Albert Einstein')
    True
    >>> fm.isvalid.name('Albert')
    True
    >>> fm.isvalid.name('john')
    False
    >>> fm.isvalid.name('Nikola_Tesla')
    False

    """
    if allow_special_characters:
        word = r"[A-Z\u00C0-\u017F][a-z\u00C0-\u017F]"
    else:
        word = r"[A-Z][a-z]"

    name_re = rf"({word}*)([-\s](({word}*)|\({word}*\)))*"
    return bool(re.fullmatch(name_re, value))


def title(value):
    """Check if ``value`` is a valid title.

    Parameters
    ----------
    value: str

        Title.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.isvalid.title('Mr')
    True
    >>> fm.isvalid.title('mr')
    False
    >>> fm.isvalid.title('Herr')
    False

    """
    title_re = r"(Mr|Ms|Mrs|Mx|Miss|Dr)"
    return bool(re.fullmatch(title_re, value))


def course(value):
    """Check if ``value`` is a valid course.

    Parameters
    ----------
    value: str

        Course.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.isvalid.course('acse')
    True
    >>> fm.isvalid.course('a_very_cool_course')
    False

    """
    course_re = r"(acse|edsml|gems|ready)"
    return bool(re.fullmatch(course_re, value))


def gender(value):
    """Check if ``value`` is a valid gender.

    Parameters
    ----------
    value: str

        Gender.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.isvalid.gender('female')
    True
    >>> fm.isvalid.gender('Female')
    False

    """
    gender_re = r"(male|female|nonbinary)"
    return bool(re.fullmatch(gender_re, value))


def fee_status(value):
    """Check if ``value`` is a valid fee status.

    Parameters
    ----------
    value: str

        Fee status.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.isvalid.fee_status('home')
    True
    >>> fm.isvalid.fee_status('overseas')
    True
    >>> fm.isvalid.fee_status('home1')
    False

    """
    fee_status_re = r"(home|overseas|(home - elq))"
    return bool(re.fullmatch(fee_status_re, value))


def country(value):
    """Check if ``value`` is a valid country.

    Parameters
    ----------
    value: str

        Country.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    ...
    >>> fm.isvalid.country('United Kingdom')
    True
    >>> fm.isvalid.country('Neverland')
    False

    """
    allowed_countries = set(fmu.COUNTRIES.keys()) | {
        "Taiwan",
        "Syria",
        "Columbia",
        "Turkey",
        "United States of America",
        "Russia",
        "Palestine",
    }
    return value in allowed_countries


def mark(value):
    """Check if ``value`` is a valid mark.

    For ``value`` to be valid, it must be:
    1. An instance of ``numbers.Real`` (float, int, or ``np.nan``).
    2. If the value is not ``np.nan``, it must be ``0 <= value <= 100``.

    Parameters
    ----------
    value: numbers.Real

        Mark.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    >>> import numpy as np
    ...
    >>> fm.isvalid.mark(100)
    True
    >>> fm.isvalid.mark(101)
    False
    >>> fm.isvalid.mark(-1)
    False
    >>> fm.isvalid.mark(np.nan)
    True
    >>> fm.isvalid.mark("100")
    False

    """
    if not isinstance(value, numbers.Real):
        logging.warning(f"Invalid type {type(value)=}.")
        return False
    elif not np.isnan(value) and not 0 <= value <= 100:
        logging.warning(f"{value=} is not in [0, 100] range.")
        return False
    else:
        return True


def assignment(value, valid_usernames=None):
    """Check if ``value`` is a valid assignment.

    For the assessment to be valid, the following conditions must be met:

    1. ``value`` must be a ``pd.Series``.
    2. Index values must be valid usernames.
    3. Index values must be unique.
    4. Index name must be "username".
    5. Data values must be valid marks (``float`` in [0, 100] range or np.nan).
    6. If ``valid_usernames`` is provided, all usernames in index must be in it.

    Parameters
    ----------
    value: pd.Series

        Assignment. Index values are usernames and data are numerical marks.

    valid_usernames: Iterable[str], optional

        Iterable of valid usernames.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``. Fail reason is logged with level
        ``warning``.

    Examples
    --------
    >>> import fakeitmakeit as fm
    >>> import pandas as pd
    ...
    >>> value = pd.Series(
    ...     data = [50.1, 70],
    ...     index = pd.Index(["abc123", "sw4321"], name="username"),
    ...     name = "mark",
    ... )
    >>> fm.isvalid.assignment(value)
    True

    """
    # Check that value is a pd.Series.
    if not isinstance(value, pd.Series):
        logging.warning(f"Invalid type {type(value)=} - pd.Series expected.")
        return False

    # Check that indicies are valid usernames.
    valid = value.index.map(username)
    if not valid.all():
        logging.warning(f"Invalid usernames: {value.index[~valid].tolist()}")
        return False

    # Check if there are any duplicated usernames.
    duplicated = value.index.duplicated()
    if duplicated.any():
        logging.warning(f"Duplicated usernames: {value.index[duplicated].tolist()}.")
        return False

    # Check that index name is correct.
    if value.index.name != "username":
        logging.warning(
            f"Invalid index name {value.index.name=} - 'username' expected."
        )
        return False

    # Check data (marks).
    valid = value.map(mark)
    if not valid.all():
        logging.warning(f"Invalid marks: {value[~valid].tolist()}.")
        return False

    if valid_usernames is not None:
        valid_usernames = set(valid_usernames)
        invalid = [u for u in valid_usernames if not username(u)]
        if invalid:
            raise ValueError(f"Invalid usernames in valid_username: {invalid}.")

        valid = value.index.isin(valid_usernames)
        if not valid.all():
            logging.warning(f"Invalid usernames in index: {value.index[~valid]}.")
            return False

    return True


def cohort(value):
    """Check if ``value`` is a valid cohort.

    Parameters
    ----------
    value: pd.DataFrame

        Cohort.

    Returns
    -------
    bool

        ``True`` if valid, otherwise ``False``.

    """
    # Check that indicies are valid usernames.
    if not value.index.map(username).all():
        invalid = value.index[~value.index.map(username)]
        logging.warning(f"Invalid usernames: {invalid.tolist()}")
        return False

    # Check the index name.
    if value.index.name != "username":
        logging.warning(
            f"Invalid index name {value.index.name} - it must be 'username'."
        )
        return False

    # Check if there are any repeated usernames.
    if not value.index.is_unique:
        invalid = value.index[value.index.duplicated()]
        logging.warning(f"There are duplicate usernames: {invalid.tolist()}.")
        return False

    # Check other columns.
    for col in set(value.columns) - {
        "username",
        "github",
        "enrollment_status",
        "comment",
    }:
        if "name" in col or col == "tutor":
            data_type = "name"
        elif "email" in col:
            data_type = "email"
        elif col == "nationality":
            data_type = "country"
        else:
            data_type = col

        # print(col, data_type)

        validation_function = globals()[f"{data_type}"]
        if not value[col].map(validation_function).all():
            invalid = value[col][~value[col].map(validation_function)]
            logging.warning(f'Errors in column "{col}": {invalid.tolist()}.')
            return False
    return True
