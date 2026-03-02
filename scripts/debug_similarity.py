import os
import sys

# Ensure backend package is importable when running from workspace root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.nlp.preprocessing import TextPreprocessor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

text = 'Python developer with React experience'
pre = TextPreprocessor(lowercase=True, remove_stop_words=False)
job = pre.preprocess_for_tfidf(text)
resume = pre.preprocess_for_tfidf(text)
print('processed:', job)
vec = TfidfVectorizer(max_features=5000, ngram_range=(1,2), stop_words='english', min_df=1, max_df=0.95, sublinear_tf=True)
m = vec.fit_transform([job, resume])
print('shape:', m.shape)
print('vocab size:', len(vec.vocabulary_))
print('vocab sample:', list(vec.vocabulary_.keys())[:20])
sim = cosine_similarity(m[0:1], m[1:2])[0][0]
print('similarity:', sim)
