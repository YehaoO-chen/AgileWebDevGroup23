// === base.js ===

function updateNavbarAvatar() {
    const defaultAvatarUrl = 'https://st2.depositphotos.com/53447130/50476/v/450/depositphotos_504768188-stock-illustration-pixel-black-cat-image-vector.jpg';
    const AVATAR_STORAGE_KEY = 'userAvatarUrl';
    const $navbarProfileImg = $('.dropdown-toggle .profile-img');

    if ($navbarProfileImg.length) {
        const storedAvatarUrl = localStorage.getItem(AVATAR_STORAGE_KEY);
        const finalUrl = storedAvatarUrl || defaultAvatarUrl;
        $navbarProfileImg.attr('src', finalUrl);
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

            // Find and execute all inline scripts
            $html.filter('script').each(function () {
                const newScript = document.createElement('script');
                if (this.src) {
                    newScript.src = this.src;
                } else {
                    newScript.textContent = this.textContent;
                }
                document.body.appendChild(newScript);
            });

            // Call page-specific initialization functions
            if (url === '/notification' && typeof window.loadNotifications === 'function') {
                console.log('Calling loadNotifications() function');
                window.loadNotifications();
            }
            
            if (url === '/dashboard' && typeof window.loadDashboardData === 'function') {
                console.log('Calling loadDashboardData() function');
                window.loadDashboardData();
            }

            // Load page-specific script files if needed
            if (url === '/notification' && typeof window.loadNotifications === 'undefined') {
                console.log('Loading external notification.js file');
                const script = document.createElement('script');
                script.src = '/static/js/notification.js';
                script.onload = function() {
                    if (typeof window.loadNotifications === 'function') {
                        window.loadNotifications();
                    }
                };
                document.body.appendChild(script);
            }
            
            // Load dashboard.js if needed
            if (url === '/dashboard') {
                const script = document.createElement('script');
                script.src = '/static/js/dashboard.js';
                script.onload = function () {
                    console.log('dashboard.js loaded');
                    if (typeof window.loadDashboardData === 'function') {
                        window.loadDashboardData();
                    } else {
                        console.error('loadDashboardData function not found');
                    }
            
                    if (typeof window.bindDashboardFilters === 'function') {
                        window.bindDashboardFilters();
                    } else {
                        console.error('bindDashboardFilters function not found');
                    }
                };
                document.body.appendChild(script);
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
    const ajaxLoadPaths = ['/mainpage', '/study_plan', '/dashboard', '/notification', '/profile'];
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