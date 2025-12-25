/**
 * Smart City Automation System - JavaScript
 */

// ==================== Toast Notifications ====================
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== Refresh Button ====================
document.addEventListener('DOMContentLoaded', () => {
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            location.reload();
        });
    }

    // Notification button
    const notificationBtn = document.getElementById('notificationBtn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/notifications');
                const notifications = await response.json();
                console.log('Notifications:', notifications);
                showToast(`${notifications.length} notifications`, 'info');
            } catch (error) {
                console.error('Error fetching notifications:', error);
            }
        });
    }

    // Auto-refresh stats every 30 seconds
    setInterval(async () => {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            updateStats(stats);
        } catch (error) {
            console.error('Stats refresh failed:', error);
        }
    }, 30000);
});

// ==================== Stats Update ====================
function updateStats(stats) {
    // Update stat values if they exist on the page
    const statElements = {
        'total_devices': document.querySelector('[data-stat="total_devices"]'),
        'active_devices': document.querySelector('[data-stat="active_devices"]'),
        'total_commands': document.querySelector('[data-stat="total_commands"]')
    };

    for (const [key, element] of Object.entries(statElements)) {
        if (element && stats[key] !== undefined) {
            element.textContent = stats[key];
        }
    }
}

// ==================== Device Control ====================
async function controlDevice(deviceId, action) {
    try {
        const response = await fetch(`/api/device/${deviceId}/control`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Device ${action} successful`, 'success');
            // Update UI without full reload
            updateDeviceStatus(deviceId, action);
        } else {
            showToast(data.error || 'Action failed', 'error');
        }

        return data;
    } catch (error) {
        showToast('Connection error', 'error');
        console.error('Device control error:', error);
        return { success: false, error: error.message };
    }
}

function updateDeviceStatus(deviceId, action) {
    const deviceElement = document.querySelector(`[data-id="${deviceId}"]`);
    if (deviceElement) {
        const statusBadge = deviceElement.querySelector('.status-badge');
        if (statusBadge) {
            const isActive = action === 'on' || action === 'green';
            statusBadge.className = `status-badge ${isActive ? 'active' : 'inactive'}`;
            statusBadge.textContent = isActive ? 'active' : 'inactive';
        }
    }
}

// ==================== Routine Execution ====================
async function executeRoutine(routineType) {
    try {
        const response = await fetch(`/api/routine/${routineType}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showToast(`${routineType} routine executed successfully`, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast(data.error || 'Routine execution failed', 'error');
        }

        return data;
    } catch (error) {
        showToast('Routine execution error', 'error');
        console.error('Routine error:', error);
        return { success: false, error: error.message };
    }
}

// ==================== Payment Processing ====================
async function processPayment(amount, type, description) {
    try {
        const response = await fetch('/api/payment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                amount: parseFloat(amount),
                type,
                currency: 'USD',
                description
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Payment of $${amount} processed successfully!`, 'success');
            return data;
        } else {
            showToast(data.error || 'Payment failed', 'error');
            return data;
        }
    } catch (error) {
        showToast('Payment processing error', 'error');
        console.error('Payment error:', error);
        return { success: false, error: error.message };
    }
}

// ==================== Local Storage Helpers ====================
const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Storage error:', e);
        }
    },

    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Storage error:', e);
            return defaultValue;
        }
    },

    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Storage error:', e);
        }
    }
};

// ==================== Theme Toggle (Future Enhancement) ====================
function toggleTheme() {
    const body = document.body;
    body.classList.toggle('light-theme');
    storage.set('theme', body.classList.contains('light-theme') ? 'light' : 'dark');
}

// ==================== Keyboard Shortcuts ====================
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + R to refresh
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        location.reload();
    }

    // Escape to close modals (if any)
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.open');
        modals.forEach(modal => modal.classList.remove('open'));
    }
});

// ==================== Utility Functions ====================
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for use in other scripts
window.SmartCity = {
    showToast,
    controlDevice,
    executeRoutine,
    processPayment,
    storage,
    formatCurrency,
    formatDate
};
