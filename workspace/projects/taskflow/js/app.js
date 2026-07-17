/**
 * TaskFlow Pro - Main App
 * =======================
 * Core application logic
 */

// Storage Keys
const STORAGE_KEYS = {
    TASKS: 'taskflow_tasks',
    USERS: 'taskflow_users',
    CURRENT_USER: 'taskflow_current_user',
    SETTINGS: 'taskflow_settings',
    ACTIVITY_LOG: 'taskflow_activity'
};

// Default Data
let defaultTasks = [];
let defaultUsers = [];

// Load initial data
async function loadInitialData() {
    try {
        // Load tasks from JSON file
        const tasksResponse = await fetch('data/tasks.json');
        defaultTasks = await tasksResponse.json();
        
        // Load users from JSON file
        const usersResponse = await fetch('data/users.json');
        defaultUsers = await usersResponse.json();
        
        // Initialize storage if empty
        if (!localStorage.getItem(STORAGE_KEYS.TASKS)) {
            localStorage.setItem(STORAGE_KEYS.TASKS, JSON.stringify(defaultTasks));
        }
        if (!localStorage.getItem(STORAGE_KEYS.USERS)) {
            localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(defaultUsers));
        }
        
        return true;
    } catch (error) {
        console.error('Error loading initial data:', error);
        return false;
    }
}

// Storage Functions
function getTasks() {
    const tasks = localStorage.getItem(STORAGE_KEYS.TASKS);
    return tasks ? JSON.parse(tasks) : [];
}

function saveTasks(tasks) {
    localStorage.setItem(STORAGE_KEYS.TASKS, JSON.stringify(tasks));
}

function getUsers() {
    const users = localStorage.getItem(STORAGE_KEYS.USERS);
    return users ? JSON.parse(users) : [];
}

function saveUsers(users) {
    localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(users));
}

function getCurrentUser() {
    const user = localStorage.getItem(STORAGE_KEYS.CURRENT_USER);
    return user ? JSON.parse(user) : null;
}

function setCurrentUser(user) {
    localStorage.setItem(STORAGE_KEYS.CURRENT_USER, JSON.stringify(user));
}

function getSettings() {
    const settings = localStorage.getItem(STORAGE_KEYS.SETTINGS);
    return settings ? JSON.parse(settings) : {
        theme: 'dark',
        language: 'ar',
        notifications: true
    };
}

function saveSettings(settings) {
    localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
}

// Auth Functions
function login(email, password) {
    const users = getUsers();
    const user = users.find(u => u.email === email);
    
    if (user) {
        // Simple check (in real app, this would be server-side)
        setCurrentUser(user);
        logActivity('login', `تسجيل دخول: ${user.name}`);
        return { success: true, user };
    }
    
    return { success: false, message: 'بيانات الدخول غير صحيحة' };
}

function logout() {
    const user = getCurrentUser();
    if (user) {
        logActivity('logout', `تسجيل خروج: ${user.name}`);
    }
    localStorage.removeItem(STORAGE_KEYS.CURRENT_USER);
}

// Activity Log
function logActivity(action, details) {
    const logs = JSON.parse(localStorage.getItem(STORAGE_KEYS.ACTIVITY_LOG) || '[]');
    logs.push({
        action,
        details,
        timestamp: new Date().toISOString(),
        user: getCurrentUser()?.name || 'Unknown'
    });
    
    // Keep only last 100 activities
    if (logs.length > 100) {
        logs.splice(0, logs.length - 100);
    }
    
    localStorage.setItem(STORAGE_KEYS.ACTIVITY_LOG, JSON.stringify(logs));
}

function getActivityLog(limit = 20) {
    const logs = JSON.parse(localStorage.getItem(STORAGE_KEYS.ACTIVITY_LOG) || '[]');
    return logs.slice(-limit).reverse();
}

// Task Functions
function createTask(task) {
    const tasks = getTasks();
    const newTask = {
        id: tasks.length > 0 ? Math.max(...tasks.map(t => t.id)) + 1 : 1,
        ...task,
        createdAt: new Date().toISOString().split('T')[0]
    };
    tasks.push(newTask);
    saveTasks(tasks);
    logActivity('create_task', `إنشاء مهمة: ${task.title}`);
    return newTask;
}

function updateTask(id, updates) {
    const tasks = getTasks();
    const index = tasks.findIndex(t => t.id === id);
    
    if (index !== -1) {
        tasks[index] = { ...tasks[index], ...updates };
        saveTasks(tasks);
        logActivity('update_task', `تحديث مهمة: ${tasks[index].title}`);
        return tasks[index];
    }
    return null;
}

function deleteTask(id) {
    const tasks = getTasks();
    const task = tasks.find(t => t.id === id);
    const filtered = tasks.filter(t => t.id !== id);
    saveTasks(filtered);
    if (task) {
        logActivity('delete_task', `حذف مهمة: ${task.title}`);
    }
    return task !== null;
}

function getTaskById(id) {
    const tasks = getTasks();
    return tasks.find(t => t.id === id);
}

function filterTasks(filters) {
    let tasks = getTasks();
    
    if (filters.status && filters.status !== 'all') {
        tasks = tasks.filter(t => t.status === filters.status);
    }
    if (filters.priority && filters.priority !== 'all') {
        tasks = tasks.filter(t => t.priority === filters.priority);
    }
    if (filters.assignee && filters.assignee !== 'all') {
        tasks = tasks.filter(t => t.assignee === filters.assignee);
    }
    if (filters.search) {
        const q = filters.search.toLowerCase();
        tasks = tasks.filter(t => 
            t.title.toLowerCase().includes(q) ||
            t.description.toLowerCase().includes(q)
        );
    }
    
    return tasks;
}

// Statistics
function getStats() {
    const tasks = getTasks();
    const users = getUsers();
    
    return {
        totalTasks: tasks.length,
        completedTasks: tasks.filter(t => t.status === 'completed').length,
        inProgressTasks: tasks.filter(t => t.status === 'in-progress').length,
        pendingTasks: tasks.filter(t => t.status === 'pending').length,
        totalUsers: users.length,
        onlineUsers: users.filter(u => u.status === 'online').length
    };
}

// User Functions
function getUserByEmail(email) {
    const users = getUsers();
    return users.find(u => u.email === email);
}

function updateUserRole(email, newRole) {
    const users = getUsers();
    const index = users.findIndex(u => u.email === email);
    
    if (index !== -1) {
        users[index].role = newRole;
        saveUsers(users);
        logActivity('update_role', `تغيير دور: ${users[index].name} -> ${newRole}`);
        return users[index];
    }
    return null;
}

function updateUserStatus(email, status) {
    const users = getUsers();
    const index = users.findIndex(u => u.email === email);
    
    if (index !== -1) {
        users[index].status = status;
        saveUsers(users);
        return users[index];
    }
    return null;
}

// Settings Functions
function updateSettings(newSettings) {
    const settings = getSettings();
    const updated = { ...settings, ...newSettings };
    saveSettings(updated);
    logActivity('update_settings', 'تحديث الإعدادات');
    return updated;
}

// Format Date
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-EG');
}

// Get User Role Display
function getRoleDisplay(role) {
    const roles = {
        'manager': 'مدير',
        'member': 'عضو',
        'viewer': 'زائر'
    };
    return roles[role] || role;
}

// Check Permission
function hasPermission(requiredRole) {
    const user = getCurrentUser();
    if (!user) return false;
    
    const roleHierarchy = {
        'manager': 3,
        'member': 2,
        'viewer': 1
    };
    
    return roleHierarchy[user.role] >= roleHierarchy[requiredRole];
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function() {
    await loadInitialData();
    
    // Set RTL/LTR based on settings
    const settings = getSettings();
    document.body.dir = settings.language === 'ar' ? 'rtl' : 'ltr';
    document.body.lang = settings.language;
});
