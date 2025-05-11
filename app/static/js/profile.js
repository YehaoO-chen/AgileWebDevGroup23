$(document).ready(function() {
    const defaultAvatarUrl = 'https://st2.depositphotos.com/53447130/50476/v/450/depositphotos_504768188-stock-illustration-pixel-black-cat-image-vector.jpg';
    const AVATAR_STORAGE_KEY = 'userAvatarUrl'; // Define a key for localStorage

    let isEditing = false;
    let originalValues = {};

    // --- Selectors ---
    const $editProfileBtn = $('#editProfileBtn');
    const $profilePhotoImg = $('#profilePhoto');
    const $changePhotoBtn = $('#changePhotoBtn');
    const $avatarUploadInput = $('#avatarUpload');
    const $navbarProfileImg = $('.dropdown-toggle .profile-img'); // Added selector for navbar image


    function updateAvatarDisplayAndStorage(url) {
        const finalUrl = url ; 
        
        $profilePhotoImg.attr('src', finalUrl);
        $navbarProfileImg.attr('src', finalUrl);
        if (url && url !== defaultAvatarUrl) {
            localStorage.setItem(AVATAR_STORAGE_KEY, url); // Store the valid URL
        } else {
            localStorage.removeItem(AVATAR_STORAGE_KEY); // Remove if default or invalid
        }
    }
    // Map field IDs to jQuery selectors and user object keys
    const profileFields = {
        profileName: { selector: $('#profileName'), key: 'fullname', type: 'text', isHeader: true, readOnly: true }, // Special handling for header name
        profileRole: { selector: $('#profileRole'), key: 'major', type: 'text', isHeader: true , readOnly: true},    // Special handling for header role
        fullName: { selector: $('#fullName'), key: 'fullname', type: 'text' },
        email: { selector: $('#email'), key: 'email', type: 'email' },
        phone: { selector: $('#phone'), key: 'phone', type: 'tel' },
        address: { selector: $('#address'), key: 'address', type: 'text' },
        major: { selector: $('#major'), key: 'major', type: 'text' },
        studentId: { selector: $('#studentId'), key: 'student_id', type: 'text' },
        username: { selector: $('#username'), key: 'username', type: 'text' }, // Usually read-only
        createTime: { selector: $('#createTime'), key: 'create_time', type: 'text', readOnly: true } // Read-only
    };

    // --- Load Initial Profile Data ---
    function loadProfileData() {

        $.ajax({
            url: '/api/profile', // GET request to fetch user data
            method: 'GET',
            dataType: 'json',
            success: function(user) {
                // Populate fields
                for (const id in profileFields) {
                    const field = profileFields[id];
                    let value = user[field.key] || ''; // Get value from user object or default to empty string

                    // Format create_time if it exists
                    if (field.key === 'create_time' && value) {
                        try {
                            value = new Date(value).toLocaleDateString(); // Basic date formatting
                        } catch (e) { console.error("Error formatting date:", e); value = user[field.key]; }
                    }

                    field.selector.text(value); // Set text content using jQuery
                }

                // Handle Avatar
                let avatarSrc = defaultAvatarUrl;
                if (user.avatar && user.avatar !== defaultAvatarUrl && user.avatar !== '' && user.avatar !== 'default.jpg') {
                    // Assuming avatar field stores filename like 'user_1_avatar.png'
                    avatarSrc = `/static/uploads/${user.avatar}`; // Construct path
                } else {
                    //  avatarSrc = `/static/images/default_avatar.png`; // Or your actual default image path
                     avatarSrc = defaultAvatarUrl; // Fallback to default avatar URL
                     localStorage.removeItem(AVATAR_STORAGE_KEY); // Remove if default or invalid
                }
                updateAvatarDisplayAndStorage(avatarSrc); // Update images immediately

                // Update header fields specifically if they differ (e.g., using fullname vs username)
                $('#profileName').text(user.fullname || user.username);
                $('#profileRole').text(user.major || 'Student'); // Example default role

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error loading profile:", textStatus, errorThrown);
                showNotification('Failed to load profile data.', 'error');
            }
        });
    }

    // --- Edit/Save Button Logic ---
    $editProfileBtn.on('click', function() {
        if (!isEditing) {
            // --- Switch to edit mode ---
            isEditing = true;
            $editProfileBtn.text('Save Changes');
            originalValues = {}; // Clear previous original values

            for (const id in profileFields) {
                const field = profileFields[id];
                if (field.readOnly) continue; // Skip read-only fields

                const currentValue = field.selector.text();
                originalValues[id] = currentValue; // Store current text

                // Create input field
                const $input = $('<input>')
                    .attr('type', field.type)
                    .attr('id', 'edit_' + id)
                    .addClass('edit-input')
                    .val(currentValue); // Set input value

                field.selector.empty().append($input); // Replace text with input using jQuery
            }
            addCancelButton();
        } else {
            // --- Save changes ---
            saveChanges();
        }
    });

    // --- Add Cancel Button ---
    function addCancelButton() {
        if ($('#cancelEditBtn').length > 0) return; // Don't add if already exists

        const $cancelBtn = $('<button>')
            .text('Cancel')
            .addClass('edit-profile-btn')
            .css({ 'background-color': '#888', 'margin-left': '10px' })
            .attr('id', 'cancelEditBtn');

        $cancelBtn.on('click', function() {
            // Restore original values
            for (const id in profileFields) {
                const field = profileFields[id];
                 if (field.readOnly) continue;
                // Find input and remove it, restore text
                const $input = $('#edit_' + id);
                if ($input.length) {
                    field.selector.text(originalValues[id]); // Restore text
                }
            }

            // Reset state
            isEditing = false;
            $editProfileBtn.text('Edit Profile');
            $(this).remove(); // Remove the cancel button itself
        });

        $editProfileBtn.after($cancelBtn); // Add cancel button after edit/save button
    }

    // --- Save Changes ---
    function saveChanges() {
        const updatedData = {};
        let hasChanges = false;

        // Collect data from input fields
        for (const id in profileFields) {
            const field = profileFields[id];
             if (field.readOnly) continue;

            const $input = $('#edit_' + id);
            if ($input.length) {
                const newValue = $input.val();
                updatedData[field.key] = newValue; // Use the model key (e.g., 'fullname')
                field.selector.text(newValue); // Update display immediately

                if (newValue !== originalValues[id]) {
                    hasChanges = true;
                }
            }
        }

        // Reset state visually first
        isEditing = false;
        $editProfileBtn.text('Edit Profile');
        $('#cancelEditBtn').remove();

        // --- Send data to the server using fetch API ---
        if (hasChanges) {
            // Note: Using PUT as it's standard for updates. Change to 'POST' if required by your API.
            $.ajax({
                url: '/api/profile',
                method: 'PUT', 
                contentType: 'application/json',
                data: JSON.stringify(updatedData),
                dataType: 'json',
                success: function(data) {
                    if (data.success) {
                        showNotification('Profile updated successfully!', 'success');
                        // Update header fields if they were edited
                        if (updatedData.hasOwnProperty('fullname')) {
                             $('#profileName').text(updatedData.fullname || originalValues['username']); // Fallback to username if fullname cleared
                        }
                         if (updatedData.hasOwnProperty('major')) {
                             $('#profileRole').text(updatedData.major || 'Student');
                        }
                        // Update originalValues map for next edit cycle
                        loadProfileData(); // Or manually update originalValues map
                    } else {
                        showNotification('Error updating profile: ' + (data.error || JSON.stringify(data.errors)), 'error');
                        // Revert visual changes on error
                        revertChangesOnError();
                    }
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.error('Error updating profile:', textStatus, errorThrown);
                    showNotification('An network error occurred during update.', 'error');
                    // Revert visual changes on error
                    revertChangesOnError();
                }
            });
        } else {
            showNotification('No changes detected.', 'info');
        }
    }

     // --- Helper to revert visual changes on error ---
    function revertChangesOnError() {
         for (const id in profileFields) {
             const field = profileFields[id];
             if (!field.readOnly && originalValues.hasOwnProperty(id)) {
                 field.selector.text(originalValues[id]); // Restore original text
             }
         }
         // Also potentially revert header fields if they were part of the edit
         if (originalValues.hasOwnProperty('profileName')) $('#profileName').text(originalValues['profileName']);
         if (originalValues.hasOwnProperty('profileRole')) $('#profileRole').text(originalValues['profileRole']);
    }


    // --- Avatar Upload Logic ---
    $changePhotoBtn.on('click', function() {
        $avatarUploadInput.click(); // Trigger hidden file input
    });

    $avatarUploadInput.on('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            // Optional: Preview image locally
            const reader = new FileReader();
            reader.onload = (e) => {
                $profilePhotoImg.attr('src', e.target.result); // Update preview
            }
            reader.readAsDataURL(file);

            // Upload the file
            uploadAvatar(file);
        }
         // Reset file input value so the same file can be selected again if needed
        $(this).val('');
    });

    function uploadAvatar(file) {
        const formData = new FormData();
        formData.append('avatar', file); // Key 'avatar' must match server expectation

        $.ajax({
            url: '/api/upload_avatar', // Your avatar upload endpoint
            method: 'POST',
            data: formData,
            processData: false, // Prevent jQuery from processing the data
            contentType: false, // Prevent jQuery from setting contentType
            dataType: 'json',
            success: function(data) {
                if (data.success && data.avatar_url) {
                    updateAvatarDisplayAndStorage(data.avatar_url);
                    showNotification('Avatar updated successfully!', 'success');
                } else {
                    showNotification('Failed to upload avatar: ' + (data.error || 'Unknown error'), 'error');
                    // Revert preview to original avatar on failure?
                    // loadProfileData(); // Reload might be simplest way to revert
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('Avatar upload error:', textStatus, errorThrown);
                showNotification('Avatar upload failed due to a network error.', 'error');
                 // Revert preview to original avatar on failure?
                 // loadProfileData();
            }
        });
    }

    // --- Notification Function (using vanilla JS is fine) ---
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.position = 'fixed';
        notification.style.bottom = '20px';
        notification.style.right = '20px';
        let bgColor = '#6c757d'; // Default info color
        if (type === 'success') {
            bgColor = '#1fa4a3'; // Your success color
        } else if (type === 'error') {
            bgColor = '#dc3545'; // Bootstrap danger color
        }
        notification.style.backgroundColor = bgColor;
        notification.style.color = 'white';
        notification.style.padding = '10px 20px';
        notification.style.borderRadius = '5px';
        notification.style.zIndex = '1000';
        notification.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // --- Initial Load ---
    loadProfileData();

}); // End of $(document).ready()