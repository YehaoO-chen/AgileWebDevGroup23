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
        notificationListElement.innerHTML = ''; // Clear previous content

        // Re-show spinner if it was hidden by clearing innerHTML
        if (spinnerContainer && notificationListElement.children.length === 0) {
             notificationListElement.appendChild(spinnerContainer);
        }

        try {
            // Fetch active received notifications (status 0 or 1) from /api/notification/
            // The backend API uses @login_required and current_user to scope notifications.
            const response = await fetch('/api/notification/');

            if (!response.ok) {
                console.error('Failed to fetch notifications, status:', response.status);
                const errorText = await response.text(); // Get more error details
                console.error('Error details:', errorText);
                notificationListElement.innerHTML = '<p class="text-danger p-3">Error loading notifications. Please try again.</p>';
                if (spinnerContainer) spinnerContainer.classList.add('d-none');
                return;
            }

            const receivedActiveNotifications = await response.json();

            if (spinnerContainer) spinnerContainer.classList.add('d-none');

            if (!Array.isArray(receivedActiveNotifications)) {
                console.error('Fetched notifications is not an array:', receivedActiveNotifications);
                notificationListElement.innerHTML = '<p class="text-warning p-3">Received unexpected data format for notifications.</p>';
                return;
            }

            // API should ideally sort, but client-side sort as a fallback
            receivedActiveNotifications.sort((a, b) => new Date(b.send_time) - new Date(a.send_time));

            if (totalNotificationsElement) totalNotificationsElement.textContent = receivedActiveNotifications.length;
            if (receivedCountElement) receivedCountElement.textContent = receivedActiveNotifications.length;
            if (sentCountElement) sentCountElement.textContent = "0"; // As we are only fetching received

            let todayNotificationsCount = 0;
            const todayStr = new Date().toLocaleDateString();

            notificationListElement.innerHTML = ''; // Clear spinner or previous content again before adding new items

            if (receivedActiveNotifications.length === 0) {
                if (emptyStateElement) emptyStateElement.classList.remove('d-none');
            } else {
                if (emptyStateElement) emptyStateElement.classList.add('d-none');
                let lastDate = null;
                receivedActiveNotifications.forEach(notification => {
                    const notificationDateStr = new Date(notification.send_time).toLocaleDateString();
                    if (notificationDateStr === todayStr) {
                        todayNotificationsCount++;
                    }

                    const currentDate = formatDate(notification.send_time);
                    if (currentDate !== lastDate) {
                        const dateDivider = document.createElement('div');
                        dateDivider.classList.add('date-divider');
                        dateDivider.innerHTML = `<span>${currentDate}</span>`;
                        notificationListElement.appendChild(dateDivider);
                        lastDate = currentDate;
                    }
                    const notificationElement = createNotificationElement(notification);
                    notificationListElement.appendChild(notificationElement);
                });
            }
            if (todayCountElement) todayCountElement.textContent = todayNotificationsCount;
            updateUnreadNotificationBadge(); // Update global badge

        } catch (error) {
            console.error('Error fetching or processing notifications:', error);
            if (spinnerContainer) spinnerContainer.classList.add('d-none');
            notificationListElement.innerHTML = '<p class="text-danger p-3">An unexpected error occurred while loading notifications. Please try again.</p>';
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
                console.log("Filter changed to:", event.target.value);
                // Currently, only "All Notifications" (received) is handled by reloading.
                // Implement other filter logic as needed.
                if (event.target.value === "All Notifications") {
                    loadAllNotifications();
                }
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