let allUsers = [];
let selectedUserIds = [];
let currentUserUsername = '';

// Fetch current user's username once
async function fetchCurrentUserUsername() {
    if (currentUserUsername) return;
    try {
        const response = await fetch('/api/profile');
        if (response.ok) {
            const userData = await response.json();
            currentUserUsername = userData.username || 'A user';
        } else {
            currentUserUsername = 'A user';
        }
    } catch (error) {
        console.error('Error fetching current user username:', error);
        currentUserUsername = 'A user';
    }
}

// Called from dashboard.html onclick
function openShareModal() {
    console.log('Opening share modal');
    selectedUserIds = [];

    const noUsers = document.getElementById('noUsersSelected');
    const selectedUsers = document.getElementById('selectedUsers');
    const searchInput = document.getElementById('userSearchInput');

    if (noUsers) noUsers.style.display = 'block';
    if (selectedUsers) selectedUsers.innerHTML = '<span id="noUsersSelected" class="text-muted small">No users selected</span>';
    if (searchInput) searchInput.value = '';

    try {
        const shareModalElement = document.getElementById('shareModal');
        if (!shareModalElement) {
            console.error('Share modal element not found');
            return;
        }
        const shareModal = bootstrap.Modal.getInstance(shareModalElement) || new bootstrap.Modal(shareModalElement);
        loadUsers();
        shareModal.show();
    } catch (error) {
        console.error('Error showing modal:', error);
        alert('Error opening share dialog: ' + error.message);
    }
}

function loadUsers() {
    const userList = document.getElementById('userList');
    if (!userList) return;

    userList.innerHTML = `
        <div class="d-flex align-items-center justify-content-center p-3">
            <div class="spinner-border spinner-border-sm text-secondary me-2" role="status"></div>
            <span>Loading users...</span>
        </div>
    `;

    fetch('/api/users')
        .then(response => response.json())
        .then(users => {
            allUsers = users;
            userList.innerHTML = '';

            if (!Array.isArray(users) || users.length === 0) {
                userList.innerHTML = `<p class="text-center text-muted p-3">No users found.</p>`;
                return;
            }

            users.forEach(user => {
                const userItem = document.createElement('div');
                userItem.className = 'form-check mb-2';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'form-check-input';
                checkbox.id = `user-${user.id}`;
                checkbox.value = user.id;
                checkbox.checked = selectedUserIds.includes(user.id);

                checkbox.addEventListener('change', function () {
                    if (this.checked) {
                        if (!selectedUserIds.includes(user.id)) {
                            selectedUserIds.push(user.id);
                        }
                    } else {
                        selectedUserIds = selectedUserIds.filter(id => id !== user.id);
                    }
                    updateSelectedUsers();
                });

                const label = document.createElement('label');
                label.className = 'form-check-label';
                label.htmlFor = `user-${user.id}`;
                label.textContent = user.username;

                userItem.appendChild(checkbox);
                userItem.appendChild(label);
                userList.appendChild(userItem);
            });

            const searchInput = document.getElementById('userSearchInput');
            if (searchInput) {
                searchInput.addEventListener('input', function () {
                    filterUsers(this.value.toLowerCase());
                });
            }
        })
        .catch(error => {
            console.error('Error loading users:', error);
            userList.innerHTML = `<p class="text-danger p-3">Error loading users.</p>`;
        });
}

function filterUsers(searchTerm) {
    const checkboxes = document.querySelectorAll('#userList .form-check');
    checkboxes.forEach(item => {
        const label = item.querySelector('.form-check-label');
        if (label) {
            item.style.display = label.textContent.toLowerCase().includes(searchTerm) ? 'block' : 'none';
        }
    });
}

function updateSelectedUsers() {
    const container = document.getElementById('selectedUsers');
    if (!container) return;

    if (selectedUserIds.length === 0) {
        container.innerHTML = '<span id="noUsersSelected" class="text-muted small">No users selected</span>';
        return;
    }

    container.innerHTML = '';
    selectedUserIds.forEach(userId => {
        const user = allUsers.find(u => u.id === userId);
        if (!user) return;

        const tag = document.createElement('span');
        tag.className = 'badge bg-info text-dark me-2 mb-2';
        tag.style.display = 'inline-flex';
        tag.style.alignItems = 'center';
        tag.style.padding = '5px 10px';
        tag.style.borderRadius = '16px';

        tag.innerHTML = `
            ${user.username}
            <button type="button" class="btn-close btn-close-white ms-2" 
                    style="font-size: 0.5rem; filter: brightness(0.8);" aria-label="Remove"
                    onclick="removeUser(${userId})"></button>
        `;

        container.appendChild(tag);
    });
}

function removeUser(userId) {
    const checkbox = document.getElementById(`user-${userId}`);
    if (checkbox) checkbox.checked = false;

    selectedUserIds = selectedUserIds.filter(id => id !== userId);
    updateSelectedUsers();
}

function shareData() {
    if (selectedUserIds.length === 0) {
        alert('Please select at least one user.');
        return;
    }

    const typeElement = document.querySelector('input[name="dataType"]:checked');
    if (!typeElement) {
        alert('Select the type of data to share.');
        return;
    }

    const type = typeElement.value;
    let dataText = "dashboard insights";

    if (type === "totalTime") {
        const val = document.getElementById('total-duration')?.textContent.trim();
        dataText = `Total Study Time: ${val} minutes`;
    } else if (type === "averageTime") {
        const val = document.getElementById('average-duration')?.textContent.trim();
        dataText = `Average Study Time: ${val} minutes`;
    }

    const message = `shared their '${dataText}' dashboard insights with you.`;

    const doneBtn = document.getElementById('doneButton');
    doneBtn.disabled = true;
    doneBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sharing...';

    fetch('/api/notification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            receiver_ids: selectedUserIds,
            content: message
        })
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(result => {
        doneBtn.disabled = false;
        doneBtn.textContent = 'Done';
        if (result.ok && result.data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('shareModal'));
            if (modal) modal.hide();
            alert('Dashboard insights shared successfully!');
        } else {
            alert('Failed to share: ' + (result.data.message || 'Unknown error'));
        }
    })
    .catch(err => {
        doneBtn.disabled = false;
        doneBtn.textContent = 'Done';
        console.error('Error sharing:', err);
        alert('An error occurred while sharing.');
    });
}

// Auto fetch username on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchCurrentUserUsername();
});
