from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    tasks: Mapped[list["Task"]] = relationship(back_populates="goal")

    def to_dict(self, include_tasks=False):
        goal_dict = {
            "id": self.id,
            "title": self.title,
        }
        if include_tasks:
            goal_dict["tasks"] = [t.to_dict() for t in self.tasks]

        return goal_dict


    @classmethod
    def from_dict(cls, goal_data):
        new_data = cls(
            title=goal_data["title"],
        )
        tasks = goal_data.get("tasks", [])
        if tasks:
            new_data.tasks = tasks
        return new_data
