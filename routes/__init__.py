from .auth_routes import auth_bp
from .course_routes import course_bp
from .assignment_routes import assignment_bp
from .forum_routes import forum_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(assignment_bp)
    app.register_blueprint(forum_bp)
