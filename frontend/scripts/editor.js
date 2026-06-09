/**
 * Notion Canvas Block Editor Behavior
 */
document.addEventListener('DOMContentLoaded', () => {
    initEditorPersistence();
    initSlashCommands();
});

function initEditorPersistence() {
    const canvas = document.querySelector('.notion-canvas');
    if (!canvas) return;

    const pageId = window.location.pathname + "-content";

    // Load persisted state if existing
    const savedContent = localStorage.getItem(pageId);
    if (savedContent) {
        canvas.innerHTML = savedContent;
    }

    // Debounce state saving to preserve CPU cycles on heavy typing loops
    let saveTimeout;
    canvas.addEventListener('input', () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            localStorage.setItem(pageId, canvas.innerHTML);
            updateHeaderStatus("Saved");
        }, 800);
        updateHeaderStatus("Saving...");
    });
}

function updateHeaderStatus(statusText) {
    const statusBtn = document.querySelector('.header-actions .btn-action:last-child');
    if (statusBtn) {
        statusBtn.textContent = statusText;
    }
}

function initSlashCommands() {
    const canvas = document.querySelector('.notion-canvas');
    if (!canvas) return;

    // Detect Notion's classic command block initiation pattern
    canvas.addEventListener('keydown', (e) => {
        if (e.key === '/') {
            console.log("💡 Slash command context intercept triggered. Displaying dynamic block menu placeholder...");
            // Production expansion: Inject a absolute-positioned popover menu here
        }
    });
}
