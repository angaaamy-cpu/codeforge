/**
 * TaskFlow Pro - Tasks Module
 * ===========================
 * Task management functionality
 */

// Task Categories
const TASK_CATEGORIES = [
    { id: 'all', name: 'الكل' },
    { id: 'design', name: 'تصميم' },
    { id: 'frontend', name: 'واجهة' },
    { id: 'backend', name: 'خلفية' },
    { id: 'bug', name: 'مشكلة' },
    { id: 'feature', name: 'ميزة' },
    { id: 'security', name: 'أمان' },
    { id: 'qa', name: 'اختبار' },
    { id: 'docs', name: 'توثيق' },
    { id: 'deploy', name: 'نشر' },
    { id: 'integration', name: 'تكامل' }
];

// Render Tasks Table
function renderTasksTable(tasks) {
    const tbody = document.getElementById('tasks-tbody');
    if (!tbody) return;
    
    clearChildren(tbody);
    
    if (tasks.length === 0) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.setAttribute('colspan', '6');
        td.className = 'text-center';
        td.style.cssText = 'padding: 2rem;';
        
        const emptyState = document.createElement('div');
        emptyState.className = 'empty-state';
        
        const icon = document.createElement('div');
        icon.className = 'empty-state-icon';
        icon.textContent = '📋';
        
        const title = document.createElement('div');
        title.className = 'empty-state-title';
        title.textContent = 'لا توجد مهام';
        
        emptyState.appendChild(icon);
        emptyState.appendChild(title);
        td.appendChild(emptyState);
        tr.appendChild(td);
        tbody.appendChild(tr);
        return;
    }
    
    tasks.forEach(task => {
        const user = getUserByEmail(task.assignee);
        const tr = document.createElement('tr');
        
        // Task cell
        const taskTd = document.createElement('td');
        const taskDiv = document.createElement('div');
        taskDiv.className = 'task-title-cell';
        
        const titleStrong = document.createElement('strong');
        titleStrong.textContent = task.title;
        
        const descSmall = document.createElement('small');
        descSmall.className = 'text-muted';
        descSmall.textContent = truncate(task.description, 60);
        
        taskDiv.appendChild(titleStrong);
        taskDiv.appendChild(descSmall);
        taskTd.appendChild(taskDiv);
        tr.appendChild(taskTd);
        
        // Status cell
        const statusTd = document.createElement('td');
        const statusSpan = document.createElement('span');
        statusSpan.className = 'badge ' + getStatusClass(task.status);
        statusSpan.textContent = getStatusText(task.status);
        statusTd.appendChild(statusSpan);
        tr.appendChild(statusTd);
        
        // Priority cell
        const priorityTd = document.createElement('td');
        const prioritySpan = document.createElement('span');
        prioritySpan.className = getPriorityClass(task.priority);
        prioritySpan.textContent = getPriorityIcon(task.priority) + ' ' + task.priority;
        priorityTd.appendChild(prioritySpan);
        tr.appendChild(priorityTd);
        
        // Assignee cell
        const assigneeTd = document.createElement('td');
        assigneeTd.textContent = user ? user.name : '-';
        tr.appendChild(assigneeTd);
        
        // Due date cell
        const dateTd = document.createElement('td');
        dateTd.textContent = formatDate(task.dueDate);
        tr.appendChild(dateTd);
        
        // Actions cell
        const actionsTd = document.createElement('td');
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'flex gap-1';
        
        if (hasPermission('member')) {
            const editBtn = document.createElement('button');
            editBtn.className = 'btn btn-sm btn-secondary';
            editBtn.textContent = 'تعديل';
            editBtn.onclick = function() { editTask(task.id); };
            actionsDiv.appendChild(editBtn);
        }
        
        if (hasPermission('manager')) {
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-sm btn-danger';
            deleteBtn.textContent = 'حذف';
            deleteBtn.onclick = function() { confirmDeleteTask(task.id); };
            actionsDiv.appendChild(deleteBtn);
        }
        
        actionsTd.appendChild(actionsDiv);
        tr.appendChild(actionsTd);
        tbody.appendChild(tr);
    });
}

// Filter Tasks
function filterTasks() {
    const filters = {
        status: document.getElementById('filter-status')?.value || 'all',
        priority: document.getElementById('filter-priority')?.value || 'all',
        assignee: document.getElementById('filter-assignee')?.value || 'all',
        search: document.getElementById('search-input')?.value || ''
    };
    
    const filtered = filterTasks(filters);
    renderTasksTable(filtered);
}

// Render Filters
function renderTaskFilters() {
    const statusSelect = document.getElementById('filter-status');
    const prioritySelect = document.getElementById('filter-priority');
    const assigneeSelect = document.getElementById('filter-assignee');
    
    if (statusSelect) {
        clearChildren(statusSelect);
        const statuses = [
            { value: 'all', label: 'جميع الحالات' },
            { value: 'pending', label: 'معلق' },
            { value: 'in-progress', label: 'قيد التنفيذ' },
            { value: 'completed', label: 'مكتمل' }
        ];
        statuses.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.value;
            opt.textContent = s.label;
            statusSelect.appendChild(opt);
        });
    }
    
    if (prioritySelect) {
        clearChildren(prioritySelect);
        const priorities = [
            { value: 'all', label: 'جميع الأولويات' },
            { value: 'high', label: 'عالية' },
            { value: 'medium', label: 'متوسطة' },
            { value: 'low', label: 'منخفضة' }
        ];
        priorities.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.value;
            opt.textContent = p.label;
            prioritySelect.appendChild(opt);
        });
    }
    
    if (assigneeSelect) {
        clearChildren(assigneeSelect);
        const users = getUsers();
        const allOpt = document.createElement('option');
        allOpt.value = 'all';
        allOpt.textContent = 'جميع الأعضاء';
        assigneeSelect.appendChild(allOpt);
        
        users.forEach(u => {
            const opt = document.createElement('option');
            opt.value = u.email;
            opt.textContent = u.name;
            assigneeSelect.appendChild(opt);
        });
    }
}

// Create Task Modal
function showCreateTaskModal() {
    if (!hasPermission('member')) {
        alert('ليس لديك صلاحية إنشاء مهام');
        return;
    }
    
    const modal = document.getElementById('task-modal');
    if (!modal) return;
    
    // Populate assignees
    const assigneeSelect = document.getElementById('task-assignee');
    if (assigneeSelect) {
        clearChildren(assigneeSelect);
        const users = getUsers();
        users.forEach(u => {
            const opt = document.createElement('option');
            opt.value = u.email;
            opt.textContent = u.name;
            assigneeSelect.appendChild(opt);
        });
    }
    
    // Populate categories
    const categorySelect = document.getElementById('task-category');
    if (categorySelect) {
        clearChildren(categorySelect);
        TASK_CATEGORIES.filter(c => c.id !== 'all').forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.name;
            categorySelect.appendChild(opt);
        });
    }
    
    // Reset form
    const form = document.getElementById('task-form');
    if (form) form.reset();
    
    // Set current user as assignee
    const currentUser = getCurrentUser();
    if (currentUser && assigneeSelect) {
        assigneeSelect.value = currentUser.email;
    }
    
    showModal('task-modal');
}

// Edit Task
function editTask(taskId) {
    const task = getTaskById(taskId);
    if (!task) return;
    
    document.getElementById('task-id').value = task.id;
    document.getElementById('task-title').value = task.title;
    document.getElementById('task-description').value = task.description;
    document.getElementById('task-status').value = task.status;
    document.getElementById('task-priority').value = task.priority;
    document.getElementById('task-assignee').value = task.assignee;
    document.getElementById('task-due-date').value = task.dueDate;
    document.getElementById('task-category').value = task.category;
    
    showModal('task-modal');
}

// Handle Task Form Submit
function handleTaskSubmit(event) {
    event.preventDefault();
    
    const taskId = document.getElementById('task-id').value;
    const taskData = {
        title: sanitizeInput(document.getElementById('task-title').value),
        description: sanitizeInput(document.getElementById('task-description').value),
        status: document.getElementById('task-status').value,
        priority: document.getElementById('task-priority').value,
        assignee: document.getElementById('task-assignee').value,
        dueDate: document.getElementById('task-due-date').value,
        category: document.getElementById('task-category').value
    };
    
    if (!taskData.title) {
        alert('يرجى إدخال عنوان المهمة');
        return;
    }
    
    if (taskId) {
        updateTask(parseInt(taskId), taskData);
    } else {
        createTask(taskData);
    }
    
    hideModal('task-modal');
    loadTasks();
}

// Confirm Delete Task
function confirmDeleteTask(taskId) {
    if (confirm('هل أنت متأكد من حذف هذه المهمة؟')) {
        deleteTask(taskId);
        loadTasks();
    }
}

// Load Tasks
function loadTasks() {
    const tasks = getTasks();
    renderTasksTable(tasks);
    updateTaskStats();
}

// Update Task Stats
function updateTaskStats() {
    const stats = getStats();
    
    const totalEl = document.getElementById('total-tasks');
    const completedEl = document.getElementById('completed-tasks');
    const inProgressEl = document.getElementById('inprogress-tasks');
    const pendingEl = document.getElementById('pending-tasks');
    
    if (totalEl) totalEl.textContent = stats.totalTasks;
    if (completedEl) completedEl.textContent = stats.completedTasks;
    if (inProgressEl) inProgressEl.textContent = stats.inProgressTasks;
    if (pendingEl) pendingEl.textContent = stats.pendingTasks;
}

// Initialize Tasks Page
document.addEventListener('DOMContentLoaded', function() {
    if (!requireAuth()) return;
    
    renderTaskFilters();
    loadTasks();
    
    // Add event listeners for filters
    document.querySelectorAll('.filter-select').forEach(select => {
        select.addEventListener('change', filterTasks);
    });
    
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterTasks, 300));
    });
});

// Debounce helper
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
