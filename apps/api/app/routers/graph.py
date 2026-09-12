from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.engines.graph_service import build_user_skill_graph
from app.models import Project, ProjectSkill, User

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("")
def get_graph(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Node/edge representation of the user's evidence graph for React Flow."""
    skill_graph = build_user_skill_graph(db, user.id)
    projects = db.query(Project).filter(Project.user_id == user.id).all()
    project_skills = db.query(ProjectSkill).join(Project).filter(Project.user_id == user.id).all()

    nodes = [{"id": "user", "type": "person", "label": user.name}]
    edges = []

    for entry in skill_graph.values():
        node_id = f"skill-{entry.skill.id}"
        nodes.append({
            "id": node_id, "type": "skill", "label": entry.skill.name, "category": entry.skill.category.name,
            "score": entry.capability.score, "level": entry.capability.level.value,
        })
        edges.append({"source": "user", "target": node_id, "type": "HAS_SKILL"})

    for project in projects:
        node_id = f"project-{project.id}"
        nodes.append({"id": node_id, "type": "project", "label": project.name})
        edges.append({"source": "user", "target": node_id, "type": "WORKED_ON"})

    for ps in project_skills:
        edges.append({"source": f"project-{ps.project_id}", "target": f"skill-{ps.skill_id}", "type": "DEMONSTRATED_BY"})

    return {"nodes": nodes, "edges": edges}
