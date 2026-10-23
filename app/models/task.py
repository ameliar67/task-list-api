from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from ..db import db
from datetime import datetime
from sqlalchemy import ForeignKey

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"))
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="tasks")

    def to_dict(self):
        task_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": bool(self.completed_at)
            }

        # Only add 'goal_id' if it is not None
        if self.goal_id is not None:
            task_dict["goal_id"] = self.goal_id

        return task_dict

    @classmethod
    def from_dict(cls, task_data):
        new_data = cls(
            title=task_data["title"],
            description=task_data["description"],
            completed_at = datetime.now() if task_data.get("is_complete") else None
        )
        return new_data