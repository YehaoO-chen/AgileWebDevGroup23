let currentFilter = 'all';

function initNotificationFeatures() {
    console.log("Initializing Notification Features...");

    const notificationListElement = document.getElementById('notificationList');
    const totalNotificationsElement = document.getElementById('total-notifications');
    const receivedCountElement = document.getElementById('received-count');
    const sentCountElement = document.getElementById('sent-count'); // This will likely show 0 or be hidden
    const todayCountElement = document.getElementById('today-count');
    const emptyStateElement = document.getElementById('emptyState');
    // Ensure spinnerContainer is accessed only if notificationListElement exists
    const spinnerContainer = notificationListElement ? notificationListElement.querySelector('.spinner-container') : null;

    // Helper function to format date
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
    }

    // Helper function to format time
    function formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    }

    // Function to create a notification HTML element for received messages
    function createNotificationElement(notification) {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('message-wrapper', 'message-received');
        messageWrapper.setAttribute('data-id', notification.id);
        messageWrapper.setAttribute('data-status', notification.status);

        let readDotHtml = '';
        if (notification.status === 0) { // Unread (status 0)
            // Red dot on top-right corner
            readDotHtml = '<span class="unread-dot" style="position: absolute; top: -5px; right: -5px; left: auto; width: 10px; height: 10px; background-color: #DC3545; border-radius: 50%; border: 1px solid white; z-index:1;"></span>';
        }

        messageWrapper.innerHTML = `
            ${readDotHtml}
            <div class="message-bubble">
                <div class="message-header">
                    <strong>${notification.sender_username || 'Unknown User'}</strong>
                </div>
                <div class="message-content">
                    ${notification.content}
                </div>
                <div class="message-footer">
                    <span class="timestamp">${formatTime(notification.send_time)}</span>
                </div>
            </div>
        `;

        if (notification.status === 0) {
            messageWrapper.style.cursor = 'pointer';
            messageWrapper.addEventListener('click', async () => {
                await markNotificationAsRead(notification.id, messageWrapper);
            });
        }
        return messageWrapper;
    }

    // Function to mark notification as read
    async function markNotificationAsRead(notificationId, element) {
        try {
            const response = await fetch(`/api/notification/${notificationId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    // Add CSRF token header if needed
                },
                body: JSON.stringify({ status: 1 }) // 1 for read
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Failed to mark notification as read:', errorData.message);
                return;
            }

            const result = await response.json();
            if (result.success) {
                console.log(`Notification ${notificationId} marked as read.`);
                const dot = element.querySelector('.unread-dot');
                if (dot) {
                    dot.remove();
                }
                element.setAttribute('data-status', '1');
                element.style.cursor = 'default';
                updateUnreadNotificationBadge(); // Update global badge
            } else {
                console.error('API reported failure in marking notification as read:', result.message);
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    // Function to load all (active received) notifications
    async function loadAllNotifications() {
        if (!notificationListElement) {
            console.error("Notification list element not found. Cannot load notifications.");
            return;
        }

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

            // Add source tagging
            received.forEach(n => n.__type = 'received');
            sent.forEach(n => n.__type = 'sent');

            let all = [...received, ...sent];

            // Screening Logic
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

            // Sort by: reverse chronological order
            all.sort((a, b) => new Date(b.send_time) - new Date(a.send_time));

            // Update statistics
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

                let element;
                if (notification.__type === 'received') {
                    element = createNotificationElement(notification); 
                } else {
                    element = document.createElement('div');
                    element.classList.add('message-wrapper', 'message-sent');
                    element.innerHTML = `
                        <div class="message-bubble ">
                            <div class="message-header">
                                <strong>To: ${notification.receiver_username}</strong>
                            </div>
                            <div class="message-content">${notification.content}</div>
                            <div class="message-footer">
                                <span class="timestamp">${formatTime(notification.send_time)}</span>
                            </div>
                        </div>
                    `;
                }

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

    

    // Function to update a global unread notification badge (e.g., in the navbar)
    async function updateUnreadNotificationBadge() {
        try {
            // The /api/notification/ endpoint returns notifications with status 0 (unread) and 1 (read).
            // We need to filter for status 0 on the client side for the unread count.
            const response = await fetch('/api/notification/'); // Backend scopes this to current_user
            if (!response.ok) {
                console.warn('Could not fetch data for unread notification badge.');
                return;
            }
            const activeNotifications = await response.json();
            let unreadCount = 0;
            if (Array.isArray(activeNotifications)) {
                unreadCount = activeNotifications.filter(n => n.status === 0).length;
            }

            const badgeElement = document.querySelector('.notification-badge'); // Adjust selector
            const notificationIcon = document.querySelector('.notification-icon-indicator'); // Adjust selector

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

    // Initial setup function
    async function initializePage() {
        // No longer need to fetch currentUserId here
        loadAllNotifications();

        // Example: Setup for a filter dropdown if you have one
        const filterDropdown = document.querySelector('.filter-dropdown'); // Ensure this ID/class exists in your HTML
        if (filterDropdown) {
            filterDropdown.addEventListener('change', (event) => {
                const value = event.target.value;
                switch (value) {
                    case 'All Notifications':
                        currentFilter = 'all';
                        break;
                    case 'Received':
                        currentFilter = 'received';
                        break;
                    case 'Sent':
                        currentFilter = 'sent';
                        break;
                    case 'Today':
                        currentFilter = 'today';
                        break;
                    case 'This Week':
                        currentFilter = 'week';
                        break;
                    default:
                        currentFilter = 'all';
                }
                loadAllNotifications();
            });
        }
    }

    // Check if we are on the notification page before running full init
    if (notificationListElement) {
        initializePage();
    } else {
        // If not on the notification page, still attempt to update the global badge
        console.log("Not on notification page, attempting to update global badge only.");
        updateUnreadNotificationBadge();
    }
}