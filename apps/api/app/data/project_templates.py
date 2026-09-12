"""Curated evidence-producing project templates used by the recommendation engine.

Each template names the skills it demonstrates. The recommendation engine picks
the template with the highest overlap against a user's current top gaps for a
target role, rather than inventing a project on the fly. The synthetic data
seeder also draws on this list so seeded projects are drawn from the same
catalog the recommendation engine recommends from.
"""

PROJECT_TEMPLATES = [
    {
        "title": "Production ML Monitoring Platform",
        "description": "Deploy a trained model behind a REST API, containerize it, wire up CI/CD, and add drift/performance monitoring dashboards.",
        "skills": ["Docker", "CI/CD", "Model Deployment", "Model Monitoring", "MLOps", "FastAPI"],
    },
    {
        "title": "Containerized Model Serving API",
        "description": "Package a scikit-learn or PyTorch model behind a versioned REST API with health checks and load testing.",
        "skills": ["Docker", "Model Deployment", "FastAPI", "REST APIs", "Python"],
    },
    {
        "title": "End-to-End ETL Data Pipeline",
        "description": "Build a scheduled pipeline that extracts data from an API, transforms it, and loads it into a warehouse schema.",
        "skills": ["ETL Pipelines", "SQL", "Data Warehousing", "Python", "Data Engineering"],
    },
    {
        "title": "Streaming Analytics Pipeline",
        "description": "Build a Kafka-based streaming pipeline with a Spark job that aggregates events in near real time.",
        "skills": ["Apache Kafka", "Apache Spark", "Big Data Processing", "Data Engineering"],
    },
    {
        "title": "RAG-Powered Knowledge Assistant",
        "description": "Build a retrieval-augmented generation assistant over a document corpus using a vector database and an LLM API.",
        "skills": ["Retrieval-Augmented Generation", "Vector Databases", "Embeddings", "LLM Integration", "Prompt Engineering", "Python"],
    },
    {
        "title": "Autonomous AI Agent for Task Automation",
        "description": "Build an LLM-driven agent that plans and calls tools to complete multi-step tasks.",
        "skills": ["AI Agent Design", "LLM Integration", "Prompt Engineering", "Python"],
    },
    {
        "title": "NLP Text Classification Service",
        "description": "Train and serve a text classification model with a labeled dataset and evaluation report.",
        "skills": ["Natural Language Processing", "Machine Learning", "Model Evaluation", "Python"],
    },
    {
        "title": "Image Classification Pipeline",
        "description": "Train a CNN on an image dataset, evaluate it, and serve predictions via an API.",
        "skills": ["Computer Vision", "Convolutional Neural Networks", "Deep Learning", "Model Deployment"],
    },
    {
        "title": "Kubernetes-Deployed Microservices App",
        "description": "Split a monolith into services, containerize each, and deploy them to a Kubernetes cluster with autoscaling.",
        "skills": ["Kubernetes", "Docker", "Microservices Architecture", "Distributed Systems"],
    },
    {
        "title": "Infrastructure-as-Code Cloud Environment",
        "description": "Provision a full cloud environment (network, compute, storage) using Terraform with reproducible modules.",
        "skills": ["Terraform", "Infrastructure as Code", "Cloud Architecture", "AWS"],
    },
    {
        "title": "Cloud Cost & Security Audit Toolkit",
        "description": "Build a script/dashboard that audits cloud spend and flags common misconfigurations.",
        "skills": ["Cloud Cost Optimization", "Cloud Security", "Cloud Architecture"],
    },
    {
        "title": "Full-Stack SaaS Dashboard",
        "description": "Build a production-style dashboard: React/Next.js frontend, FastAPI backend, PostgreSQL, auth, and deployment.",
        "skills": ["React", "Next.js", "FastAPI", "PostgreSQL", "REST APIs", "TypeScript"],
    },
    {
        "title": "Accessible Design System",
        "description": "Build a reusable, accessible component library with documented usage and automated accessibility checks.",
        "skills": ["Web Accessibility", "CSS", "React", "Responsive Design"],
    },
    {
        "title": "Real-Time Collaboration App",
        "description": "Build a multi-user real-time app using websockets/message queues with optimistic UI updates.",
        "skills": ["State Management", "Message Queues", "Node.js", "React"],
    },
    {
        "title": "Application Security Review & Hardening",
        "description": "Perform a structured OWASP-based security review of an existing app and remediate the top findings.",
        "skills": ["Application Security", "OWASP Top 10", "Threat Modeling", "Security Auditing"],
    },
    {
        "title": "Penetration Testing Lab Report",
        "description": "Run a structured penetration test against an intentionally vulnerable target and document findings and remediations.",
        "skills": ["Penetration Testing", "Network Security", "Application Security"],
    },
    {
        "title": "Zero-Trust IAM Rollout",
        "description": "Design and implement least-privilege identity and access controls across a sample cloud environment.",
        "skills": ["Identity & Access Management", "Cloud Security", "Threat Modeling"],
    },
    {
        "title": "A/B Testing & Experimentation Platform",
        "description": "Build a lightweight experimentation framework with statistical significance testing and a results dashboard.",
        "skills": ["A/B Testing", "Statistics", "Data Visualization", "SQL"],
    },
    {
        "title": "Analytics Data Model & BI Dashboard",
        "description": "Design a star-schema data model and build BI dashboards answering real business questions.",
        "skills": ["Data Modeling", "Data Warehousing", "Data Visualization", "SQL"],
    },
    {
        "title": "SRE Incident Response Runbook & Observability Stack",
        "description": "Instrument a service with metrics/logs/traces and write incident response runbooks with defined SLOs.",
        "skills": ["Monitoring & Observability", "Site Reliability Engineering", "Incident Response"],
    },
    {
        "title": "CI/CD Pipeline Overhaul",
        "description": "Design a multi-stage CI/CD pipeline with automated testing, staged rollouts, and rollback.",
        "skills": ["CI/CD", "GitHub Actions", "Release Management", "Testing Fundamentals"],
    },
    {
        "title": "Product Discovery & Roadmap Case Study",
        "description": "Run structured user research, synthesize findings, and produce a prioritized roadmap with rationale.",
        "skills": ["User Research", "Roadmapping", "Requirements Analysis", "Stakeholder Communication"],
    },
    {
        "title": "Recommender System Prototype",
        "description": "Build a collaborative-filtering or content-based recommender and evaluate it offline.",
        "skills": ["Recommender Systems", "Machine Learning", "Model Evaluation", "Python"],
    },
]
