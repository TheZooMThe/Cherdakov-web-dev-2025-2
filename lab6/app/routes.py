from flask import Blueprint, render_template, send_from_directory, current_app, abort
from app.repositories import CategoryRepository, ImageRepository
from app.models import db
from app.models import Course, Review
from sqlalchemy.orm import joinedload

category_repository = CategoryRepository(db)
image_repository = ImageRepository(db)

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    categories = category_repository.get_all_categories()
    return render_template(
        'index.html',
        categories=categories,
    )

from flask import current_app

@bp.route('/images/<image_id>')
def image(image_id):
    img = image_repository.get_by_id(image_id)
    if img is None:
        abort(404)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], img.storage_filename)



