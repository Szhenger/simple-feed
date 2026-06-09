/**
 * Native HTML5 Kanban Triage Pipeline Controller
 */
document.addEventListener('DOMContentLoaded', () => {
    initKanbanPipeline();
});

function initKanbanPipeline() {
    const cards = document.querySelectorAll('.kanban-card');
    const columns = document.querySelectorAll('.column-cards-wrapper');

    if (cards.length === 0 || columns.length === 0) return;

    // Initialize Card Drag Listeners
    cards.forEach(card => {
        // Force attribute layer to enable browser drop-shadow drag representations
        card.setAttribute('draggable', 'true');

        card.addEventListener('dragstart', (e) => {
            card.classList.add('dragging');
            e.dataTransfer.setData('text/plain', card.id || '');
            e.dataTransfer.effectAllowed = 'move';
        });

        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
        });
    });

    // Initialize Column Drop Intercept Drop Zones
    columns.forEach(column => {
        column.addEventListener('dragover', (e) => {
            e.preventDefault(); // Required macro statement to allow drop executions
            e.dataTransfer.dropEffect = 'move';
            
            const draggingCard = document.querySelector('.kanban-card.dragging');
            if (draggingCard) {
                // Determine layout positioning based on mouse hover coordinates
                const afterElement = getDragAfterElement(column, e.clientY);
                if (afterElement == null) {
                    column.appendChild(draggingCard);
                } else {
                    column.insertBefore(draggingCard, afterElement);
                }
            }
        });

        column.addEventListener('drop', () => {
            // Re-tally metrics across all pipelines immediately upon node drop
            recalculateColumnCounters();
        });
    });
}

/**
 * Calculates mouse positional offsets to insert elements mid-list
 */
function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.notion-card:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

function recalculateColumnCounters() {
    const columns = document.querySelectorAll('.kanban-column');
    
    columns.forEach(col => {
        const countBadge = col.querySelector('.column-count');
        const cardsPresent = col.querySelectorAll('.kanban-card').length;
        
        if (countBadge) {
            countBadge.textContent = cardsPresent;
        }
    });
    
    console.log("📋 Tracking matrices re-synchronized against client canvas states.");
}
