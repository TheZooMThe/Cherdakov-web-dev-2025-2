from app.models import Course, Review
from sqlalchemy.orm import joinedload

class CourseRepository:
    def __init__(self, db):
        self.db = db

    def _all_query(self, name, category_ids):
        query = self.db.select(Course)

        if name:
            query = query.filter(Course.name.ilike(f'%{name}%'))

        if category_ids:
            query = query.filter(Course.category_id.in_(category_ids))

        return query

    def get_pagination_info(self, name=None, category_ids=None):
        query = self._all_query(name, category_ids)
        return self.db.paginate(query)

    def get_all_courses(self, name=None, category_ids=None, pagination=None):
        if pagination is not None:
            return pagination.items 
        
        return self.db.session.execute(self._all_query(name, category_ids)).scalars()

    def get_course_by_id(self, course_id):
        return self.db.session.get(Course, course_id)
    
    def new_course(self):
        return Course()

    def add_course(self, author_id, name, category_id, short_desc, full_desc, background_image_id):
        course = Course(
            author_id=author_id,
            name=name,
            category_id=category_id,
            short_desc=short_desc,
            full_desc=full_desc,
            background_image_id=background_image_id
        )
        try:
            self.db.session.add(course)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e  # Пробрасываем любое другое исключение
        
        return course
    

    def get_reviews_query(self, course_id):
        return self.db.session.query(Review).options(joinedload(Review.user)).filter(Review.course_id == course_id)
    
    def course_exists(self, course_id):
        return self.db.session.query(Course.id).filter_by(id=course_id).scalar() is not None

    def get_recent_reviews(self, course_id, limit=5):
        return (
            self.db.session.query(Review)
            .options(joinedload(Review.user))
            .filter(Review.course_id == course_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_user_review(self, course_id, user_id):
        return (
            self.db.session.query(Review)
            .filter_by(course_id=course_id, user_id=user_id)
            .first()
        )

    def has_user_reviewed(self, course_id, user_id):
        return self.get_user_review(course_id, user_id) is not None

    def create_review(self, course_id, user_id, rating, text):
        course = self.get_course_by_id(course_id)
        if not course:
            return None

        review = Review(
            course_id=course_id,
            user_id=user_id,
            rating=rating,
            text=text
        )
        self.db.session.add(review)
        course.rating_sum += rating
        course.rating_num += 1
        self.db.session.commit()
        return review
    
    def get_paginated_reviews(self, course_id, sort_order='new', page=1, per_page=5):
        """Возвращает пагинированные отзывы с сортировкой"""
        query = self.get_reviews_query(course_id)
        query = self._apply_review_sorting(query, sort_order)
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def _apply_review_sorting(self, query, sort_order):
        """Применяет сортировку к запросу отзывов"""
        if sort_order == 'positive':
            return query.order_by(Review.rating.desc(), Review.created_at.desc())
        elif sort_order == 'negative':
            return query.order_by(Review.rating.asc(), Review.created_at.desc())
        else:  
            return query.order_by(Review.created_at.desc())