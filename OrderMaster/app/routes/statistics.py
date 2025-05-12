from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.models.order import Order
from app.models.contract import Contract
from app.models.account import Account

statistics_bp = Blueprint('statistics', __name__, url_prefix='/statistics')

@statistics_bp.route('/')
@login_required
def index():
    # 获取所有合约
    active_contracts = Contract.get_active_contracts()
    exited_contracts = Contract.get_exited_contracts()
    
    # 获取所有账户
    accounts = Account.get_all()
    
    # 这里可以添加更多统计数据的计算
    
    return render_template(
        'statistics/index.html',
        active_contracts=active_contracts,
        exited_contracts=exited_contracts,
        accounts=accounts
    )

@statistics_bp.route('/contracts/<int:contract_id>')
@login_required
def contract_statistics(contract_id):
    # 获取特定合约的详细信息
    contract = Contract.get_by_id(contract_id)
    if not contract:
        flash('合约不存在')
        return redirect(url_for('statistics.index'))
    
    # 获取该合约的所有订单
    orders = Order.get_by_contract(contract_id)
    
    # 这里可以添加更多针对特定合约的统计计算
    
    return render_template(
        'statistics/contract_detail.html',
        contract=contract,
        orders=orders
    )

@statistics_bp.route('/accounts/<int:account_id>')
@login_required
def account_statistics(account_id):
    # 获取特定账户的详细信息
    account = Account.get_by_id(account_id)
    if not account:
        flash('账户不存在')
        return redirect(url_for('statistics.index'))
    
    # 这里可以添加更多针对特定账户的统计计算
    
    return render_template(
        'statistics/account_detail.html',
        account=account
    )