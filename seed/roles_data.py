"""Synthetic role library: 40+ roles with weighted skill requirements.

Each role: (title, category, description, level, skills)
  skills: list of (skill_name, importance in {CRITICAL,HIGH,MEDIUM,LOW}, min_capability_score)
"""

ROLES = [
    ("Backend Engineer", "Software Engineering", "Builds and maintains server-side systems and APIs.", "Mid", [
        ("Python", "CRITICAL", 60), ("REST APIs", "CRITICAL", 55), ("SQL", "HIGH", 50),
        ("PostgreSQL", "HIGH", 45), ("System Design", "MEDIUM", 40), ("Docker", "MEDIUM", 35),
        ("Testing Fundamentals", "HIGH", 45), ("Caching Strategies", "LOW", 30),
    ]),
    ("Frontend Engineer", "Software Engineering", "Builds user-facing web interfaces.", "Mid", [
        ("JavaScript", "CRITICAL", 55), ("React", "CRITICAL", 55), ("CSS", "HIGH", 50),
        ("TypeScript", "HIGH", 45), ("Web Accessibility", "MEDIUM", 35), ("Frontend Performance", "MEDIUM", 35),
        ("State Management", "HIGH", 40), ("Responsive Design", "MEDIUM", 40),
    ]),
    ("Full Stack Engineer", "Software Engineering", "Works across frontend and backend of an application.", "Mid", [
        ("JavaScript", "CRITICAL", 50), ("React", "HIGH", 45), ("Python", "HIGH", 45),
        ("REST APIs", "CRITICAL", 50), ("SQL", "HIGH", 40), ("Docker", "MEDIUM", 30),
        ("System Design", "MEDIUM", 35), ("Testing Fundamentals", "MEDIUM", 35),
    ]),
    ("Mobile Engineer", "Software Engineering", "Builds native or cross-platform mobile applications.", "Mid", [
        ("JavaScript", "HIGH", 45), ("TypeScript", "MEDIUM", 40), ("REST APIs", "HIGH", 45),
        ("State Management", "HIGH", 40), ("Testing Fundamentals", "MEDIUM", 35), ("System Design", "LOW", 30),
    ]),
    ("Software Engineer (Generalist)", "Software Engineering", "Broad engineering role spanning multiple systems.", "Entry", [
        ("Python", "HIGH", 40), ("Data Structures", "CRITICAL", 45), ("Algorithms", "CRITICAL", 45),
        ("Version Control (Git)", "HIGH", 40), ("Testing Fundamentals", "MEDIUM", 35), ("SQL", "MEDIUM", 35),
    ]),
    ("Staff Software Engineer", "Software Engineering", "Senior engineer driving cross-team technical direction.", "Senior", [
        ("System Design", "CRITICAL", 75), ("Distributed Systems", "HIGH", 65), ("Technical Decision-Making", "CRITICAL", 70),
        ("Mentorship", "HIGH", 60), ("Python", "HIGH", 65), ("Microservices Architecture", "MEDIUM", 55),
    ]),

    ("AI/ML Engineer", "AI/ML", "Builds and ships machine learning systems into production.", "Mid", [
        ("Python", "CRITICAL", 60), ("Machine Learning", "CRITICAL", 60), ("SQL", "MEDIUM", 40),
        ("Statistics", "HIGH", 45), ("Docker", "MEDIUM", 40), ("MLOps", "MEDIUM", 35),
        ("Model Deployment", "HIGH", 45), ("Cloud Architecture", "MEDIUM", 35),
    ]),
    ("Machine Learning Engineer", "AI/ML", "Focuses on training, evaluating, and deploying ML models.", "Mid", [
        ("Python", "CRITICAL", 60), ("Machine Learning", "CRITICAL", 65), ("Statistics", "HIGH", 50),
        ("Feature Engineering", "HIGH", 45), ("Model Evaluation", "HIGH", 45), ("MLOps", "HIGH", 45),
        ("Docker", "MEDIUM", 40), ("Scikit-learn", "MEDIUM", 40),
    ]),
    ("Deep Learning Engineer", "AI/ML", "Specializes in neural network architectures and training.", "Senior", [
        ("Deep Learning", "CRITICAL", 65), ("Neural Networks", "CRITICAL", 65), ("PyTorch", "HIGH", 55),
        ("Python", "CRITICAL", 60), ("Statistics", "HIGH", 50), ("Hyperparameter Tuning", "MEDIUM", 45),
    ]),
    ("NLP Engineer", "AI/ML", "Builds systems that process and generate human language.", "Mid", [
        ("Natural Language Processing", "CRITICAL", 60), ("Python", "CRITICAL", 55), ("Large Language Models", "HIGH", 50),
        ("Transformers", "HIGH", 50), ("Machine Learning", "HIGH", 50), ("Embeddings", "MEDIUM", 40),
    ]),
    ("Computer Vision Engineer", "AI/ML", "Builds systems that extract information from images and video.", "Mid", [
        ("Computer Vision", "CRITICAL", 60), ("Convolutional Neural Networks", "HIGH", 55), ("Python", "CRITICAL", 55),
        ("Deep Learning", "HIGH", 55), ("Machine Learning", "HIGH", 45),
    ]),
    ("AI Product Engineer", "AI/ML", "Integrates AI capabilities directly into product experiences.", "Mid", [
        ("LLM Integration", "CRITICAL", 55), ("Prompt Engineering", "HIGH", 50), ("Python", "HIGH", 45),
        ("REST APIs", "HIGH", 45), ("Product Management", "MEDIUM", 35), ("AI Agent Design", "MEDIUM", 40),
    ]),
    ("Applied Scientist", "AI/ML", "Applies research techniques to solve applied ML problems.", "Senior", [
        ("Machine Learning", "CRITICAL", 65), ("Research Methodology", "HIGH", 55), ("Statistics", "CRITICAL", 60),
        ("Deep Learning", "HIGH", 55), ("Experimental Design", "MEDIUM", 45), ("Academic Writing", "LOW", 35),
    ]),

    ("Data Scientist", "Data", "Extracts insight and builds predictive models from data.", "Mid", [
        ("Python", "CRITICAL", 55), ("Statistics", "CRITICAL", 55), ("Machine Learning", "HIGH", 50),
        ("SQL", "HIGH", 50), ("Data Visualization", "MEDIUM", 40), ("A/B Testing", "MEDIUM", 40),
    ]),
    ("Data Engineer", "Data", "Builds pipelines and infrastructure for reliable data movement.", "Mid", [
        ("Python", "HIGH", 50), ("SQL", "CRITICAL", 55), ("ETL Pipelines", "CRITICAL", 55),
        ("Data Warehousing", "HIGH", 45), ("Apache Spark", "MEDIUM", 40), ("Apache Kafka", "MEDIUM", 35),
        ("Cloud Architecture", "MEDIUM", 40),
    ]),
    ("Data Analyst", "Data", "Analyzes data to answer business questions.", "Entry", [
        ("SQL", "CRITICAL", 50), ("Data Analysis", "CRITICAL", 45), ("Data Visualization", "HIGH", 40),
        ("Statistics", "MEDIUM", 35), ("Stakeholder Communication", "MEDIUM", 35),
    ]),
    ("Analytics Engineer", "Data", "Bridges data engineering and analytics with modeled datasets.", "Mid", [
        ("SQL", "CRITICAL", 55), ("Data Modeling", "HIGH", 45), ("ETL Pipelines", "HIGH", 45),
        ("Data Warehousing", "MEDIUM", 40), ("Python", "MEDIUM", 40),
    ]),
    ("BI Developer", "Data", "Builds dashboards and reporting for business stakeholders.", "Entry", [
        ("SQL", "CRITICAL", 45), ("Data Visualization", "CRITICAL", 45), ("Data Modeling", "MEDIUM", 35),
        ("Stakeholder Communication", "MEDIUM", 35),
    ]),
    ("Data Architect", "Data", "Designs enterprise-scale data systems and standards.", "Senior", [
        ("Data Modeling", "CRITICAL", 65), ("Data Warehousing", "CRITICAL", 60), ("Cloud Architecture", "HIGH", 55),
        ("System Design", "HIGH", 55), ("Data Engineering", "HIGH", 55),
    ]),

    ("Cloud Engineer", "Cloud", "Builds and operates cloud infrastructure.", "Mid", [
        ("Cloud Architecture", "CRITICAL", 55), ("AWS", "HIGH", 50), ("Infrastructure as Code", "HIGH", 45),
        ("Terraform", "MEDIUM", 40), ("Linux Administration", "MEDIUM", 40), ("Networking Fundamentals", "MEDIUM", 40),
    ]),
    ("Cloud Architect", "Cloud", "Designs cloud systems for scale, cost, and reliability.", "Senior", [
        ("Cloud Architecture", "CRITICAL", 70), ("System Design", "CRITICAL", 65), ("Cloud Cost Optimization", "HIGH", 55),
        ("Cloud Security", "HIGH", 55), ("Terraform", "MEDIUM", 50),
    ]),
    ("Cloud Security Engineer", "Cloud", "Secures cloud workloads and infrastructure.", "Mid", [
        ("Cloud Security", "CRITICAL", 55), ("Cloud Architecture", "HIGH", 50), ("Identity & Access Management", "HIGH", 50),
        ("Network Security", "MEDIUM", 40), ("Threat Modeling", "MEDIUM", 40),
    ]),
    ("Solutions Architect", "Cloud", "Designs technical solutions aligned to customer or business needs.", "Senior", [
        ("Cloud Architecture", "CRITICAL", 60), ("System Design", "HIGH", 55), ("Stakeholder Communication", "HIGH", 50),
        ("REST APIs", "MEDIUM", 45),
    ]),

    ("DevOps Engineer", "DevOps", "Automates delivery pipelines and infrastructure operations.", "Mid", [
        ("Docker", "CRITICAL", 50), ("CI/CD", "CRITICAL", 50), ("Kubernetes", "HIGH", 45),
        ("Infrastructure as Code", "HIGH", 45), ("Linux Administration", "MEDIUM", 40), ("Monitoring & Observability", "MEDIUM", 40),
    ]),
    ("MLOps Engineer", "DevOps", "Operationalizes machine learning systems in production.", "Mid", [
        ("Docker", "CRITICAL", 55), ("MLOps", "CRITICAL", 55), ("CI/CD", "HIGH", 50),
        ("Model Deployment", "HIGH", 50), ("Model Monitoring", "HIGH", 45), ("Kubernetes", "MEDIUM", 45),
        ("Cloud Architecture", "MEDIUM", 40),
    ]),
    ("Site Reliability Engineer", "DevOps", "Ensures reliability and performance of production systems.", "Senior", [
        ("Site Reliability Engineering", "CRITICAL", 60), ("Monitoring & Observability", "CRITICAL", 55),
        ("Incident Response", "HIGH", 50), ("Kubernetes", "HIGH", 50), ("Distributed Systems", "MEDIUM", 45),
    ]),
    ("Platform Engineer", "DevOps", "Builds internal developer platforms and tooling.", "Mid", [
        ("Kubernetes", "CRITICAL", 50), ("Infrastructure as Code", "HIGH", 50), ("CI/CD", "HIGH", 45),
        ("Cloud Architecture", "MEDIUM", 45), ("Configuration Management", "MEDIUM", 40),
    ]),
    ("Release Engineer", "DevOps", "Manages build, versioning, and release processes.", "Mid", [
        ("CI/CD", "CRITICAL", 50), ("Release Management", "CRITICAL", 45), ("Version Control (Git)", "HIGH", 45),
        ("Configuration Management", "MEDIUM", 35),
    ]),

    ("Security Engineer", "Cybersecurity", "Builds and maintains security controls across systems.", "Mid", [
        ("Application Security", "CRITICAL", 55), ("Network Security", "HIGH", 50), ("Cryptography", "MEDIUM", 40),
        ("Threat Modeling", "HIGH", 45), ("Security Auditing", "MEDIUM", 40),
    ]),
    ("Penetration Tester", "Cybersecurity", "Simulates attacks to find exploitable weaknesses.", "Mid", [
        ("Penetration Testing", "CRITICAL", 55), ("Application Security", "CRITICAL", 55), ("Networking Fundamentals", "HIGH", 45),
        ("OWASP Top 10", "HIGH", 45),
    ]),
    ("Security Analyst", "Cybersecurity", "Monitors and responds to security events.", "Entry", [
        ("Network Security", "HIGH", 40), ("Incident Response", "HIGH", 40), ("Security Auditing", "MEDIUM", 35),
        ("Application Security", "MEDIUM", 35),
    ]),
    ("Application Security Engineer", "Cybersecurity", "Embeds security practices into the software development lifecycle.", "Mid", [
        ("Application Security", "CRITICAL", 55), ("OWASP Top 10", "CRITICAL", 50), ("Threat Modeling", "HIGH", 45),
        ("REST APIs", "MEDIUM", 40),
    ]),
    ("Security Architect", "Cybersecurity", "Designs security strategy across an organization's systems.", "Senior", [
        ("Threat Modeling", "CRITICAL", 65), ("Cloud Security", "HIGH", 60), ("Identity & Access Management", "HIGH", 55),
        ("System Design", "HIGH", 55),
    ]),

    ("Product Manager", "Product", "Defines product direction and prioritizes what gets built.", "Mid", [
        ("Product Management", "CRITICAL", 55), ("Roadmapping", "HIGH", 50), ("Stakeholder Communication", "HIGH", 50),
        ("User Research", "MEDIUM", 40), ("Requirements Analysis", "HIGH", 45),
    ]),
    ("Technical Product Manager", "Product", "Product manager with deep technical fluency.", "Mid", [
        ("Product Management", "CRITICAL", 55), ("System Design", "MEDIUM", 40), ("REST APIs", "MEDIUM", 35),
        ("Requirements Analysis", "HIGH", 45), ("Stakeholder Communication", "HIGH", 50),
    ]),
    ("UX Designer", "Product", "Designs usable, intuitive user experiences.", "Mid", [
        ("UX Design", "CRITICAL", 55), ("User Research", "CRITICAL", 50), ("Responsive Design", "MEDIUM", 40),
        ("Web Accessibility", "MEDIUM", 40), ("Presentation Skills", "MEDIUM", 35),
    ]),
    ("Product Analyst", "Product", "Uses data to inform product decisions.", "Entry", [
        ("SQL", "HIGH", 40), ("Data Analysis", "CRITICAL", 45), ("A/B Testing", "HIGH", 40),
        ("Data Visualization", "MEDIUM", 35),
    ]),

    ("Business Intelligence Analyst", "Analytics", "Turns raw data into business reporting and insight.", "Entry", [
        ("SQL", "CRITICAL", 45), ("Data Visualization", "HIGH", 40), ("Data Analysis", "HIGH", 40),
        ("Stakeholder Communication", "MEDIUM", 35),
    ]),
    ("Marketing Analyst", "Analytics", "Analyzes marketing performance and customer behavior data.", "Entry", [
        ("Data Analysis", "CRITICAL", 40), ("SQL", "HIGH", 35), ("A/B Testing", "HIGH", 40),
        ("Data Visualization", "MEDIUM", 35),
    ]),

    ("Research Scientist", "Research", "Conducts original research to advance the state of the art.", "Senior", [
        ("Research Methodology", "CRITICAL", 65), ("Machine Learning", "HIGH", 60), ("Academic Writing", "HIGH", 55),
        ("Experimental Design", "HIGH", 55), ("Statistics", "HIGH", 55),
    ]),
    ("Research Engineer", "Research", "Implements and scales research ideas into working systems.", "Mid", [
        ("Python", "CRITICAL", 55), ("Machine Learning", "HIGH", 55), ("Deep Learning", "HIGH", 50),
        ("Research Methodology", "MEDIUM", 40), ("PyTorch", "MEDIUM", 45),
    ]),
]
