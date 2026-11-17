from flask import Blueprint , abort , make_response, request, Response
from ..db import db
from app.models.task import Task
from app.routes.route_utilities import validate_model, create_model, get_filtered_tasks
from datetime import datetime
import os
import requests

task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")

@task_bp.post("")
def create_new_task():
    request_body = request.get_json()
    return create_model(Task, request_body)


@task_bp.get("")
def get_all_tasks():
    tasks_response = get_filtered_tasks(Task, request)
            
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
    send_message_to_slack(task_id)
    task.completed_at = datetime.now()
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@task_bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None
    db.session.commit()

    return Response(status=204, mimetype="application/json")

def send_message_to_slack(task_id):
    task = validate_model(Task,task_id)

    slack_token = os.environ.get('SLACK_TOKEN')
    if not slack_token:
        print("SLACK_TOKEN environment variable is missing!")
        return
    url = os.environ.get('SLACK_API_URL')
    payload = {
        "text": (f"Someone just completed the task {task.title}"),
        "channel": "task-notification"
    }
    headers = {
        "Authorization": f"Bearer {slack_token}"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    
        response_data = response.json()
        if response_data.get("ok"):
            print("Message sent successfully!")
        else:
            print(f"Slack API Error: {response_data.get('error')}")

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
            
    return Response(status=204, mimetype="application/json")