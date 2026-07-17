/**
 * TaskFlow Pro - Utilities
 * ========================
 * Common utility functions
 */

// Date formatting
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-EG', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('ar-EG', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'الآن';
    if (minutes < 60) return `منذ ${minutes} دقيقة`;
    if (hours < 24) return `منذ ${hours} ساعة`;
    if (days < 7) return `منذ ${days} يوم`;
    return formatDate(dateString);
}

// String utilities
function truncate(str, length = 50) {
    if (!str) return '';
    if (str.length <= length) return str;
    return str.substring(0, length) + '...';
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function sanitizeInput(input) {
    if (typeof input !== 'string') return '';
    return input.replace(/[<>]/g, '').trim();
}

// Validation
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function isValidDate(dateString) {
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date);
}

// Generate ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Status helpers
function getStatusClass(status) {
    const classes = {
        'pending': 'badge-warning',
        'in-progress': 'badge-info',
        'completed': 'badge-success',
        'blocked': 'badge-error'
    };
    return classes[status] || 'badge-info';
}

function getStatusText(status) {
    const texts = {
        'pending': 'معلق',
        'in-progress': 'قيد التنفيذ',
        'completed': 'مكتمل',
        'blocked': 'محظور'
    };
    return texts[status] || status;
}

// Priority helpers
function getPriorityClass(priority) {
    const classes = {
        'high': 'priority-high',
        'medium': 'priority-medium',
        'low': 'priority-low'
    };
    return classes[priority] || '';
}

function getPriorityIcon(priority) {
    const icons = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    };
    return icons[priority] || '⚪';
}

// DOM helpers
function createElement(tag, className, content) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (content) el.textContent = content;
    return el;
}

function clearChildren(element) {
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Event delegation helper
function delegate(element, event, selector, handler) {
    element.addEventListener(event, function(e) {
        const target = e.target.closest(selector);
        if (target && element.contains(target)) {
            handler.call(target, e);
        }
    });
}

// Local storage helpers
function clearAllData() {
    Object.values(STORAGE_KEYS).forEach(key => {
        localStorage.removeItem(key);
    });
}

function exportData() {
    const data = {
        tasks: getTasks(),
        users: getUsers(),
        settings: getSettings(),
        activity: getActivityLog()
    };
    return JSON.stringify(data, null, 2);
}

function importData(jsonString) {
    try {
        const data = JSON.parse(jsonString);
        if (data.tasks) saveTasks(data.tasks);
        if (data.users) saveUsers(data.users);
        if (data.settings) saveSettings(data.settings);
        return true;
    } catch (e) {
        console.error('Import failed:', e);
        return false;
    }
}

// Chart helpers
function createSimpleBarChart(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    clearChildren(container);
    
    const maxValue = Math.max(...data.map(d => d.value));
    
    data.forEach(item => {
        const barItem = document.createElement('div');
        barItem.className = 'bar-item';
        
        const bar = document.createElement('div');
        bar.className = 'bar';
        bar.style.height = `${(item.value / maxValue) * 150}px`;
        
        const value = document.createElement('div');
        value.className = 'bar-value';
        value.textContent = item.value;
        
        const label = document.createElement('div');
        label.className = 'bar-label';
        label.textContent = item.label;
        
        barItem.appendChild(value);
        barItem.appendChild(bar);
        barItem.appendChild(label);
        container.appendChild(barItem);
    });
}

// Animation helpers
function animate(element, keyframes, options = {}) {
    return element.animate(keyframes, {
        duration: options.duration || 300,
        easing: options.easing || 'ease',
        fill: options.fill || 'forwards'
    });
}

function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.display = '';
    animate(element, [
        { opacity: 0 },
        { opacity: 1 }
    ], { duration });
}

function fadeOut(element, duration = 300) {
    return new Promise(resolve => {
        animate(element, [
            { opacity: 1 },
            { opacity: 0 }
        ], { duration }).onfinish = () => {
            element.style.display = 'none';
            element.style.opacity = '';
            resolve();
        };
    });
}

// Export for use in other files
window.utils = {
    formatDate,
    formatDateTime,
    getRelativeTime,
    truncate,
    escapeHtml,
    sanitizeInput,
    isValidEmail,
    isValidDate,
    generateId,
    getStatusClass,
    getStatusText,
    getPriorityClass,
    getPriorityIcon,
    createElement,
    clearChildren,
    showModal,
    hideModal,
    delegate,
    clearAllData,
    exportData,
    importData,
    createSimpleBarChart,
    animate,
    fadeIn,
    fadeOut
};
