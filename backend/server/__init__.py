from flask import Flask, request
from flask_jwt_extended import JWTManager
from .db import init_casedb, initialize_database
from .login import login_bp
from .signup import signup_bp
from .comment import comment_bp
from .files import files_bp
from .newcase import newcase_bp
from .case import case_bp
from .db_thread import DBThread
from .similarity import similarity_bp
from .search import search_bp
from .emailthread import emlthread_bp
from .dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'WEBTOPSy'
    jwt = JWTManager(app)
    init_casedb()
    initialize_database()
    app.register_blueprint(login_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(newcase_bp)
    app.register_blueprint(case_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(similarity_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(emlthread_bp)
    app.register_blueprint(dashboard_bp)


    app.db_thread = DBThread()

    @app.route('/shutdown', methods=['POST'])
    def shutdown():
        app.db_thread.stop()
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return 'Server shutting down...'

    return app