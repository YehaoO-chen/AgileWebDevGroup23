document.addEventListener('DOMContentLoaded', function () {
    loadAllNotifications();
});

function loadAllNotifications() {
    const container = document.getElementById('notificationList');
    container.innerHTML = `
        <div class="d-flex align-items-center justify-content-center p-3">
            <div class="spinner-border text-secondary" role="status"></div>
        </div>
    `;

    Promise.all([
        fetch('/api/notifications/received').then(res => res.json()),
        fetch('/api/notifications/sent').then(res => res.json())
    ])
    .then(([received, sent]) => {
        container.innerHTML = '';

        if (received.length === 0 && sent.length === 0) {
            container.innerHTML = `<p class="text-center text-muted p-3">No notifications found.</p>`;
            return;
        }

        [...received.map(n => ({ ...n, type: 'received' })), ...sent.map(n => ({ ...n, type: 'sent' }))]
            .sort((a, b) => new Date(b.send_time) - new Date(a.send_time))
            .forEach(item => {
                const card = document.createElement('div');
                card.className = `notification-card ${item.type}`;
                const direction = item.type === 'received'
                    ? `<strong>From:</strong> ${item.sender_username}`
                    : `<strong>To:</strong> ${item.receiver_username}`;
                card.innerHTML = `
                    <p>${direction}</p>
                    <p>${item.content}</p>
                    <p class="text-muted small">${new Date(item.send_time).toLocaleString()}</p>
                `;
                container.appendChild(card);
            });
    })
    .catch(err => {
        console.error('Error loading notifications:', err);
        container.innerHTML = `<p class="text-danger text-center">Failed to load notifications.</p>`;
    });
}
