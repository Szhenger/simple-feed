import { Formatter } from './app.js';

/**
 * Metrics Dashboard & Workspace Configuration Overlay
 */
document.addEventListener('DOMContentLoaded', () => {
    initSettingsModal();
    initTelemetryStream();
});

function initSettingsModal() {
    const modal = document.getElementById('settings-modal');
    const openBtn = document.getElementById('open-settings');
    const closeBtn = document.getElementById('close-settings');

    if (!modal) return;

    // Handle open toggle via custom intercept
    if (openBtn) {
        openBtn.addEventListener('click', (e) => {
            e.preventDefault();
            modal.classList.add('open');
        });
    }

    // Explicit close button hook
    if (closeBtn) {
        closeBtn.addEventListener('click', () => modal.classList.remove('open'));
    }

    // Implicit background window dismiss click hook
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('open');
    });
}

function initTelemetryStream() {
    const vectorCountNode = document.querySelector('.metric-card:nth-child(1) .card-value');
    const latencyNode = document.querySelector('.metric-card:nth-child(3) .card-value');
    
    if (!vectorCountNode || !latencyNode) return;

    let totalVectors = parseInt(vectorCountNode.textContent.replace(/,/g, ''), 10);

    // Simulate reactive write-barrier telemetry from Celery workers
    setInterval(() => {
        // Mock occasional incoming batch increments
        if (Math.random() > 0.4) {
            totalVectors += Math.floor(Math.random() * 8) + 1;
            vectorCountNode.textContent = Formatter.number(totalVectors);
            
            // Apply millisecond fluctuation tracking back to kernel performance metrics
            const currentLatency = 1.15 + (Math.random() * 0.35);
            latencyNode.textContent = `${Formatter.decimal(currentLatency, 2)}ms`;
        }
    }, 2500);
}
