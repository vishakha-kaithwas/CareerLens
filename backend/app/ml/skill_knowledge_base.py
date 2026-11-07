"""
Curated Skill Knowledge Base and Dependency Definitions.

Maps canonical skills to:
- category: Domain categorization
- prerequisites: Foundational prerequisite skills (directed dependency edges)
- related_skills: Complementary or adjacent technologies
- learning_topics: Core conceptual milestones to master
- practical_projects: Specific, realistic deliverables to build
- estimated_hours: Realistic learning time estimate
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SkillDefinition(BaseModel):
    """Metadata, dependency graph edges, and learning tasks for a skill."""
    name: str = Field(..., description="Canonical skill name matching taxonomy")
    category: str = Field(..., description="Domain category")
    prerequisites: List[str] = Field(default_factory=list, description="Immediate prerequisite skills")
    related_skills: List[str] = Field(default_factory=list, description="Adjacent or complementary tools")
    learning_topics: List[str] = Field(default_factory=list, description="Core conceptual topics to learn")
    practical_projects: List[str] = Field(default_factory=list, description="Concrete portfolio projects to build")
    deliverables: List[str] = Field(default_factory=list, description="Expected verifiable artifacts")
    estimated_hours: int = Field(20, description="Estimated hands-on hours to bridge the gap")


SKILL_KNOWLEDGE_BASE: Dict[str, SkillDefinition] = {
    # Programming Languages
    "Python": SkillDefinition(
        name="Python",
        category="Programming Languages",
        prerequisites=[],
        related_skills=["Bash", "SQL"],
        learning_topics=["Object-Oriented Programming", "AsyncIO & Generators", "Typing & Data Structures", "Virtual Environments & Packaging"],
        practical_projects=["Build a concurrent CLI data-processing tool with logging and type hints."],
        deliverables=["GitHub repository with unit tests, typing with mypy, and clean modular structure."],
        estimated_hours=25,
    ),
    "TypeScript": SkillDefinition(
        name="TypeScript",
        category="Programming Languages",
        prerequisites=["JavaScript"],
        related_skills=["Node.js", "React"],
        learning_topics=["Interfaces & Type Aliases", "Generics & Utility Types", "TSConfig & Build Tools"],
        practical_projects=["Migrate a vanilla JavaScript utility library to strictly-typed TypeScript."],
        deliverables=["Published NPM package or GitHub repo passing tsc --noEmit with zero any types."],
        estimated_hours=20,
    ),
    "SQL": SkillDefinition(
        name="SQL",
        category="Databases",
        prerequisites=[],
        related_skills=["PostgreSQL", "MySQL", "Python"],
        learning_topics=["Complex Joins & Subqueries", "Indexing & Execution Plans (EXPLAIN)", "Window Functions & CTEs", "Transactions & ACID guarantees"],
        practical_projects=["Design a multi-table relational schema and write analytical window queries."],
        deliverables=["SQL migration script with indexes and an execution plan performance benchmark."],
        estimated_hours=20,
    ),

    # Backend Frameworks
    "RESTful APIs": SkillDefinition(
        name="RESTful APIs",
        category="Backend Development",
        prerequisites=["Python"],
        related_skills=["FastAPI", "Flask", "Django"],
        learning_topics=["HTTP Methods & Status Codes", "Idempotency & Caching", "API Versioning & OpenAPI Specs", "Authentication & Rate Limiting"],
        practical_projects=["Build and document an OpenAPI 3.0 compliant REST API with filtering and pagination."],
        deliverables=["FastAPI or Flask API repository with Swagger documentation and automated endpoint tests."],
        estimated_hours=20,
    ),
    "FastAPI": SkillDefinition(
        name="FastAPI",
        category="Backend Development",
        prerequisites=["Python", "RESTful APIs"],
        related_skills=["Pydantic", "Docker", "PostgreSQL"],
        learning_topics=["Pydantic Schemas & Dependency Injection", "Async Endpoints & Background Tasks", "Custom Middlewares & Exception Handlers", "Authentication with JWT"],
        practical_projects=["Build a production-grade asynchronous REST API with JWT auth and SQL database."],
        deliverables=["Containerized FastAPI app with test suite passing pytest and OpenAPI schema."],
        estimated_hours=25,
    ),
    "Django": SkillDefinition(
        name="Django",
        category="Backend Development",
        prerequisites=["Python", "SQL", "RESTful APIs"],
        related_skills=["PostgreSQL", "Docker"],
        learning_topics=["Django ORM & Migrations", "Django REST Framework (DRF) Viewsets", "Admin Panel & Middleware", "Celery Task Queue"],
        practical_projects=["Build a multi-user CRUD platform with relational models and DRF authentication."],
        deliverables=["Complete Django repo with migrations, automated model tests, and API endpoints."],
        estimated_hours=30,
    ),

    # Databases
    "PostgreSQL": SkillDefinition(
        name="PostgreSQL",
        category="Databases",
        prerequisites=["SQL"],
        related_skills=["Python", "FastAPI", "Redis"],
        learning_topics=["Postgres Data Types (JSONB, UUID)", "Query Optimization & Vacuuming", "Connection Pooling (PgBouncer)", "Foreign Keys & Constraints"],
        practical_projects=["Connect a backend service to PostgreSQL using SQLAlchemy or asyncpg with connection pooling."],
        deliverables=["Alembic migration history and database integration test suite."],
        estimated_hours=25,
    ),
    "Redis": SkillDefinition(
        name="Redis",
        category="Databases",
        prerequisites=["RESTful APIs"],
        related_skills=["FastAPI", "PostgreSQL"],
        learning_topics=["In-memory Key-Value Structures", "Caching Strategies (Cache-Aside, Write-Through)", "Pub/Sub & Message Queues", "Rate Limiting with Redis"],
        practical_projects=["Implement a Redis caching layer for an API endpoint to reduce database query load."],
        deliverables=["Benchmarked API demonstrating 5x latency reduction using Redis caching."],
        estimated_hours=15,
    ),

    # Cloud & DevOps
    "Docker": SkillDefinition(
        name="Docker",
        category="Cloud & DevOps",
        prerequisites=["Linux"],
        related_skills=["Kubernetes", "CI/CD", "AWS"],
        learning_topics=["Multi-stage Dockerfiles", "Image Optimization & Layer Caching", "Docker Compose Multi-container Networking", "Volume Mounting & Environment Secrets"],
        practical_projects=["Containerize a backend API and database service using multi-stage builds and Docker Compose."],
        deliverables=["Optimized Dockerfile (<150MB image) and working docker-compose.yml."],
        estimated_hours=20,
    ),
    "Kubernetes": SkillDefinition(
        name="Kubernetes",
        category="Cloud & DevOps",
        prerequisites=["Docker", "Linux"],
        related_skills=["AWS", "Terraform", "CI/CD"],
        learning_topics=["Pods, Deployments, and Services", "ConfigMaps & Secrets", "Ingress Controllers", "Horizontal Pod Autoscalers (HPA)"],
        practical_projects=["Deploy a containerized microservice to a local Minikube or k3s cluster."],
        deliverables=["Kubernetes YAML manifests (Deployment, Service, ConfigMap) with health readiness probes."],
        estimated_hours=35,
    ),
    "CI/CD": SkillDefinition(
        name="CI/CD",
        category="Cloud & DevOps",
        prerequisites=["Git", "Docker"],
        related_skills=["Linux", "Kubernetes"],
        learning_topics=["GitHub Actions Workflow Syntax", "Automated Testing on Pull Requests", "Docker Image Publishing to GHCR/DockerHub", "Staging vs Production Deployments"],
        practical_projects=["Create an end-to-end GitHub Actions workflow that runs pytest, builds Docker, and pushes image."],
        deliverables=[".github/workflows/ci.yml with status badge and automated test reporting."],
        estimated_hours=15,
    ),
    "AWS": SkillDefinition(
        name="AWS",
        category="Cloud & DevOps",
        prerequisites=["Docker", "Linux"],
        related_skills=["Terraform", "CI/CD"],
        learning_topics=["EC2, ECS, and Lambda (Serverless)", "S3 Bucket Policies & IAM Roles", "VPC Networking & Security Groups", "RDS Cloud Databases"],
        practical_projects=["Deploy a containerized FastAPI application on AWS ECS (Fargate) or App Runner."],
        deliverables=["Live URL of deployed application and IAM configuration documentation."],
        estimated_hours=30,
    ),
    "Linux": SkillDefinition(
        name="Linux",
        category="Software Engineering Fundamentals",
        prerequisites=[],
        related_skills=["Bash", "Docker"],
        learning_topics=["Bash Shell Navigation & Permissions", "Process Management (systemctl, ps, top)", "SSH & Key Management", "Networking (curl, netstat, iptables)"],
        practical_projects=["Provision a Linux VM, configure SSH keys, set up a firewall, and run a background daemon."],
        deliverables=["Shell setup script and documented server hardening steps."],
        estimated_hours=15,
    ),
    "Git": SkillDefinition(
        name="Git",
        category="Software Engineering Fundamentals",
        prerequisites=[],
        related_skills=["CI/CD"],
        learning_topics=["Branching Strategies (GitFlow, Trunk-Based)", "Interactive Rebasing & Cherry-Picking", "Resolving Merge Conflicts", "Pull Request Etiquette & Semantic Commits"],
        practical_projects=["Manage an open-source contribution or multi-branch feature lifecycle."],
        deliverables=["Clean Git log with conventional commits and merged pull requests."],
        estimated_hours=10,
    ),

    # AI & Machine Learning
    "Machine Learning": SkillDefinition(
        name="Machine Learning",
        category="Machine Learning",
        prerequisites=["Python", "SQL"],
        related_skills=["Scikit-Learn", "Deep Learning"],
        learning_topics=["Supervised vs Unsupervised Learning", "Feature Engineering & Data Preprocessing", "Model Evaluation (Precision, Recall, ROC-AUC)", "Cross-Validation & Overfitting"],
        practical_projects=["Build an end-to-end tabular predictive model with baseline comparisons."],
        deliverables=["Jupyter notebook or reproducible Python script with validation metrics."],
        estimated_hours=35,
    ),
    "Scikit-Learn": SkillDefinition(
        name="Scikit-Learn",
        category="Machine Learning",
        prerequisites=["Python", "Machine Learning"],
        related_skills=["Pandas", "NumPy"],
        learning_topics=["Pipelines & ColumnTransformers", "Hyperparameter Tuning with GridSearchCV", "Classification & Regression Estimators"],
        practical_projects=["Build an automated training pipeline combining imputation, scaling, and classification."],
        deliverables=["Trained model artifact with serialization (joblib) and unit tests."],
        estimated_hours=20,
    ),
    "Deep Learning": SkillDefinition(
        name="Deep Learning",
        category="AI & GenAI",
        prerequisites=["Python", "Machine Learning"],
        related_skills=["PyTorch", "TensorFlow"],
        learning_topics=["Neural Network Architectures (MLP, CNN, RNN)", "Backpropagation & Loss Functions", "Optimizers (Adam, SGD) & Learning Rates", "Regularization (Dropout, BatchNorm)"],
        practical_projects=["Train a neural network classifier on image or text data."],
        deliverables=["Training loss/accuracy curves and saved checkpoint file."],
        estimated_hours=40,
    ),
    "PyTorch": SkillDefinition(
        name="PyTorch",
        category="AI & GenAI",
        prerequisites=["Python", "Deep Learning"],
        related_skills=["Natural Language Processing"],
        learning_topics=["Tensors & Autograd Engine", "nn.Module & DataLoader pipelines", "GPU Training with CUDA", "Model Checkpointing & Inference"],
        practical_projects=["Implement a custom PyTorch model training loop with validation checkpoints."],
        deliverables=["Reproducible PyTorch training and evaluation script."],
        estimated_hours=30,
    ),
    "Natural Language Processing": SkillDefinition(
        name="Natural Language Processing",
        category="AI & GenAI",
        prerequisites=["Python", "Machine Learning"],
        related_skills=["Large Language Models", "PyTorch"],
        learning_topics=["Tokenization & Stop Words", "TF-IDF & Word Embeddings", "Transformers & Attention Mechanisms", "Sentence Transformers & Cosine Similarity"],
        practical_projects=["Build a semantic text search engine using dense vector embeddings."],
        deliverables=["Working search engine indexing and retrieving document text based on semantic queries."],
        estimated_hours=30,
    ),
    "Large Language Models": SkillDefinition(
        name="Large Language Models",
        category="AI & GenAI",
        prerequisites=["Python", "Natural Language Processing"],
        related_skills=["RESTful APIs", "FastAPI"],
        learning_topics=["Prompt Engineering & Few-Shot Learning", "Retrieval-Augmented Generation (RAG)", "Structured Output Validation (Pydantic)", "Vector Databases & Chunking"],
        practical_projects=["Build a RAG question-answering assistant over custom documentation."],
        deliverables=["End-to-end RAG system with retrieval evaluations and hallucination checks."],
        estimated_hours=30,
    ),
}
