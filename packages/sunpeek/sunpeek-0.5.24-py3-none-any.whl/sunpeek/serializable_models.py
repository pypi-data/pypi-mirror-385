import datetime as dt
import numpy as np
from dataclasses import field
import uuid
import enum
import json
from typing import Union, Any, Dict, List, Tuple

from pydantic.dataclasses import dataclass
from pydantic import field_validator, field_serializer, model_validator, Field
from typing import Annotated

import sunpeek.components as cmp
from sunpeek.common.errors import AlgorithmError
from sunpeek.common.unit_uncertainty import Q, parse_quantity
from sunpeek.components.helpers import SensorMap, DatetimeTemplates, AccuracyClass, InstallCondition, AlgoCheckMode, \
    IsVirtual
from sunpeek.components.fluids import UninitialisedFluid
from sunpeek.base_model import BaseModel, Quantity
from sunpeek.components.types import Collector as ORMCollector
from sunpeek.components.types import ApertureParameters


class ComponentBase(BaseModel):
    sensor_map: Dict[str, str | None] | None = None

    @field_validator('sensor_map', mode='before')
    @classmethod
    def get_raw_name(cls, v):
        out = {}
        for key, item in v.items():
            if isinstance(item, SensorMap):
                try:
                    out[key] = item.sensor.raw_name
                except AttributeError:
                    pass
            else:
                out[key] = item
        return out


class SensorTypeValidator(BaseModel):
    name: str
    compatible_unit_str: str
    description: str
    # min_limit: Quantity | None
    # max_limit: Quantity | None
    # # non_neg: bool
    # max_fill_period: dt.datetime | None
    # sensor_hangs_period: dt.datetime | None
    # # high_maxerr_const: Quantity | None
    # # high_maxerr_perc: Quantity | None
    # # medium_maxerr_const: Quantity | None
    # # medium_maxerr_perc: Quantity | None
    # # low_maxerr_const: Quantity | None
    # # low_maxerr_perc: Quantity | None
    # # standard_install_maxerr_const: Quantity | None
    # # standard_install_maxerr_perc: Quantity | None
    # # poor_install_maxerr_const: Quantity | None
    # # poor_install_maxerr_perc: Quantity | None
    info_checks: dict | None
    max_fill_period: dt.datetime | None
    sensor_hangs_period: dt.datetime | None
    lower_replace_min: Quantity | None
    lower_replace_max: Quantity | None
    lower_replace_value: Quantity | None
    upper_replace_min: Quantity | None
    upper_replace_max: Quantity | None
    upper_replace_value: Quantity | None
    # equation: str | None
    common_units: list | None


class IAM_Method(BaseModel):
    method_type: str


class IAM_ASHRAE(IAM_Method):
    method_type: str = 'IAM_ASHRAE'
    b: Quantity


class IAM_K50(IAM_Method):
    method_type: str = 'IAM_K50'
    k50: Quantity


class IAM_Ambrosetti(IAM_Method):
    method_type: str = 'IAM_Ambrosetti'
    kappa: Quantity


class IAM_Interpolated(IAM_Method):
    method_type: str = 'IAM_Interpolated'
    aoi_reference: Quantity
    iam_reference: Quantity


class CollectorBase(BaseModel):
    name: str
    test_reference_area: str | None = Field(...)
    test_type: str | None = None
    gross_length: Quantity | None = None
    iam_method: IAM_K50 | IAM_ASHRAE | IAM_Ambrosetti | IAM_Interpolated | None = None
    manufacturer_name: str | None = None
    product_name: str | None = None
    test_report_id: str | None = None
    licence_number: str | None = None
    certificate_date_issued: dt.datetime | str | None = None
    certificate_lab: str | None = None
    certificate_details: str | None = None
    collector_type: str
    area_gr: Quantity | None = None
    area_ap: Quantity | None = None
    gross_width: Quantity | None = None
    gross_height: Quantity | None = None
    a1: Quantity | None = Field(...)
    a2: Quantity | None = Field(...)
    a5: Quantity | None = None
    a8: Quantity | None = None
    kd: Quantity | None = None
    eta0b: Quantity | None = None
    eta0hem: Quantity | None = None
    f_prime: Quantity | None = None
    concentration_ratio: Quantity | None = None
    calculation_info: Dict[str, str] | None = None
    aperture_parameters: ApertureParameters | None = None

    @field_validator('certificate_date_issued', mode='before')
    @classmethod
    def parse_certificate_date(cls, v):
        """Convert datetime strings to datetime objects for database compatibility."""
        if v is None or isinstance(v, dt.datetime):
            return v
        if isinstance(v, str):
            try:
                return dt.datetime.fromisoformat(v.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return v
        return v


class CollectorUpdate(CollectorBase):
    name: str | None = None
    collector_type: str | None = None


class Collector(CollectorBase):
    id: int | None = None
    name: str | None = None

    def __str__(self):
        return f'{self.__class__.__name__} {self.name}'

    def __repr__(self):
        return self.__str__()

    @field_validator('a1', 'a2', 'a5', 'a8', 'kd', 'eta0b', 'eta0hem', 'f_prime', 'concentration_ratio', mode='before')
    @classmethod
    def to_default_unit(cls, val, info):
        # Convert collector performance parameters to default unit -> easier to get unified display in web-ui
        if val is None:
            return None
        default_unit = ORMCollector.get_default_unit(info.field_name)
        val = parse_quantity(val).to(default_unit)
        return val
        # return Quantity.from_orm(val)

    @field_validator('aperture_parameters', mode='before')
    @classmethod
    def to_default_unit__aperture(cls, val):
        # Convert collector aperture_parameters to default unit -> easier to get unified display in web-ui
        if val is None:
            return None
        for k, v in val.items():
            if v is None:
                val[k] = None
            else:
                default_unit = ORMCollector.get_default_unit(k)
                val[k] = parse_quantity(v).to(default_unit)
                # val[k] = Quantity.from_orm(parse_quantity(v).to(default_unit))

        return val


class CollectorQDT(CollectorBase):
    a1: Quantity
    a2: Quantity
    a5: Quantity
    a8: Quantity | None = None


class CollectorSST(CollectorBase):
    ceff: Quantity


class SensorBase(BaseModel):
    description: str | None = None
    accuracy_class: AccuracyClass | None = None
    installation_condition: InstallCondition | None = None
    info: dict | None = {}
    raw_name: str | None = None
    native_unit: str | None = None
    sensor_type: str | None = None

    @field_validator('info', mode='before')
    @classmethod
    def convert_info(cls, v):
        if isinstance(v, cmp.SensorInfo):
            return v._info
        return v

    @field_validator('native_unit', mode='before')
    @classmethod
    def check_unit(cls, v):
        if isinstance(v, str):
            Q(1, v)

        return v


class Sensor(SensorBase):
    id: int | None = None
    plant_id: int | None = None
    raw_name: str | None = None
    sensor_type: str | None = None
    native_unit: str | None = None
    formatted_unit: str | None = None
    is_virtual: bool | None = None
    can_calculate: bool | None = None
    is_mapped: bool | None = None
    is_infos_set: bool | None = None

    @field_validator('sensor_type', mode='before')
    @classmethod
    def convert_sensor_type(cls, v):
        if isinstance(v, cmp.SensorType):
            return v.name
        return v


class NewSensor(SensorBase):
    raw_name: str
    native_unit: str | None = None


class BulkUpdateSensor(Sensor):
    id: int


class FluidDefinition(BaseModel):
    id: int | None = None
    model_type: str
    name: str
    manufacturer: str | None = None
    description: str | None = None
    is_pure: bool
    dm_model_sha1: str | None = None
    hc_model_sha1: str | None = None
    heat_capacity_unit_te: str | None = None
    heat_capacity_unit_out: str | None = None
    heat_capacity_unit_c: str | None = None
    density_unit_te: str | None = None
    density_unit_out: str | None = None
    density_unit_c: str | None = None
    # heat_capacity_onnx: str | None
    # density_onnx: str | None

    # @validator('heat_capacity_onnx', 'density_onnx', pre=True)
    # def onnx_to_str(cls, v):
    #     try:
    #         return v.hex()
    #     except AttributeError:
    #         return v


class Fluid(BaseModel):
    id: int | None = None
    name: str | None = None
    manufacturer_name: str | None = None
    product_name: str | None = None
    fluid: FluidDefinition
    concentration: Quantity | None = None


class FluidSummary(BaseModel):
    name: str | None = None
    fluid: str
    concentration: Quantity | None = None

    @field_validator('fluid', mode='before')
    @classmethod
    def fluid_name(cls, v):
        try:
            return v.name
        except AttributeError:
            return v

    @field_validator('concentration', mode='before')
    @classmethod
    def handle_empty_string_for_concentration(cls, v):
        if v == "":
            return None
        return v


class FluidExport(BaseModel):
    fluid: str
    concentration: Union[Quantity, None]

    @field_validator('fluid', mode='before')
    @classmethod
    def fluid_name(cls, v):
        try:
            return v.name
        except AttributeError:
            return v


class Array(ComponentBase):
    id: int | None = None
    plant_id: int | None = None
    name: str | None = None
    collector: str | None = Field(...)
    area_gr: Quantity | None = None
    area_ap: Quantity | None = None
    azim: Quantity | None = Field(...)
    tilt: Quantity | None = Field(...)
    row_spacing: Quantity | None = None
    n_rows: Quantity | None = None
    ground_tilt: Quantity | None = None
    mounting_level: Quantity | None = None
    fluidvol_total: Quantity | None = None
    rho_ground: Quantity | None = None
    rho_colbackside: Quantity | None = None
    rho_colsurface: Quantity | None = None
    max_aoi_shadow: Quantity | None = None
    min_elevation_shadow: Quantity | None = None

    @field_validator('collector', mode='before')
    @classmethod
    def convert_coll(cls, v):
        if isinstance(v, cmp.Collector):
            if v.name is None:
                return 'unnamed collector'
            else:
                return v.name
        return v

    def __str__(self):
        return f'{self.__class__.__name__} {self.name}'

    def __repr__(self):
        return self.__str__()


class NewArray(Array):
    name: str
    collector: str
    sensors: Dict[str, NewSensor] | None = None
    sensor_map: dict | None = None


class ArrayUpdate(Array):
    collector: str | None = None
    azim: Quantity | None = None
    tilt: Quantity | None = None


class ArrayExport(Array):
    @field_validator('sensor_map')
    @classmethod
    def remove_mapped_virtuals(cls, val):
        return {slot: s for slot, s in val.items() if not '__virtual__' in s}


class DataUploadDefaults(BaseModel):
    id: int | None = None
    datetime_template: DatetimeTemplates | None = None
    datetime_format: str | None = None
    timezone: str | None = None
    csv_separator: str | None = None
    csv_decimal: str | None = None
    csv_encoding: str | None = None
    index_col: int | None = None

    def as_serializable_dict(self):
        return json.loads(self.model_dump_json())


class OperationalEventExport(BaseModel):
    """
    Timestamps are exported as timezone-aware UTC datetime objects (e.g. 2024-01-01T07:00:00+00:00).
    All input datetimes must be timezone-aware.
    """
    # Timestamps are exported as UTC naive datetimes, seems to be the least problematic.
    # Conversion back to timezone aware datetimes is handled in ORM class OperationalEvent.
    event_start: dt.datetime
    event_end: dt.datetime | None = None
    ignored_range: bool = False
    description: str | None = None

    @field_validator("event_start", "event_end", mode='before')
    @classmethod
    def to_utc(cls, v):
        """Ensure all datetimes are timezone-aware and converted to UTC.
        """
        # if v is not None and v.tzinfo is not None:
        #     v = v.astimezone(dt.timezone.utc).replace(tzinfo=None)
        # return v
        if v is None:
            return v
        if isinstance(v, str):
            try:
                v = dt.datetime.fromisoformat(v)
            except ValueError:
                raise ValueError(f"Invalid datetime format: {v!r}. Expected datetime or ISO 8601 string.")
        if not isinstance(v, dt.datetime):
            raise ValueError("Expected datetime or ISO 8601 string.")
        if v.tzinfo is None or v.utcoffset() is None:
            raise ValueError("Datetime must be timezone-aware.")
        return v.astimezone(dt.timezone.utc)

    @field_serializer("event_start", "event_end")
    def serialize_datetime(self, value: dt.datetime | None) -> str | None:
        """Serialize datetimes using '+00:00' format instead of 'Z' for consistency."""
        if value is None:
            return None
        # Use isoformat() which produces '+00:00' format for UTC
        return value.isoformat()

    @classmethod
    def from_orm(cls, obj):
        """Build from ORM and return a JSON-serializable dict (datetimes / enums handled by Pydantic).
        This keeps FastAPI out of core code while letting tests do `json=config`.
        """
        model = super().model_validate(obj)
        return json.loads(model.model_dump_json(exclude_unset=True))

    @classmethod
    def from_any(cls, item):
        """Accept ORM instance, dict, or already-correct pydantic model and return a plain dict for export."""
        if item is None:
            return None
        if isinstance(item, cls):
            return item.model_dump(mode='json', exclude_unset=True)
        if isinstance(item, dict):
            return item
        return cls.from_orm(item)

    @classmethod
    def many_from_any(cls, seq):
        """Accept list, possibly nested one level (e.g. [events] instead of events), and coerce to list[dict]."""
        if seq is None:
            return []
        # Flatten one level if someone passed [events] instead of events
        if isinstance(seq, list) and len(seq) == 1 and isinstance(seq[0], list):
            seq = seq[0]
        out = []
        for it in seq:
            d = cls.from_any(it)
            if d is not None:
                out.append(d)
        return out


class PlantBase(ComponentBase):
    latitude: Quantity | None = Field(...)
    longitude: Quantity | None = Field(...)
    owner: str | None = None
    operator: str | None = None
    description: str | None = None
    location_name: str | None = None
    elevation: Quantity | None = None
    fluid_solar: FluidSummary | str | None = None
    arrays: List[Array] | None = None
    fluidvol_total: Quantity | None = None
    raw_sensors: List[Sensor] | None = None

    @field_validator('fluid_solar', mode='before')
    @classmethod
    def convert_fluid(cls, v):
        if isinstance(v, cmp.Fluid):
            if isinstance(v, UninitialisedFluid):
                return FluidSummary(name=v.fluid_def_name, fluid=v.fluid_def_name, concentration=None)
            return FluidSummary(name=v.name, fluid=v.fluid.name, concentration=getattr(v, 'concentration', None))
        return v


class OperationalEventForPlant(BaseModel):
    """
    Operational event representation for Plant API responses.
    Returns timezone-naive timestamps in plant's local timezone.
    """
    event_start: dt.datetime  # timezone-naive in plant's local timezone
    event_end: dt.datetime | None = None
    timezone: str  # plant.local_tz_string_with_DST
    ignored_range: bool = False
    description: str | None = None


class Plant(PlantBase):
    name: str
    id: int | None = None
    local_tz_string_with_DST: str | None = None
    tz_data_offset: float | None = None
    data_upload_defaults: DataUploadDefaults | None = None
    operational_events: List[OperationalEventForPlant] | None = None
    virtuals_calculation_uptodate: bool | None = None

    @field_validator('operational_events', mode='before')
    @classmethod
    def convert_operational_events_to_local_timezone(cls, v, info):
        """Convert operational events from ORM/Export format to API response format with timezone-naive timestamps."""
        if v is None or not v:
            return v

        # Get plant's local timezone from validation context
        # The plant object should be in info.data
        plant_data = info.data if hasattr(info, 'data') else {}
        tz_string = plant_data.get('local_tz_string_with_DST')

        if tz_string is None:
            # This will happen during initial validation - we'll get tz_string from the ORM object
            # Try to get it from the first event's plant if it's an ORM object
            if v and hasattr(v[0], 'plant') and hasattr(v[0].plant, 'local_tz_string_with_DST'):
                tz_string = v[0].plant.local_tz_string_with_DST

        if tz_string is None:
            from sunpeek.common.errors import TimeZoneError
            raise TimeZoneError(
                'Plant latitude and longitude must be set to determine local timezone for operational events.'
            )

        import pytz
        tz = pytz.timezone(tz_string)

        result = []
        for event in v:
            # Handle ORM objects
            if hasattr(event, 'event_start') and hasattr(event, 'plant'):
                event_start = event.event_start.astimezone(tz).replace(tzinfo=None) if event.event_start else None
                event_end = event.event_end.astimezone(tz).replace(tzinfo=None) if event.event_end else None

                result.append(OperationalEventForPlant(
                    event_start=event_start,
                    event_end=event_end,
                    timezone=tz_string,
                    description=event.description,
                    ignored_range=event.ignored_range,
                ))
            # Handle dicts (already validated)
            elif isinstance(event, dict):
                # If it's already in the correct format, keep it
                if 'timezone' in event and isinstance(event.get('event_start'), dt.datetime):
                    if event['event_start'].tzinfo is None:
                        # Already naive, just pass through
                        result.append(event)
                        continue

                # It might be an Export format (timezone-aware UTC) - convert it
                event_start_utc = event.get('event_start')
                event_end_utc = event.get('event_end')

                if isinstance(event_start_utc, str):
                    event_start_utc = dt.datetime.fromisoformat(event_start_utc)
                if isinstance(event_end_utc, str):
                    event_end_utc = dt.datetime.fromisoformat(event_end_utc) if event_end_utc else None

                # Convert from UTC to local timezone and make naive
                if event_start_utc and event_start_utc.tzinfo:
                    event_start = event_start_utc.astimezone(tz).replace(tzinfo=None)
                else:
                    event_start = event_start_utc

                if event_end_utc and event_end_utc.tzinfo:
                    event_end = event_end_utc.astimezone(tz).replace(tzinfo=None)
                else:
                    event_end = event_end_utc

                result.append(OperationalEventForPlant(
                    event_start=event_start,
                    event_end=event_end,
                    timezone=tz_string,
                    description=event.get('description'),
                    ignored_range=event.get('ignored_range', False),
                ))
            else:
                # Pydantic model - convert similarly
                result.append(event)

        return result

    def __str__(self):
        return f'{self.__class__.__name__} {self.name}'

    def __repr__(self):
        return self.__str__()


class UpdatePlant(PlantBase):
    name: str | None = None
    sensors: Dict[str, NewSensor] | None = None
    latitude: Quantity | None = None
    longitude: Quantity | None = None
    fluid_solar: FluidSummary | str | None = None
    data_upload_defaults: DataUploadDefaults | None = None
    operational_events: List[OperationalEventExport] | None = None


class NewPlant(PlantBase):
    name: str
    latitude: Quantity
    longitude: Quantity
    fluid_solar: FluidSummary | None = None
    raw_sensors: List[NewSensor] | None = None
    sensor_map: dict | None = None


class PlantExport(PlantBase):
    name: str | None = None
    latitude: Quantity | None = None
    longitude: Quantity | None = None
    local_tz_string_with_DST: str | None = None
    tz_data_offset: float | None = None
    data_upload_defaults: DataUploadDefaults | None = None
    operational_events: List[OperationalEventExport] | None = None
    arrays: List[ArrayExport | None] = []
    fluid_solar: FluidExport | None = None

    @field_validator('raw_sensors')
    @classmethod
    def replace_raw_sensors(cls, val):
        try:
            return [sensor for sensor in val if not sensor['is_virtual']]
        except TypeError:
            return [sensor for sensor in val if not sensor.is_virtual]

    @field_validator('sensor_map')
    @classmethod
    def remove_mapped_virtuals(cls, val):
        return {slot: s for slot, s in val.items() if not '__virtual__' in s}

    @field_validator("operational_events", mode='before')
    @classmethod
    def _normalize_events(cls, v):
        return OperationalEventExport.many_from_any(v)


class PlantImported(BaseModel):
    # response model for /plants/import
    plant: Plant
    new_collectors: List[Collector]
    new_fluid_definitions: List[FluidDefinition | None]


class PlantSummaryBase(BaseModel):
    name: str | None = None
    owner: str | None = None
    operator: str | None = None
    description: str | None = None
    location_name: str | None = None
    latitude: Quantity | None = None
    longitude: Quantity | None = None
    elevation: Quantity | None = None


class PlantSummary(PlantSummaryBase):
    id: int
    name: str
    virtuals_calculation_uptodate: bool | None = None


class PlantDataStartEnd(BaseModel):
    start: dt.datetime | None = None
    end: dt.datetime | None = None


class PlantTimezone(BaseModel):
    timezone: str | None = None
    tz_data_offset: float | None = None


class OperationalEvent(BaseModel):
    """
    For API responses: Returns timezone-naive timestamps in plant's local timezone.
    Timestamps are converted from UTC to the plant's local timezone (plant.local_tz_string_with_DST)
    and returned without timezone information, along with the timezone string.
    """
    id: int | None = None
    plant: Union[str, PlantSummary]
    event_start: dt.datetime  # timezone-naive in plant's local timezone
    event_end: dt.datetime | None = None
    timezone: str  # plant.local_tz_string_with_DST
    ignored_range: bool = False
    description: str | None = None

    @model_validator(mode='before')
    @classmethod
    def extract_from_orm(cls, data):
        """Handle conversion from ORM OperationalEvent to timezone-naive timestamps in plant's local timezone."""
        # If it's already a dict (e.g., from API input), pass through
        if isinstance(data, dict):
            return data

        # If it's an ORM object, convert timestamps
        if hasattr(data, 'event_start') and hasattr(data, 'plant'):
            # Get plant's local timezone
            tz_string = data.plant.local_tz_string_with_DST

            if tz_string is None:
                from sunpeek.common.errors import TimeZoneError
                raise TimeZoneError(
                    'Plant latitude and longitude must be set to determine local timezone for operational events.'
                )

            import pytz
            tz = pytz.timezone(tz_string)

            # Convert timestamps from UTC to plant's local timezone and make naive
            event_start = data.event_start.astimezone(tz).replace(tzinfo=None) if data.event_start else None
            event_end = data.event_end.astimezone(tz).replace(tzinfo=None) if data.event_end else None

            return {
                'id': data.id,
                'plant': data.plant,
                'event_start': event_start,
                'event_end': event_end,
                'timezone': tz_string,
                'description': data.description,
                'ignored_range': data.ignored_range,
            }

        return data


class UpdateOperationalEvent(BaseModel):
    """
    Model for updating an operational event. All fields are optional.
    Timestamps can be either:
    - Timezone-aware (e.g., "2024-01-01T10:00:00+01:00")
    - Timezone-naive with timezone field (e.g., "2024-01-01T10:00:00" + timezone="Europe/Vienna")
    """
    event_start: dt.datetime | None = None
    event_end: dt.datetime | None = None
    timezone: str | None = None
    description: str | None = None
    ignored_range: bool | None = None

    @field_validator("event_start", "event_end", mode='before')
    @classmethod
    def parse_datetime(cls, v):
        """Parse datetime strings to datetime objects (accept both aware and naive)."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                v = dt.datetime.fromisoformat(v)
            except ValueError:
                raise ValueError(f"Invalid datetime format: {v!r}. Expected datetime or ISO 8601 string.")
        if not isinstance(v, dt.datetime):
            raise ValueError("Expected datetime or ISO 8601 string.")
        return v

    @model_validator(mode='after')
    def validate_naive_timestamps_have_timezone(self):
        """Ensure timezone-naive timestamps are accompanied by a timezone field."""
        # Check event_start
        if self.event_start is not None:
            if self.event_start.tzinfo is None or self.event_start.utcoffset() is None:
                # Naive timestamp - must have timezone field
                if self.timezone is None:
                    raise ValueError(
                        "Timezone-naive timestamp for 'event_start' requires 'timezone' field. "
                        "Either provide a timezone-aware timestamp (e.g., '2024-01-01T10:00:00+01:00') "
                        "or include the 'timezone' field (e.g., timezone='Europe/Vienna')."
                    )

        # Check event_end
        if self.event_end is not None:
            if self.event_end.tzinfo is None or self.event_end.utcoffset() is None:
                # Naive timestamp - must have timezone field
                if self.timezone is None:
                    raise ValueError(
                        "Timezone-naive timestamp for 'event_end' requires 'timezone' field. "
                        "Either provide a timezone-aware timestamp (e.g., '2024-01-01T10:00:00+01:00') "
                        "or include the 'timezone' field (e.g., timezone='Europe/Vienna')."
                    )

        return self


class Error(BaseModel):
    error: str
    message: str
    detail: str


class Job(BaseModel):
    id: uuid.UUID
    status: cmp.helpers.ResultStatus
    result_url: str | None = None
    plant: str | None = None

    @field_validator('plant', mode='before')
    @classmethod
    def plant_to_str(cls, v):
        if v is not None:
            return v.name


class JobReference(BaseModel):
    job_id: uuid.UUID
    href: str

    @field_validator('job_id')
    @classmethod
    def uuid_to_str(cls, v):
        if v is not None:
            return str(v)


class ConfigExport(BaseModel):
    collectors: List[Collector]
    fluid_definitions: List[FluidDefinition | None]
    plant: PlantExport
    data_upload_defaults: DataUploadDefaults | None = None
    operational_events: List[OperationalEventExport]

    @field_validator("operational_events", mode='before')
    @classmethod
    def _coerce_operational_events(cls, v):
        return OperationalEventExport.many_from_any(v)

    @classmethod
    def _remove_ids(cls, item):
        if hasattr(item, 'id'):
            del item.id
        if hasattr(item, 'plant_id'):
            del item.plant_id
        if isinstance(item, BaseModel):
            for atr, val in item.__dict__.items():
                if isinstance(val, list):
                    item.__dict__[atr] = [cls._remove_ids(val_i) for val_i in val]
                else:
                    item.__dict__[atr] = cls._remove_ids(val)
        return item

    @model_validator(mode='after')
    def _exclude_id(self):
        self.collectors = [self._remove_ids(col) for col in self.collectors]
        self.fluid_definitions = [self._remove_ids(f_def) for f_def in self._remove_ids(self.fluid_definitions)]
        self.plant = self._remove_ids(self.plant)
        self.data_upload_defaults = self._remove_ids(self.data_upload_defaults)
        return self

    @field_validator("operational_events", mode='before')
    @classmethod
    def _normalize_events(cls, v):
        return OperationalEventExport.many_from_any(v)


class ConfigImport(BaseModel):
    collectors: List[Collector] = []
    fluid_definitions: List[FluidDefinition | None] = []
    plant: NewPlant
    data_upload_defaults: DataUploadDefaults | None = None
    operational_events: List[OperationalEventExport | None] = []


class SensorSlotValidator(BaseModel):
    """
    A pydantic class used to hold and validate information on a component sensor slot.

    Parameters
    ----------
    name : str
        The name of the slot, which behaves like a component attribute and can be used to access the mapped sensor from
        the component. e.g. te_amb. `name` only needs to be unique and understandable in the context of a specific
        component, e.g. the `tp` slot of a plant includes the total power of all arrays, whereas `tp` of an array is
        just that array's power.
    descriptive_name : str
        A longer more descriptive name, e.g. for display to a user in a front end client. Limited to 24 characters
    description : str
        A description of the purpose and use of the slot.
    virtual : enum
        Whether the sensor for a slot is always virtual, can be virtual given certain conditions, or is never virtual
    """

    name: str
    sensor_type: Union[str, SensorTypeValidator]
    descriptive_name: Annotated[str, Field(max_length=57)]
    virtual: IsVirtual
    description: str | None = None


## Power Check Method -----------------------

class PowerCheckOutputPlant(BaseModel):
    id: int | None = None
    plant: Plant

    n_intervals: int | None = None
    total_interval_length: Union[dt.timedelta, None] = None
    datetime_intervals_start: Union[List[dt.datetime], None] = None
    datetime_intervals_end: Union[List[dt.datetime], None] = None

    tp_measured: Quantity | None = None
    tp_sp_measured: Quantity | None = None
    tp_sp_estimated: Quantity | None = None
    tp_sp_estimated_safety: Quantity | None = None
    mean_tp_sp_measured: Quantity | None = None
    mean_tp_sp_estimated: Quantity | None = None
    mean_tp_sp_estimated_safety: Quantity | None = None

    target_actual_slope: Quantity | None = None
    target_actual_slope_safety: Quantity | None = None

    fluid_solar: FluidSummary | None = None
    mean_temperature: Quantity | None = None
    mean_fluid_density: Quantity | None = None
    mean_fluid_heat_capacity: Quantity | None = None

    @field_validator('datetime_intervals_start', 'datetime_intervals_end', mode='before')
    @classmethod
    def array_to_list(cls, val):
        if isinstance(val, np.ndarray):
            return list(val)


class PowerCheckOutputData(BaseModel):
    id: int | None = None

    te_amb: Quantity | None = None
    te_in: Quantity | None = None
    te_out: Quantity | None = None
    te_op: Quantity | None = None
    te_op_deriv: Quantity | None = None

    aoi: Quantity | None = None
    iam_b: Quantity | None = None
    ve_wind: Quantity | None = None

    rd_gti: Quantity | None = None
    rd_bti: Quantity | None = None
    rd_dti: Quantity | None = None


class PowerCheckOutputArray(BaseModel):
    id: int | None = None
    array: Array
    data: PowerCheckOutputData | None = None

    tp_sp_measured: Quantity | None = None
    tp_sp_estimated: Quantity | None = None
    tp_sp_estimated_safety: Quantity | None = None
    mean_tp_sp_measured: Quantity | None = None
    mean_tp_sp_estimated: Quantity | None = None
    mean_tp_sp_estimated_safety: Quantity | None = None


class PowerCheckOutput(BaseModel):
    id: int | None = None
    plant: PlantSummary

    datetime_eval_start: dt.datetime
    datetime_eval_end: dt.datetime

    # Algorithm settings
    # pc_method_name: str
    method_name: str
    evaluation_mode: str
    formula: int
    wind_used: bool

    # Results
    settings: Dict[str, Any]  # Type checking done in PowerCheckSettings
    plant_output: PowerCheckOutputPlant
    array_output: List[PowerCheckOutputArray]


class PowerCheckSettings(BaseModel):
    """Settings for Power Check evaluation.

    Time-related fields (interval_length, max_gap_in_interval) are specified in seconds.
    """
    safety_uncertainty: Union[float, None] = None
    safety_pipes: Union[float, None] = None
    safety_others: Union[float, None] = None
    evaluation_mode: str | None = None
    formula: int | None = None
    wind_used: bool | None = None
    interval_length: int | None = None  # seconds
    max_nan_density: float | None = None
    min_data_in_interval: int | None = None
    max_gap_in_interval: int | None = None  # seconds
    min_intervals_in_output: int | None = None

    @field_validator('interval_length', 'max_gap_in_interval', 'min_data_in_interval', 'min_intervals_in_output')
    @classmethod
    def validate_non_negative_int(cls, v, info):
        """Validate that integer fields are non-negative when provided."""
        if v is not None and v < 0:
            raise ValueError(f'{info.field_name} must be non-negative (>= 0), got {v}')
        return v

    @field_validator('max_nan_density')
    @classmethod
    def validate_max_nan_density(cls, v):
        """Validate that max_nan_density is between 0.0 and 1.0 when provided."""
        if v is not None:
            if v < 0.0:
                raise ValueError(f'max_nan_density must be non-negative (>= 0.0), got {v}')
            if v > 1.0:
                raise ValueError(f'max_nan_density must be at most 1.0, got {v}')
        return v


# def dataclass_to_pydantic(cls: dataclasses.dataclass, name: str) -> BaseModel:
#     # get attribute names and types from dataclass into pydantic format
#     pydantic_field_kwargs = dict()
#     for _field in dataclasses.fields(cls):
#         # check is field has default value
#         if isinstance(_field.default, dataclasses._MISSING_TYPE):
#             # no default
#             default = ...
#         else:
#             default = _field.default
#
#         try:
#             for i, typ in enumerate(_field.type.__args__):
#
#         except AttributeError:
#             pass
#
#         pydantic_field_kwargs[ _field.name] = (_field.type, default)
#
#     return pydantic.create_model(name, **pydantic_field_kwargs, __base__=BaseModel)


class ProblemType(str, enum.Enum):
    component_slot = 'Component slot'
    real_sensor_missing = 'Real sensor'
    virtual_sensor_missing = 'Virtual sensor'
    real_or_virtual_sensor_missing = 'Real or virtual sensor'
    component_attrib = 'Component attribute problem'
    fluid_missing = 'Fluid missing'
    collector_missing = 'Collector missing'
    collector_type = 'Wrong collector type'
    collector_param = 'Invalid collector parameter'
    sensor_info = 'Sensor info problem'
    component_missing = 'Component missing'
    other_problem = 'Unspecified problem'
    unexpected_in_calc = 'Unexpected calculation error'
    unexpected_getting_problems = 'Unexpected error getting problem report'


@dataclass
class CoreProblem:
    """A class used to hold information on a problem / missing info for a calculation / CoreStrategy.
    Can be used to track problems / missing information back to the root cause.

    Parameters
    ----------
    problem_type : ProblemType enum
    affected_component : Plant, Array, Collector, optional
        The component where some problem occurs / information is missing.
    affected_item_name : str, optional
        Typically the name of the affected sensor slot or attribute of the affected component.
    description : str, optional
    """
    problem_type: ProblemType
    affected_component: Union[Plant, Array, Collector, None] = None
    affected_item_name: str | None = None
    description: str | None = None

    # def __init__(self, problem_type, affected_component=None, affected_item_name=None, description=None):
    #     # Defining an explicit init because affected_component got silently cast into the wrong serializable model.
    #     self.problem_type = problem_type
    #     self.affected_item_name = affected_item_name
    #     self.description = description
    #
    #     if affected_component is None:
    #         self.affected_component = None
    #         return
    #
    #     if isinstance(affected_component, sunpeek.components.physical.Plant):
    #         self.affected_component = Plant.from_orm(affected_component)
    #     elif isinstance(affected_component, sunpeek.components.physical.Array):
    #         self.affected_component = Array.from_orm(affected_component)
    #     elif isinstance(affected_component, sunpeek.components.types.Collector):
    #         self.affected_component = Collector.from_orm(affected_component)
    #     else:
    #         raise ValueError(f'Unexpected component: Expected ORM Plant, Array or Collector, '
    #                          f'got {type(affected_component)}.')


@dataclass
class CoreMethodFeedback:
    """Standardized reporting of problems / missing information required to perform some calculation.

    This applies to all calculations in SunPeek, i.e. both virtual sensors and other calculations e.g. Power Check.
    Any CoreStrategy and CoreAlgorithm holds / can return a CoreMethodFeedback which holds structured information as to
    what problems / missing information there is that prevents the strategy / algo to complete.

    CoreMethodFeedback implements an n-level tree, where each node (CoreMethodFeedback) has n leaves (own_feedback)
    and points at m other nodes (sub_feedback). sub_feedback is implemented as dict with key == strategy name.

    Parameters
    ----------
    success : bool, optional, default True
        True if the algo or strategy holding / producing the problem report is successful, meaning that at least
        parts of its results can be calculated and / or only optional information is missing.
    own_feedback : List[AlgoProblem], optional
        List of reported problems that affect the algo / strategy itself (as opposed to problems coming from called /
        sub algorithms). Example: Strategy needs some component attribute, but that attribute is None.
    sub_feedback : Dict[str, CoreMethodFeedback], optional
        Problems that are not directly associated to the algo / strategy holding this CoreMethodFeedback, but rather
        stem from a previous calculation / strategy. Example: Strategy needs some virtual sensor, but that had its own
        problems, reported as a CoreMethodFeedback.
    virtuals_feedback : Dict[Tuple[Any, str], 'CoreMethodFeedback']
        Problems arising from virtual sensors. These are kept separate from sub_feedback because the same virtual sensor
        report might appear in several locations of the problem tree, but should only be parsed once.
    problem_slots : List[str], optional
        Set by virtual sensor strategies, problem_slots can be used to report partial success, i.e.:
        If a strategy is successful for some but not all virtual sensors, the success flag can be set to True,
        and the CoreMethodFeedback applies only to the virtual sensor slot names which cannot be calculated,
        i.e. the problem_slots.
    """
    success: bool | None = True
    own_feedback: Union[List[CoreProblem], None] = None
    sub_feedback: Union[Dict[str, 'CoreMethodFeedback'], None] = None
    virtuals_feedback: Union[Dict[Tuple[Any, str], 'CoreMethodFeedback'], None] = None
    problem_slots: Union[List[str], None] = field(default_factory=list)  # Used if some virtual sensors / slots fail

    @property
    def successful_strategy_str(self) -> str | None:
        """Loop through strategies, return name of first successful strategy, or None if no strategy was successful.
        """
        if not self.success:
            return None
        for strategy_name, feedback in self.sub_feedback.items():
            if feedback.success:
                return strategy_name
        return None

    @staticmethod
    def get_virtual_state(component, slot_name) -> IsVirtual:
        try:
            is_virtual = component.sensor_slots[slot_name].virtual
        except KeyError:
            raise AlgorithmError(f'Error adding AlgoProblem: '
                                 f'Component slot {slot_name} not found in component {component}.')
        return is_virtual

    @staticmethod
    def _cname(component: cmp.Component) -> str:
        """Return verbose component name with class + name.
        """
        class_name = component.__class__.__name__.lower()
        if isinstance(component, cmp.Plant):
            return class_name
        return f'{class_name} "{component.name}"'

    def add_own(self, feedback: CoreProblem | List[CoreProblem]) -> None:
        """Add "leaf" to problem tree: add 1 or more AlgoProblems to report.
        """
        if feedback is None:
            return
        lst = self.own_feedback or []
        if not isinstance(feedback, list):
            feedback = [feedback]
        lst.extend(feedback)
        self.own_feedback = lst
        self.success = False

    def add_virtual(self, component: cmp.Component, slot_name: str, feedback: 'CoreMethodFeedback') -> None:
        """Add subtree of virtual sensor problems to `self.virtuals_reports`.
        """
        self.virtuals_feedback = self.virtuals_feedback or {}
        self.virtuals_feedback[(component, slot_name)] = feedback

    def add_sub(self, strategy_name: str, feedback: 'CoreMethodFeedback') -> None:
        """Add subtree to problem tree: Add 1 CoreMethodFeedback subtree.
        """
        self.sub_feedback = self.sub_feedback or {}
        self.sub_feedback[strategy_name] = feedback
        self.success = False

    def add_missing_component(self, component: cmp.Component,
                              missing_component_class_name: str,
                              description: str) -> None:
        """Add a "missing component" AlgoProblem as own problem.
        """
        algo_problem = CoreProblem(ProblemType.component_missing, component, missing_component_class_name, description)
        self.add_own(algo_problem)

    def add_missing_sensor(self, component: cmp.Component,
                           slot_name: str,
                           check_mode: AlgoCheckMode,
                           # enforce_real: bool = False
                           ) -> None:
        """Add a "missing sensor" AlgoProblem as own problem.
        """
        is_virtual = self.get_virtual_state(component, slot_name)
        if is_virtual is IsVirtual.never:
            self.add_missing_real_sensor(component, slot_name)
            return

        if is_virtual is IsVirtual.always:
            problem_type = ProblemType.virtual_sensor_missing
            description = (f'"{component.sensor_slots[slot_name].descriptive_name}" '
                           f'({slot_name}) in {self._cname(component)}: '
                           f'Virtual sensor calculation failed.')

        elif is_virtual is IsVirtual.possible:
            problem_type = ProblemType.real_or_virtual_sensor_missing
            description = (f'"{component.sensor_slots[slot_name].descriptive_name}" ({slot_name}) '
                           f'in {self._cname(component)}: '
                           f'Sensor missing or virtual sensor calculation failed.')
        else:
            raise ValueError(f'Unexpected IsVirtual value of slot {slot_name}: "{is_virtual}". '
                             f'Expected one of {", ".join(list(IsVirtual))}')

        self.add_own(CoreProblem(problem_type, component, slot_name, description))

        s = getattr(component, slot_name)
        if s is None or not s.is_virtual:
            return

        # If virtual sensor for which calculation failed: Add subtree to problem tree
        if check_mode is None:
            raise AlgorithmError(f'Input "check_mode" required to treat a virtual sensor in problem reporting.')
        add_vsensor = ((check_mode == AlgoCheckMode.config_and_data) or
                       (check_mode == AlgoCheckMode.config_only and s._problems is not None))
        if add_vsensor:
            self.add_virtual(component, slot_name, s.problems)

    def add_missing_real_sensor(self, component: cmp.Component,
                                slot_name: str,
                                # description: str = None,
                                ) -> None:
        """Add a "missing real sensor" AlgoProblem as own problem.
        """
        if IsVirtual.always == self.get_virtual_state(component, slot_name):
            raise ValueError(f'Component slot {slot_name} in {component.name} can never be real. '
                             f'This is an internal SunPeek error. Please report it.')

        description = (f'"{component.sensor_slots[slot_name].descriptive_name}" '
                       f'({slot_name}) in {self._cname(component)}: '
                       f'Sensor missing.')

        self.add_own(CoreProblem(ProblemType.real_sensor_missing, component, slot_name, description))

    def add_missing_sensor_info(self, component: cmp.Component, slot_name: str = None,
                                info_name: str = None, description: str = None) -> None:
        """Add a "missing fluid" AlgoProblem as own problem.
        """
        if description is None:
            if info_name is None:
                raise AlgorithmError(f'"info_name" required to generate missing sensor info description.')
            description = (f'Sensor info "{info_name}" missing for sensor '
                           f'"{component.sensors[slot_name].raw_name}" '
                           f'({slot_name} in {self._cname(component)}). '
                           f'This can be fixed on the Sensor Details page.')
        algo_problem = CoreProblem(ProblemType.sensor_info, component, slot_name, description)
        self.add_own(algo_problem)

    def add_missing_attrib(self, component: Union[cmp.Component, cmp.Collector],
                           attrib_name: str, description: str = None) -> None:
        """Add a "missing attribute" AlgoProblem as own problem.
        """
        description = (f'Missing information "{attrib_name}" in {self._cname(component)}. '
                       f'{"" if description is None else description}')
        algo_problem = CoreProblem(ProblemType.component_slot, component, attrib_name, description)
        self.add_own(algo_problem)

    def add_zero_collector_param(self, component: cmp.Collector,
                                 attrib_name: str) -> None:
        """Add a "component_attrib" AlgoProblem as own problem, for collector parameters that should be nonzero.
        """
        description = (f'Collector parameter "{attrib_name}" is None or zero but is required to be nonzero.'
                       f'in {self._cname(component)}.')
        algo_problem = CoreProblem(ProblemType.collector_param, component, attrib_name, description)
        self.add_own(algo_problem)

    def add_nonzero_collector_param(self, component: cmp.Collector,
                                    attrib_name: str) -> None:
        """Add a "component_attrib" AlgoProblem as own problem, for collector parameters that should be zero.
        """
        description = (f'Collector parameter "{attrib_name}" is nonzero but is required to be zero, '
                       f'in {self._cname(component)}.')
        algo_problem = CoreProblem(ProblemType.collector_param, component, attrib_name, description)
        self.add_own(algo_problem)

    def add_missing_collector(self, component: cmp.Component, slot_name: str) -> None:
        """Add a "missing collector" AlgoProblem as own problem.
        """
        description = (f'"{slot_name}" in {self._cname(component)}: '
                       f'Collector is missing (None) or invalid (UninitialisedCollector). '
                       f'In case you defined a collector, this is an internal SunPeek error. Please report it.')
        algo_problem = CoreProblem(ProblemType.component_missing, component, slot_name, description)
        self.add_own(algo_problem)

    def add_wrong_collector_type(self, component: cmp.Collector,
                                 expected: cmp.CollectorTypes | List[cmp.CollectorTypes],
                                 received: cmp.CollectorTypes) -> None:
        """Add a "wrong collector type" AlgoProblem as own problem.
        """
        expected = expected if isinstance(expected, list) else [expected]
        expected = [x.value if isinstance(x, enum.Enum) else x for x in expected]
        received = received.value if isinstance(received, enum.Enum) else received
        description = (f'Wrong collector type: '
                       f'Expected a collector of type {" or ".join(expected)}, '
                       f'but received "{received}".')
        algo_problem = CoreProblem(ProblemType.collector_type, component, '', description)
        self.add_own(algo_problem)

    def add_missing_fluid(self, component: cmp.Component, slot_name: str) -> None:
        """Add a "missing fluid" AlgoProblem as own problem.
        """
        description = (f'"{slot_name}" in {self._cname(component)}: '
                       f'Fluid is missing (None) or invalid (UninitialisedFluid). '
                       f'In case you defined a fluid, this is an internal SunPeek error. Please report it.')
        algo_problem = CoreProblem(ProblemType.fluid_missing, component, slot_name, description)
        self.add_own(algo_problem)

    def add_generic_slot_problem(self, component: cmp.Component, description: str) -> None:
        """Add a generic ProblemType.component_slot AlgoProblem as own problem
        """
        self.add_own(CoreProblem(ProblemType.component_slot, component, description=description))

    def parse(self,
              include_successful_strategies: bool = False,
              include_problem_slots: bool = True,
              ) -> str:
        """Parse CoreMethodFeedback into single string. Includes virtual sensors as sub-report.
        """
        main_report = self.to_tree(include_successful_strategies, include_problem_slots).parse()
        virtuals_root = self.virtuals_to_tree(include_successful_strategies)
        virtuals = '' if virtuals_root.is_leaf else f'\nVirtual Sensors:\n{virtuals_root.parse(node_whitespace=False)}'

        return main_report + virtuals

    def to_tree(self, include_successful_strategies: bool, include_problem_slots: bool = True) -> 'TreeNode':
        """Return the root node representing the CoreMethodFeedback as an n-tree. Virtual sensor problems are left out.
        """
        root_node = TreeNode()
        # Add own problems as children leaves
        if self.own_feedback is not None:
            for algo_problem in self.own_feedback:
                root_node.add(TreeNode(algo_problem.description))
        # Add sub_feedback as children nodes
        if self.sub_feedback is not None:
            for k, v in self.sub_feedback.items():
                include_slots = v.problem_slots and include_problem_slots
                skip = v.success and not include_successful_strategies and not include_slots
                if skip:
                    continue
                if not v.success:
                    root_node.add(TreeNode(k, v.to_tree(include_successful_strategies, include_problem_slots).children))
                    continue
                if not v.problem_slots:
                    root_node.add(TreeNode(k, [TreeNode('No problems found.')]))
                else:  # partial success, some virtual sensors missing
                    message = f'Some virtual sensors could not be calculated: {", ".join(self.problem_slots)}. {k}'
                    root_node.add(
                        TreeNode(message, v.to_tree(include_successful_strategies, include_problem_slots).children))

        return root_node

    def virtuals_to_tree(self, include_successful_strategies: bool) -> 'TreeNode':
        """Return the root node representing the virtual sensor ProblemReports as an n-tree.
        """
        virtuals_feedback = self.collect_virtuals_feedback()
        root_node = TreeNode()
        if not virtuals_feedback:
            return root_node

        for k, v in virtuals_feedback.items():
            component, slot = k
            message = (f'"{component.sensor_slots[slot].descriptive_name}" '
                       f'({slot}) in {self._cname(component)}: '
                       f'Virtual sensor calculation failed. Details:')
            root_node.add(TreeNode(message, v.to_tree(include_successful_strategies).children))

        return root_node

    def collect_virtuals_feedback(self) -> Dict[Tuple[Any, str], 'CoreMethodFeedback']:
        """Recursively collect all virtual sensor feedback in CoreMethodFeedback, avoiding duplicate entries.
        """
        v_feedback = {}
        # Collect own virtual sensor report
        if self.virtuals_feedback is not None:
            v_feedback.update(self.virtuals_feedback)
        # Collect virtual sensor report in sub-strategies
        if self.sub_feedback is not None:
            for sub_report in self.sub_feedback.values():
                v_feedback.update(sub_report.collect_virtuals_feedback())

        return v_feedback


class TreeNode:
    """n-tree, consisting of structural information (nodes, leaves) and string messages.
    """

    def __init__(self, message: str = '', children: List['TreeNode'] = None):
        self.message = message
        self.children = children or []

    def add(self, child: 'TreeNode'):
        self.children.append(child)

    @property
    def is_leaf(self) -> bool:
        return not bool(self.children)

    def parse(self, level: int = -1, node_whitespace: bool = True) -> str:
        """Return string representation of the tree.
        """
        output = ''
        indentation = '  ' * level
        if self.message:
            bullet = '-' if self.is_leaf else ">"
            newline = f'\n' if node_whitespace and not self.is_leaf else ''
            output += f'{newline}{indentation}{bullet} {self.message}\n'
        for child in self.children:
            output += child.parse(level + 1, node_whitespace=node_whitespace)
        return output


# Goal = Report success / problems of a specific Power Check strategy.
@dataclass
class PowerCheckFeedback:
    evaluation_mode: str
    formula: int
    wind_used: bool
    success: bool
    problem_str: str
