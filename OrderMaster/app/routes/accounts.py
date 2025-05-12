from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.account import Account
from app.utils.db import with_db_retry

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')

@accounts_bp.route('/')
@login_required
@with_db_retry()
def list_accounts():
    account_type = request.args.get('type', 'all')
    
    if account_type == 'large':
        accounts = Account.get_by_type('large')
    elif account_type == 'small':
        accounts = Account.get_by_type('small')
    else:
        accounts = Account.get_all()
    
    return render_template('accounts/list.html', 
                          accounts=accounts, 
                          account_type=account_type)

@accounts_bp.route('/new', methods=['GET', 'POST'])
@login_required
@with_db_retry()
def new_account():
    if current_user.role != 'decision_maker':
        flash('只有决策者可以创建新账户')
        return redirect(url_for('accounts.list_accounts'))
    
    if request.method == 'POST':
        account_data = {
            'account_name': request.form.get('account_name'),
            'account_type': request.form.get('account_type'),
            'initial_value': request.form.get('initial_value'),
            'current_value': request.form.get('initial_value'),  # 初始时当前值等于初始值
            'risk_fund': request.form.get('risk_fund')
        }
        
        Account.create(account_data)
        flash('账户创建成功')
        return redirect(url_for('accounts.list_accounts'))
    
    return render_template('accounts/edit.html')

@accounts_bp.route('/<int:account_id>/edit', methods=['GET', 'POST'])
@login_required
@with_db_retry()
def edit_account(account_id):
    if current_user.role != 'decision_maker':
        flash('只有决策者可以修改账户')
        return redirect(url_for('accounts.list_accounts'))
    
    account = Account.get_by_id(account_id)
    if not account:
        flash('账户不存在')
        return redirect(url_for('accounts.list_accounts'))
    
    if request.method == 'POST':
        account_data = {
            'account_name': request.form.get('account_name'),
            'account_type': request.form.get('account_type'),
            'initial_value': request.form.get('initial_value'),
            'current_value': request.form.get('current_value'),
            'risk_fund': request.form.get('risk_fund')
        }
        
        Account.update(account_id, account_data)
        flash('账户更新成功')
        return redirect(url_for('accounts.list_accounts'))
    
    return render_template('accounts/edit.html', account=account)

@accounts_bp.route('/<int:account_id>/delete', methods=['POST'])
@login_required
@with_db_retry()
def delete_account(account_id):
    if current_user.role != 'decision_maker':
        flash('只有决策者可以删除账户')
        return redirect(url_for('accounts.list_accounts'))
    
    account = Account.get_by_id(account_id)
    if not account:
        flash('账户不存在')
        return redirect(url_for('accounts.list_accounts'))
    
    try:
        Account.delete(account_id)
        flash('账户删除成功')
    except Exception as e:
        flash(f'删除账户失败: {str(e)}')
    
    return redirect(url_for('accounts.list_accounts'))