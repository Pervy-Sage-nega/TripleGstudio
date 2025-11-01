/**
 * Global Modal System for Site Diary
 */

class GlobalModal {
    constructor() {
        this.overlay = null;
        this.modal = null;
        this.callback = null;
        this.init();
    }

    init() {
        if (document.getElementById('global-modal-overlay')) return;
        if (!document.body) return;

        this.overlay = document.createElement('div');
        this.overlay.id = 'global-modal-overlay';
        this.overlay.className = 'global-modal-overlay';
        
        this.modal = document.createElement('div');
        this.modal.className = 'global-modal';
        
        this.overlay.appendChild(this.modal);
        document.body.appendChild(this.overlay);

        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });
    }

    show(options) {
        const {
            type = 'info',
            icon = 'fa-info-circle',
            title = 'Confirmation',
            subtitle = '',
            message = '',
            details = null,
            confirmText = 'Confirm',
            cancelText = 'Cancel',
            showCancel = true,
            onConfirm = null,
            onCancel = null,
            confirmClass = 'global-modal-btn-primary'
        } = options;

        this.callback = onConfirm;

        const iconHtml = `<div class="global-modal-icon ${type}"><i class="fas ${icon}"></i></div>`;
        const subtitleHtml = subtitle ? `<p class="global-modal-subtitle">${subtitle}</p>` : '';
        const detailsHtml = details ? `
            <div class="global-modal-details">
                ${Object.entries(details).map(([key, value]) => 
                    `<p><strong>${key}:</strong> ${value}</p>`
                ).join('')}
            </div>
        ` : '';
        const cancelBtn = showCancel ? 
            `<button class="global-modal-btn global-modal-btn-secondary" id="global-modal-cancel">
                <i class="fas fa-times"></i> ${cancelText}
            </button>` : '';

        this.modal.innerHTML = `
            <div class="global-modal-header">
                <button class="global-modal-close" id="global-modal-close">
                    <i class="fas fa-times"></i>
                </button>
                ${iconHtml}
                <h3 class="global-modal-title">${title}</h3>
                ${subtitleHtml}
            </div>
            <div class="global-modal-body">
                <p class="global-modal-message">${message}</p>
                ${detailsHtml}
                <div class="global-modal-loading" id="global-modal-loading">
                    <div class="global-modal-spinner"></div>
                    <p class="global-modal-loading-text">Processing...</p>
                </div>
                <div class="global-modal-footer">
                    ${cancelBtn}
                    <button class="global-modal-btn ${confirmClass}" id="global-modal-confirm">
                        <i class="fas fa-check"></i> ${confirmText}
                    </button>
                </div>
            </div>
        `;

        document.getElementById('global-modal-close').addEventListener('click', () => this.close());
        if (showCancel) {
            document.getElementById('global-modal-cancel').addEventListener('click', () => {
                if (onCancel) onCancel();
                this.close();
            });
        }
        document.getElementById('global-modal-confirm').addEventListener('click', () => this.handleConfirm());

        this.overlay.classList.add('active');
        
        // Trigger icon pop-up animation
        setTimeout(() => {
            const icon = this.modal.querySelector('.global-modal-icon');
            if (icon) icon.classList.add('pop');
        }, 100);
    }

    handleConfirm() {
        if (this.callback) {
            const result = this.callback();
            if (result instanceof Promise) {
                this.showLoading();
                result.then(() => this.close()).catch(() => this.hideLoading());
            } else if (result !== false) {
                this.close();
            }
        } else {
            this.close();
        }
    }

    showLoading() {
        const loading = document.getElementById('global-modal-loading');
        const footer = this.modal.querySelector('.global-modal-footer');
        if (loading) loading.classList.add('active');
        if (footer) footer.style.display = 'none';
    }

    hideLoading() {
        const loading = document.getElementById('global-modal-loading');
        const footer = this.modal.querySelector('.global-modal-footer');
        if (loading) loading.classList.remove('active');
        if (footer) footer.style.display = 'flex';
    }

    close() {
        this.overlay.classList.remove('active');
        this.callback = null;
    }

    success(title, message, onConfirm = null) {
        this.show({
            type: 'success',
            icon: 'fa-check-circle',
            title,
            message,
            confirmText: 'OK',
            showCancel: false,
            confirmClass: 'global-modal-btn-success',
            onConfirm
        });
    }

    error(title, message, onConfirm = null) {
        this.show({
            type: 'danger',
            icon: 'fa-exclamation-circle',
            title,
            message,
            confirmText: 'OK',
            showCancel: false,
            confirmClass: 'global-modal-btn-danger',
            onConfirm
        });
    }

    warning(title, message, onConfirm = null, onCancel = null) {
        this.show({
            type: 'warning',
            icon: 'fa-exclamation-triangle',
            title,
            message,
            confirmText: 'Proceed',
            cancelText: 'Cancel',
            showCancel: true,
            confirmClass: 'global-modal-btn-primary',
            onConfirm,
            onCancel
        });
    }

    confirmAction(title, message, onConfirm = null, onCancel = null) {
        this.show({
            type: 'info',
            icon: 'fa-question-circle',
            title,
            message,
            confirmText: 'Confirm',
            cancelText: 'Cancel',
            showCancel: true,
            confirmClass: 'global-modal-btn-primary',
            onConfirm,
            onCancel
        });
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.globalModal = new GlobalModal();
    });
} else {
    window.globalModal = new GlobalModal();
}
