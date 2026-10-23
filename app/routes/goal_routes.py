from flask import Blueprint , abort , make_response, request, Response
from ..db import db
from app.models.goal import Goal
from app.models.task import Task
from app.routes.route_utilities import validate_model
from datetime import datetime

goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

@goal_bp.post("")
def create_new_goal():
    request_body = request.get_json()
    if "title" not in request_body:
        return {"details": "Invalid data"}, 400
    new_goal = Goal.from_dict(request_body)

    db.session.add(new_goal)
    db.session.commit()
    return new_goal.to_dict(), 201

@goal_bp.post("/<goal_id>/tasks")
def post_task_ids_to_goal(goal_id):

    request_body = request.get_json()

    goal = validate_model(Goal, goal_id)
    task_ids = request_body.get("task_ids", [])

    tasks = []
    for task_id in task_ids:
        task = validate_model(Task, task_id)
        tasks.append(task)

    goal.tasks = tasks
    db.session.commit()

    response_body = {
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks]
    }

    return response_body, 200


@goal_bp.get("")
def get_all_tasks():
    query = db.select(Goal)
    title = request.args.get("title")

    if title:
        query = query.where(Goal.title == title)  

    goals = db.session.scalars(query)
    tasks_response = [goal.to_dict() for goal in goals]
            
    return tasks_response, 200


@goal_bp.get("/<goal_id>")
def get_one_task(goal_id):
    task = validate_model(Goal,goal_id)

    return task.to_dict(),200

@goal_bp.get("/<goal_id>/tasks")
def get_tasks(goal_id):
    tasks = validate_model(Goal,goal_id)

    return tasks.to_dict(include_tasks=True), 200


@goal_bp.put("/<goal_id>")
def update_task(goal_id):
    goal = validate_model(Goal,goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@goal_bp.delete("/<goal_id>")
def delete_planet(goal_id):
    goal = validate_model(Goal,goal_id)
    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

