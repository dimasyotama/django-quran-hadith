// Assuming this is in main.js, line numbers will differ.
// Let's count lines from where the actual JS logic starts.
// (Comments and blank lines would shift this)

// 1
document.addEventListener('DOMContentLoaded', function () {
// 2
    const darkModeToggle = document.getElementById('darkModeToggle');
// 3
    const iconSun = document.getElementById('icon-sun');
// 4
    const iconMoon = document.getElementById('icon-moon');
// 5
    const htmlEl = document.documentElement;
// 6

// 7
    const mobileMenuButton = document.getElementById('mobileMenuButton');
// 8
    const mobileMenuFlyout = document.getElementById('mobile-menu-flyout');
// 9
    const iconMenuBurger = document.getElementById('icon-menu-burger');
// 10
    const iconMenuClose = document.getElementById('icon-menu-close');
// 11

// 12
    function setTheme(theme) {
// 13
        if (theme === 'dark') {
// 14
            htmlEl.classList.add('dark');
// 15
            if(iconSun) iconSun.style.display = 'none'; // Check if element exists
// 16
            if(iconMoon) iconMoon.style.display = 'block';// Check if element exists
// 17
            localStorage.setItem('theme', 'dark');
// 18
        } else {
// 19
            htmlEl.classList.remove('dark');
// 20
            if(iconSun) iconSun.style.display = 'block'; // Check if element exists
// 21
            if(iconMoon) iconMoon.style.display = 'none'; // Check if element exists
// 22
            localStorage.setItem('theme', 'light');
// 23
        }
// 24
    }
// 25

// 26
    const storedTheme = localStorage.getItem('theme');
// 27
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
// 28
    if (storedTheme) {
// 29
        setTheme(storedTheme);
// 30
    } else {
// 31
        setTheme(systemPrefersDark ? 'dark' : 'light');
// 32  <-- If line 33 is column 2, the error might be the start of the next line or related to this block
    }
// 33  <-- Line 33 could be here if you have extra comments/lines above
// 34
    if(darkModeToggle) { // Check if the button exists before adding listener
// 35
        darkModeToggle.addEventListener('click', () => {
// 36
            const currentTheme = htmlEl.classList.contains('dark') ? 'dark' : 'light';
// 37
            setTheme(currentTheme === 'dark' ? 'light' : 'dark');
// 38
        });
// 39
    }
// 40

// 41
    if(mobileMenuButton && mobileMenuFlyout && iconMenuBurger && iconMenuClose) { // Check elements
// 42
        mobileMenuButton.addEventListener('click', () => {
// 43
            const isExpanded = mobileMenuButton.getAttribute('aria-expanded') === 'true';
// 44
            mobileMenuButton.setAttribute('aria-expanded', String(!isExpanded));
// 45
            mobileMenuFlyout.classList.toggle('hidden');
// 46
            iconMenuBurger.classList.toggle('hidden');
// 47
            iconMenuClose.classList.toggle('hidden');
// 48
        });
// 49
    }
// 50
});