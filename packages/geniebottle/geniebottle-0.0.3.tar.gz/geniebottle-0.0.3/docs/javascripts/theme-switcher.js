/**
 * Ancient Scroll Theme Switcher for Genie Bottle Documentation
 * Allows switching between Medieval, Ancient China, and Ancient Japan themes
 * Persists user preference in localStorage
 */

(function() {
  'use strict';

  const THEME_KEY = 'geniebottle-theme';
  const THEMES = {
    medieval: 'Codex',
    china: 'Juàn',
    japan: 'Emaki'
  };

  /**
   * Get the current theme from localStorage or default to 'medieval'
   */
  function getCurrentTheme() {
    return localStorage.getItem(THEME_KEY) || 'medieval';
  }

  /**
   * Apply the theme to the document
   */
  function applyTheme(theme) {
    if (!THEMES[theme]) {
      theme = 'medieval';
    }
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
  }

  /**
   * Create the theme switcher UI
   */
  function createThemeSwitcher() {
    // Check if switcher already exists
    if (document.querySelector('.theme-switcher')) {
      return;
    }

    // Try to find the header inner container
    const headerInner = document.querySelector('.md-header__inner');
    if (!headerInner) {
      // Fallback to body if header not found
      console.warn('Header not found, waiting...');
      return;
    }

    const switcher = document.createElement('div');
    switcher.className = 'theme-switcher';

    const label = document.createElement('label');
    label.textContent = 'Theme';
    label.setAttribute('for', 'theme-select');

    const select = document.createElement('select');
    select.id = 'theme-select';
    select.setAttribute('aria-label', 'Select documentation theme');
    select.setAttribute('data-tooltip', 'Choose scroll style: Codex (Medieval), Juàn (Chinese), or Emaki (Japanese)');

    // Create options with historically accurate scroll names
    const shortNames = {
      medieval: 'Codex',
      china: 'Juàn',
      japan: 'Emaki'
    };

    Object.entries(shortNames).forEach(([value, name]) => {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = name;
      select.appendChild(option);
    });

    // Set current theme
    const currentTheme = getCurrentTheme();
    select.value = currentTheme;

    // Add change listener
    select.addEventListener('change', (e) => {
      const newTheme = e.target.value;
      applyTheme(newTheme);
    });

    switcher.appendChild(label);
    switcher.appendChild(select);

    // Append to header instead of body
    headerInner.appendChild(switcher);
  }

  /**
   * Initialize the theme system
   */
  function init() {
    // Apply saved theme immediately to prevent flash
    const savedTheme = getCurrentTheme();
    applyTheme(savedTheme);

    // Create switcher when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', createThemeSwitcher);
    } else {
      createThemeSwitcher();
    }
  }

  // Run initialization
  init();

  // Handle page navigation in single-page apps (MkDocs Material)
  document.addEventListener('DOMContentLoaded', function() {
    // MkDocs Material instant loading support
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList' && !document.querySelector('.theme-switcher')) {
          createThemeSwitcher();
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: false
    });
  });

  // Export for debugging
  window.GenieBottleTheme = {
    getCurrentTheme,
    applyTheme,
    availableThemes: Object.keys(THEMES)
  };
})();
