from flask import Flask, render_template, Blueprint, request

main_views_bp = Blueprint('main_views', __name__)
app = Flask(__name__)


def create_app(app):
    app.register_blueprint(main_views_bp)
    return app


@main_views_bp.route('/')
def index():
	return render_template('index.html')
