from decimal import Decimal
from typing import Annotated, Set

from pydantic import BaseModel, Field, model_validator
from pydantic_extra_types.currency_code import Currency

from .holiday import Holiday


class Fringe(BaseModel):
    fixed: Annotated[Decimal, Field(max_digits=6, decimal_places=3, ge=0.0)] = None
    percentage: Annotated[Decimal, Field(max_digits=4, decimal_places=3, ge=0.0)] = None
    holidays: Set[Holiday] = None

    @model_validator(mode='after')
    def validate_at_least_one_provided(self):
        if self.fixed is None and self.percentage is None:
            raise ValueError('At least one of fixed or percentage must be provided.')
        return self


class Wage(BaseModel):
    currency: Currency = 'USD'
    rate: Annotated[Decimal, Field(max_digits=6, decimal_places=3, ge=0.0)]
    fringe: Fringe
