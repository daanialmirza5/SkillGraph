from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import AuditEvent, Project, ProjectSkill, Skill, User
from app.schemas.schemas import ProjectCreate, ProjectOut

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(
    limit: int = Query(default=100, le=500),
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Project]:
    return (
        db.query(Project)
        .filter(Project.user_id == user.id)
        .order_by(Project.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "NOT_FOUND", "message": "Project not found"}})
    return project


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Project:
    if payload.skill_ids:
        found = db.query(Skill.id).filter(Skill.id.in_(payload.skill_ids)).count()
        if found != len(set(payload.skill_ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": {"code": "INVALID_SKILL_ID", "message": "One or more skill_ids do not exist"}})

    project = Project(
        user_id=user.id,
        name=payload.name,
        description=payload.description,
        role_title=payload.role_title,
        duration_months=payload.duration_months,
        technologies=payload.technologies,
        responsibilities=payload.responsibilities,
        outcomes=payload.outcomes,
        repository_url=payload.repository_url,
        demo_url=payload.demo_url,
        complexity=payload.complexity,
        is_production=payload.is_production,
        started_on=payload.started_on,
        completed_on=payload.completed_on,
    )
    db.add(project)
    db.flush()
    for skill_id in set(payload.skill_ids):
        db.add(ProjectSkill(project_id=project.id, skill_id=skill_id))
    db.add(AuditEvent(user_id=user.id, action="PROJECT_CREATED", entity_type="Project", entity_id=project.id, new_value={"name": project.name}))
    db.commit()
    db.refresh(project)
    return project
