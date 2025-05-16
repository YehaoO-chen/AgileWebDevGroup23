// === base.js ===

function updateNavbarAvatar() {
    const defaultAvatarUrl = 'https://st2.depositphotos.com/53447130/50476/v/450/depositphotos_504768188-stock-illustration-pixel-black-cat-image-vector.jpg';
    const AVATAR_STORAGE_KEY = 'userAvatarUrl'; // Same key used in profile.js
    const $navbarProfileImg = $('.dropdown-toggle .profile-img'); // Selector for the navbar image
    console.log("check...."); // Optional log

    if ($navbarProfileImg.length) { // Check if the element exists
        console.log("Navbar profile image element found."); // Optional log
        $.ajax({
            url: '/api/profile', // GET request to fetch user data
            method: 'GET',
            dataType: 'json',
            success: function(user) {
                
                if (user.avatar && user.avatar !== defaultAvatarUrl && user.avatar !== '' && user.avatar !== 'default.jpg') {
                    // Assuming avatar field stores filename like 'user_1_avatar.png'
                    avatarSrc = `/static/uploads/${user.avatar}`; // Construct path
                } else {
                    //  avatarSrc = `/static/images/default_avatar.png`; // Or your actual default image path
                     avatarSrc = defaultAvatarUrl; // Fallback to default avatar URL
                }
                console.log("Avatar source set to:", avatarSrc); // Optional log
                console.log($navbarProfileImg)
                $navbarProfileImg.attr('src', avatarSrc);

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error loading profile:", textStatus, errorThrown);
                showNotification('Failed to load profile data.', 'error');
            }
        });



    } else {
        console.warn("Navbar profile image element not found.");
    }
}

function loadMainContent(url) {
    console.log('Loading content for URL:', url);
    $.ajax({
        url: url,
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function (data) {
            const $html = $($.parseHTML(data, document, true));
            const titleText = $html.filter('title').text().trim();
            if (titleText === 'Login - ProcrastiNo') {
                window.location.href = '/';
                return;
            }

            // Update the main content
            $('main').html(data);


            
    // Initialization for JS everytimes the page is switched
    if (url === '/mainpage') {
        if (typeof initMainpageFeatures === 'function') {
            initMainpageFeatures(); 
        }else {
                    console.warn("initMainpageFeatures function not found for /mainpage, but was expected.");
                }
    }
    if (url === '/studyplan') {
        if (typeof initStudyplanFeatures === 'function') {
            initStudyplanFeatures(); 
        }else {
            console.warn("initStudyplanFeatures function not found for /studyplan, but was expected.");
        }
    }
    if (url === '/dashboard') {
        if (typeof initDashboardFeatures === 'function') {
            initDashboardFeatures();
        }else {
                    console.warn("initDashboardFeatures function not found for /dashboard, but was expected.");
                }
    }
    
    if (url === '/notification') {
        if (typeof initNotificationFeatures === 'function') {
            initNotificationFeatures(); 
        }else {
                    console.warn("initNotificationFeatures function not found for /notification, but was expected.");
                }
    }


            window.scrollTo(0, 0);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error("Error loading content:", textStatus, errorThrown);
            $('main').html('<p class="error">Sorry, could not load the page content.</p>');
        }
    });
}

$(document).ready(function () {
    console.log('Document ready, initializing base.js');
    
    updateNavbarAvatar();
    const currentPath = location.pathname;

    // Define which paths should be loaded via AJAX initially.
    // Exclude paths like /login, /signup, /logout which are typically full page loads.
    const ajaxLoadPaths = ['/mainpage', '/studyplan', '/dashboard', '/notification', '/profile'];
    // Determine the actual path to load content for (e.g., map '/' to '/home')

    let pathToLoad = currentPath;
    let activeLinkSelectorPath = currentPath;

    if (currentPath === '/') {
        pathToLoad = '/mainpage';
        activeLinkSelectorPath = '/mainpage';
    }

    if (ajaxLoadPaths.includes(pathToLoad)) {
        console.log("Initial AJAX load for path:", pathToLoad);
        loadMainContent(pathToLoad);
    } else {
        console.log("Path not in initial AJAX load list:", currentPath);
    }

    $('.sidebar .nav-custom').removeClass('active');
    $('.dropdown-menu .dropdown-item').removeClass('active');
    $('.profile-img').removeClass('active-profile');

    const activeLink = $(`.sidebar a.nav-custom[href="${activeLinkSelectorPath}"]`);
    if (activeLink.length) {
        activeLink.addClass('active');
    } else if (currentPath === '/profile') {
        $('.dropdown-menu .dropdown-item[href="/profile"]').addClass('active');
        $('.profile-img').addClass('active-profile');
    }

    $('.sidebar').on('click', 'a.nav-custom', function (event) {
        const targetUrl = $(this).attr('href');
        if (targetUrl && targetUrl.startsWith('/') && !$(this).closest('.logout').length) {
            event.preventDefault();
            
            // Update UI first for responsiveness
            $('.sidebar .nav-custom').removeClass('active');
            $(this).addClass('active');
            
            if (targetUrl === '/profile') {
                $('.dropdown-menu .dropdown-item[href="/profile"]').addClass('active');
                $('.profile-img').addClass('active-profile');
            } else {
                $('.dropdown-menu .dropdown-item[href="/profile"]').removeClass('active');
                $('.profile-img').removeClass('active-profile');
            }
            
            // Then load content
            loadMainContent(targetUrl);
            history.pushState({ path: targetUrl }, '', targetUrl);
        }
    });

    $(window).on('popstate', function (event) {
        let targetPath = location.pathname;
        if (event.originalEvent.state && event.originalEvent.state.path) {
            targetPath = event.originalEvent.state.path;
        }
        
        // Update UI
        $('.sidebar .nav-custom').removeClass('active');
        $('.dropdown-menu .dropdown-item').removeClass('active');
        $('.profile-img').removeClass('active-profile');

        const activeLink = $(`.sidebar a.nav-custom[href="${targetPath}"]`);
        if (activeLink.length) {
            activeLink.addClass('active');
        } else if (targetPath === '/profile') {
            $('.dropdown-menu .dropdown-item[href="/profile"]').addClass('active');
            $('.profile-img').addClass('active-profile');
        }
        
        // Load content
        loadMainContent(targetPath);
    });
});