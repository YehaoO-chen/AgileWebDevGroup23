// notification.js
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有删除按钮
    const deleteButtons = document.querySelectorAll('.delete-btn');
    
    // 为每个删除按钮添加点击事件
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 获取当前通知卡片
            const notificationCard = this.closest('.notification-card');
            
            // 添加淡出动画
            notificationCard.style.opacity = '0';
            notificationCard.style.transform = 'translateX(100px)';
            notificationCard.style.transition = 'opacity 0.3s, transform 0.3s';
            
            // 动画结束后移除元素
            setTimeout(() => {
                notificationCard.remove();
                
                // 如果没有通知了，显示一个空状态
                const notificationList = document.querySelector('.notification-list');
                if (notificationList.children.length === 0) {
                    const emptyState = document.createElement('div');
                    emptyState.className = 'empty-state';
                    emptyState.innerHTML = '<p>No notifications to display.</p>';
                    notificationList.appendChild(emptyState);
                }
            }, 300);
        });
    });
});