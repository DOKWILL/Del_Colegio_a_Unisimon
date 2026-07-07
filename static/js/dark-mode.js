/**
 * Dark mode toggle with localStorage persistence.
 */
(function() {
    const THEME_KEY = 'unisimon-theme';

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const icon = document.getElementById('dark-mode-icon');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    // Apply saved theme on load
    const saved = localStorage.getItem(THEME_KEY) || 'light';
    applyTheme(saved);

    // Toggle on click
    document.addEventListener('DOMContentLoaded', function() {
        const toggle = document.getElementById('dark-mode-toggle');
        if (toggle) {
            toggle.addEventListener('click', function() {
                const current = document.documentElement.getAttribute('data-theme') || 'light';
                const next = current === 'dark' ? 'light' : 'dark';
                localStorage.setItem(THEME_KEY, next);
                applyTheme(next);
            });
        }
    });
})();
