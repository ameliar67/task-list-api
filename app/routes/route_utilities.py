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