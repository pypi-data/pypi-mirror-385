import datetime

from dateutil import relativedelta
from collections import defaultdict

from sqlalchemy import func
from sqlalchemy.exc import DataError
from sqlalchemy.orm import aliased

from zou.app.models.day_off import DayOff
from zou.app.models.department import Department
from zou.app.models.project import Project
from zou.app.models.task import Task
from zou.app.models.task_type import TaskType
from zou.app.models.time_spent import TimeSpent
from zou.app.models.entity import Entity
from zou.app.models.entity_type import EntityType
from zou.app.models.person import Person

from zou.app.utils import fields, date_helpers

from zou.app.services import user_service, projects_service
from zou.app.services.exception import WrongDateFormatException


def get_time_spents_for_entity(entity_id):
    """
    Return all time spents related to given entity.
    """
    query = (
        TimeSpent.query.join(Task)
        .filter(Task.entity_id == entity_id)
        .order_by(TimeSpent.date.desc())
    )
    return TimeSpent.serialize_list(query.all())


def get_year_table(
    person_id=None, project_id=None, department_ids=None, studio_id=None
):
    """
    Return a table giving time spent by user and by month for given year.
    """
    return get_yearly_table(
        None,
        detail_level="year",
        person_id=person_id,
        project_id=project_id,
        department_ids=department_ids,
        studio_id=studio_id,
    )


def get_month_table(
    year, person_id=None, project_id=None, department_ids=None, studio_id=None
):
    """
    Return a table giving time spent by user and by month for given year.
    """
    return get_yearly_table(
        year,
        person_id=person_id,
        project_id=project_id,
        department_ids=department_ids,
        studio_id=studio_id,
    )


def get_week_table(
    year, person_id=None, project_id=None, department_ids=None, studio_id=None
):
    """
    Return a table giving time spent by user and by week for given year.
    """
    return get_yearly_table(
        year,
        "week",
        person_id=person_id,
        project_id=project_id,
        department_ids=department_ids,
        studio_id=studio_id,
    )


def get_day_table(
    year,
    month,
    person_id=None,
    project_id=None,
    department_ids=None,
    studio_id=None,
):
    """
    Return a table giving time spent by user and by day for given year and
    month.
    """
    time_spents = get_time_spents_for_month(
        year,
        month,
        person_id=person_id,
        project_id=project_id,
        department_ids=department_ids,
        studio_id=studio_id,
    )
    return get_table_from_time_spents(time_spents, "day")


def get_yearly_table(
    year=None,
    detail_level="month",
    person_id=None,
    project_id=None,
    department_ids=None,
    studio_id=None,
):
    """
    Return a table giving time spent by user and by week or month for given
    year. Week or month detail level can be selected through *detail_level*
    argument.
    """
    time_spents = get_time_spents_for_year(
        year=year,
        person_id=person_id,
        project_id=project_id,
        department_ids=department_ids,
        studio_id=studio_id,
    )
    return get_table_from_time_spents(time_spents, detail_level)


def get_time_spents_for_year(
    year=None,
    person_id=None,
    project_id=None,
    department_ids=None,
    studio_id=None,
):
    """
    Return all time spents for given year.
    """
    query = TimeSpent.query

    if person_id is not None:
        query = query.filter(TimeSpent.person_id == person_id)

    if year is not None:
        query = query.filter(
            TimeSpent.date.between(
                datetime.datetime(int(year), 1, 1),
                datetime.datetime(int(year), 12, 31),
            )
        )

    if project_id is not None or department_ids is not None:
        query = query.join(Task)

    if project_id is not None:
        if isinstance(project_id, list):
            query = query.filter(Task.project_id.in_(project_id))
        else:
            query = query.filter(Task.project_id == project_id)

    if department_ids:
        query = query.join(TaskType).filter(
            TaskType.department_id.in_(department_ids)
        )

    if studio_id is not None:
        query = query.join(Person, Person.id == TimeSpent.person_id).filter(
            Person.studio_id == studio_id
        )

    return query.all()


def get_time_spents_for_month(
    year,
    month,
    person_id=None,
    project_id=None,
    department_ids=None,
    studio_id=None,
):
    """
    Return all time spents for given month.
    """
    date = datetime.datetime(int(year), int(month), 1)
    next_month = date + relativedelta.relativedelta(months=1)
    query = TimeSpent.query.filter(TimeSpent.date >= date).filter(
        TimeSpent.date < next_month
    )

    if person_id is not None:
        query = query.filter(TimeSpent.person_id == person_id)

    if project_id is not None or department_ids is not None:
        query = query.join(Task)

    if project_id is not None:
        if isinstance(project_id, list):
            query = query.filter(Task.project_id.in_(project_id))
        else:
            query = query.filter(Task.project_id == project_id)

    if department_ids:
        query = query.join(TaskType).filter(
            TaskType.department_id.in_(department_ids)
        )

    if studio_id is not None:
        query = query.join(Person, Person.id == TimeSpent.person_id).filter(
            Person.studio_id == studio_id
        )

    return query.all()


def get_table_from_time_spents(time_spents, detail_level="month"):
    """
    Buid a time spent table based on given time spents and given level
    of detail (week, day or month).
    """
    result = {}
    for time_spent in time_spents:
        if detail_level == "week":
            unit = str(time_spent.date.isocalendar()[1])
        elif detail_level == "day":
            unit = str(time_spent.date.day)
        elif detail_level == "year":
            unit = str(time_spent.date.year)
        else:
            unit = str(time_spent.date.month)

        person_id = str(time_spent.person_id)
        if unit not in result:
            result[unit] = {}
        if person_id not in result[unit]:
            result[unit][person_id] = 0
        result[unit][person_id] += time_spent.duration
    return result


def get_time_spents(
    person_id, date=None, project_ids=None, department_ids=None
):
    """
    Return time spents for given person and date.
    """
    try:
        query = TimeSpent.query.filter_by(
            person_id=person_id, date=func.cast(date, TimeSpent.date.type)
        )

        if project_ids is not None or department_ids is not None:
            query = query.join(Task)

        if project_ids is not None:
            query = query.filter(Task.project_id.in_(project_ids))

        if department_ids:
            query = query.join(TaskType)
            query = query.filter(TaskType.department_id.in_(department_ids))
    except DataError:
        raise WrongDateFormatException
    return fields.serialize_list(query.all())


def get_time_spents_range(person_id, start_date, end_date):
    """
    Returns time spents for person and date range.
    """
    try:
        query = TimeSpent.query.filter_by(person_id=person_id)
        time_spents = query.filter(
            TimeSpent.date.between(
                func.cast(start_date, TimeSpent.date.type),
                func.cast(end_date, TimeSpent.date.type),
            )
        ).all()
    except DataError:
        raise WrongDateFormatException
    return fields.serialize_list(time_spents)


def get_time_spent(person_id, task_id, date):
    """
    Return time spent for given person, task and date.
    """
    try:
        time_spent = TimeSpent.query.filter_by(
            person_id=person_id,
            task_id=task_id,
            date=func.cast(date, TimeSpent.date.type),
        ).first()
    except DataError:
        raise WrongDateFormatException
    if time_spent is not None:
        return time_spent.serialize()
    else:
        return None


def get_day_off(person_id, date):
    """
    Return day off for given person and date.
    """
    try:
        day_off = DayOff.get_by(
            func.cast(date, DayOff.date.type).between(
                DayOff.date, DayOff.end_date
            ),
            person_id=person_id,
        )
    except DataError:
        raise WrongDateFormatException
    if day_off is not None:
        return day_off.serialize()
    else:
        return {}


def get_year_time_spents(
    person_id, year, project_id=None, department_ids=None
):
    """
    Return aggregated time spents at task level for given person and month.
    """
    start, end = date_helpers.get_year_interval(year)
    entries = get_person_time_spent_entries(
        person_id,
        TimeSpent.date >= func.cast(start, TimeSpent.date.type),
        TimeSpent.date < func.cast(end, TimeSpent.date.type),
        project_id=project_id,
        department_ids=department_ids,
    )
    return build_results(entries)


def get_month_time_spents(
    person_id, year, month, project_id=None, department_ids=None
):
    """
    Return aggregated time spents at task level for given person and month.
    """
    start, end = date_helpers.get_month_interval(year, month)
    entries = get_person_time_spent_entries(
        person_id,
        TimeSpent.date >= func.cast(start, TimeSpent.date.type),
        TimeSpent.date < func.cast(end, TimeSpent.date.type),
        project_id=project_id,
        department_ids=department_ids,
    )
    return build_results(entries)


def get_week_time_spents(
    person_id, year, week, project_id=None, department_ids=None
):
    """
    Return aggregated time spents at task level for given person and week.
    """
    start, end = date_helpers.get_week_interval(year, week)
    entries = get_person_time_spent_entries(
        person_id,
        TimeSpent.date >= func.cast(start, TimeSpent.date.type),
        TimeSpent.date < func.cast(end, TimeSpent.date.type),
        project_id=project_id,
        department_ids=department_ids,
    )
    return build_results(entries)


def get_day_time_spents(
    person_id, year, month, day, project_id=None, department_ids=None
):
    """
    Return aggregated time spents at task level for given person and day.
    """
    start, end = date_helpers.get_day_interval(year, month, day)
    entries = get_person_time_spent_entries(
        person_id,
        TimeSpent.date >= func.cast(start, TimeSpent.date.type),
        TimeSpent.date < func.cast(end, TimeSpent.date.type),
        project_id=project_id,
        department_ids=department_ids,
    )
    return build_results(entries)


def get_person_time_spent_entries(
    person_id, *args, project_id=None, department_ids=None
):
    """
    Return aggregated time spents at task level for given person and
    query filter (args).
    """
    Sequence = aliased(Entity, name="sequence")
    Episode = aliased(Entity, name="episode")
    query = (
        Task.query.with_entities(Task.id, Task.task_type_id)
        .join(Entity, Entity.id == Task.entity_id)
        .join(Project, Project.id == Task.project_id)
        .join(TimeSpent)
        .join(EntityType)
        .group_by(
            Task.id,
            Task.task_type_id,
            Project.id,
            Project.name,
            Entity.name,
            EntityType.name,
            Sequence.name,
            Episode.name,
        )
        .outerjoin(Sequence, Sequence.id == Entity.parent_id)
        .outerjoin(Episode, Episode.id == Sequence.parent_id)
        .filter(TimeSpent.person_id == person_id)
        .add_columns(
            Project.id,
            Project.name,
            Entity.name,
            EntityType.name,
            Sequence.name,
            Episode.name,
            func.sum(TimeSpent.duration),
        )
    )

    if project_id is not None:
        if isinstance(project_id, list):
            query = query.filter(Task.project_id.in_(project_id))
        else:
            query = query.filter(Task.project_id == project_id)

    if department_ids:
        query = query.join(TaskType, TaskType.id == Task.task_type_id).filter(
            TaskType.department_id.in_(department_ids)
        )

    for arg in args:
        query = query.filter(arg)

    return query.all()


def build_results(entries):
    """
    Build results with information to build a time sheet based on given entries
    (tasks + time spent duration aggregate)
    """
    result = []
    for (
        task_id,
        task_type_id,
        project_id,
        project_name,
        entity_name,
        entity_type_name,
        sequence_name,
        episode_name,
        duration,
    ) in entries:
        result.append(
            {
                "task_id": str(task_id),
                "task_type_id": str(task_type_id),
                "project_id": str(project_id),
                "project_name": project_name,
                "entity_name": entity_name,
                "entity_type_name": entity_type_name,
                "sequence_name": sequence_name,
                "episode_name": episode_name,
                "duration": duration,
            }
        )
    return result


def get_day_offs_for_month(year, month):
    """
    Get all day off entries for given year and month.
    """
    start, end = date_helpers.get_month_interval(year, month)
    return get_day_offs_between(start, end)


def get_person_day_offs_for_week(person_id, year, week):
    """
    Get all day off entries for given person, year and week.
    """
    start, end = date_helpers.get_week_interval(year, week)
    return get_day_offs_between(start, end, person_id=person_id)


def get_person_day_offs_for_month(person_id, year, month):
    """
    Get all day off entries for given person, year and week.
    """
    start, end = date_helpers.get_month_interval(year, month)
    return get_day_offs_between(start, end, person_id=person_id)


def get_person_day_offs_for_year(person_id, year):
    """
    Get all day off entries for given person, year.
    """
    start, end = date_helpers.get_year_interval(year)
    return get_day_offs_between(start, end, person_id=person_id)


def get_day_offs_between(
    start=None, end=None, person_id=None, exclude_id=None
):
    """
    Get all day off entries for given person, start and end date.
    """
    query = DayOff.query
    if person_id is not None:
        query = query.filter(DayOff.person_id == person_id)

    if start is not None:
        query = query.filter(
            func.cast(start, DayOff.end_date.type) <= DayOff.end_date
        )
    if end is not None:
        query = query.filter(func.cast(end, DayOff.date.type) >= DayOff.date)

    if exclude_id is not None:
        query = query.filter(DayOff.id != exclude_id)

    return DayOff.serialize_list(query.all())


def get_timezoned_interval(start, end):
    """
    Get time intervals adapted to the user timezone.
    """
    timezone = user_service.get_timezone()
    return date_helpers.get_timezoned_interval(start, end, timezone)


def get_project_month_time_spents(project_id, timezone=None):
    """
    Get aggregated time spents by department by person by month for given
    project.
    """
    data = {}
    query = (
        TimeSpent.query.join(Task)
        .join(TaskType, TaskType.id == Task.task_type_id)
        .join(Department, Department.id == TaskType.department_id)
        .filter(Task.project_id == project_id)
        .add_columns(Department.id)
        .order_by(TimeSpent.date)
    )

    for time_spent, department_id in query.all():
        date_key = date_helpers.get_simple_string_with_timezone_from_date(
            time_spent.date, timezone
        )[0:7]
        if department_id not in data:
            data[department_id] = {"total": 0}
        if time_spent.person_id not in data[department_id]:
            data[department_id][time_spent.person_id] = {"total": 0}
        if date_key not in data[department_id][time_spent.person_id]:
            data[department_id][time_spent.person_id][date_key] = 0

        data[department_id][time_spent.person_id][
            date_key
        ] += time_spent.duration
        data[department_id]["total"] += time_spent.duration
        data[department_id][time_spent.person_id][
            "total"
        ] += time_spent.duration
    return data


def get_project_task_type_time_spents(
    project_id, task_type_id, start_date, end_date
):
    """
    Returns time spents for project and task type in a date range.
    """
    try:
        query = TimeSpent.query.join(Task).filter(
            Task.project_id == project_id, Task.task_type_id == task_type_id
        )
        if start_date is not None:
            query = query.filter(
                TimeSpent.date >= func.cast(start_date, TimeSpent.date.type)
            )
        if end_date is not None:
            query = query.filter(
                TimeSpent.date <= func.cast(end_date, TimeSpent.date.type)
            )

        time_spents = query.order_by(TimeSpent.date.desc()).all()

        result = defaultdict(list)
        for ts in time_spents:
            result[str(ts.person_id)].append(ts.serialize())

    except DataError:
        raise WrongDateFormatException
    return dict(result)


def get_day_offs_between_for_project(
    project_id,
    start_date=None,
    end_date=None,
    safe=False,
    current_user_id=None,
):
    """
    Get all day off entries for project, start and end date.
    """
    project = projects_service.get_project(project_id, relations=True)
    try:
        query = DayOff.query.filter(DayOff.person_id.in_(project["team"]))
        if start_date is not None:
            query = query.filter(
                func.cast(start_date, DayOff.end_date.type) <= DayOff.end_date
            )
        if end_date is not None:
            query = query.filter(
                func.cast(end_date, DayOff.date.type) >= DayOff.date
            )

        days_offs = query.order_by(DayOff.date).all()

        result = defaultdict(list)
        for day_off in days_offs:
            day_off_person_id = str(day_off.person_id)
            result[day_off_person_id].append(
                day_off.serialize()()
                if safe or current_user_id == day_off_person_id
                else day_off.serialize_safe()
            )
    except DataError:
        raise WrongDateFormatException
    return dict(result)
