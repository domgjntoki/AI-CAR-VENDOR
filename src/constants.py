from enum import Enum

DB_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

FILTER_MAPPING = {
    "brand": lambda col, value: col.in_(value),
    "model": lambda col, value: col.in_(value),
    "min_year": lambda col, value: col >= value,
    "max_year": lambda col, value: col <= value,
    "min_price": lambda col, value: col >= value,
    "max_price": lambda col, value: col <= value,
    "fuel_type": lambda col, value: col.in_(value),
    "color": lambda col, value: col.in_(value),
    "mileage": lambda col, value: col <= value,
    "doors": lambda col, value: col == value,
    "transmission": lambda col, value: col.in_(value),
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
