var currentFilter = 'all';

function initNotificationFeatures() {
    console.log("Initializing Notification Features...");

    const notificationListElement = document.getElementById('notificationList');
    const totalNotificationsElement = document.getElementById('total-notifications');
    const receivedCountElement = document.getElementById('received-count');
    const sentCountElement = document.getElementById('sent-count');
    const todayCountElement = document.getElementById('today-count');
    const emptyStateElement = document.getElementById('emptyState');
    const spinnerContainer = notificationListElement ? notificationListElement.querySelector('.spinner-container') : null;

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
    }

    function formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    }

    function createNotificationElement(notification) {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('message-wrapper');
        messageWrapper.setAttribute('data-id', notification.id);
        messageWrapper.setAttribute('data-status', notification.status);

        const isSent = notification.__type === 'sent';
        if (isSent) {
            messageWrapper.classList.add('message-sent');
        } else {
            messageWrapper.classList.add('message-received');
        }

        let readDotHtml = '';
        if (notification.status === 0 && !isSent) {
            readDotHtml = '<span class="unread-dot" style="position: absolute; top: -5px; right: -5px; width: 10px; height: 10px; background-color: #DC3545; border-radius: 50%; border: 1px solid white; z-index:1;"></span>';
        }

        const messageHeader = isSent
            ? `<strong>To: ${notification.receiver_username || 'Unknown User'}</strong>`
            : `<strong>From: ${notification.sender_username || 'Unknown User'}</strong>`;

        messageWrapper.innerHTML = `
            ${readDotHtml}
            <div class="message-bubble ${isSent ? 'bg-light' : ''}">
                <div class="message-header">
                    ${messageHeader}
                </div>
                <div class="message-content">
                    ${notification.content}
                </div>
                <div class="message-footer">
                    <span class="timestamp">${formatTime(notification.send_time)}</span>
                </div>
            </div>
        `;

        messageWrapper.style.cursor = 'pointer';
        messageWrapper.addEventListener('click', async () => {
            if (!isSent && notification.status === 0) {
                await markNotificationAsRead(notification.id, messageWrapper);
            }
            openNotificationModal(notification);
        });

        return messageWrapper;
    }

    async function markNotificationAsRead(notificationId, element) {
        try {
            const response = await fetch(`/api/notification/${notificationId}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 1 })
            });

            const result = await response.json();
            if (result.success) {
                const dot = element.querySelector('.unread-dot');
                if (dot) dot.remove();
                element.setAttribute('data-status', '1');
                element.style.cursor = 'default';
                updateUnreadNotificationBadge();
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    async function loadAllNotifications() {
        if (!notificationListElement) return;

        if (spinnerContainer) spinnerContainer.classList.remove('d-none');
        if (emptyStateElement) emptyStateElement.classList.add('d-none');
        notificationListElement.innerHTML = '';

        try {
            const [receivedRes, sentRes] = await Promise.all([
                fetch('/api/notification/'),
                fetch('/api/notifications/sent')
            ]);

            const received = receivedRes.ok ? await receivedRes.json() : [];
            const sent = sentRes.ok ? await sentRes.json() : [];

            received.forEach(n => n.__type = 'received');
            sent.forEach(n => n.__type = 'sent');

            let all = [...received, ...sent];

            const now = new Date();
            const todayStr = now.toLocaleDateString();
            const startOfWeek = new Date(now);
            startOfWeek.setDate(now.getDate() - now.getDay());
            startOfWeek.setHours(0, 0, 0, 0);

            if (currentFilter === 'received') {
                all = received;
            } else if (currentFilter === 'sent') {
                all = sent;
            } else if (currentFilter === 'today') {
                all = all.filter(n => new Date(n.send_time).toLocaleDateString() === todayStr);
            } else if (currentFilter === 'week') {
                all = all.filter(n => new Date(n.send_time) >= startOfWeek);
            }

            all.sort((a, b) => new Date(b.send_time) - new Date(a.send_time));

            totalNotificationsElement.textContent = all.length;
            receivedCountElement.textContent = received.length;
            sentCountElement.textContent = sent.length;

            if (all.length === 0) {
                if (emptyStateElement) emptyStateElement.classList.remove('d-none');
                if (spinnerContainer) spinnerContainer.classList.add('d-none');
                todayCountElement.textContent = '0';
                return;
            }

            let todayCount = 0;
            let lastDate = null;

            all.forEach(notification => {
                const sendDate = new Date(notification.send_time);
                const dateStr = sendDate.toLocaleDateString();
                if (dateStr === todayStr) todayCount++;

                const currentDate = formatDate(notification.send_time);
                if (currentDate !== lastDate) {
                    const divider = document.createElement('div');
                    divider.classList.add('date-divider');
                    divider.innerHTML = `<span>${currentDate}</span>`;
                    notificationListElement.appendChild(divider);
                    lastDate = currentDate;
                }

                const element = createNotificationElement(notification);
                notificationListElement.appendChild(element);
            });

            todayCountElement.textContent = todayCount;
            if (spinnerContainer) spinnerContainer.classList.add('d-none');
            updateUnreadNotificationBadge();
        } catch (error) {
            console.error('Error loading notifications:', error);
            notificationListElement.innerHTML = '<p class="text-danger p-3">An error occurred while loading notifications. Please try again.</p>';
            if (spinnerContainer) spinnerContainer.classList.add('d-none');
        }
    }

    async function updateUnreadNotificationBadge() {
        try {
            const response = await fetch('/api/notification/');
            if (!response.ok) return;

            const activeNotifications = await response.json();
            const unreadCount = activeNotifications.filter(n => n.status === 0).length;

            const badgeElement = document.querySelector('.notification-badge');
            const notificationIcon = document.querySelector('.notification-icon-indicator');

            if (badgeElement) {
                badgeElement.textContent = unreadCount > 0 ? unreadCount : '';
                badgeElement.style.display = unreadCount > 0 ? 'inline-block' : 'none';
            }
            if (notificationIcon) {
                notificationIcon.style.display = unreadCount > 0 ? 'block' : 'none';
            }
        } catch (error) {
            console.warn('Error updating unread notification badge:', error);
        }
    }

    function initializePage() {
        loadAllNotifications();

        const filterDropdown = document.querySelector('.filter-dropdown');
        if (filterDropdown) {
            filterDropdown.addEventListener('change', (event) => {
                const value = event.target.value;
                switch (value) {
                    case 'All Notifications': currentFilter = 'all'; break;
                    case 'Received': currentFilter = 'received'; break;
                    case 'Sent': currentFilter = 'sent'; break;
                    case 'Today': currentFilter = 'today'; break;
                    case 'This Week': currentFilter = 'week'; break;
                    default: currentFilter = 'all';
                }
                loadAllNotifications();
            });
        }
    }

    function openNotificationModal(notification) {
        const isSharedDashboard = notification.content.includes('dashboard insights');

        if (isSharedDashboard) {
            const modalEl = document.getElementById('notificationChartModal');
            const canvas = document.getElementById('notificationChartCanvas');

            if (!canvas || !modalEl) return;

            const ctx = canvas.getContext('2d');
            if (window.notificationChartInstance) {
                window.notificationChartInstance.destroy();
            }

            const sharedValue = extractStudyValue(notification.content); 

            window.notificationChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Shared Study Time'],
                    datasets: [{
                        label: 'Minutes',
                        data: [sharedValue],
                        backgroundColor: 'rgba(64, 173, 162, 0.7)',
                        borderColor: 'rgba(64, 173, 162, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 300 
                        }
                    }
                }
            });

            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        } else {
            alert("This notification does not contain shared dashboard data.");
        }
    }

    function extractStudyValue(content) {
        const match = content.match(/(\d+)\s*minutes?/i);
        return match ? parseInt(match[1]) : 0;
    }

    initializePage();

}


