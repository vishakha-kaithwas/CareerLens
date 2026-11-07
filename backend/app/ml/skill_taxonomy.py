"""
Skill taxonomy and normalization repository.

Maps synonyms and variants (e.g. 'postgres', 'postgresql', 'psql') to standardized
canonical names, categorizing them across Programming Languages, Frameworks,
Databases, Cloud & DevOps, ML/AI, and Tools.
"""

from typing import Dict, List, Set

# Canonical skill -> list of aliases/synonyms
CANONICAL_SKILLS: Dict[str, List[str]] = {
    # Languages
    "Python": ["python", "python3", "py"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript", "ts"],
    "Java": ["java", "core java", "j2ee"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp", "c sharp", ".net"],
    "Go": ["golang", "go language"],
    "Rust": ["rust", "rustlang"],
    "SQL": ["sql", "structured query language"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Bash": ["bash", "shell scripting", "sh"],

    # Frameworks & Libraries
    "FastAPI": ["fastapi", "fast-api"],
    "Flask": ["flask"],
    "Django": ["django", "django rest framework", "drf"],
    "React": ["react", "react.js", "reactjs"],
    "Next.js": ["next.js", "nextjs"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Express": ["express.js", "expressjs", "express"],
    "Vue.js": ["vue", "vue.js", "vuejs"],
    "Angular": ["angular", "angularjs"],
    "Spring Boot": ["spring boot", "springboot", "spring framework"],

    # Databases
    "PostgreSQL": ["postgresql", "postgres", "psql"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "Elasticsearch": ["elasticsearch", "elastic search"],
    "SQLite": ["sqlite", "sqlite3"],

    # Cloud & DevOps
    "Docker": ["docker", "containerization", "docker-compose"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "Azure": ["azure", "microsoft azure"],
    "Google Cloud Platform": ["gcp", "google cloud", "google cloud platform"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment", "github actions", "gitlab ci", "jenkins"],
    "Terraform": ["terraform"],
    "Linux": ["linux", "ubuntu", "debian", "redhat", "centos"],
    "Git": ["git", "github", "gitlab"],

    # AI & Machine Learning
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "dl"],
    "Natural Language Processing": ["nlp", "natural language processing"],
    "PyTorch": ["pytorch"],
    "TensorFlow": ["tensorflow", "tf"],
    "Scikit-Learn": ["scikit-learn", "sklearn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Large Language Models": ["llm", "llms", "large language models", "prompt engineering"],

    # Software Engineering & Concepts
    "RESTful APIs": ["rest api", "restful api", "rest apis", "restful apis", "rest web services"],
    "GraphQL": ["graphql"],
    "Microservices": ["microservices", "microservice architecture"],
    "System Design": ["system design", "distributed systems", "high availability"],
    "Unit Testing": ["unit testing", "test driven development", "tdd", "pytest", "jest"],
    "Agile": ["agile", "scrum", "kanban"],
}

# Soft skills taxonomy
SOFT_SKILLS: Dict[str, List[str]] = {
    "Communication": ["communication", "verbal communication", "written communication", "presentation skills"],
    "Leadership": ["leadership", "mentor", "mentoring", "team lead", "lead", "guidance"],
    "Problem Solving": ["problem solving", "analytical thinking", "critical thinking", "troubleshooting"],
    "Collaboration": ["collaboration", "teamwork", "cross-functional teams", "team player"],
    "Adaptability": ["adaptability", "flexibility", "fast learner", "growth mindset"],
    "Time Management": ["time management", "prioritization", "multitasking"],
}

# Inverted index for O(1) alias -> canonical lookup
ALIAS_TO_CANONICAL: Dict[str, str] = {}
for canonical, aliases in CANONICAL_SKILLS.items():
    ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in aliases:
        ALIAS_TO_CANONICAL[alias.lower()] = canonical

SOFT_ALIAS_TO_CANONICAL: Dict[str, str] = {}
for canonical, aliases in SOFT_SKILLS.items():
    SOFT_ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in aliases:
        SOFT_ALIAS_TO_CANONICAL[alias.lower()] = canonical
