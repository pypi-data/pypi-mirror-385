from dataclasses import dataclass

from db_drift.models.complex_abstract_models import DatabaseObjectIndexLike


@dataclass
class Index(DatabaseObjectIndexLike):
    uniqueness: str
    tablespace: str | None = None
