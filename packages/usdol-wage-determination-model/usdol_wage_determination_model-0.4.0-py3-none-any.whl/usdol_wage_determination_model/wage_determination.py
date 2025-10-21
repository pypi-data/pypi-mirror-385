from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, NonNegativeInt, model_validator

from .construction_type import ConstructionType
from .date_range import DateRange
from .job import Job
from .location import Location
from .wage import Wage


class WageDetermination(BaseModel):
    decision_number: Annotated[str, Field(pattern=r'^[A-Z]{2}[0-9]{8}$')]
    modification_number: NonNegativeInt
    publication_date: date
    effective: DateRange
    active: bool
    construction_type: ConstructionType
    location: Location
    rate_identifier: str
    survey_date: date
    job: Job
    wage: Wage = None
    notes: str = None

    @model_validator(mode='after')
    def validate_dates(self):
        if self.effective.start_date < self.publication_date:
            raise ValueError(f'Effective start date of {self.effective.start_date} cannot '
                             f'be before publication date of {self.publication_date}')
        if self.survey_date > self.publication_date:
            raise ValueError(f'Survey completion date of {self.survey_date} cannot '
                             f'be after publication date of {self.publication_date}')
        return self

    def model_dump_json(self, *args, **kwargs):
        if 'exclude_none' not in kwargs:
            kwargs['exclude_none'] = True
        return super().model_dump_json(*args, **kwargs)

    def model_dump_tuple(self, *args, **kwargs):
        return (
            self.decision_number,
            str(self.modification_number),
            self.publication_date.isoformat(),
            self.effective.start_date.isoformat(),
            self.effective.end_date.isoformat(),
            str(self.active),
            str(self.construction_type),
            self.location.state,
            self.location.county,
            str(self.location.zone.center.latitude) if self.location.zone else '',
            str(self.location.zone.center.longitude) if self.location.zone else '',
            str(self.location.zone.radius_min) if self.location.zone else '',
            str(self.location.zone.radius_max) if self.location.zone else '',
            self.survey_date.isoformat(),
            self.job.classification,
            self.job.subclassification,
            str(self.wage.currency) if self.wage else '',
            str(self.wage.rate) if self.wage else '',
            str(self.wage.fringe.fixed) if self.wage else '',
            str(self.wage.fringe.percentage) if self.wage else '',
            str(sorted(str(h) for h in self.wage.fringe.holidays)) if self.wage else '',
            self.notes if self.notes else '',
        )
