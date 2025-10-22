// MCPlaywright Test Addon - Content Script
// Injects a visual indicator showing the addon is active

(function() {
    'use strict';

    // Create visual indicator
    const indicator = document.createElement('div');
    indicator.id = 'mcplaywright-firefox-indicator';
    indicator.innerHTML = `
        <div style="
            position: fixed;
            top: 10px;
            right: 10px;
            background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%);
            color: #000;
            padding: 8px 16px;
            border-radius: 6px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 12px;
            font-weight: bold;
            z-index: 999999;
            box-shadow: 0 4px 12px rgba(0, 255, 0, 0.3);
            border: 2px solid #00ff00;
            animation: mcplay-pulse 2s ease-in-out infinite;
        ">
            🦊 MCPlaywright Firefox Addon Active
        </div>
        <style>
            @keyframes mcplay-pulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.85; transform: scale(0.98); }
            }
        </style>
    `;

    // Inject when DOM is ready
    if (document.body) {
        document.body.appendChild(indicator);
    } else {
        document.addEventListener('DOMContentLoaded', () => {
            document.body.appendChild(indicator);
        });
    }

    // Log to console for verification
    console.log('%c🦊 MCPlaywright Firefox Test Addon Loaded',
                'background: #00ff00; color: #000; padding: 4px 8px; border-radius: 4px; font-weight: bold;');
    console.log('Addon ID: mcplaywright-test@example.com');
    console.log('Page URL:', window.location.href);
    console.log('User Agent:', navigator.userAgent);
})();
