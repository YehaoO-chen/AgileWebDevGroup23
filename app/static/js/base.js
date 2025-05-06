// Function to update the navbar avatar from localStorage
function updateNavbarAvatar() {
    const defaultAvatarUrl = 'https://st2.depositphotos.com/53447130/50476/v/450/depositphotos_504768188-stock-illustration-pixel-black-cat-image-vector.jpg';
    const AVATAR_STORAGE_KEY = 'userAvatarUrl'; // Same key used in profile.js
    const $navbarProfileImg = $('.dropdown-toggle .profile-img'); // Selector for the navbar image

    if ($navbarProfileImg.length) { // Check if the element exists
        const storedAvatarUrl = localStorage.getItem(AVATAR_STORAGE_KEY);
        const finalUrl = storedAvatarUrl || defaultAvatarUrl; // Use stored URL or default

        $navbarProfileImg.attr('src', finalUrl);

    } else {
        $navbarProfileImg.attr('src', defaultAvatarUrl);
        console.warn("Navbar profile image element not found."); // Optional warning
    }
}

// Function to initialize Study Plan functionality
function initStudyPlan() {
    // Get references to elements
    const studyInput = document.getElementById('studyInput');
    const addButton = document.getElementById('addButton');
    const openTab = document.getElementById('openTab');
    const completedTab = document.getElementById('completedTab');
    const openTasks = document.getElementById('openTasks');
    const completedTasks = document.getElementById('completedTasks');
    
    if (!studyInput || !addButton || !openTab || !completedTab || !openTasks || !completedTasks) {
        console.warn('Study Plan elements not found, skipping initialization');
        return; // Exit if elements not found
    }
    
    console.log('Initializing Study Plan functionality');
    
    // Tab switching functionality
    openTab.addEventListener('click', function() {
        openTab.classList.add('active');
        completedTab.classList.remove('active');
        openTasks.style.display = 'block';
        completedTasks.style.display = 'none';
    });
    
    completedTab.addEventListener('click', function() {
        completedTab.classList.add('active');
        openTab.classList.remove('active');
        completedTasks.style.display = 'block';
        openTasks.style.display = 'none';
    });
    
    // Add new task functionality
    addButton.addEventListener('click', function() {
        const taskText = studyInput.value.trim();
        if (taskText) {
            addTask(taskText);
            studyInput.value = '';
        }
    });
    
    // Also allow Enter key to add task
    studyInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const taskText = studyInput.value.trim();
            if (taskText) {
                addTask(taskText);
                studyInput.value = '';
            }
        }
    });
    
    // Function to add new task
    function addTask(text) {
        const taskItem = document.createElement('div');
        taskItem.className = 'study-item';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'study-checkbox';
        
        const taskText = document.createElement('span');
        taskText.className = 'study-text';
        taskText.textContent = text;
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
            </svg>
        `;
        
        taskItem.appendChild(checkbox);
        taskItem.appendChild(taskText);
        taskItem.appendChild(deleteBtn);
        
        openTasks.appendChild(taskItem);
    }
}

// Function to initialize page-specific functionality based on URL
function initPageSpecificFunctionality(path) {
    if (path.includes('/studyplan')) {
        // Wait a brief moment for DOM to be fully ready after AJAX load
        setTimeout(initStudyPlan, 50);
    }
    // Add more page-specific initializations as needed
}

// Function to load content into the main area via AJAX
function loadMainContent(url) {
    $.ajax({
        url: url,
        method: 'GET',
        // Send a header to tell the server this is an AJAX request
        // Or use a query parameter like url + '?partial=true'
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(data) {
            try {
                // Use jQuery to parse the HTML string and find the title element
                const $html = $($.parseHTML(data, document, true)); // 'true' to include scripts if needed later
                const titleText = $html.filter('title').text().trim();

                // Check if the title matches the login page title
                if (titleText === 'Login - ProcrastiNo') {
                    console.log("Received login page content, redirecting to root.");
                    // Redirect to the root URL (or login page if preferred)
                    window.location.href = '/'; // Or window.location.href = '/login';
                    return; // Stop further processing in this success handler
                }
            } catch (e) {
                // If parsing fails, log error but proceed with caution
                console.warn("Could not parse response HTML to check title:", e);
            }
            // Replace the content of the <main> tag
            $('main').html(data);
            
            // Scroll to top or handle focus
            window.scrollTo(0, 0);
            
            // Initialize functionality specific to this page
            initPageSpecificFunctionality(url);
            
            // Set up event delegation for checkbox changes
            $(document).off('change', '.study-checkbox').on('change', '.study-checkbox', function() {
                const taskItem = $(this).closest('.study-item')[0];
                const openTasks = document.getElementById('openTasks');
                const completedTasks = document.getElementById('completedTasks');
                
                if (!openTasks || !completedTasks) return;
                
                if ($(this).is(':checked')) {
                    // Move to completed tasks
                    openTasks.removeChild(taskItem);
                    completedTasks.appendChild(taskItem);
                } else {
                    // Move back to open tasks
                    completedTasks.removeChild(taskItem);
                    openTasks.appendChild(taskItem);
                }
            });
            
            // Set up event delegation for delete buttons
            $(document).off('click', '.delete-btn').on('click', '.delete-btn', function() {
                $(this).closest('.study-item').remove();
            });
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error("Error loading content:", textStatus, errorThrown);
            // Display an error message to the user in the main area
            $('main').html('<p class="error">Sorry, could not load the page content.</p>');
        }
    });
}

$(document).ready(function() {
    // --- Navbar Avatar Update ---
    updateNavbarAvatar(); // Call immediately on load
    const currentPath = location.pathname;

    // Define which paths should be loaded via AJAX initially.
    // Exclude paths like /login, /signup, /logout which are typically full page loads.
    const ajaxLoadPaths = ['/home', '/study_plan', '/studyplan', '/dashboard', '/notification', '/profile'];
    // Determine the actual path to load content for (e.g., map '/' to '/home')
    let pathToLoad = currentPath;
    let activeLinkSelectorPath = currentPath;

    if (currentPath === '/') {
        // If the root path should display the 'home' content and highlight the 'home' link
        pathToLoad = '/home';
        activeLinkSelectorPath = '/home';
    }

    // Check if the determined path is one we should load via AJAX
    if (ajaxLoadPaths.includes(pathToLoad)) {
        console.log("Initial AJAX load for path:", pathToLoad); // For debugging
        loadMainContent(pathToLoad);
    } else {
        // If the current path isn't meant for AJAX loading (e.g., /login),
        // we assume the server rendered the full correct page.
        // We still might want to set the active class based on server rendering.
        console.log("Path not in initial AJAX load list:", currentPath); // For debugging
        // The server-side Jinja {% if request.endpoint == ... %} should handle the active class here.
        // If Jinja logic is removed, you might need JS logic here too.
    }

    // --- Set Active Class Based on Initial Path (Client-side) ---
    // This ensures the active class is correct even if server-side logic is missing or different,
    // and handles the mapping of '/' to '/home' link.
    $('.sidebar .nav-custom').removeClass('active');
    $('.dropdown-menu .dropdown-item').removeClass('active');
    $('.profile-img').removeClass('active-profile');

    // Find the link corresponding to the path that should be active
    const activeLink = $(`.sidebar a.nav-custom[href="${activeLinkSelectorPath}"]`);

    if (activeLink.length) {
        activeLink.addClass('active');
        console.log("Set active class on:", activeLinkSelectorPath); // For debugging
    } else if (currentPath === '/profile') { // Special handling for profile in dropdown
         $('.dropdown-menu .dropdown-item[href="/profile"]').addClass('active');
         $('.profile-img').addClass('active-profile');
         console.log("Set active class on: profile (dropdown)"); // For debugging
    }

    // --- AJAX Navigation --- << UNCOMMENT THIS SECTION >>
    // Attach click listener to sidebar navigation links
    // Use event delegation on a stable parent (like '.sidebar')
    $('.sidebar').on('click', 'a.nav-custom', function(event) {
        // Get the URL from the link's href
        const targetUrl = $(this).attr('href');

        // Check if it's an internal link (avoids external links or javascript:;)
        // and not the logout link (which should cause a full redirect)
        if (targetUrl && targetUrl.startsWith('/') && !$(this).closest('.logout').length) {
            event.preventDefault(); // Prevent default full page load

            // Load the content via AJAX using the existing function
            loadMainContent(targetUrl);

            // Update the browser URL bar without reloading
            history.pushState({ path: targetUrl }, '', targetUrl);

            // --- Add active class handling ---
            // Remove active class from all nav links
            $('.sidebar .nav-custom').removeClass('active');
            // Add active class to the clicked link
            $(this).addClass('active');
            // Also handle the profile link in the dropdown if necessary
            if (targetUrl === '/profile') {
                $('.dropdown-menu .dropdown-item[href="/profile"]').addClass('active');
                $('.profile-img').addClass('active-profile'); // If you have styles for this
            } else {
                $('.dropdown-menu .dropdown-item[href="/profile"]').removeClass('active');
                 $('.profile-img').removeClass('active-profile');
            }


        }
        // Allow default behavior for logout or external links
    });

    // Handle browser back/forward buttons << UNCOMMENT THIS SECTION >>
    $(window).on('popstate', function(event) {
        let targetPath = location.pathname; // Default to current path
        // Check if the event has state (means it was triggered by pushState)
        if (event.originalEvent.state && event.originalEvent.state.path) {
            targetPath = event.originalEvent.state.path;
        }
        // Load the content for the URL associated with the state or current location
        loadMainContent(targetPath);

        // --- Update active class on back/forward ---
        $('.sidebar .nav-custom').removeClass('active');
        $('.dropdown-menu .dropdown-item').removeClass('active');
        $('.profile-img').removeClass('active-profile');

        // Find the link corresponding to the new path and add active class
        const activeLink = $(`.sidebar a.nav-custom[href="${targetPath}"]`);
        if (activeLink.length) {
            activeLink.addClass('active');
        } else if (targetPath === '/profile') {
             $('.dropdown-menu .dropdown-item[href="/profile"]').addClass('active');
             $('.profile-img').addClass('active-profile');
        }
    });

    // --- Other base.js functionality ---
    console.log("DOM is fully ready.");


});
