// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('订单管理系统已加载');
    
    // 为所有确认操作添加确认对话框
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || '确定要执行此操作吗？';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 处理展开/收起功能
    document.querySelectorAll('.toggle-accounts').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const contractId = this.dataset.contractId;
            const detailsRow = document.getElementById(`accounts-${contractId}`);
            const icon = this.querySelector('i');
            
            // 检查元素是否存在
            if (!detailsRow) {
                console.error(`找不到合约 ${contractId} 的关联账户行`);
                return;
            }
            
            // 确保td元素存在
            let tdElement = detailsRow.querySelector('td');
            if (!tdElement) {
                tdElement = document.createElement('td');
                tdElement.setAttribute('colspan', '12');
                detailsRow.appendChild(tdElement);
            }
            
            // 切换显示状态
            detailsRow.classList.toggle('show');
            
            // 切换图标
            if (detailsRow.classList.contains('show')) {
                icon.classList.remove('fa-plus');
                icon.classList.add('fa-minus');
                
                // 如果还没有加载账户数据，则加载
                let accountsList = detailsRow.querySelector('.associated-accounts-list');
                if (!accountsList) {
                    accountsList = document.createElement('div');
                    accountsList.className = 'associated-accounts-list';
                    tdElement.appendChild(accountsList);
                }
                
                const accounts = this.dataset.associatedAccounts;
                if (accounts && (!accountsList.children.length)) {
                    try {
                        // 检查accounts是否为空字符串
                        if (accounts.trim() === '') {
                            accountsList.innerHTML = '<div class="text-muted p-3">暂无关联账户</div>';
                            return;
                        }
                        
                        // 预处理账户数据
                        const accountsArray = accounts.split(',').map(account => {
                            const [name, type = '未知'] = account.trim().split('|');
                            return {
                                name: name,
                                type: type,
                                status: 'pending'  // 默认状态
                            };
                        });
                        
                        accountsList.innerHTML = displayAssociatedAccounts(accountsArray);
                    } catch (error) {
                        console.error('处理关联账户数据时出错:', error);
                        accountsList.innerHTML = '<div class="text-danger p-3">加载账户数据时出错</div>';
                    }
                }
            } else {
                icon.classList.remove('fa-minus');
                icon.classList.add('fa-plus');
            }
        });
    });
});

// 格式化日期时间
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '';
    const date = new Date(dateTimeStr);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 显示关联账户列表
// 修改displayAssociatedAccounts函数
function displayAssociatedAccounts(accounts) {
    if (!accounts || accounts.length === 0) return '<div class="text-muted p-3">暂无关联账户</div>';
    
    // 直接使用传入的账户数组，不再需要JSON.parse
    const accountsList = accounts.map(accountData => {
        return `
            <div class="account-record mb-2">
                <div class="card">
                    <div class="card-body d-flex justify-content-between align-items-center">
                        <div class="account-info">
                            <div class="account-name">
                                <i class="fas fa-user-circle me-2"></i>
                                <span class="fw-bold">${accountData.name}</span>
                            </div>
                            <div class="account-details text-muted">
                                <small>类型：${accountData.type || '-'}</small>
                            </div>
                        </div>
                        <div class="account-status-section d-flex align-items-center">
                            <span class="badge ${getStatusBadgeClass(accountData.status)} me-3">
                                ${getStatusText(accountData.status)}
                            </span>
                            <button class="btn btn-sm ${getActionButtonClass(accountData.status)}" 
                                    ${accountData.status !== 'pending' ? 'disabled' : ''}>
                                ${getActionButtonText(accountData.status)}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    return `
        <div class="associated-accounts-list p-3">
            ${accountsList}
        </div>
    `;
}

// 获取状态对应的样式类
function getStatusBadgeClass(status) {
    switch(status) {
        case 'pending':
            return 'bg-warning';
        case 'active':
            return 'bg-success';
        case 'completed':
            return 'bg-secondary';
        default:
            return 'bg-light';
    }
}

// 获取状态显示文本
function getStatusText(status) {
    switch(status) {
        case 'pending':
            return '待执行';
        case 'active':
            return '执行中';
        case 'completed':
            return '已完成';
        default:
            return '未知状态';
    }
}

// 获取操作按钮样式
function getActionButtonClass(status) {
    return status === 'pending' ? 'btn-success' : 'btn-secondary';
}

// 获取操作按钮文本
function getActionButtonText(status) {
    return status === 'pending' ? '执行' : '已执行';
}