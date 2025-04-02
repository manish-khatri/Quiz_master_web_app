from flask_restful import Resource, reqparse
from flask import jsonify
from ..models import db, Quiz
import uuid

quiz_parser = reqparse.RequestParser()
quiz_parser.add_argument('q_name', type=str, required=True, help='Quiz name is required')
quiz_parser.add_argument('chp_id', type=str, required=True, help='Chapter ID is required')
quiz_parser.add_argument('sub_id', type=str, required=True, help='Subject ID is required')
quiz_parser.add_argument('date_of_quiz', type=str)
quiz_parser.add_argument('time_dur', type=str)

class QuizResource(Resource):
    def get(self):
        quizzes = Quiz.query.all()
        return jsonify([{
            'q_id': quiz.q_id,
            'q_name': quiz.q_name,
            'chp_id': quiz.chp_id,
            'sub_id': quiz.sub_id,
            'date_of_quiz': str(quiz.date_of_quiz),
            'time_dur': str(quiz.time_dur)
        } for quiz in quizzes])

    def post(self):
        data = quiz_parser.parse_args()
        new_quiz = Quiz(
            q_id='Qz' + str(uuid.uuid4().hex[:8]),
            q_name=data['q_name'],
            chp_id=data['chp_id'],
            sub_id=data['sub_id'],
            date_of_quiz=data.get('date_of_quiz', None),
            time_dur=data.get('time_dur', None)
        )
        db.session.add(new_quiz)
        db.session.commit()
        return {'message': 'Quiz created successfully', 'quiz': data}, 201
