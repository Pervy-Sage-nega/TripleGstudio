document.addEventListener('DOMContentLoaded', function () {
    const modalOverlay = document.getElementById('customModalOverlay');
    const closeButton = modalOverlay ? modalOverlay.querySelector('.custom-modal-close') : null;
    let autoDismissTimer = null;

    function showModal() {
        if (modalOverlay) {
            modalOverlay.style.display = 'flex';
            setTimeout(() => {
                modalOverlay.classList.add('custom-visible');
            }, 10);
        }
    }

    function hideModal() {
        if (modalOverlay) {
            if (autoDismissTimer) {
                clearTimeout(autoDismissTimer);
                autoDismissTimer = null;
            }
            modalOverlay.classList.add('custom-fade-out');
            modalOverlay.classList.remove('custom-visible');
            setTimeout(() => {
                modalOverlay.style.display = 'none';
                modalOverlay.classList.remove('custom-fade-out');
            }, 400);
        }
    }

    // Show modal if messages exist
    if (modalOverlay) {
        showModal();

        // Auto-dismiss after 5s
        autoDismissTimer = setTimeout(() => {
            hideModal();
        }, 5000000);
    }

    // Close button
    if (closeButton) {
        closeButton.addEventListener('click', hideModal);
    }

    // Cancel and Confirm buttons
    if (modalOverlay) {
        const cancelBtns = modalOverlay.querySelectorAll('.custom-btn-cancel');
        const confirmBtns = modalOverlay.querySelectorAll('.custom-btn-confirm');
        cancelBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                hideModal();
            });
        });
        confirmBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                hideModal();
            });
        });
    }

    // Close on overlay click
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function (event) {
            if (event.target === modalOverlay) hideModal();
        });
    }

    // Pause auto-dismiss on hover
    if (modalOverlay) {
        modalOverlay.addEventListener('mouseenter', function () {
            if (autoDismissTimer) {
                clearTimeout(autoDismissTimer);
                autoDismissTimer = null;
            }
        });

        modalOverlay.addEventListener('mouseleave', function () {
            if (!autoDismissTimer) {
                autoDismissTimer = setTimeout(() => {
                    hideModal();
                }, 3000000);
            }
        });
    }
});
