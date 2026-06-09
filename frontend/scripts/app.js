/**
 * Shared Application Core Module
 */
document.addEventListener('DOMContentLoaded', () => {
    initGlobalNavigation();
});

function initGlobalNavigation() {
    // Select workspace navigation nodes for active route mapping
    const menuItems = document.querySelectorAll('.menu-item');
    const currentPath = window.location.pathname;

    menuItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href)) {
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        }
    });

    console.log("🚀 SimpleFeed++ Common Runtime Loaded.");
}

// Global utility for localized data formatting
export const Formatter = {
    number: (num) => new Intl.NumberFormat('en-US').format(num),
    decimal: (num, places = 3) => num.toFixed(places)
};
