import json
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ScoringEngine:
    def __init__(self):
        """Initialize scoring engine"""
        from .answer_evaluator import AnswerEvaluator
        self.evaluator = AnswerEvaluator()
    
    def grade_exam(self, exam_session, questions, answers):
        """Grade an entire exam"""
        results = {
            'session_id': exam_session.id,
            'student_id': exam_session.student_id,
            'exam_id': exam_session.exam_id,
            'graded_at': datetime.now(),
            'questions': [],
            'total_score': 0,
            'max_score': 0
        }
        
        for question in questions:
            # Find student's answer
            student_answer = next(
                (a for a in answers if a.question_id == question.id), 
                None
            )
            
            if not student_answer or not student_answer.answer_text:
                # No answer provided
                question_result = {
                    'question_id': question.id,
                    'score': 0,
                    'max_score': question.max_score,
                    'feedback': 'No answer provided'
                }
            else:
                # Grade the answer
                question_result = self.grade_question(
                    question, 
                    student_answer.answer_text
                )
            
            results['questions'].append(question_result)
            results['total_score'] += question_result['score']
            results['max_score'] += question.max_score
        
        # Calculate percentage
        if results['max_score'] > 0:
            results['percentage'] = (results['total_score'] / results['max_score']) * 100
        else:
            results['percentage'] = 0
        
        return results
    
    def grade_question(self, question, student_answer):
        """Grade a single question"""
        result = {
            'question_id': question.id,
            'max_score': question.max_score,
            'score': 0,
            'feedback': '',
            'evaluation_details': {}
        }
        
        if question.question_type == 'objective':
            # Simple exact match for objective questions
            if student_answer.strip().lower() == question.correct_answer.strip().lower():
                result['score'] = question.max_score
                result['feedback'] = 'Correct!'
            else:
                result['score'] = 0
                result['feedback'] = 'Incorrect'
        
        elif question.question_type == 'subjective':
            # Use NLP evaluation for subjective questions
            rubric = None
            if question.rubric:
                try:
                    rubric = json.loads(question.rubric)
                except:
                    logger.warning(f"Invalid rubric format for question {question.id}")
            
            evaluation = self.evaluator.evaluate_answer(
                student_answer,
                question.answer_key,
                rubric
            )
            
            # Calculate score
            result['score'] = evaluation['overall_score'] * question.max_score
            result['feedback'] = ' '.join(evaluation['feedback'])
            result['evaluation_details'] = {
                'semantic_similarity': evaluation['semantic_similarity'],
                'keyword_coverage': evaluation['keyword_coverage'],
                'length_ratio': evaluation['length_ratio']
            }
        
        return result
    
    def generate_report(self, grading_results):
        """Generate a detailed grading report"""
        report = {
            'summary': {
                'total_score': grading_results['total_score'],
                'max_score': grading_results['max_score'],
                'percentage': grading_results['percentage'],
                'grade': self._calculate_grade(grading_results['percentage'])
            },
            'question_breakdown': [],
            'strengths': [],
            'areas_for_improvement': []
        }
        
        # Analyze each question
        for q_result in grading_results['questions']:
            percentage = (q_result['score'] / q_result['max_score'] * 100) if q_result['max_score'] > 0 else 0
            
            breakdown = {
                'question_id': q_result['question_id'],
                'score': q_result['score'],
                'max_score': q_result['max_score'],
                'percentage': percentage,
                'feedback': q_result['feedback']
            }
            
            if 'evaluation_details' in q_result:
                breakdown['details'] = q_result['evaluation_details']
            
            report['question_breakdown'].append(breakdown)
            
            # Identify strengths and weaknesses
            if percentage >= 80:
                report['strengths'].append(f"Question {q_result['question_id']}: Excellent understanding")
            elif percentage < 50:
                report['areas_for_improvement'].append(f"Question {q_result['question_id']}: Needs improvement")
        
        return report
    
    def _calculate_grade(self, percentage):
        """Calculate letter grade from percentage"""
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'