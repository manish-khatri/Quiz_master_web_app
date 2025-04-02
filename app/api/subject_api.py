from flask_restful import Resource, reqparse
from flask import jsonify
from ..models import db, Subject
import uuid

subject_parser = reqparse.RequestParser()
subject_parser.add_argument('sub_name', type=str, required=True, help='Subject name is required')
subject_parser.add_argument('sub_desc', type=str)

class SubjectResource(Resource):
    def get(self):
        subjects = Subject.query.all()
        return jsonify([{'sub_id': sub.sub_id, 'sub_name': sub.sub_name, 'sub_desc': sub.sub_desc} for sub in subjects])

    def post(self):
        data = subject_parser.parse_args()
        new_subject = Subject(
            sub_id='S' + str(uuid.uuid4().hex[:8]),
            sub_name=data['sub_name'],
            sub_desc=data.get('sub_desc', '')
        )
        db.session.add(new_subject)
        db.session.commit()
        return {'message': 'Subject created successfully', 'subject': data}, 201

class SubjectDetailResource(Resource):
    def get(self, sub_id):
        subject = Subject.query.get(sub_id)
        if not subject:
            return {'message': 'Subject not found'}, 404
        return jsonify({'sub_id': subject.sub_id, 'sub_name': subject.sub_name, 'sub_desc': subject.sub_desc})

    def put(self, sub_id):
        subject = Subject.query.get(sub_id)
        if not subject:
            return {'message': 'Subject not found'}, 404
        data = subject_parser.parse_args()
        subject.sub_name = data['sub_name']
        subject.sub_desc = data.get('sub_desc', subject.sub_desc)
        db.session.commit()
        return {'message': 'Subject updated successfully'}

    def delete(self, sub_id):
        subject = Subject.query.get(sub_id)
        if not subject:
            return {'message': 'Subject not found'}, 404
        db.session.delete(subject)
        db.session.commit()
        return {'message': 'Subject deleted successfully'}
