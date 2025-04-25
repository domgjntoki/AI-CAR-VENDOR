from enum import Enum

from sqlalchemy import or_

DB_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

FILTER_MAPPING = {
    "brand": lambda col, value: or_(*[col.ilike(f"%{v}%") for v in value])
    if value
    else None,
    "model": lambda col, value: or_(*[col.ilike(f"%{v}%") for v in value])
    if value
    else None,
    "min_year": lambda col, value: col >= value if value else None,
    "max_year": lambda col, value: col <= value if value else None,
    "min_price": lambda col, value: col >= value if value else None,
    "max_price": lambda col, value: col <= value if value else None,
    "fuel_type": lambda col, value: or_(*[col.ilike(f"%{v}%") for v in value])
    if value
    else None,
    "color": lambda col, value: or_(*[col.ilike(f"%{v}%") for v in value])
    if value
    else None,
    "mileage": lambda col, value: col <= value if value else None,
    "doors": lambda col, value: col == value if value else None,
    "transmission": lambda col, value: or_(*[col.ilike(f"%{v}%") for v in value])
    if value
    else None,
}


class Environment(str, Enum):
    LOCAL = "LOCAL"
    TESTING = "TESTING"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"

    @property
    def is_debug(self):
        return self in (self.LOCAL, self.STAGING, self.TESTING)

    @property
    def is_testing(self):
        return self == self.TESTING

    @property
    def is_deployed(self) -> bool:
        return self in (self.STAGING, self.PRODUCTION)
