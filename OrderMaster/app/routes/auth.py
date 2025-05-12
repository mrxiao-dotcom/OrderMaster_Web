from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
import sys
import traceback

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"尝试登录: 用户名={username}, 密码={password}", file=sys.stderr)
        
        try:
            user = User.get_by_username(username)
            
            if user:
                print(f"找到用户: id={user.id}, 用户名={user.username}, 角色={user.role}", file=sys.stderr)
                print(f"存储的密码={user.password}", file=sys.stderr)
                
                # 直接比较密码
                if password == user.password:
                    print("密码匹配成功，正在登录...", file=sys.stderr)
                    
                    try:
                        login_user(user)
                        print("Flask-Login登录成功", file=sys.stderr)
                    except Exception as e:
                        print(f"Flask-Login登录失败: {str(e)}", file=sys.stderr)
                        print(traceback.format_exc(), file=sys.stderr)
                        flash('登录过程出错，请联系管理员')
                        return render_template('login.html')
                    
                    try:
                        next_page = request.args.get('next')
                        redirect_url = next_page or url_for('orders.overview')
                        print(f"准备重定向到: {redirect_url}", file=sys.stderr)
                        return redirect(redirect_url)
                    except Exception as e:
                        print(f"重定向失败: {str(e)}", file=sys.stderr)
                        print(traceback.format_exc(), file=sys.stderr)
                        flash('重定向失败，请联系管理员')
                        return render_template('login.html')
                else:
                    print(f"密码不匹配: 输入={password}, 存储={user.password}", file=sys.stderr)
                    flash('密码错误')
            else:
                print(f"用户 {username} 不存在", file=sys.stderr)
                flash('用户不存在')
        except Exception as e:
            print(f"登录过程中发生异常: {str(e)}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            flash('登录过程出错，请联系管理员')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    print(f"用户 {current_user.username} 正在登出", file=sys.stderr)
    logout_user()
    return redirect(url_for('auth.login'))