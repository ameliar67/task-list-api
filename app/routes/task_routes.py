from flask import Blueprint , abort , make_response, request, Response
from ..db import db
from app.models.task import Task
from app.routes.route_utilities import validate_model
from datetime import datetime

task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")

@task_bp.post("")
def create_new_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body:
        return {"details": "Invalid data"}, 400
    new_task = Task.from_dict(request_body)

    db.session.add(new_task)
    db.session.commit()
    return new_task.to_dict(), 201


@task_bp.get("")
def get_all_tasks():
    query = db.select(Task)
    title = request.args.get("title")

    if title:
        query = query.where(Task.title == title)

    description = request.args.get("description")
    if description:
        query = query.where(Task.description.ilike(f"%{description}%")) 

    is_complete = request.args.get("is_complete")
    if is_complete is not None:
        is_complete_bool = is_complete.lower() == "true"
        if is_complete_bool:
            query = query.where(Task.completed_at.is_not(None))
        else:
            query = query.where(Task.completed_at.is_(None))   

    sort_order = request.args.get("sort")
    if sort_order == "desc":
        query = query.order_by(Task.title.desc())
    elif sort_order == "asc":
        query = query.order_by(Task.title.asc())

    tasks = db.session.scalars(query)
    tasks_response = [task.to_dict() for task in tasks]
            
    return tasks_response, 200


@task_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task,task_id)

    return task.to_dict(),200


@task_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task,task_id)
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body:
        return {"details": "Invalid data"}, 400

    task.title = request_body["title"]
    if "is_complete" in request_body:
        is_complete = request_body["is_complete"]
        
        if is_complete:
            if not task.completed_at:
                task.completed_at = datetime.now()
        else:
            task.completed_at = None
    task.description = request_body["description"]
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@task_bp.delete("/<task_id>")
def delete_planet(task_id):
    task = validate_model(Task,task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@task_bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = datetime.now()
    db.session.commit()

    return Response(status=204)


@task_bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None
    db.session.commit()

    return Response(status=204)