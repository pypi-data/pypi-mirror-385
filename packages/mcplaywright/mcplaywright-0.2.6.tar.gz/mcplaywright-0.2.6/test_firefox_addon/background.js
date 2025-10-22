// MCPlaywright Test Addon - Background Script
// Handles addon lifecycle and browser action

console.log('🦊 MCPlaywright Firefox Test Addon - Background script loaded');

// Listen for browser action clicks
browser.browserAction.onClicked.addListener((tab) => {
    console.log('MCPlaywright Test Addon clicked on tab:', tab.id);

    // Send message to content script
    browser.tabs.sendMessage(tab.id, {
        type: 'addon-clicked',
        timestamp: Date.now(),
        tabId: tab.id
    }).catch(err => {
        console.log('Could not send message to tab:', err.message);
    });

    // Show notification (if we had notifications permission)
    console.log('✅ MCPlaywright Firefox addon is working!');
});

// Log when addon is installed
browser.runtime.onInstalled.addListener((details) => {
    console.log('MCPlaywright addon installed:', details.reason);
    console.log('Addon version:', browser.runtime.getManifest().version);
});

// Keep addon active
console.log('MCPlaywright Test Addon ready');
console.log('Manifest:', browser.runtime.getManifest());
