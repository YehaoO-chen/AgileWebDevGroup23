$(document).ready(function() {
    const $studyInput = $('#studyInput');
    const $addButton = $('#addButton');
    const $openTasksContainer = $('#openTasks');
    const $completedTasksContainer = $('#completedTasks');
    const $openTab = $('#openTab');
    const $completedTab = $('#completedTab');

    // Function to display a study plan item
    function displayStudyPlan(plan, container) {
        const itemHtml = `
            <div class="study-item" data-id="${plan.id}">
                <input type="checkbox" class="study-checkbox" ${plan.status === 1 ? 'checked' : ''}>
                <span class="study-text ${plan.status === 1 ? 'completed-text' : ''}">${plan.content}</span>
                <button class="delete-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                        <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                    </svg>
                </button>
            </div>
        `;
        container.prepend(itemHtml); // Prepend to add to the top
    }

    // Function to load study plans
    function loadStudyPlans(status = 0) { // Default to open tasks (status 0)
        const container = status === 0 ? $openTasksContainer : $completedTasksContainer;
        container.html(''); // Clear current tasks

        $.ajax({
            url: `/api/studyplan?status=${status}`,
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.study_plans) {
                    response.study_plans.forEach(plan => {
                        displayStudyPlan(plan, container);
                    });
                } else {
                    console.error("Error loading study plans:", response.message);
                    // Optionally display an error message to the user
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("AJAX error loading study plans:", textStatus, errorThrown);
            }
        });
    }

    // Add button click event
    $addButton.on('click', function() {
        const content = $studyInput.val().trim();
        if (content === '') {
            alert('Please enter a study plan.'); // Or use a more sophisticated notification
            return;
        }

        $.ajax({
            url: '/api/studyplan',
            method: 'POST',
            contentType: 'application/json', // Set content type for JSON data
            data: JSON.stringify({ content: content }), // Convert data to JSON string
            dataType: 'json', // Expect JSON response
            success: function(response) {
                if (response.success && response.study_plan) {
                    // Add to the "Open Goals" tab
                    displayStudyPlan(response.study_plan, $openTasksContainer);
                    $studyInput.val(''); // Clear the input field
                    // Ensure "Open Goals" tab is active and visible
                    $openTab.click();
                } else {
                    alert('Error creating study plan: ' + (response.message || 'Unknown error'));
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error creating study plan:", textStatus, errorThrown);
                alert('An error occurred while adding the study plan. Please try again.');
            }
        });
    });

    // Tab switching
    $openTab.on('click', function() {
        $(this).addClass('active');
        $completedTab.removeClass('active');
        $openTasksContainer.show();
        $completedTasksContainer.hide();
        loadStudyPlans(0); // Load open tasks
    });

    $completedTab.on('click', function() {
        $(this).addClass('active');
        $openTab.removeClass('active');
        $completedTasksContainer.show();
        $openTasksContainer.hide();
        loadStudyPlans(1); // Load completed tasks
    });

    // Event delegation for checkbox changes
    $(document).on('change', '.study-checkbox', function() {
        const $item = $(this).closest('.study-item');
        const planId = $item.data('id');
        const isChecked = $(this).is(':checked');
        const newStatus = isChecked ? 1 : 0; // 1 for completed, 0 for open

        $.ajax({
            url: `/api/studyplan/${planId}`,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({ status: newStatus }),
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // Move the item to the correct tab
                    $item.remove();
                    if (newStatus === 1) {
                        displayStudyPlan(response.study_plan, $completedTasksContainer);
                        // If user is on open tab, they won't see it move unless they switch
                    } else {
                        displayStudyPlan(response.study_plan, $openTasksContainer);
                         // If user is on completed tab, they won't see it move unless they switch
                    }
                    // Optional: Reload the current tab to reflect all changes
                    if ($openTab.hasClass('active')) {
                        loadStudyPlans(0);
                    } else {
                        loadStudyPlans(1);
                    }
                } else {
                    alert('Error updating plan status: ' + (response.message || 'Unknown error'));
                    // Revert checkbox state on error
                    $(this).prop('checked', !isChecked);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error updating plan status:", textStatus, errorThrown);
                alert('An error occurred while updating the plan. Please try again.');
                $(this).prop('checked', !isChecked); // Revert checkbox
            }
        });
    });

    // Event delegation for delete button clicks
    $(document).on('click', '.delete-btn', function() {
        const $item = $(this).closest('.study-item');
        const planId = $item.data('id');

        if (!confirm('Are you sure you want to delete this study plan?')) {
            return;
        }

        $.ajax({
            url: `/api/studyplan/${planId}`,
            method: 'DELETE',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    $item.remove();
                } else {
                    alert('Error deleting study plan: ' + (response.message || 'Unknown error'));
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error deleting study plan:", textStatus, errorThrown);
                alert('An error occurred while deleting the study plan. Please try again.');
            }
        });
    });


    // Initial load of open tasks
    loadStudyPlans(0);
});