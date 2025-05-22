from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
import sys
import traceback
import logging

# 配置日志
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.info(f"尝试登录: 用户名={username}")
        
        try:
            user = User.get_by_username(username)
            
            if user:
                logger.info(f"找到用户: id={user.id}, 用户名={user.username}, 角色={user.role}")
                logger.info(f"存储的密码={user.password}")
                
                # 直接比较密码
                if password == user.password:
                    logger.info("密码匹配成功，正在登录...")
                    
                    try:
                        login_user(user)
                        logger.info("Flask-Login登录成功")
                    except Exception as e:
                        logger.error(f"Flask-Login登录失败: {str(e)}")
                        logger.error(traceback.format_exc())
                        flash('登录过程出错，请联系管理员')
                        return render_template('login.html')
                    
                    try:
                        next_page = request.args.get('next')
                        redirect_url = next_page or url_for('orders.overview')
                        logger.info(f"准备重定向到: {redirect_url}")
                        return redirect(redirect_url)
                    except Exception as e:
                        logger.error(f"重定向失败: {str(e)}")
                        logger.error(traceback.format_exc())
                        flash('重定向失败，请联系管理员')
                        return render_template('login.html')
                else:
                    logger.warning(f"密码不匹配: 输入={password}, 存储={user.password}")
                    flash('密码错误')
            else:
                logger.warning(f"用户 {username} 不存在")
                flash('用户不存在')
        except Exception as e:
            logger.error(f"登录过程中发生异常: {str(e)}")
            logger.error(traceback.format_exc())
            flash('登录过程出错，请联系管理员')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logger.info(f"用户 {current_user.username} 正在登出")
    logout_user()
    return redirect(url_for('auth.login'))