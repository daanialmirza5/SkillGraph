from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import Importance

if TYPE_CHECKING:
    from app.models.skill import Skill


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[str] = mapped_column(String(64), default="Mid")  # Entry, Mid, Senior


class RoleSkill(Base):
    __tablename__ = "role_skills"
    __table_args__ = (UniqueConstraint("role_id", "skill_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    importance: Mapped[Importance] = mapped_column(Enum(Importance), nullable=False)
    min_capability_score: Mapped[int] = mapped_column(Integer, default=40)  # 0-100 threshold

    skill: Mapped["Skill"] = relationship()
    role: Mapped["Role"] = relationship()
