import spacy
import pandas as pd
import os
import json
from source import barsToScan

DATA_DIR='wordResults/'

common_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
            'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',
            'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do',
            'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
            'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 's', 't', 'can', 'will', 'just', 'should', 'now', '\'ve', '\'ll', '\'s', 'place', 'go',
            'austin', 'get', 'time', 'bar', 'bars', 'know', '\'re', '\'m', 'would', 'went', 'way', 'could', 'going',
            'make', 'take', 'say', 'what', 'gets', '\'d']

nlp=spacy.load('en')

def get_aspects(x):
    doc=nlp(x)  # Tokenize and extract grammatical components
    print(type(doc))
    doc=[i.text for i in doc if i.text not in common_words and i.pos_ in ['NOUN', 'PROPN', 'VERB']]  # Remove common words and retain only nouns
    print(type(doc))
    doc=list(map(lambda i: i.lower(),doc)) ## Normalize text to lower case
    print(type(doc))
    doc=pd.Series(doc)
    print(type(doc))
    #doc=doc.value_counts().head().index.tolist() ## Get 5 most frequent nouns
    doc = doc.value_counts()
    print(type(doc))
    return doc

def getWords():
	print('p')
	for bar in barsToScan:
		print('Processing {}'.format(bar))
		filename = bar.lower() + '.txt'
		#con=open(os.path.join(DATA_DIR, filename))
		con=open(os.path.join('barTextFiles/', filename))
		rev=con.read()
		con.close()

		results = {}
		tempResults = get_aspects(rev)
		for k,v in tempResults.items():
			if v > 4:
				results[k] = v
		for k,v in results.items():
			print(k,v)
		resultsFileName = bar.lower() + ' results.json'
		with open(os.path.join(DATA_DIR, resultsFileName), 'w') as f:
			json.dump(results, f)

