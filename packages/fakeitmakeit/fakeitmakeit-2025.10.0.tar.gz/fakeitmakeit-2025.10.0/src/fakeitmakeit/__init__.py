from importlib.metadata import version

from .factory import (
    assignment,
    cid,
    cohort,
    country,
    course,
    email,
    feedback,
    gender,
    mark,
    name,
    student,
    title,
    username,
)

__version__ = version("fakeitmakeit")

__all__ = [
    "assignment",
    "cid",
    "cohort",
    "country",
    "course",
    "email",
    "feedback",
    "gender",
    "mark",
    "name",
    "student",
    "title",
    "username",
]
