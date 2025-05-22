import sys
import logging
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from app.utils.db import get_db
from app.models.contract import Contract
from app.models.order import Order
from app.models.account import Account
from datetime import datetime

logger = logging.getLogger(__name__)
orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/')
@login_required
def overview():
    try:
        status_filter = request.args.get('status', 'active')
        logger.info(f"获取订单总览，状态过滤: {status_filter}")
        
        if status_filter == 'active':
            contracts = Contract.get_active_contracts()
        else:
            contracts = Contract.get_exited_contracts()
        
        # 对每个合约的 orders 按 account_id 去重，只保留每个账户最新的订单
        for contract in contracts:
            unique_orders = {}
            for order in contract['orders']:
                aid = order.get('account_id')
                if aid not in unique_orders:
                    unique_orders[aid] = order
                else:
                    # 保留 created_at 最新的
                    if order['created_at'] > unique_orders[aid]['created_at']:
                        unique_orders[aid] = order
            contract['orders'] = list(unique_orders.values())
        
        logger.info(f"获取到 {len(contracts)} 个合约")
        logger.debug(f"当前用户角色: {current_user.role}")
        logger.debug(f"是否为决策者: {current_user.role == 'decision_maker'}")
        logger.debug(f"是否为下单员: {current_user.role == 'executor'}")
        
        return render_template('orders/overview.html', 
                             contracts=contracts, 
                             status_filter=status_filter,
                             is_decision_maker=current_user.role == 'decision_maker')
    except Exception as e:
        logger.error(f"获取订单总览时出错: {str(e)}")
        logger.error(traceback.format_exc())
        flash('获取订单数据时出错，请稍后重试', 'error')
        return redirect(url_for('auth.login'))

@orders_bp.route('/contract/new', methods=['GET', 'POST'])
@login_required
def new_contract():
    if request.method == 'POST':
        try:
            print("接收到的表单数据:", request.form, file=sys.stderr)
            
            # 获取表单数据
            contract_data = {
                'contract_name': request.form.get('contract_name'),
                'period': request.form.get('period'),
                'stop_loss_amount': float(request.form.get('stop_loss_amount')),
                'entry_time': request.form.get('entry_time'),
                'period_upgrade_time': request.form.get('period_upgrade_time'),
                'ma_price': float(request.form.get('ma_price')) if request.form.get('ma_price') else None,
                'price': float(request.form.get('price')) if request.form.get('price') else None,
                'actual_entry_price': float(request.form.get('actual_entry_price')) if request.form.get('actual_entry_price') else None,
                'stop_loss_price': float(request.form.get('stop_loss_price')) if request.form.get('stop_loss_price') else None,
                'bollinger_period': request.form.get('bollinger_period'),
                'created_by': current_user.id
            }
            
            print("处理后的合约数据:", contract_data, file=sys.stderr)
            
            # 保存到数据库
            db = get_db()
            cursor = db.cursor()
            
            try:
                # 插入合约数据
                sql = """
                    INSERT INTO contracts (
                        contract_name, period, stop_loss_amount, entry_time, 
                        period_upgrade_time, ma_price, price, actual_entry_price,
                        stop_loss_price, bollinger_period, created_at, created_by
                    ) VALUES (
                        %(contract_name)s, %(period)s, %(stop_loss_amount)s, %(entry_time)s,
                        %(period_upgrade_time)s, %(ma_price)s, %(price)s, %(actual_entry_price)s,
                        %(stop_loss_price)s, %(bollinger_period)s, NOW(), %(created_by)s
                    )
                """
                cursor.execute(sql, contract_data)
                contract_id = cursor.lastrowid
                db.commit()
                
                # 检查是否是 AJAX 请求
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'message': '合约创建成功',
                        'redirect': url_for('orders.overview')
                    })
                else:
                    flash('合约创建成功', 'success')
                    return redirect(url_for('orders.overview'))
                
            except Exception as e:
                db.rollback()
                raise e
            
        except Exception as e:
            print(f"保存合约时出错: {str(e)}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
            
            # 检查是否是 AJAX 请求
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': f'保存合约失败: {str(e)}'
                }), 400
            else:
                flash(f'保存合约失败: {str(e)}', 'error')
                return redirect(url_for('orders.new_contract'))
        finally:
            cursor.close()
            
    return render_template('orders/new_contract.html')

@orders_bp.route('/contract/<int:contract_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contract(contract_id):
    if current_user.role != 'decision_maker':
        flash('只有决策者可以修改合约')
        return redirect(url_for('orders.overview'))
    
    contract = Contract.get_by_id(contract_id)
    
    if request.method == 'POST':
        # 处理表单数据
        contract_data = {
            'contract_name': request.form.get('contract_name'),
            'period': request.form.get('period'),
            'stop_loss_amount': float(request.form.get('stop_loss_amount')),
            'bollinger_period': int(request.form.get('bollinger_period')),
            'entry_time': request.form.get('entry_time'),
            'period_upgrade_time': request.form.get('period_upgrade_time'),
            'ma_price': float(request.form.get('ma_price')) if request.form.get('ma_price') else None,
            'price': float(request.form.get('price')) if request.form.get('price') else None,
            'actual_entry_price': float(request.form.get('actual_entry_price')) if request.form.get('actual_entry_price') else None,
            'stop_loss_price': float(request.form.get('stop_loss_price')) if request.form.get('stop_loss_price') else None
        }
        
        try:
            Contract.update(contract_id, contract_data)
            flash('合约更新成功', 'success')
        except Exception as e:
            flash(f'合约更新失败: {str(e)}', 'error')
            logger.error(f"更新合约时出错: {str(e)}")
            logger.error(traceback.format_exc())
        
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

@orders_bp.route('/contract/<int:contract_id>/delete', methods=['POST'])
@login_required
def delete_contract(contract_id):
    if current_user.role != 'decision_maker':
        flash('只有决策者可以删除合约')
        return redirect(url_for('orders.overview'))
    
    contract = Contract.get_by_id(contract_id)
    if not contract:
        flash('合约不存在')
        return redirect(url_for('orders.overview'))
    
    # 检查是否所有关联订单都是待执行状态
    if not Order.all_pending_by_contract(contract_id):
        flash('有订单已执行，无法删除合约')
        return redirect(url_for('orders.overview'))
    
    # 删除所有关联的订单
    orders = Order.get_by_contract(contract_id)
    for order in orders:
        Order.delete(order['id'])
    
    # 删除合约
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM contracts WHERE id = %s", (contract_id,))
        db.commit()
        flash('合约删除成功')
    except Exception as e:
        db.rollback()
        flash(f'删除合约失败: {str(e)}')
    finally:
        cursor.close()
    
    return redirect(url_for('orders.overview'))