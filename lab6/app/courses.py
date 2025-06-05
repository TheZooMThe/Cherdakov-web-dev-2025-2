from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from app.models import db
from app.repositories import CourseRepository, UserRepository, CategoryRepository, ImageRepository
from app.models import Course, Review
user_repository = UserRepository(db)
course_repository = CourseRepository(db)
category_repository = CategoryRepository(db)
image_repository = ImageRepository(db)


bp = Blueprint('courses', __name__)

COURSE_PARAMS = [
    'author_id', 'name', 'category_id', 'short_desc', 'full_desc'
]

def params():
    return { p: request.form.get(p) or None for p in COURSE_PARAMS }

def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': [x for x in request.args.getlist('category_ids') if x],
    }

@bp.route('/')
def index():
    pagination = course_repository.get_pagination_info(**search_params())
    courses = course_repository.get_all_courses(pagination=pagination)
    categories = category_repository.get_all_categories()
    return render_template('courses/index.html',
                           courses=courses,
                           categories=categories,
                           pagination=pagination,
                           search_params=search_params())

@bp.route('/new')
@login_required
def new():
    course = course_repository.new_course()
    categories = category_repository.get_all_categories()
    users = user_repository.get_all_users()
    return render_template('courses/new.html',
                           categories=categories,
                           users=users,
                           course=course)

@bp.route('/create', methods=['POST'])
@login_required
def create():
    f = request.files.get('background_img')
    img = None
    course = None 

    try:
        if f and f.filename:
            img = image_repository.add_image(f)

        image_id = img.id if img else None
        course = course_repository.add_course(**params(), background_image_id=image_id)
    except IntegrityError as err:
        flash(f'Возникла ошибка при записи данных в БД. Проверьте корректность введённых данных. ({err})', 'danger')
        categories = category_repository.get_all_categories()
        users = user_repository.get_all_users()
        return render_template('courses/new.html',
                            categories=categories,
                            users=users,
                            course=course)

    flash(f'Курс {course.name} был успешно добавлен!', 'success')

    return redirect(url_for('courses.index'))

from flask_login import current_user




@bp.route('/<int:course_id>')
def show_course(course_id):
    course = course_repository.get_course_by_id(course_id)
    if course is None:
        abort(404)

    recent_reviews = course_repository.get_recent_reviews(course_id)

    user_review = None
    if current_user.is_authenticated:
        user_review = course_repository.get_user_review(course_id, current_user.id)

    return render_template('courses/show.html',
                           course=course,
                           recent_reviews=recent_reviews,
                           user_review=user_review)


@bp.route('/courses/<int:course_id>/reviews/create', methods=['POST'])
@login_required
def create_review(course_id):
    rating = int(request.form.get('rating', 5))
    text = request.form.get('text', '').strip()

    if not text:
        flash('Текст отзыва не может быть пустым.', 'danger')
        return redirect(url_for('courses.show_course', course_id=course_id))

    if not course_repository.course_exists(course_id):
        abort(404)

    if course_repository.has_user_reviewed(course_id, current_user.id):
        flash('Вы уже оставили отзыв на этот курс.', 'warning')
        return redirect(url_for('courses.show_course', course_id=course_id))

    course_repository.create_review(course_id, current_user.id, rating, text)
    flash('Отзыв успешно добавлен.', 'success')
    return redirect(url_for('courses.show_course', course_id=course_id))

@bp.route('/courses/<int:course_id>/reviews')
def reviews(course_id):
    course = course_repository.get_course_by_id(course_id)
    if course is None:
        abort(404)

    sort_order = request.args.get('sort', 'new')
    page = request.args.get('page', 1, type=int)
    per_page = 5

    pagination = course_repository.get_paginated_reviews(
        course_id, 
        sort_order, 
        page, 
        per_page
    )
    reviews = pagination.items

    return render_template('courses/reviews.html',
                           course=course,
                           reviews=reviews,
                           pagination=pagination,
                           sort_order=sort_order)
