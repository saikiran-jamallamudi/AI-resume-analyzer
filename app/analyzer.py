"""Transparent, deterministic resume-to-job-description analysis."""

import re
from collections import OrderedDict

SKILL_CATALOG = OrderedDict({
    "Python": ["python", "python 3"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript"],
    "C": ["c language", " c "],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "c sharp"],
    "SQL": ["sql", "structured query language"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "SQLite": ["sqlite"],
    "MongoDB": ["mongodb", "mongo db"],
    "Redis": ["redis"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "React": ["react", "react.js", "reactjs"],
    "Next.js": ["next.js", "nextjs"],
    "Node.js": ["node.js", "nodejs", "node js"],
    "Express": ["express.js", "expressjs", "express"],
    "Flask": ["flask"],
    "Django": ["django"],
    "FastAPI": ["fastapi"],
    "Spring Boot": ["spring boot"],
    "REST APIs": ["rest api", "restful api", "rest apis"],
    "GraphQL": ["graphql"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Linux": ["linux"],
    "AWS": ["amazon web services", "aws"],
    "Microsoft Azure": ["microsoft azure", "azure"],
    "Google Cloud": ["google cloud", "gcp"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment"],
    "Postman": ["postman"],
    "pytest": ["pytest"],
    "Unit Testing": ["unit testing", "unit tests"],
    "Agile": ["agile"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "Generative AI": ["generative ai", "genai"],
    "LLMs": ["large language model", "large language models", "llm", "llms"],
    "Prompt Engineering": ["prompt engineering"],
    "Natural Language Processing": ["natural language processing", "nlp"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Power BI": ["power bi"],
    "Tableau": ["tableau"],
    "Microsoft Excel": ["microsoft excel", "excel"],
    "Apache Spark": ["apache spark", "pyspark", "spark"],
    "HTML Parsing": ["beautifulsoup", "beautiful soup"],
    "OAuth": ["oauth", "oauth2"],
    "JWT": ["jwt", "json web token"],
    "Microservices": ["microservices", "microservice architecture"],
    "OOP": ["object oriented programming", "oop"],
    "Data Structures": ["data structures"],
    "Algorithms": ["algorithms", "algorithm design"],
})

STOP_WORDS = {
    "the", "and", "for", "with", "you", "your", "are", "our", "this", "that",
    "from", "have", "has", "will", "can", "who", "what", "when", "where",
    "job", "role", "work", "team", "years", "year", "experience", "using",
    "about", "into", "their", "they", "them", "than", "then", "also", "such",
    "must", "should", "required", "preferred", "good", "strong", "plus",
    "ability", "skills", "skill", "responsibilities", "requirements",
}


def normalize_text(text):
    text = (text or "").lower()
    text = text.replace("&", " and ")
    return re.sub(r"\s+", " ", text).strip()


def _contains_term(text, term):
    """Match aliases as phrases/tokens to avoid substring false positives."""
    escaped = re.escape(term.strip().lower())
    if not escaped:
        return False
    pattern = r"(?<![a-z0-9])" + escaped + r"(?![a-z0-9])"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def extract_skills(text):
    normalized = normalize_text(text)
    found = []
    for skill, aliases in SKILL_CATALOG.items():
        terms = [skill, *aliases]
        if any(_contains_term(normalized, alias) for alias in terms):
            found.append(skill)
    return found


def extract_keywords(text, limit=30):
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]{2,}", normalize_text(text))
    counts = {}
    for word in words:
        cleaned = word.strip("./-")
        if len(cleaned) < 3 or cleaned in STOP_WORDS or cleaned.isdigit():
            continue
        counts[cleaned] = counts.get(cleaned, 0) + 1
    ordered = sorted(counts, key=lambda word: (-counts[word], word))
    return ordered[:limit]


def analyze_resume(resume_text, job_description):
    resume_text = (resume_text or "").strip()
    job_description = (job_description or "").strip()
    if len(resume_text) < 30:
        raise ValueError("Resume text must contain at least 30 characters.")
    if len(job_description) < 30:
        raise ValueError("Job description must contain at least 30 characters.")

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    matched = [skill for skill in job_skills if skill in resume_skills]
    missing = [skill for skill in job_skills if skill not in resume_skills]
    skill_coverage = len(matched) / len(job_skills) if job_skills else 0.0

    resume_words = set(extract_keywords(resume_text, limit=500))
    job_words = set(extract_keywords(job_description, limit=500))
    relevant_words = job_words
    keyword_matches = sorted(resume_words & relevant_words)
    keyword_coverage = (
        len(keyword_matches) / len(relevant_words) if relevant_words else 0.0
    )

    # Skill coverage is weighted more heavily than generic keyword overlap.
    score = round((0.8 * skill_coverage + 0.2 * keyword_coverage) * 100)
    recommendations = build_recommendations(matched, missing, keyword_matches)

    return {
        "match_score": max(0, min(100, score)),
        "matched_skills": matched,
        "missing_skills": missing,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "keyword_coverage": round(keyword_coverage * 100),
        "skill_coverage": round(skill_coverage * 100),
        "matched_keywords": keyword_matches[:20],
        "recommendations": recommendations,
        "summary": build_summary(score, matched, missing, job_skills),
    }


def build_recommendations(matched, missing, keyword_matches):
    recommendations = []
    if missing:
        recommendations.append(
            "Review the missing skills list. Add a skill only when you have "
            "genuine experience, coursework, or a project that demonstrates it: "
            + ", ".join(missing[:8]) + "."
        )
    else:
        recommendations.append(
            "The resume contains all detected job-description skills. "
            "Strengthen the evidence with specific project or work examples."
        )

    if matched:
        recommendations.append(
            "Move the strongest matching skills into relevant project or "
            "experience bullets, showing what you built and how you used them: "
            + ", ".join(matched[:6]) + "."
        )
    if keyword_matches:
        recommendations.append(
            "Use relevant job-description wording naturally where it accurately "
            "describes your work. Potential terms include: "
            + ", ".join(keyword_matches[:8]) + "."
        )
    recommendations.append(
        "Quantify outcomes only when you can verify the figures. Do not add "
        "unfamiliar technologies or unsupported claims just to increase a score."
    )
    return recommendations


def build_summary(score, matched, missing, job_skills):
    if not job_skills:
        return (
            "No catalog skills were detected in the job description. "
            "Add role-specific terms to the skill catalog for a more useful analysis."
        )
    if score >= 75:
        level = "strong"
    elif score >= 45:
        level = "moderate"
    else:
        level = "limited"
    return (
        f"This is a {level} keyword and skill alignment based on the terms detected. "
        f"{len(matched)} of {len(job_skills)} detected job skills matched; "
        f"{len(missing)} were not found in the resume text."
    )
