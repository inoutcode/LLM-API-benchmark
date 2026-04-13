"""
认证路由
"""
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from ..models import db, User


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    username = data['username']
    password = data['password']
    
    user = User.query.filter_by(username=username).first()
    
    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    login_user(user, remember=True)
    session.permanent = True
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """获取当前用户信息"""
    return jsonify({
        'user': current_user.to_dict()
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    data = request.get_json()
    
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Missing old_password or new_password'}), 400
    
    old_password = data['old_password']
    new_password = data['new_password']
    
    if not current_user.check_password(old_password):
        return jsonify({'error': 'Invalid old password'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200
