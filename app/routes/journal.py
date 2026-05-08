from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.journal import Journal, Schedule
from datetime import datetime, date

journal_bp = Blueprint('journal', __name__)

@journal_bp.route('/journal')
@login_required
def index():
    journals = Journal.query.filter_by(user_id=current_user.id)\
        .order_by(Journal.is_pinned.desc(), Journal.updated_at.desc()).all()
    schedules = Schedule.query.filter_by(user_id=current_user.id)\
        .filter(Schedule.date >= date.today())\
        .order_by(Schedule.date.asc()).limit(5).all()
    return render_template('journal/index.html', journals=journals, schedules=schedules)

@journal_bp.route('/journal/new', methods=['GET', 'POST'])
@login_required
def new():
    jtype = request.args.get('type', 'note')
    if request.method == 'POST':
        journal = Journal(
            user_id=current_user.id,
            title=request.form.get('title', 'Tanpa Judul'),
            content=request.form.get('content', ''),
            mood=request.form.get('mood', 'happy'),
            color=request.form.get('color', 'pink'),
            type=request.form.get('type', 'note')
        )
        db.session.add(journal)
        db.session.commit()
        flash('Jurnal berhasil disimpan! 📖', 'success')
        return redirect(url_for('journal.view', journal_id=journal.id))
    return render_template('journal/editor.html', journal=None, jtype=jtype)

@journal_bp.route('/journal/<int:journal_id>')
@login_required
def view(journal_id):
    journal = Journal.query.get_or_404(journal_id)
    if journal.user_id != current_user.id:
        return redirect(url_for('journal.index'))
    return render_template('journal/view.html', journal=journal)

@journal_bp.route('/journal/<int:journal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(journal_id):
    journal = Journal.query.get_or_404(journal_id)
    if journal.user_id != current_user.id:
        return redirect(url_for('journal.index'))
    if request.method == 'POST':
        journal.title = request.form.get('title', journal.title)
        journal.content = request.form.get('content', journal.content)
        journal.mood = request.form.get('mood', journal.mood)
        journal.color = request.form.get('color', journal.color)
        journal.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Jurnal diperbarui! 📖', 'success')
        return redirect(url_for('journal.view', journal_id=journal.id))
    return render_template('journal/editor.html', journal=journal, jtype=journal.type)

@journal_bp.route('/journal/<int:journal_id>/delete', methods=['POST'])
@login_required
def delete(journal_id):
    journal = Journal.query.get_or_404(journal_id)
    if journal.user_id != current_user.id:
        return jsonify({'success': False})
    db.session.delete(journal)
    db.session.commit()
    return jsonify({'success': True})

@journal_bp.route('/journal/<int:journal_id>/pin', methods=['POST'])
@login_required
def pin(journal_id):
    journal = Journal.query.get_or_404(journal_id)
    if journal.user_id != current_user.id:
        return jsonify({'success': False})
    journal.is_pinned = not journal.is_pinned
    db.session.commit()
    return jsonify({'success': True, 'pinned': journal.is_pinned})

@journal_bp.route('/journal/<int:journal_id>/favorite', methods=['POST'])
@login_required
def favorite(journal_id):
    journal = Journal.query.get_or_404(journal_id)
    if journal.user_id != current_user.id:
        return jsonify({'success': False})
    journal.is_favorite = not journal.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'favorite': journal.is_favorite})

@journal_bp.route('/journal/autosave/<int:journal_id>', methods=['POST'])
@login_required
def autosave(journal_id):
    journal = Journal.query.get_or_404(journal_id)
    if journal.user_id != current_user.id:
        return jsonify({'success': False})
    journal.content = request.json.get('content', journal.content)
    journal.title = request.json.get('title', journal.title)
    journal.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})

# Schedule routes
@journal_bp.route('/journal/schedule')
@login_required
def schedule():
    schedules = Schedule.query.filter_by(user_id=current_user.id)\
        .order_by(Schedule.date.asc(), Schedule.time.asc()).all()
    return render_template('journal/schedule.html', schedules=schedules, today=date.today())

@journal_bp.route('/journal/schedule/add', methods=['POST'])
@login_required
def add_schedule():
    try:
        sched = Schedule(
            user_id=current_user.id,
            title=request.form.get('title'),
            description=request.form.get('description', ''),
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            time=datetime.strptime(request.form.get('time'), '%H:%M').time() if request.form.get('time') else None,
            color=request.form.get('color', 'pink')
        )
        db.session.add(sched)
        db.session.commit()
        return jsonify({'success': True, 'id': sched.id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@journal_bp.route('/journal/schedule/<int:sched_id>/done', methods=['POST'])
@login_required
def done_schedule(sched_id):
    sched = Schedule.query.get_or_404(sched_id)
    if sched.user_id != current_user.id:
        return jsonify({'success': False})
    sched.is_done = not sched.is_done
    db.session.commit()
    return jsonify({'success': True, 'done': sched.is_done})

@journal_bp.route('/journal/schedule/<int:sched_id>/delete', methods=['POST'])
@login_required
def delete_schedule(sched_id):
    sched = Schedule.query.get_or_404(sched_id)
    if sched.user_id != current_user.id:
        return jsonify({'success': False})
    db.session.delete(sched)
    db.session.commit()
    return jsonify({'success': True})