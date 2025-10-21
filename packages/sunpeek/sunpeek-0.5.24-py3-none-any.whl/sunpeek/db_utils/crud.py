from typing import Union
import datetime as dt

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, column, select
import sunpeek.components as cmp
from sunpeek.common.errors import SensorNotFoundError


def get_plants(session: Session,
               plant_id: int = None,
               plant_name: str = None,
               load_sensors: bool = False):
    """
    Gets a plant by name from the database, or all plants if no `plant_name` or `plant_id` parameter is supplied
    Parameters
    ----------
    session
    plant_id
    plant_name

    Returns
    -------
    common.components.Plant object, if `plant_name` or `plant_id` param is supplied, otherwise list of all
    common.components.Plant objects in the DB.
    """

    if load_sensors:
        stmt = select(cmp.Plant).options(joinedload(cmp.Plant.raw_sensors))
    else:
        stmt = select(cmp.Plant)

    if plant_id is not None:
        if load_sensors:
            return session.execute(stmt.filter(cmp.Plant.id == plant_id)).unique().scalar_one()
        return session.execute(stmt.filter(cmp.Plant.id == plant_id)).scalar_one()
    elif plant_name is not None:
        if load_sensors:
            return session.execute(stmt.filter(cmp.Plant.name == plant_name)).unique().scalar_one()
        return session.execute(stmt.filter(cmp.Plant.name == plant_name)).scalar_one()
    else:
        if load_sensors:
            return session.execute(stmt).unique().scalars().all()
        return session.execute(stmt).scalars().all()


def get_components(session: Session,
                   # component: Union[cmp.Component, cmp.Sensor, cmp.OperationalEvent, str],
                   component: Union['cmp.Component', 'cmp.Sensor', 'cmp.OperationalEvent', str],
                   id: int = None,
                   name: str = None,
                   plant_id: int = None,
                   plant_name: str = None,
                   attr = None):
    """
    Get a component, or list of components from the database.

    Parameters
    ----------
    session
    component: An instance of a subclass of cmp.Component
    id
    name
    plant_id
    plant_name

    Returns
    -------
    Component object, or list of Component objects
    """

    if isinstance(component, str):
        component = cmp.__dict__[component]

    stmt = select(component)

    if id is not None:
        obj = session.execute(stmt.filter(component.id == id)).scalar_one()
        if plant_id is not None and obj.plant_id != plant_id:
            raise SensorNotFoundError(
                f"{component.__name__} with id {id} has a plant_id that does not match the passed "
                f"plant_id. This means that the component is associated with a different plant or "
                f"no plant, probably an incorrect id or plant_id was passed.")
        return session.execute(stmt.filter(component.id == id)).scalar_one()

    # Apply plant filters BEFORE name filters to avoid MultipleResultsFound errors
    if plant_id is not None:
        stmt = stmt.filter(component.plant_id == plant_id)
    if plant_name is not None:
        stmt = stmt.join(cmp.Plant, component.plant_id == cmp.Plant.id).filter(cmp.Plant.name == plant_name)

    # Now apply name filters with the plant filters already in place
    if name is not None and component != cmp.Sensor:
        return session.execute(stmt.filter(component.name == name)).scalar_one()
    elif name is not None and component == cmp.Sensor:
        return session.execute(stmt.filter(component.raw_name == name)).scalar_one()

    return session.execute(stmt).scalars().all()


def get_sensors(session: Session, id: int = None, raw_name: str = None, plant_id: int = None, plant_name: str = None):
    """
    Get all sensors, all sensors of a given plant, or a specific sensor. Note, parameters have the following precedence:
    id, name, plant_id, plant_name. So if a component name is given, all further parameters are ignored

    Parameters
    ----------
    session
    id
    raw_name
    plant_id
    plant_name

    Returns
    -------
    Sensor object, or list of Sensor objects
    """

    return get_components(session, cmp.Sensor, id, raw_name, plant_id, plant_name)


def create_component(session: Session, component: cmp.Component, commit=True):
    """
    Add a new component to the database

    Parameters
    ----------
    session
    component: An instance of a subclass of cmp.Component
    commit: whether to commit the new components, if set to false, session.commit() must be called later.

    Returns
    -------
    The updated object after commit to the database. This may have had modifications made by database side logic.
    """
    session.add(component)
    if commit:
        session.commit()
    return component


def update_component(session: Session, component: cmp.helpers.ORMBase, commit=True):
    """Updates a component to the database.

    Parameters
    ----------
    session
    component: An instance of a subclass of cmp.Component
    commit: whether to commit the new components, if set to false, session.commit() must be called later.

    Returns
    -------
    The updated object after commit to the database. This may have had modifications made by database side logic.
    """
    session.add(component)
    if commit:
        session.commit()

    return component


def delete_component(session: Session, component: cmp.Component) -> None:
    """
    Removes a component from the database

    Parameters
    ----------
    session
    component: An instance of a subclass of cmp.Component

    Returns
    -------
    The updated object after commit to the database. This may have had modifications made by database side logic.
    """
    session.delete(component)
    session.commit()


def get_operational_events(session: Session, event_id=None, plant_id=None, search_start=None, search_end=None):
    if search_start is None and search_end is None:
        return get_components(session, cmp.OperationalEvent, id=event_id, plant_id=plant_id)

    if search_end is None:
        search_end = dt.datetime(9999, 1, 1, 0, 0)
    if search_start is None:
        search_end = dt.datetime(1900, 1, 1, 0, 0)

    stmt = select(cmp.OperationalEvent).join(cmp.Plant).where(cmp.Plant.id == plant_id).where(
        or_(
            and_(cmp.OperationalEvent.event_start >= search_start, cmp.OperationalEvent.event_start <= search_end),
            and_(cmp.OperationalEvent.event_end >= search_start, cmp.OperationalEvent.event_end <= search_end),
            and_(cmp.OperationalEvent.event_start <= search_end, cmp.OperationalEvent.event_end >= search_start)
        ))

    events = session.execute(stmt).scalars().all()

    return events
