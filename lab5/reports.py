from flask import Blueprint, render_template, request, make_response
from models import VisitLog, User, db
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/visits')
def visit_log():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    visits = VisitLog.query.order_by(VisitLog.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('visit_log.html', visits=visits)

@reports_bp.route('/pages')
def pages_report():
    query = (
        db.session.query(
            VisitLog.path,
            func.count(VisitLog.id).label('total')
        )
        .group_by(VisitLog.path)
        .order_by(func.count(VisitLog.id).desc())
    )
    report = query.all()
    return render_template('pages_report.html', report=report)

@reports_bp.route('/users')
def users_report():
    query = (
        db.session.query(
            User,
            func.count(VisitLog.id).label('total')
        )
        .outerjoin(VisitLog, VisitLog.user_id == User.id)
        .group_by(User.id)
        .order_by(func.count(VisitLog.id).desc())
    )
    report = query.all()
    return render_template('users_report.html', report=report)

@reports_bp.route('/export/<report_type>')
def export_csv(report_type):
    if report_type == 'pages':
        data = db.session.query(VisitLog.path, func.count(VisitLog.id)).group_by(VisitLog.path).all()
        csv_content = "Страница,Количество посещений\n" + "\n".join([f"{row[0]},{row[1]}" for row in data])
    elif report_type == 'users':
        data = db.session.query(User, func.count(VisitLog.id)).outerjoin(VisitLog).group_by(User.id).all()
        csv_content = "Пользователь,Количество посещений\n" + "\n".join([f"{row[0].get_fullname() if row[0] else 'Неаутентифицированный'},{row[1]}" for row in data])
    else:
        return "Invalid report type", 400

    response = make_response(csv_content)
    response.headers['Content-Disposition'] = f'attachment; filename={report_type}_report.csv'
    response.headers['Content-type'] = 'text/csv'
    return response