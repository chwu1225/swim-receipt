"""
Main Routes - Home page and navigation (Demo Mode)
"""
from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page - redirect to dashboard"""
    return redirect(url_for('main.dashboard'))


@main_bp.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')
