"""Constants and terms for NLP processing."""

SKILL_HEADERS = [
    'skills', 'technical skills', 'core competencies', 'expertise',
    'technologies', 'tools', 'programming languages', 'key skills',
    'professional skills', 'summary of skills', 'competencies', 'experience'
]

EXPERIENCE_HEADERS = [
    'experience', 'work experience', 'employment', 'professional experience',
    'career', 'work history', 'employment history'
]

SKILL_ALIASES = {
    'html5': 'html',
    'css3': 'css',
    'reactjs': 'react',
    'react.js': 'react',
    'node.js': 'node',
    'nodejs': 'node',
    'vue.js': 'vue',
    'vuejs': 'vue',
    'angularjs': 'angular',
    'postgres': 'postgresql',
    'k8s': 'kubernetes',
    'golang': 'go',
    'aws': 'amazon web services',
    'gcp': 'google cloud',
    'machine learning': 'ml',
    'natural language processing': 'nlp'
}

TECH_PATTERNS = [
    r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|go|rust|php|swift|kotlin|ios|android)\b',
    r'\b(react(?:\.?js)?|angular(?:\.?js)?|vue(?:\.?js)?|node\.?js|django|flask|spring|express|uikit|swiftui)\b',
    r'\b(sql|mysql|postgresql|postgres|mongodb|redis|aws|docker|kubernetes|k8s|git|jenkins|ci/cd)\b',
    r'\b(machine learning|ml|nlp|data science|tensorflow|pytorch|pandas|numpy|ai)\b',
    r'\b(html5?|css3?|rest api|restful|json|graphql|agile|scrum|jira|ui|ux|ui/ux|ux/ui|qa)\b',
]

NEGATION_WORDS = [
    ' no ', ' not ', ' lack ', ' lacking ', ' without ', 
    ' bad at ', ' poor ', ' zero ', ' limited ', ' basic ', ' none ',
    " don't ", " dont ", " do not ", " didn't ", " didnt ", " did not ",
    " haven't ", " havent ", " have not "
]

GENERIC_WORDS = {
    'hands', 'managing', 'working', 'using', 'familiar', 'data', 'big', 'machine', 'learning', 'skill', 'skills',
    'plus', 'party', 'coding', 'development', 'developer', 'design', 'integration', 'application', 'business', 
    'analytical', 'quality', 'analysis', 'solutions', 'tool', 'tools', 'environment', 'team', 'degree', 'ms', 'bs',
    'language', 'languages', 'professional', 'ensure', 'education', 'new'
}

NOISE_KEYWORDS = {
    'experience', 'experienced', 'knowledge', 'understanding', 'proficiency', 'familiarity', 'ability', 'years'
}

STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
    'dare', 'ought', 'used', 'i', 'me', 'my', 'myself', 'we', 'our',
    'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
    'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
    'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would',
    'could', 'ought', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours',
    'into', 'onto', 'upon', 'about', 'above', 'below', 'under', 'over',
    'out', 'through', 'during', 'before', 'after', 'then', 'once', 'here',
    'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
    # Domain-specific noise words to ignore for scoring and highlighting
    'experience', 'experienced', 'skill', 'skills', 'year', 'years', 'knowledge',
    'ability', 'proficient', 'proficiency', 'familiar', 'familiarity', 'working',
    'using', 'required', 'requirements', 'responsibilities', 'responsibility',
    'professional', 'ensure', 'education', 'new'
}