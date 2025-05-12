from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.contract import Contract
from app.models.order import Order
from app.models.account import Account
from datetime import datetime

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/')
@login_required
def overview():
    status_filter = request.args.get('status', 'active')
    
    if status_filter == 'active':
        contracts = Contract.get_active_contracts()
    else:
        contracts = Contract.get_exited_contracts()
    
    # 添加调试日志
    print(f"当前用户角色: {current_user.role}")
    print(f"是否为决策者: {current_user.role == 'decision_maker'}")
    print(f"是否为下单员: {current_user.role == 'executor'}")
    
    return render_template('orders/overview.html', 
                          contracts=contracts, 
                          status_filter=status_filter,
                          is_decision_maker=current_user.role == 'decision_maker')

@orders_bp.route('/contract/new', methods=['GET', 'POST'])
@login_required
def new_contract():
    if current_user.role != 'decision_maker':
        flash('只有决策者可以创建新合约')
        return redirect(url_for('orders.overview'))
    
    if request.method == 'POST':
        # 处理表单数据
        contract_data = {
            'contract_name': request.form.get('contract_name'),
            'period': request.form.get('period'),
            'stop_loss_amount': request.form.get('stop_loss_amount'),
            'bollinger_period': request.form.get('bollinger_period'),
            'created_by': current_user.id,
            'entry_time': request.form.get('entry_time'),
            'period_upgrade_time': request.form.get('period_upgrade_time'),
            'ma_price': request.form.get('ma_price'),
            'price': request.form.get('price'),  # 使用单个价格字段
            'actual_entry_price': request.form.get('actual_entry_price'),
            'stop_loss_price': request.form.get('stop_loss_price')
        }
        
        # 处理数值字段
        for field in ['ma_price', 'price', 'actual_entry_price', 'stop_loss_price']:
            if contract_data[field]:
                contract_data[field] = float(contract_data[field])
        
        contract_id = Contract.create(contract_data)
        
        # 处理关联账户（多选）
        account_ids = request.form.getlist('account_ids')
        for account_id in account_ids:
            Order.create({
                'contract_id': contract_id,
                'account_id': account_id,
                'status': 'pending'
            })
        
        flash('合约创建成功')
        return redirect(url_for('orders.overview'))
    
    # 获取可用账户列表
    available_accounts = Account.get_available_accounts()
    return render_template('orders/edit_contract.html', accounts=available_accounts)

@orders_bp.route('/contract/<int:contract_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contract(contract_id):
    if current_user.role != 'decision_maker':
        flash('只有决策者可以修改合约')
        return redirect(url_for('orders.overview'))
    
    contract = Contract.get_by_id(contract_id)
    
    # 检查是否所有关联订单都是待执行状态
    if not Order.all_pending_by_contract(contract_id):
        flash('有订单已执行，无法修改合约')
        return redirect(url_for('orders.overview'))
    
    if request.method == 'POST':
        # 处理表单数据
        contract_data = {
            'contract_name': request.form.get('contract_name'),
            'period': request.form.get('period'),
            'stop_loss_amount': request.form.get('stop_loss_amount'),
            'bollinger_period': request.form.get('bollinger_period')
        }
        
        Contract.update(contract_id, contract_data)
        flash('合约更新成功')
        return redirect(url_for('orders.overview'))
    
    return render_template('orders/edit_contract.html', contract=contract)

@orders_bp.route('/contract/<int:contract_id>/accounts', methods=['GET', 'POST'])
@login_required
def contract_accounts(contract_id):
    if current_user.role != 'decision_maker':
        flash('只有决策者可以管理合约关联账号')
        return redirect(url_for('orders.overview'))
    
    contract = Contract.get_by_id(contract_id)
    if not contract:
        flash('合约不存在')
        return redirect(url_for('orders.overview'))
    
    # 获取当前关联的订单
    orders = Order.get_by_contract(contract_id)
    existing_account_ids = [order['account_id'] for order in orders]
    
    # 获取可用的账号列表（排除已关联的账号）
    available_accounts = Account.get_available_accounts()
    
    return render_template('orders/contract_accounts.html',
                         contract=contract,
                         orders=orders,
                         available_accounts=available_accounts,
                         existing_account_ids=existing_account_ids)

@orders_bp.route('/contract/<int:contract_id>/accounts/add', methods=['POST'])
@login_required
def add_account(contract_id):
    if current_user.role != 'decision_maker':
        flash('只有决策者可以添加关联账号')
        return redirect(url_for('orders.overview'))
    
    contract = Contract.get_by_id(contract_id)
    if not contract:
        flash('合约不存在')
        return redirect(url_for('orders.overview'))
    
    # 获取选中的账号ID列表
    account_ids = request.form.getlist('account_ids')
    if not account_ids:
        flash('请选择要添加的账号')
        return redirect(url_for('orders.contract_accounts', contract_id=contract_id))
    
    # 为每个选中的账号创建订单
    for account_id in account_ids:
        Order.create({
            'contract_id': contract_id,
            'account_id': account_id,
            'status': 'pending'
        })
    
    flash('账号添加成功')
    return redirect(url_for('orders.contract_accounts', contract_id=contract_id))

@orders_bp.route('/contract/<int:contract_id>/accounts/<int:order_id>/remove', methods=['POST'])
@login_required
def remove_account(contract_id, order_id):
    if current_user.role != 'decision_maker':
        flash('只有决策者可以移除关联账号')
        return redirect(url_for('orders.overview'))
    
    order = Order.get_by_id(order_id)
    if not order or order['contract_id'] != contract_id:
        flash('订单不存在')
        return redirect(url_for('orders.contract_accounts', contract_id=contract_id))
    
    if order['status'] != 'pending':
        flash('只能移除待执行状态的订单')
        return redirect(url_for('orders.contract_accounts', contract_id=contract_id))
    
    # 删除订单
    Order.delete(order_id)
    flash('账号移除成功')
    return redirect(url_for('orders.contract_accounts', contract_id=contract_id))

@orders_bp.route('/order/<int:order_id>/execute', methods=['POST'])
@login_required
def execute_order(order_id):
    # 检查用户权限
    if current_user.role != 'executor':
        return jsonify({'success': False, 'message': '只有下单员可以执行订单'}), 403
    
    # 获取订单信息
    order = Order.get_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'message': '订单不存在'}), 404
    
    # 检查订单状态
    if order['status'] != 'pending':
        return jsonify({'success': False, 'message': '只能执行待执行状态的订单'}), 400
    
    try:
        # 执行订单
        Order.execute(order_id, current_user.id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/order/<int:order_id>/exit', methods=['POST'])
@login_required
def exit_order(order_id):
    # 检查用户权限
    if current_user.role != 'executor':
        return jsonify({'success': False, 'message': '只有下单员可以执行出场操作'}), 403
    
    # 获取订单信息
    order = Order.get_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'message': '订单不存在'}), 404
    
    # 检查订单状态
    if order['status'] != 'executed':
        return jsonify({'success': False, 'message': '只能出场已执行状态的订单'}), 400
    
    # 获取出场价格
    exit_price = request.form.get('exit_price')
    if not exit_price:
        return jsonify({'success': False, 'message': '请输入出场价格'}), 400
    
    try:
        # 执行出场
        Order.exit(order_id, float(exit_price), current_user.id)
        return jsonify({'success': True})
    except ValueError:
        return jsonify({'success': False, 'message': '出场价格格式不正确'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500