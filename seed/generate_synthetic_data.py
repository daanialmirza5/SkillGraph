"""Generates the full synthetic dataset for SkillGraph: skills, roles, learning
resources, assessment questions, and 20 internally-consistent user profiles with
claimed skills, evidence, projects, career goals, assessment attempts,
recommendations, and audit events.

Run with: python -m seed.generate_synthetic_data
"""

from __future__ import annotations

import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "apps" / "api"))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.data.project_templates import PROJECT_TEMPLATES  # noqa: E402
from app.engines.gap_engine import compute_role_gap  # noqa: E402
from app.engines.recommendation_engine import recommend_project_for_role  # noqa: E402
from app.models import (  # noqa: E402
    AssessmentAttempt,
    AssessmentQuestion,
    AuditEvent,
    CareerGoal,
    Evidence,
    LearningResource,
    Profile,
    Project,
    ProjectSkill,
    Recommendation,
    Role,
    RoleSkill,
    Skill,
    SkillCategory,
    SkillRelationship,
    User,
    UserSkill,
)
from app.models.enums import EvidenceType, Importance, RelationshipType, UserRole, VerificationStatus  # noqa: E402

from seed.assessment_questions_data import ASSESSMENT_QUESTIONS  # noqa: E402
from seed.learning_resources_data import LEARNING_RESOURCES  # noqa: E402
from seed.personas import PERSONAS  # noqa: E402
from seed.roles_data import ROLES  # noqa: E402
from seed.skills_data import CATEGORIES, EXTRA_RELATIONSHIPS, SKILLS  # noqa: E402

random.seed(20260912)

DEMO_PASSWORD = "SkillGraph2026!"

FIRST_NAMES = [
    "Aayush", "Priya", "Jordan", "Maya", "Kenji", "Fatima", "Lucas", "Elena", "Omar", "Nadia",
    "Ethan", "Sofia", "Ravi", "Chloe", "Diego", "Amara", "Noah", "Yuki", "Isabel", "Malik",
]
LAST_NAMES = [
    "Sharma", "Patel", "Kim", "Chen", "Tanaka", "Hassan", "Silva", "Rossi", "Farouk", "Ivanova",
    "Brooks", "Costa", "Mehta", "Dubois", "Alvarez", "Okafor", "Bennett", "Sato", "Reyes", "Nasser",
]


def build_skill_lookup(session) -> dict[str, Skill]:
    return {s.name: s for s in session.query(Skill).all()}


def seed_taxonomy(session) -> None:
    print("Seeding skill taxonomy...")
    categories = {}
    for name in CATEGORIES:
        cat = SkillCategory(name=name, description=f"{name}-related skills.")
        session.add(cat)
        categories[name] = cat
    session.flush()

    skills_by_name: dict[str, Skill] = {}
    for name, category_name, description, aliases, _parent in SKILLS:
        skill = Skill(name=name, category_id=categories[category_name].id, description=description, aliases=aliases)
        session.add(skill)
        skills_by_name[name] = skill
    session.flush()

    for name, _category_name, _description, _aliases, parent_name in SKILLS:
        if parent_name:
            skills_by_name[name].parent_skill_id = skills_by_name[parent_name].id
            session.add(SkillRelationship(from_skill_id=skills_by_name[parent_name].id, to_skill_id=skills_by_name[name].id, relationship_type=RelationshipType.SUBSKILL_OF))

    for from_name, to_name, rel_type in EXTRA_RELATIONSHIPS:
        session.add(SkillRelationship(from_skill_id=skills_by_name[from_name].id, to_skill_id=skills_by_name[to_name].id, relationship_type=RelationshipType(rel_type)))

    session.commit()
    print(f"  {len(skills_by_name)} skills, {len(CATEGORIES)} categories.")


def seed_roles(session) -> None:
    print("Seeding role library...")
    skills_by_name = build_skill_lookup(session)
    for title, category, description, level, role_skills in ROLES:
        role = Role(title=title, category=category, description=description, level=level)
        session.add(role)
        session.flush()
        for skill_name, importance, min_score in role_skills:
            session.add(RoleSkill(role_id=role.id, skill_id=skills_by_name[skill_name].id, importance=Importance(importance), min_capability_score=min_score))
    session.commit()
    print(f"  {len(ROLES)} roles seeded.")


def seed_learning_resources(session) -> None:
    print("Seeding learning resources...")
    skills_by_name = build_skill_lookup(session)
    for skill_name, title, rtype, description, evidence_type, hours in LEARNING_RESOURCES:
        session.add(LearningResource(skill_id=skills_by_name[skill_name].id, title=title, type=rtype, description=description, produces_evidence_type=evidence_type, estimated_hours=hours))
    session.commit()
    print(f"  {len(LEARNING_RESOURCES)} learning resources seeded.")


def seed_assessment_questions(session) -> None:
    print("Seeding assessment question bank...")
    skills_by_name = build_skill_lookup(session)
    for skill_name, difficulty, question, options, correct, explanation in ASSESSMENT_QUESTIONS:
        session.add(AssessmentQuestion(skill_id=skills_by_name[skill_name].id, difficulty=difficulty, question=question, options=options, correct_answer=correct, explanation=explanation))
    session.commit()
    print(f"  {len(ASSESSMENT_QUESTIONS)} assessment questions seeded.")


def random_date_within(months_min: int, months_max: int) -> date:
    days = random.randint(months_min * 30, months_max * 30)
    return date.today() - timedelta(days=days)


def create_evidence_for_skill(session, user_id: int, skill: Skill, tier: str, project_id: int | None = None) -> Evidence:
    if tier == "strong":
        ev_type = random.choice([EvidenceType.PROJECT, EvidenceType.WORK_EXPERIENCE, EvidenceType.PROJECT])
        complexity = random.randint(4, 5)
        months_range = (0, 10)
        verification = random.choice([VerificationStatus.SELF_REPORTED, VerificationStatus.VERIFIED, VerificationStatus.SELF_REPORTED])
    else:  # developing
        ev_type = random.choice([EvidenceType.COURSE, EvidenceType.CERTIFICATION, EvidenceType.PROJECT])
        complexity = random.randint(2, 3)
        months_range = (8, 30)
        verification = random.choice([VerificationStatus.UNVERIFIED, VerificationStatus.SELF_REPORTED])

    ev = Evidence(
        user_id=user_id,
        skill_id=skill.id,
        type=ev_type,
        title=f"{ev_type.value.replace('_', ' ').title()}: {skill.name}",
        description=f"Synthetic {ev_type.value.lower()} evidence demonstrating {skill.name}.",
        date=random_date_within(*months_range),
        source="synthetic-seed",
        verification_status=verification,
        complexity=complexity,
        project_id=project_id if ev_type == EvidenceType.PROJECT else None,
    )
    session.add(ev)
    session.flush()
    session.add(AuditEvent(user_id=user_id, action="EVIDENCE_ADDED", entity_type="Evidence", entity_id=ev.id, new_value={"skill": skill.name, "type": ev_type.value}))
    return ev


def create_projects_for_persona(session, user_id: int, persona_skill_names: set[str], skills_by_name: dict[str, Skill]) -> list[Project]:
    matching_templates = [t for t in PROJECT_TEMPLATES if len(set(t["skills"]) & persona_skill_names) >= 2]
    if len(matching_templates) < 4:
        matching_templates = [t for t in PROJECT_TEMPLATES if set(t["skills"]) & persona_skill_names]
    chosen = random.sample(matching_templates, k=min(len(matching_templates), random.randint(5, 7)))

    projects = []
    for template in chosen:
        overlap_skills = [s for s in template["skills"] if s in skills_by_name]
        started = random_date_within(3, 20)
        project = Project(
            user_id=user_id,
            name=template["title"],
            description=template["description"],
            duration_months=random.randint(1, 4),
            technologies=overlap_skills,
            responsibilities="Designed, built, and shipped the system end to end.",
            outcomes="Delivered a working system demonstrating the listed skills.",
            complexity=random.randint(3, 5),
            is_production=random.random() > 0.6,
            started_on=started,
            completed_on=started + timedelta(days=30 * random.randint(1, 4)),
        )
        session.add(project)
        session.flush()
        for skill_name in overlap_skills:
            session.add(ProjectSkill(project_id=project.id, skill_id=skills_by_name[skill_name].id))
        session.add(AuditEvent(user_id=user_id, action="PROJECT_CREATED", entity_type="Project", entity_id=project.id, new_value={"name": project.name}))
        projects.append(project)
    return projects


def seed_users(session) -> list[User]:
    print("Seeding synthetic user profiles, projects, and evidence...")
    skills_by_name = build_skill_lookup(session)
    roles_by_title = {r.title: r for r in session.query(Role).all()}

    users = []
    name_idx = 0
    for persona in PERSONAS:
        for _ in range(2):  # 2 users per persona = 20 users
            first = FIRST_NAMES[name_idx]
            last = LAST_NAMES[name_idx]
            email = f"{first.lower()}.{last.lower()}@skillgraph.dev"
            user = User(email=email, name=f"{first} {last}", hashed_password=hash_password(DEMO_PASSWORD), role=UserRole.USER)
            session.add(user)
            session.flush()

            target_role = roles_by_title.get(persona["target_role"])
            profile = Profile(user_id=user.id, headline=persona["name"], bio=f"Synthetic profile modeling a {persona['name'].lower()} career trajectory.", persona=persona["key"], target_role_id=target_role.id if target_role else None, target_level="Mid", target_timeline_months=6)
            session.add(profile)

            all_persona_skills = set(persona["strong_skills"]) | set(persona["developing_skills"]) | set(persona["evidence_gap_skills"])
            for skill_name in all_persona_skills:
                session.add(UserSkill(user_id=user.id, skill_id=skills_by_name[skill_name].id, claimed=True))
            session.flush()

            projects = create_projects_for_persona(session, user.id, all_persona_skills, skills_by_name)
            project_by_skill: dict[str, int] = {}
            for project in projects:
                for tech in project.technologies:
                    project_by_skill.setdefault(tech, project.id)

            for skill_name in persona["strong_skills"]:
                for _ in range(random.randint(2, 4)):
                    create_evidence_for_skill(session, user.id, skills_by_name[skill_name], "strong", project_id=project_by_skill.get(skill_name))
            for skill_name in persona["developing_skills"]:
                create_evidence_for_skill(session, user.id, skills_by_name[skill_name], "developing", project_id=project_by_skill.get(skill_name))
            # evidence_gap_skills intentionally get NO evidence.

            session.commit()

            if target_role:
                gap_result = compute_role_gap(session, user.id, target_role.id)
                goal = CareerGoal(user_id=user.id, target_role_id=target_role.id, timeline_months=6, active=True, baseline_readiness=gap_result.readiness if gap_result else 0.0)
                session.add(goal)
                session.flush()
                session.add(AuditEvent(user_id=user.id, action="ROLE_SELECTED", entity_type="CareerGoal", entity_id=goal.id, new_value={"target_role_id": target_role.id, "baseline_readiness": goal.baseline_readiness}))
                session.commit()

            users.append(user)
            name_idx += 1

    admin = User(email="admin@skillgraph.dev", name="SkillGraph Admin", hashed_password=hash_password(DEMO_PASSWORD), role=UserRole.ADMIN)
    session.add(admin)
    session.flush()
    session.add(Profile(user_id=admin.id, headline="Platform Administrator"))
    session.commit()
    users.append(admin)

    print(f"  {len(users)} users seeded (20 personas + 1 admin). Demo password for all: {DEMO_PASSWORD}")
    return users


def seed_assessment_attempts(session, users: list[User]) -> None:
    print("Seeding a sample of assessment attempts...")
    questions_by_skill: dict[int, list[AssessmentQuestion]] = {}
    for q in session.query(AssessmentQuestion).all():
        questions_by_skill.setdefault(q.skill_id, []).append(q)

    count = 0
    for user in users[:12]:
        user_skills = session.query(UserSkill).filter(UserSkill.user_id == user.id).all()
        candidate_skill_ids = [us.skill_id for us in user_skills if us.skill_id in questions_by_skill]
        if not candidate_skill_ids:
            continue
        skill_id = random.choice(candidate_skill_ids)
        questions = questions_by_skill[skill_id]
        # Deterministic pseudo-performance: mostly correct for demo realism.
        answers = {}
        correct_count = 0
        for q in questions:
            if random.random() < 0.75:
                answers[q.id] = q.correct_answer
                correct_count += 1
            else:
                answers[q.id] = "incorrect-demo-answer"
        total = len(questions)
        became_evidence = (correct_count / total) >= 0.7 if total else False
        attempt = AssessmentAttempt(user_id=user.id, skill_id=skill_id, score=correct_count, total=total, answers={str(k): v for k, v in answers.items()}, became_evidence=became_evidence)
        session.add(attempt)
        session.flush()
        if became_evidence:
            skill = session.get(Skill, skill_id)
            session.add(Evidence(user_id=user.id, skill_id=skill_id, type=EvidenceType.ASSESSMENT, title=f"Verified assessment: {skill.name}", date=date.today(), verification_status=VerificationStatus.VERIFIED, complexity=3, source="synthetic-seed"))
        session.add(AuditEvent(user_id=user.id, action="ASSESSMENT_COMPLETED", entity_type="AssessmentAttempt", entity_id=attempt.id, new_value={"score": correct_count, "total": total}))
        count += 1
    session.commit()
    print(f"  {count} assessment attempts seeded.")


def seed_recommendations(session, users: list[User]) -> None:
    print("Seeding sample recommendations (human-in-the-loop demo states)...")
    demo_users = [u for u in users if u.profile and u.profile.target_role_id][:6]
    statuses_cycle = ["SUGGESTED", "ACCEPTED", "REJECTED", "SUGGESTED", "EDITED", "SUGGESTED"]
    count = 0
    for user, status in zip(demo_users, statuses_cycle):
        recs = recommend_project_for_role(session, user.id, user.profile.target_role_id, top_n=1)
        if not recs:
            continue
        r = recs[0]
        rec = Recommendation(user_id=user.id, type="PROJECT", title=r.title, description=r.description, reason=r.reason, target_skills=r.target_skill_names, target_role_id=user.profile.target_role_id, expected_gap_reduction=r.expected_gap_reduction, status=status)
        session.add(rec)
        session.flush()
        if status in ("ACCEPTED", "REJECTED"):
            action = "RECOMMENDATION_ACCEPTED" if status == "ACCEPTED" else "RECOMMENDATION_REJECTED"
            session.add(AuditEvent(user_id=user.id, action=action, entity_type="Recommendation", entity_id=rec.id, new_value={"status": status}))
        count += 1
    session.commit()
    print(f"  {count} recommendations seeded.")


def main() -> None:
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        if session.query(User).count() > 0:
            print("Database already contains users — skipping seed to avoid duplicates.")
            print("Delete skillgraph.db and re-run to reseed from scratch.")
            return

        seed_taxonomy(session)
        seed_roles(session)
        seed_learning_resources(session)
        seed_assessment_questions(session)
        users = seed_users(session)
        seed_assessment_attempts(session, users)
        seed_recommendations(session, users)

        skill_count = session.query(Skill).count()
        role_count = session.query(Role).count()
        project_count = session.query(Project).count()
        evidence_count = session.query(Evidence).count()
        print("\n=== SEED SUMMARY ===")
        print(f"Skills: {skill_count}")
        print(f"Roles: {role_count}")
        print(f"Users: {session.query(User).count()}")
        print(f"Projects: {project_count}")
        print(f"Evidence records: {evidence_count}")
        print(f"Learning resources: {session.query(LearningResource).count()}")
        print(f"Assessment questions: {session.query(AssessmentQuestion).count()}")
        print(f"Assessment attempts: {session.query(AssessmentAttempt).count()}")
        print(f"Recommendations: {session.query(Recommendation).count()}")
        print(f"Audit events: {session.query(AuditEvent).count()}")
        print(f"\nDemo login: any seeded email (e.g. {users[0].email}) / password: {DEMO_PASSWORD}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
