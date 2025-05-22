@bp.route('/add_contract', methods=['GET', 'POST'])
@login_required
def add_contract():
    # 获取所有可用账户
    accounts = Account.query.filter_by(is_active=True).all()
    
    # 添加调试信息
    print(f"Debug - 获取到的账户数量: {len(accounts)}")
    for account in accounts:
        print(f"Debug - 账户信息: ID={account.id}, 名称={account.name}, 类型={account.type}")
    
    if request.method == 'POST':
        # 处理表单提交
        selected_accounts = request.form.getlist('selected_accounts')
        
        # 创建新合约
        contract = Contract(
            # ... existing code ...
        )
        db.session.add(contract)
        db.session.flush()  # 获取新创建的合约ID
        
        # 添加关联账户
        for account_id in selected_accounts:
            contract_account = ContractAccount(
                contract_id=contract.id,
                account_id=account_id,
                status='pending'  # 初始状态为待执行
            )
            db.session.add(contract_account)
        
        try:
            db.session.commit()
            flash('合约创建成功', 'success')
            return redirect(url_for('orders.overview'))
        except Exception as e:
            db.session.rollback()
            flash('合约创建失败，请重试', 'error')
            return render_template('orders/modals/add_contract.html', accounts=accounts)
    
    # GET请求，渲染表单
    return render_template('orders/modals/add_contract.html', accounts=accounts)