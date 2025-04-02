# from flask import Blueprint
# from flask_restful import Api

# api_bp = Blueprint('api', __name__, url_prefix='/api')
# api = Api(api_bp)


# def init_api(app):
#     from .subject_api import SubjectResource, SubjectDetailResource
#     from .chapter_api import ChapterResource
#     from .quiz_api import QuizResource

#     api.add_resource(SubjectResource, '/subjects')
#     api.add_resource(SubjectDetailResource, '/subjects/<string:sub_id>')

#     api.add_resource(ChapterResource, '/chapters')

#     api.add_resource(QuizResource, '/quizzes')

#     app.register_blueprint(api_bp)

from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)


def init_api(app):
    from .subject_api import SubjectResource, SubjectDetailResource
    from .chapter_api import ChapterResource
    from .quiz_api import QuizResource

    api.add_resource(SubjectResource, '/subjects')
    api.add_resource(SubjectDetailResource, '/subjects/<string:sub_id>')

    api.add_resource(ChapterResource, '/chapters')

    api.add_resource(QuizResource, '/quizzes')

    app.register_blueprint(api_bp)
