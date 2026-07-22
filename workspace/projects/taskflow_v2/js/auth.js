/**
 * TaskFlow Pro - Authentication
 * =============================
 * Authentication & authorization
 */

// Check if user is logged in
function isLoggedIn() {
    return getCurrentUser() !== null;
}

// Require authentication
function requireAuth(redirectUrl = 'login.html') {
    if (!isLoggedIn()) {
        window.location.href = redirectUrl;
        return false;
    }
    return true;
}

// Require specific role
function requireRole(role) {
    if (!requireAuth()) return false;
    if (!hasPermission(role)) {
        alert('ليس لديك صلاحية للوصول إلى هذه الصفحة');
        window.location.href = 'dashboard.html';
        return false;
    }
    return true;
}

// Login handler
function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (!email || !password) {
        showAlert('يرجى إدخال البريد الإلكتروني وكلمة المرور', 'error');
        return;
    }
    
    const result = login(email, password);
    
    if (result.success) {
        showAlert('تم تسجيل الدخول بنجاح!', 'success');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 500);
    } else {
        showAlert(result.message, 'error');
    }
}

// Logout handler
function handleLogout() {
    logout();
    window.location.href = 'login.html';
}

// Role-based UI
function updateUIForRole() {
    const user = getCurrentUser();
    if (!user) return;
    
    // Show/hide based on role
    const role = user.role;
    
    // Manager-only elements
    document.querySelectorAll('.manager-only').forEach(el => {
        el.style.display = role === 'manager' ? '' : 'none';
    });
    
    // Admin/Manager elements
    document.querySelectorAll('.admin-only').forEach(el => {
        el.style.display = role === 'manager' ? '' : 'none';
    });
    
    // Member elements
    document.querySelectorAll('.member-only').forEach(el => {
        el.style.display = (role === 'manager' || role === 'member') ? '' : 'none';
    });
    
    // Update user display
    const userNameEl = document.getElementById('user-name');
    const userRoleEl = document.getElementById('user-role');
    
    if (userNameEl) userNameEl.textContent = user.name;
    if (userRoleEl) userRoleEl.textContent = getRoleDisplay(user.role);
}

// Simulate password check (in real app, this would be server-side)
function verifyPassword(inputPassword) {
    // Demo validation - in production, this would be server-side
    return typeof inputPassword === 'string' && inputPassword.length >= 1;
}

// Alert helper
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}
