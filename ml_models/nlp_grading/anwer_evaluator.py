import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import logging
from transformers import AutoTokenizer, AutoModel

logger = logging.getLogger(__name__)

class AnswerEvaluator:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        """Initialize answer evaluator with pre-trained model"""
        try:
            self.sentence_model = SentenceTransformer(model_name)
            logger.info(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            self.sentence_model = None
        
        # Initialize text processor
        from .text_processor import TextProcessor
        self.text_processor = TextProcessor()
    
    def get_embeddings(self, texts):
        """Get sentence embeddings for texts"""
        if self.sentence_model is None:
            logger.error("Sentence model not loaded")
            return None
        
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            embeddings = self.sentence_model.encode(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return None
    
    def calculate_similarity(self, text1, text2):
        """Calculate semantic similarity between two texts"""
        embeddings = self.get_embeddings([text1, text2])
        if embeddings is None:
            return 0.0
        
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(similarity)
    
    def evaluate_answer(self, student_answer, model_answer, rubric=None):
        """Evaluate student answer against model answer"""
        evaluation = {
            'semantic_similarity': 0.0,
            'keyword_coverage': 0.0,
            'length_ratio': 0.0,
            'overall_score': 0.0,
            'feedback': []
        }
        
        # Calculate semantic similarity
        semantic_sim = self.calculate_similarity(student_answer, model_answer)
        evaluation['semantic_similarity'] = semantic_sim
        
        # Extract keywords from model answer
        model_keywords = self.text_processor.extract_keywords(model_answer)
        student_keywords = self.text_processor.extract_keywords(student_answer)
        
        # Calculate keyword coverage
        if model_keywords:
            covered_keywords = set(student_keywords) & set(model_keywords)
            keyword_coverage = len(covered_keywords) / len(model_keywords)
            evaluation['keyword_coverage'] = keyword_coverage
            
            # Provide feedback on missing keywords
            missing_keywords = set(model_keywords) - set(student_keywords)
            if missing_keywords:
                evaluation['feedback'].append(
                    f"Consider discussing: {', '.join(list(missing_keywords)[:3])}"
                )
        
        # Calculate length ratio
        student_length = len(student_answer.split())
        model_length = len(model_answer.split())
        length_ratio = min(student_length / model_length, 1.0) if model_length > 0 else 0
        evaluation['length_ratio'] = length_ratio
        
        # Apply rubric if provided
        if rubric:
            evaluation = self._apply_rubric(evaluation, rubric)
        else:
            # Default scoring weights
            evaluation['overall_score'] = (
                0.5 * semantic_sim +
                0.3 * keyword_coverage +
                0.2 * length_ratio
            )
        
        # Generate feedback
        if evaluation['overall_score'] < 0.5:
            evaluation['feedback'].append("Your answer needs more detail and coverage of key concepts.")
        elif evaluation['overall_score'] < 0.7:
            evaluation['feedback'].append("Good attempt, but some important points are missing.")
        elif evaluation['overall_score'] < 0.9:
            evaluation['feedback'].append("Very good answer with minor gaps.")
        else:
            evaluation['feedback'].append("Excellent answer!")
        
        return evaluation
    
    def _apply_rubric(self, evaluation, rubric):
        """Apply custom rubric to evaluation"""
        # Rubric format: {'weights': {'semantic': 0.5, 'keywords': 0.3, 'length': 0.2}, 
        #                 'required_keywords': [...], 'min_length': 50}
        
        weights = rubric.get('weights', {})
        evaluation['overall_score'] = (
            weights.get('semantic', 0.5) * evaluation['semantic_similarity'] +
            weights.get('keywords', 0.3) * evaluation['keyword_coverage'] +
            weights.get('length', 0.2) * evaluation['length_ratio']
        )
        
        # Check required keywords
        if 'required_keywords' in rubric:
            required = set(rubric['required_keywords'])
            student_text = evaluation.get('student_answer', '').lower()
            missing_required = [kw for kw in required if kw.lower() not in student_text]
            
            if missing_required:
                evaluation['overall_score'] *= 0.8  # Penalty for missing required keywords
                evaluation['feedback'].append(
                    f"Missing required concepts: {', '.join(missing_required)}"
                )
        
        return evaluation
