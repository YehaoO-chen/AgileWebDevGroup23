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
updateNavbarAvatar();
// 