import re
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        """Initialize text processor with NLP tools"""
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        # Initialize tools
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Load spaCy model
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            logger.warning("spaCy model not found. Some features will be limited.")
            self.nlp = None
    
    def clean_text(self, text):
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def tokenize(self, text):
        """Tokenize text into words"""
        return word_tokenize(text)
    
    def remove_stopwords(self, tokens):
        """Remove stopwords from token list"""
        return [token for token in tokens if token not in self.stop_words]
    
    def lemmatize(self, tokens):
        """Lemmatize tokens"""
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def process_text(self, text, remove_stop=True, lemmatize=True):
        """Full text preprocessing pipeline"""
        # Clean text
        text = self.clean_text(text)
        
        # Tokenize
        tokens = self.tokenize(text)
        
        # Remove stopwords
        if remove_stop:
            tokens = self.remove_stopwords(tokens)
        
        # Lemmatize
        if lemmatize:
            tokens = self.lemmatize(tokens)
        
        return tokens
    
    def extract_keywords(self, text, top_n=10):
        """Extract keywords using TF-IDF or spaCy"""
        if self.nlp:
            doc = self.nlp(text)
            # Extract noun phrases and named entities as keywords
            keywords = []
            
            # Add noun phrases
            for chunk in doc.noun_chunks:
                keywords.append(chunk.text.lower())
            
            # Add named entities
            for ent in doc.ents:
                keywords.append(ent.text.lower())
            
            # Add important single words (nouns and verbs)
            for token in doc:
                if token.pos_ in ['NOUN', 'VERB'] and not token.is_stop:
                    keywords.append(token.text.lower())
            
            # Remove duplicates and return top N
            keywords = list(set(keywords))
            return keywords[:top_n]
        else:
            # Fallback to simple frequency-based extraction
            tokens = self.process_text(text)
            freq_dist = nltk.FreqDist(tokens)
            return [word for word, freq in freq_dist.most_common(top_n)]
    
    def get_sentences(self, text):
        """Split text into sentences"""
        return sent_tokenize(text)

