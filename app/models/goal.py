from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db
from .task import Task

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    tasks: Mapped[list["Task"]] = relationship(back_populates="goal")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
        }

    def to_dict_with_tasks(self):
        goal_dict = self.to_dict()
        goal_dict["tasks"] = [task.to_dict() for task in self.tasks]

        return goal_dict

    @classmethod
    def from_dict(cls, goal_data):
        new_data = cls(
            title=goal_data["title"],
        )
        tasks = goal_data.get("tasks", [])
        if tasks:
            new_data.tasks = [Task.from_dict(task) for task in tasks]
        return new_data
