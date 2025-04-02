from flask_restful import Resource, reqparse
from flask import jsonify
from ..models import db, Chapter
import uuid
chapter_parser = reqparse.RequestParser()
chapter_parser.add_argument('chp_name', type=str, required=True, help='Chapter name is required')
chapter_parser.add_argument('chp_desc', type=str)
chapter_parser.add_argument('sub_id', type=str, required=True, help='Subject ID is required')


class ChapterResource(Resource):
    def get(self):
        chapters = Chapter.query.all()
        return jsonify([{
            'chp_id': chp.chp_id,
            'chp_name': chp.chp_name,
            'chp_desc': chp.chp_desc,
            'sub_id': chp.sub_id
        } for chp in chapters])

    def post(self):
        data = chapter_parser.parse_args()
        new_chapter = Chapter(
            chp_id='C' + str(uuid.uuid4().hex[:8]),
            chp_name=data['chp_name'],
            chp_desc=data.get('chp_desc', ''),
            sub_id=data['sub_id']
        )
        db.session.add(new_chapter)
        db.session.commit()
        return {'message': 'Chapter created successfully', 'chapter': data}, 201
