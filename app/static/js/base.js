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


            
    // TODO:🌟 Initialization for JS everytimes the page is switched
    if (url === '/mainpage') {
        if (typeof initMainpageFeatures === 'function') {
            initMainpageFeatures(); // ✅ 🟨 mainpage 初始化
        }
    }
    if (url === '/studyplan') {
        if (typeof initStudyplanFeatures === 'function') {
            initStudyplanFeatures(); // ✅ 🟨 studyplan 初始化
        }
    }
    if (url === '/dashboard') {
        if (typeof initDashboardFeatures === 'function') {
            initDashboardFeatures(); // ✅ 🟨 dashboard 初始化
        }
    }
    
    if (url === '/notification') {
        if (typeof initNotificationFeatures === 'function') {
            initNotificationFeatures(); // ✅ 🟨 notification 初始化（
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