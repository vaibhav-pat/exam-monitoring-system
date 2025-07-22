from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page - redirect based on authentication status"""
    if current_user.is_authenticated:
        if current_user.is_instructor():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('exam.index'))
    else:
        return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

