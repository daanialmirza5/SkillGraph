from sqlalchemy import Enum, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import RelationshipType


class SkillCategory(Base):
    __tablename__ = "skill_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("skill_categories.id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    parent_skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills.id"), nullable=True)

    category: Mapped["SkillCategory"] = relationship()
    parent: Mapped["Skill | None"] = relationship(remote_side=[id])


class SkillRelationship(Base):
    __tablename__ = "skill_relationships"
    __table_args__ = (UniqueConstraint("from_skill_id", "to_skill_id", "relationship_type"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    to_skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    relationship_type: Mapped[RelationshipType] = mapped_column(Enum(RelationshipType), nullable=False)

    from_skill: Mapped["Skill"] = relationship(foreign_keys=[from_skill_id])
    to_skill: Mapped["Skill"] = relationship(foreign_keys=[to_skill_id])


class UserSkill(Base):
    """A CLAIMED skill: the user states they have it. Evidence is tracked separately."""

    __tablename__ = "user_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    claimed: Mapped[bool] = mapped_column(default=True)

    skill: Mapped["Skill"] = relationship()
