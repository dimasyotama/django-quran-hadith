// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // Enables dark mode to be toggled via a 'dark' class on the <html> tag
  content: [
    './**/templates/**/*.html',    // Scans all .html files in all template folders of all apps
    './templates/**/*.html',        // Scans .html files in a project-level template folder (if you have one)
    './core/static/core/js/**/*.js', // Scans JS files in your core app's static js folder
    // Add paths to any other app's static JS folders if they manipulate Tailwind classes:
    // './quran_app/static/quran_app/js/**/*.js',
    // './hadith_app/static/hadith_app/js/**/*.js',
  ],
  theme: {
    extend: {
      fontFamily: {
        // Sets a modern, cross-platform sans-serif font stack as the default.
        // Your '.font-quran' or '.font-arabic' class for Arabic text will be
        // defined separately in your main CSS input file (e.g., tailwind-input.css).
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', '"Noto Sans"', 'sans-serif', '"Apple Color Emoji"', '"Segoe UI Emoji"', '"Segoe UI Symbol"', '"Noto Color Emoji"'],
      },
      colors: {
        // Green shades for general branding and Hadith section accents
        'brand-green': {
          light: '#6EE7B7',     // emerald-300 (example)
          DEFAULT: '#10B981',   // emerald-500 (example)
          dark: '#059669',      // emerald-600 (example)
          foreground: '#047857', // emerald-700 for text on light green backgrounds (example)
        },
        // Blue shades for Qur'an section accents
        'brand-blue': {
          light: '#93C5FD',     // blue-300 (example)
          DEFAULT: '#3B82F6',   // blue-500 (example)
          dark: '#2563EB',      // blue-600 (example)
          foreground: '#1E40AF', // blue-800 for text on light blue backgrounds (example)
        },
        // You can add more custom colors here if needed
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'), // Provides base styling for form elements
    // require('@tailwindcss/typography'), // Useful if you have blocks of text (like articles or Markdown content) that you want to style with good defaults.
  ],
}