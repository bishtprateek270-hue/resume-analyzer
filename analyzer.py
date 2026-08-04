import re
from typing import Dict, Set, Tuple, List

# Comprehensive list of technology and soft skills
# Keys are lowercase search keys (often normalized), values are standard user-facing names.
SKILLS_DICT = {
    # Programming Languages
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "c++": "C++",
    "c#": "C#",
    "c programming": "C",
    "golang": "Go",
    "go programming": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "scala": "Scala",
    "r programming": "R",
    "perl": "Perl",
    "shell script": "Bash/Shell",
    "bash": "Bash/Shell",
    "sql": "SQL",
    "html": "HTML",
    "css": "CSS",
    "sass": "Sass",
    "less": "Less",

    # Frontend Frameworks & Libraries
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "angular": "Angular",
    "angularjs": "Angular",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "svelte": "Svelte",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "nuxt.js": "Nuxt.js",
    "gatsby": "Gatsby",
    "redux": "Redux",
    "tailwind": "TailwindCSS",
    "tailwindcss": "TailwindCSS",
    "bootstrap": "Bootstrap",
    "jquery": "jQuery",
    "webpack": "Webpack",
    "vite": "Vite",

    # Backend Frameworks & Technologies
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring boot": "Spring Boot",
    "spring framework": "Spring Framework",
    "asp.net": "ASP.NET",
    ".net": ".NET",
    "dotnet": ".NET",
    "ruby on rails": "Ruby on Rails",
    "rails": "Ruby on Rails",
    "laravel": "Laravel",
    "nestjs": "NestJS",
    "graphql": "GraphQL",
    "rest api": "RESTful APIs",
    "restful": "RESTful APIs",
    "soap": "SOAP",
    "microservices": "Microservices",
    "grpc": "gRPC",

    # Databases & Caching
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "mariadb": "MariaDB",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "oracle": "Oracle DB",
    "sql server": "MS SQL Server",
    "neo4j": "Neo4j",
    "firebase": "Firebase",
    "firestore": "Firestore",
    "elasticsearch": "Elasticsearch",

    # DevOps, Cloud & Systems
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "circleci": "CircleCI",
    "github actions": "GitHub Actions",
    "nginx": "Nginx",
    "apache": "Apache",
    "linux": "Linux",
    "unix": "Unix",
    "prometheus": "Prometheus",
    "grafana": "Grafana",

    # Data Science, Machine Learning & AI
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "artificial intelligence": "AI",
    "ai": "AI",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "computer vision": "Computer Vision",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "keras": "Keras",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "hadoop": "Hadoop",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "data engineering": "Data Engineering",
    "llm": "LLMs",
    "large language models": "LLMs",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "huggingface": "Hugging Face",
    "vector database": "Vector Databases",
    "pinecone": "Pinecone",
    "chromadb": "ChromaDB",

    # Mobile & Game Development
    "flutter": "Flutter",
    "react native": "React Native",
    "xamarin": "Xamarin",
    "ionic": "Ionic",
    "android sdk": "Android SDK",
    "unity": "Unity 3D",
    "unreal engine": "Unreal Engine",

    # Testing & Security
    "selenium": "Selenium",
    "cypress": "Cypress",
    "jest": "Jest",
    "mocha": "Mocha",
    "junit": "JUnit",
    "pytest": "PyTest",
    "penetration testing": "Penetration Testing",
    "cybersecurity": "Cybersecurity",
    "cryptography": "Cryptography",
    "owasp": "OWASP",

    # Business, Management & Methodology
    "agile": "Agile",
    "scrum": "Scrum",
    "kanban": "Kanban",
    "project management": "Project Management",
    "product management": "Product Management",
    "jira": "Jira",
    "confluence": "Confluence",
    "trello": "Trello",
    "gitflow": "GitFlow",
    "sdlc": "SDLC",

    # Soft Skills & Communication
    "communication": "Communication",
    "leadership": "Leadership",
    "teamwork": "Teamwork",
    "collaboration": "Collaboration",
    "problem solving": "Problem Solving",
    "critical thinking": "Critical Thinking",
    "time management": "Time Management",
    "mentorship": "Mentorship",
    "negotiation": "Negotiation",
}

# Categories for front-end rendering
SKILL_CATEGORIES = {
    "Programming Languages": ["Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "Perl", "Bash/Shell", "SQL", "HTML", "CSS", "Sass", "Less"],
    "Frontend": ["React", "Angular", "Vue.js", "Svelte", "Next.js", "Nuxt.js", "Gatsby", "Redux", "TailwindCSS", "Bootstrap", "jQuery", "Webpack", "Vite"],
    "Backend & APIs": ["Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot", "Spring Framework", "ASP.NET", ".NET", "Ruby on Rails", "Laravel", "NestJS", "GraphQL", "RESTful APIs", "SOAP", "Microservices", "gRPC"],
    "Databases": ["MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "MariaDB", "Cassandra", "DynamoDB", "Oracle DB", "MS SQL Server", "Neo4j", "Firebase", "Firestore", "Elasticsearch"],
    "DevOps & Cloud": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "Git", "GitHub", "GitLab", "CI/CD", "CircleCI", "GitHub Actions", "Nginx", "Apache", "Linux", "Unix", "Prometheus", "Grafana"],
    "Data Science & AI": ["Machine Learning", "Deep Learning", "AI", "NLP", "Computer Vision", "TensorFlow", "PyTorch", "Keras", "Scikit-Learn", "Pandas", "NumPy", "SciPy", "Apache Spark", "Hadoop", "Tableau", "Power BI", "Data Science", "Data Analysis", "Data Engineering", "LLMs", "LangChain", "LlamaIndex", "Hugging Face", "Vector Databases", "Pinecone", "ChromaDB"],
    "Mobile & Games": ["Flutter", "React Native", "Xamarin", "Ionic", "Android SDK", "Unity 3D", "Unreal Engine"],
    "QA & Security": ["Selenium", "Cypress", "Jest", "Mocha", "JUnit", "PyTest", "Penetration Testing", "Cybersecurity", "Cryptography", "OWASP"],
    "Management & Soft Skills": ["Agile", "Scrum", "Kanban", "Project Management", "Product Management", "Jira", "Confluence", "Trello", "GitFlow", "SDLC", "Communication", "Leadership", "Teamwork", "Collaboration", "Problem Solving", "Critical Thinking", "Time Management", "Mentorship", "Negotiation"]
}

def extract_skills(text: str) -> Set[str]:
    """
    Scans the text and extracts skills listed in SKILLS_DICT.
    Uses precise token boundary matching for single words and substring search for phrases.
    """
    text_lower = text.lower()
    
    # Normalize punctuation but keep vital characters: +, #, ., / (for C++, C#, .NET, CI/CD)
    # We substitute other punctuation with whitespace
    normalized_text = re.sub(r'[^\w\s\+\#\.\/]', ' ', text_lower)
    
    # Tokenize text
    tokens = set(normalized_text.split())
    
    found_skills = set()
    for key, value in SKILLS_DICT.items():
        # For multi-word or special-character phrases
        if ' ' in key or '/' in key or key in ['c++', 'c#', '.net']:
            if key in text_lower:
                found_skills.add(value)
        else:
            if key in tokens:
                found_skills.add(value)
                
    return found_skills

def detect_years_of_experience(text: str) -> float:
    """
    Estimates the candidate's years of experience using regex heuristics.
    Looks for numbers associated with "years of experience" or similar.
    Returns the maximum detected value, or 0.0 if not found.
    """
    text_lower = text.lower()
    # Patterns: "X+ years", "X years of experience", "X yrs exp", etc.
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:\+|plus)?\s*(?:years?|yrs?)(?:\s+of)?\s*(?:experience|exp|work|background|career)?\b',
        r'(?:experience|exp|work)\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b'
    ]
    
    matches = []
    for pattern in patterns:
        for match in re.finditer(pattern, text_lower):
            try:
                val = float(match.group(1))
                # Ignore outliers (e.g. over 40 years is probably a phone digit or something else)
                if val <= 40:
                    matches.append(val)
            except ValueError:
                pass
                
    # If no pattern matches, try to look at job history date intervals (simplified check)
    # Let's return the max value found or default to 0.0
    return max(matches) if matches else 0.0

def detect_required_experience(text: str) -> float:
    """
    Extracts the required years of experience from the job description text.
    Returns 0.0 if not specified.
    """
    text_lower = text.lower()
    
    # Patterns for JD requirements: "3+ years", "minimum of 5 years", "requires 2 years"
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:\+|plus)?\s*(?:years?|yrs?)(?:\s+of)?\s*(?:required|experience|exp|work|background)?\b',
        r'(?:require|prefer|expect|minimum|at least)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b'
    ]
    
    matches = []
    for pattern in patterns:
        for match in re.finditer(pattern, text_lower):
            try:
                val = float(match.group(1))
                if val <= 25: # JDs rarely ask for >25 years
                    matches.append(val)
            except ValueError:
                pass
                
    return max(matches) if matches else 0.0

# Degree hierarchy mapping
DEGREE_LEVELS = {
    "phd": 5, "ph.d": 5, "doctorate": 5, "doctor of philosophy": 5,
    "master": 4, "ms": 4, "m.s": 4, "mtech": 4, "m.tech": 4, "mba": 4, "m.b.a": 4, "msc": 4, "m.sc": 4,
    "bachelor": 3, "bs": 3, "b.s": 3, "btech": 3, "b.tech": 3, "ba": 3, "b.a": 3, "bsc": 3, "b.sc": 3, "bba": 3,
    "associate": 2, "diploma": 1, "high school": 1
}

def detect_education(text: str) -> str:
    """
    Detects the highest education level in the text.
    Returns the degree name (e.g. "Master's") or "Not Specified".
    """
    text_lower = text.lower()
    highest_level = 0
    highest_degree = "Not Specified"
    
    degree_labels = {
        5: "PhD / Doctorate",
        4: "Master's Degree",
        3: "Bachelor's Degree",
        2: "Associate Degree",
        1: "Diploma / High School"
    }
    
    for degree_keyword, level in DEGREE_LEVELS.items():
        # Match exact word or boundary to avoid false matching (e.g. "ba" matching inside "database")
        pattern = r'\b' + re.escape(degree_keyword) + r'\b'
        if re.search(pattern, text_lower):
            if level > highest_level:
                highest_level = level
                highest_degree = degree_labels[level]
                
    return highest_degree

def calculate_ats_score(resume_text: str, jd_text: str, job_title: str = "") -> Dict[str, any]:
    """
    Deterministic scoring algorithm for matching a resume to a job description.
    Weights:
      - Skills Match: 60%
      - Experience Match: 20%
      - Education Match: 10%
      - Formatting & Sections: 10%
    """
    # 1. Skills Scoring
    jd_skills = extract_skills(jd_text)
    resume_skills = extract_skills(resume_text)
    
    # Baseline skill expansion based on target job title
    expanded_jd_skills = set(jd_skills)
    
    if job_title:
        title_lower = job_title.lower()
        baselines = []
        # AI / ML Engineering
        if any(kw in title_lower for kw in ["ai", "ml", "machine learning", "deep learning", "artificial intelligence", "data scientist"]):
            baselines = ["Python", "SQL", "Pandas", "Machine Learning", "Git", "PyTorch", "TensorFlow"]
        # Frontend Engineering
        elif any(kw in title_lower for kw in ["frontend", "front-end", "react", "angular", "vue", "web developer"]):
            baselines = ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Git"]
        # Backend Engineering
        elif any(kw in title_lower for kw in ["backend", "back-end", "django", "node", "express", "fastapi", "spring"]):
            baselines = ["SQL", "Git", "Docker", "RESTful APIs", "CI/CD"]
        # DevOps / Cloud
        elif any(kw in title_lower for kw in ["devops", "cloud", "sre", "platform", "infrastructure"]):
            baselines = ["Docker", "Kubernetes", "AWS", "Git", "CI/CD", "Terraform"]
        # Mobile
        elif any(kw in title_lower for kw in ["mobile", "ios", "android", "flutter", "react native"]):
            baselines = ["Git", "RESTful APIs", "JavaScript", "React Native" if "native" in title_lower else "Swift"]
            
        # Add baselines that are not already present in the JD, but limit it to avoid overloading
        for skill in baselines:
            expanded_jd_skills.add(skill)
            
    # If expanded JD skills is still empty, fall back to matching resume skills against top common skills
    if not expanded_jd_skills:
        # If JD has no detectable skills, require a baseline profile
        expanded_jd_skills = {"Python", "Git", "SQL", "RESTful APIs"}

    matched_skills = expanded_jd_skills.intersection(resume_skills)
    missing_skills = expanded_jd_skills - resume_skills
    
    skills_score = (len(matched_skills) / len(expanded_jd_skills)) * 100
        
    # 2. Experience Scoring
    candidate_exp = detect_years_of_experience(resume_text)
    required_exp = detect_required_experience(jd_text)
    
    if required_exp > 0:
        experience_score = min(1.0, candidate_exp / required_exp) * 100
    else:
        # If JD doesn't specify experience, default to a realistic junior expectations (e.g. 2 years baseline)
        # to ensure they are scored critically rather than giving a free 100%
        experience_score = min(1.0, candidate_exp / 2.0) * 100
        
    # 3. Education Scoring
    candidate_edu = detect_education(resume_text)
    required_edu_str = detect_education(jd_text)
    
    cand_level = 0
    req_level = 0
    
    for degree, lvl in DEGREE_LEVELS.items():
        if degree in candidate_edu.lower():
            cand_level = max(cand_level, lvl)
        if degree in required_edu_str.lower():
            req_level = max(req_level, lvl)
            
    if req_level > 0:
        if cand_level >= req_level:
            education_score = 100.0
        else:
            education_score = (cand_level / req_level) * 100
    else:
        # Default to expecting Bachelor's level for software/technical roles
        if cand_level >= 3: # Bachelor's
            education_score = 100.0
        else:
            education_score = (cand_level / 3.0) * 100
        
    # 4. Sections & Formatting Scoring
    # Check sections
    sections = {
        "experience": ["experience", "work history", "employment", "professional background", "career", "history"],
        "projects": ["projects", "key achievements", "academic projects", "personal projects", "portfolio"],
        "education": ["education", "academic qualification", "credentials", "degrees", "university"],
        "skills": ["skills", "technical skills", "competencies", "expertise", "technologies", "key skills"]
    }
    
    detected_sections = []
    section_score = 0.0
    text_lower = resume_text.lower()
    
    # 15 points per section present (max 60)
    for section_name, keywords in sections.items():
        for keyword in keywords:
            # Look for keywords as standalone headers
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                detected_sections.append(section_name.capitalize())
                section_score += 15.0
                break
                
    # 20 points for email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if re.search(email_pattern, text_lower):
        section_score += 20.0
        
    # 20 points for phone number
    phone_pattern = r'(?:\+?\d{1,3}[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}'
    if re.search(phone_pattern, text_lower):
        section_score += 20.0
        
    # 5. Overall Calculation with strict penalties
    overall_score = (
        0.60 * skills_score +
        0.20 * experience_score +
        0.10 * education_score +
        0.10 * section_score
    )
    
    # Apply length penalty (very thin resumes get capped)
    length_ratio = len(resume_text.strip()) / 2500.0
    length_penalty = min(1.0, max(0.5, length_ratio))
    overall_score = overall_score * length_penalty
    
    # Apply critical section penalties (deduct points if missing baseline components)
    if "Experience" not in detected_sections:
        overall_score -= 20.0
    if "Projects" not in detected_sections:
        overall_score -= 10.0
    if "Skills" not in detected_sections:
        overall_score -= 10.0
        
    # Bound overall score between 0 and 100
    overall_score = max(0.0, min(100.0, overall_score))
    
    # Categorize skills breakdown
    skills_by_category = {}
    for cat_name, cat_skills in SKILL_CATEGORIES.items():
        cat_matches = [s for s in matched_skills if s in cat_skills]
        cat_missing = [s for s in missing_skills if s in cat_skills]
        if cat_matches or cat_missing:
            skills_by_category[cat_name] = {
                "matched": cat_matches,
                "missing": cat_missing
            }
            
    return {
        "ats_score": round(overall_score),
        "skills_score": round(skills_score),
        "experience_score": round(experience_score),
        "education_score": round(education_score),
        "section_score": round(section_score),
        "matched_skills": list(matched_skills),
        "missing_skills": list(missing_skills),
        "detected_sections": detected_sections,
        "candidate_experience": candidate_exp,
        "required_experience": required_exp,
        "candidate_education": candidate_edu,
        "required_education": required_edu_str if req_level > 0 else "Not Specified",
        "skills_by_category": skills_by_category
    }
