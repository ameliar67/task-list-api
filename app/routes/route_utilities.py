from flask import abort, make_response
from ..db import db


def validate_model(cls,id):
    try:
        task_id = int(id)
    except:
        response = {"message": f"{cls.__name__} {id} invalid"}
        abort(make_response(response , 400))

    if not cls.title:
        response = {"message": f"{cls.__name__} {task_id} title required"}
        abort(make_response(response , 400))


    query = db.select(cls).where(cls.id == task_id)
    task = db.session.scalar(query)
    
    if not task:
        response = {"message": f"{cls.__name__} {task_id} not found"}
        abort(make_response(response, 404))

    return task

def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)
    except KeyError as e:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201

def get_filtered_tasks(cls, request):
    query = db.select(cls)
    title = request.args.get("title")

    if title:
        query = query.where(cls.title == title)

    description = request.args.get("description")
    if description:
        query = query.where(cls.description.ilike(f"%{description}%")) 

    is_complete = request.args.get("is_complete")
    if is_complete is not None:
        is_complete_bool = is_complete.lower() == "true"
        if is_complete_bool:
            query = query.where(cls.completed_at.is_not(None))
        else:
            query = query.where(cls.completed_at.is_(None))   

    sort_order = request.args.get("sort")
    if sort_order == "desc":
        query = query.order_by(cls.title.desc())
    elif sort_order == "asc":
        query = query.order_by(cls.title.asc())

    tasks = db.session.scalars(query)
    tasks_response = [task.to_dict() for task in tasks]
    return tasks_response