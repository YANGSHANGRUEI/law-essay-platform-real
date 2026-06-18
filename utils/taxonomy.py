import json
import os

TAXONOMY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "taxonomy.json"
)


def load_taxonomy() -> dict:
    with open(TAXONOMY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def list_fields(taxonomy: dict | None = None) -> list[str]:
    data = taxonomy if taxonomy is not None else load_taxonomy()
    return sorted(data.keys())


def list_subjects(field: str, taxonomy: dict | None = None) -> list[str]:
    data = taxonomy if taxonomy is not None else load_taxonomy()
    return sorted(data.get(field, {}).keys())


def list_teachers(field: str, subject: str, taxonomy: dict | None = None) -> list[str]:
    data = taxonomy if taxonomy is not None else load_taxonomy()
    return sorted(data.get(field, {}).get(subject, {}).keys())


def _teacher_periods(
    field: str, subject: str, teacher: str, taxonomy: dict | None = None
) -> dict:
    data = taxonomy if taxonomy is not None else load_taxonomy()
    return data.get(field, {}).get(subject, {}).get(teacher, {})


def list_academic_years(
    field: str, subject: str, teacher: str, taxonomy: dict | None = None
) -> list[str]:
    periods = _teacher_periods(field, subject, teacher, taxonomy)
    return sorted(periods.keys(), reverse=True)


def list_semesters(
    field: str,
    subject: str,
    teacher: str,
    academic_year: str,
    taxonomy: dict | None = None,
) -> list[str]:
    periods = _teacher_periods(field, subject, teacher, taxonomy)
    return sorted(periods.get(academic_year, {}).keys())


def list_exam_periods(
    field: str,
    subject: str,
    teacher: str,
    academic_year: str,
    semester: str,
    taxonomy: dict | None = None,
) -> list[str]:
    periods = _teacher_periods(field, subject, teacher, taxonomy)
    return periods.get(academic_year, {}).get(semester, [])


def build_year_value(academic_year: str, semester: str, exam_period: str) -> str:
    return f"{academic_year}-{semester}-{exam_period}"


def parse_year_parts(year: str) -> tuple[str, str, str]:
    parts = year.split("-", 2)
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    return year, "", ""
