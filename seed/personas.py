"""Persona definitions used to generate internally-consistent synthetic profiles.

Each persona lists:
  strong_skills   -> claimed, multiple pieces of recent, higher-complexity evidence
  developing_skills -> claimed, one or two weaker/older evidence items
  evidence_gap_skills -> claimed with ZERO evidence (demonstrates the evidence-gap concept)
  target_role    -> the role title this persona's career goal points at
"""

PERSONAS = [
    {
        "key": "frontend_focused",
        "name": "Frontend-focused Engineer",
        "strong_skills": ["JavaScript", "React", "CSS", "HTML", "TypeScript"],
        "developing_skills": ["Next.js", "State Management", "Web Accessibility", "REST APIs"],
        "evidence_gap_skills": ["Cloud Architecture", "Docker"],
        "target_role": "Frontend Engineer",
    },
    {
        "key": "backend_focused",
        "name": "Backend-focused Engineer",
        "strong_skills": ["Python", "SQL", "REST APIs", "PostgreSQL", "FastAPI"],
        "developing_skills": ["System Design", "Docker", "Caching Strategies"],
        "evidence_gap_skills": ["Kubernetes", "MLOps"],
        "target_role": "Backend Engineer",
    },
    {
        "key": "ai_focused",
        "name": "AI-focused Engineer",
        "strong_skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "Statistics"],
        "developing_skills": ["MLOps", "Docker", "Natural Language Processing"],
        "evidence_gap_skills": ["Kubernetes", "Cloud Architecture"],
        "target_role": "AI/ML Engineer",
    },
    {
        "key": "data_focused",
        "name": "Data-focused Engineer",
        "strong_skills": ["SQL", "Python", "ETL Pipelines", "Data Warehousing", "Data Modeling"],
        "developing_skills": ["Apache Spark", "Statistics", "Data Visualization"],
        "evidence_gap_skills": ["Machine Learning", "Cloud Architecture"],
        "target_role": "Data Engineer",
    },
    {
        "key": "devops_focused",
        "name": "DevOps-focused Engineer",
        "strong_skills": ["Docker", "Kubernetes", "CI/CD", "Linux Administration", "Infrastructure as Code"],
        "developing_skills": ["Terraform", "Monitoring & Observability", "Cloud Architecture"],
        "evidence_gap_skills": ["Python", "Machine Learning"],
        "target_role": "DevOps Engineer",
    },
    {
        "key": "cybersecurity_focused",
        "name": "Cybersecurity-focused Engineer",
        "strong_skills": ["Application Security", "OWASP Top 10", "Network Security", "Threat Modeling"],
        "developing_skills": ["Penetration Testing", "Cryptography", "Cloud Security"],
        "evidence_gap_skills": ["Python", "Cloud Architecture"],
        "target_role": "Security Engineer",
    },
    {
        "key": "student",
        "name": "Student",
        "strong_skills": ["Python", "Data Structures", "Algorithms"],
        "developing_skills": ["SQL", "Version Control (Git)", "Machine Learning"],
        "evidence_gap_skills": ["Docker", "Cloud Architecture", "System Design"],
        "target_role": "Software Engineer (Generalist)",
    },
    {
        "key": "career_switcher",
        "name": "Career Switcher (into Data)",
        "strong_skills": ["SQL", "Data Analysis", "Data Visualization"],
        "developing_skills": ["Python", "Statistics"],
        "evidence_gap_skills": ["Machine Learning", "Data Engineering", "Cloud Architecture"],
        "target_role": "Data Analyst",
    },
    {
        "key": "early_career",
        "name": "Early-career Engineer",
        "strong_skills": ["Python", "JavaScript", "REST APIs", "Version Control (Git)"],
        "developing_skills": ["SQL", "React", "Testing Fundamentals"],
        "evidence_gap_skills": ["System Design", "Docker"],
        "target_role": "Full Stack Engineer",
    },
    {
        "key": "experienced",
        "name": "Experienced Engineer",
        "strong_skills": ["System Design", "Distributed Systems", "Python", "Technical Decision-Making", "Mentorship"],
        "developing_skills": ["Cloud Architecture", "Kubernetes", "Microservices Architecture"],
        "evidence_gap_skills": ["Machine Learning"],
        "target_role": "Staff Software Engineer",
    },
]
