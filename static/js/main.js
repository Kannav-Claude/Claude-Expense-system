// main.js — students will add JavaScript here as features are built

function openVideoModal() {
    const modal = document.getElementById('videoModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeVideoModal() {
    const modal = document.getElementById('videoModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

// Close modal when pressing Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeVideoModal();
    }
});

// Date filter validation
function initDateFilter() {
    var form = document.getElementById('filterForm');
    if (!form) { return; }
    form.addEventListener('submit', function(e) {
        var start = document.getElementById('start_date').value;
        var end = document.getElementById('end_date').value;
        if (start && end && start > end) {
            e.preventDefault();
            alert('Start date must be on or before the end date.');
        }
    });
}

document.addEventListener('DOMContentLoaded', initDateFilter);
