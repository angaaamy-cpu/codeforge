/**
 * TaskFlow Pro - Reports Module
 * ============================
 * Reporting & analytics functionality
 */

// Generate Weekly Summary
function generateWeeklySummary() {
    const tasks = getTasks();
    const users = getUsers();
    const activities = getActivityLog(50);
    
    const completedTasks = tasks.filter(t => t.status === 'completed');
    const inProgressTasks = tasks.filter(t => t.status === 'in-progress');
    const pendingTasks = tasks.filter(t => t.status === 'pending');
    
    // Tasks by category
    const tasksByCategory = {};
    tasks.forEach(task => {
        tasksByCategory[task.category] = (tasksByCategory[task.category] || 0) + 1;
    });
    
    // Tasks by assignee
    const tasksByAssignee = {};
    tasks.forEach(task => {
        tasksByAssignee[task.assignee] = (tasksByAssignee[task.assignee] || 0) + 1;
    });
    
    // Calculate completion rate
    const completionRate = tasks.length > 0 
        ? Math.round((completedTasks.length / tasks.length) * 100) 
        : 0;
    
    return {
        totalTasks: tasks.length,
        completedTasks: completedTasks.length,
        inProgressTasks: inProgressTasks.length,
        pendingTasks: pendingTasks.length,
        completionRate,
        tasksByCategory,
        tasksByAssignee,
        teamSize: users.length,
        recentActivities: activities.slice(0, 10)
    };
}

// Render Weekly Summary
function renderWeeklySummary() {
    const summary = generateWeeklySummary();
    
    // Stats
    document.getElementById('report-total-tasks').textContent = summary.totalTasks;
    document.getElementById('report-completed').textContent = summary.completedTasks;
    document.getElementById('report-inprogress').textContent = summary.inProgressTasks;
    document.getElementById('report-pending').textContent = summary.pendingTasks;
    
    // Completion rate ring
    const ring = document.getElementById('completion-ring');
    if (ring) {
        const circumference = 2 * Math.PI * 45;
        const offset = circumference - (summary.completionRate / 100) * circumference;
        ring.style.strokeDashoffset = offset;
    }
    
    document.getElementById('completion-percentage').textContent = summary.completionRate + '%';
    
    // Category breakdown
    renderCategoryChart(summary.tasksByCategory);
    
    // Team productivity
    renderTeamProductivity(summary.tasksByAssignee);
    
    // Recent activity
    renderActivityFeed(summary.recentActivities);
}

// Render Category Chart
function renderCategoryChart(data) {
    const container = document.getElementById('category-chart');
    if (!container) return;
    
    clearChildren(container);
    
    const colors = {
        'design': '#7c3aed',
        'frontend': '#3b82f6',
        'backend': '#10b981',
        'bug': '#ef4444',
        'feature': '#f59e0b',
        'security': '#dc2626',
        'qa': '#6366f1',
        'docs': '#8b5cf6',
        'deploy': '#14b8a6',
        'integration': '#f97316'
    };
    
    const total = Object.values(data).reduce((sum, val) => sum + val, 0);
    
    Object.entries(data).forEach(([category, count]) => {
        const percentage = Math.round((count / total) * 100);
        
        const item = document.createElement('div');
        item.className = 'mb-2';
        
        const flexDiv = document.createElement('div');
        flexDiv.className = 'flex justify-between mb-1';
        
        const catSpan = document.createElement('span');
        catSpan.textContent = TASK_CATEGORIES.find(c => c.id === category)?.name || category;
        
        const countSpan = document.createElement('span');
        countSpan.textContent = count + ' (' + percentage + '%)';
        
        flexDiv.appendChild(catSpan);
        flexDiv.appendChild(countSpan);
        item.appendChild(flexDiv);
        
        const barContainer = document.createElement('div');
        barContainer.className = 'progress-bar';
        
        const barFill = document.createElement('div');
        barFill.className = 'progress-bar-fill';
        barFill.style.cssText = 'width: ' + percentage + '%; background-color: ' + (colors[category] || '#7c3aed');
        
        barContainer.appendChild(barFill);
        item.appendChild(barContainer);
        container.appendChild(item);
    });
}

// Render Team Productivity
function renderTeamProductivity(data) {
    const container = document.getElementById('team-productivity');
    if (!container) return;
    
    clearChildren(container);
    
    const users = getUsers();
    
    users.forEach(user => {
        const taskCount = data[user.email] || 0;
        const completedTasks = getTasks().filter(t => 
            t.assignee === user.email && t.status === 'completed'
        ).length;
        
        const item = document.createElement('div');
        item.className = 'team-member-card mb-2';
        
        const row1 = document.createElement('div');
        row1.className = 'flex items-center gap-2';
        
        const avatar = document.createElement('span');
        avatar.textContent = user.avatar;
        
        const name = document.createElement('span');
        name.className = 'member-name';
        name.textContent = user.name;
        
        row1.appendChild(avatar);
        row1.appendChild(name);
        item.appendChild(row1);
        
        const row2 = document.createElement('div');
        row2.className = 'flex gap-3';
        
        const col1 = document.createElement('div');
        col1.className = 'text-center';
        const val1 = document.createElement('div');
        val1.className = 'font-bold';
        val1.textContent = taskCount;
        const label1 = document.createElement('div');
        label1.className = 'text-muted';
        label1.style.cssText = 'font-size: 0.7rem;';
        label1.textContent = 'إجمالي';
        col1.appendChild(val1);
        col1.appendChild(label1);
        
        const col2 = document.createElement('div');
        col2.className = 'text-center';
        const val2 = document.createElement('div');
        val2.className = 'font-bold text-success';
        val2.textContent = completedTasks;
        const label2 = document.createElement('div');
        label2.className = 'text-muted';
        label2.style.cssText = 'font-size: 0.7rem;';
        label2.textContent = 'مكتمل';
        col2.appendChild(val2);
        col2.appendChild(label2);
        
        row2.appendChild(col1);
        row2.appendChild(col2);
        item.appendChild(row2);
        
        container.appendChild(item);
    });
}

// Render Activity Feed
function renderActivityFeed(activities) {
    const container = document.getElementById('activity-feed');
    if (!container) return;
    
    clearChildren(container);
    
    const icons = {
        'login': '🔐',
        'logout': '🔓',
        'create_task': '✨',
        'update_task': '✏️',
        'delete_task': '🗑️',
        'update_settings': '⚙️',
        'update_role': '👤'
    };
    
    activities.forEach(activity => {
        const item = document.createElement('div');
        item.className = 'activity-item';
        
        const iconDiv = document.createElement('div');
        iconDiv.className = 'activity-icon';
        iconDiv.textContent = icons[activity.action] || '📝';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'activity-content';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'activity-text';
        textDiv.textContent = activity.details;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'activity-time';
        timeDiv.textContent = getRelativeTime(activity.timestamp);
        
        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeDiv);
        
        item.appendChild(iconDiv);
        item.appendChild(contentDiv);
        
        container.appendChild(item);
    });
}

// Render Team Performance Chart
function renderTeamPerformanceChart() {
    const container = document.getElementById('performance-chart');
    if (!container) return;
    
    const users = getUsers();
    const chartData = users.map(user => {
        const tasks = getTasks().filter(t => t.assignee === user.email);
        return {
            label: user.name.substring(0, 3),
            value: tasks.filter(t => t.status === 'completed').length
        };
    });
    
    createSimpleBarChart('performance-chart', chartData);
}

// Export Report
function exportReport() {
    const summary = generateWeeklySummary();
    const reportContent = `
# تقرير TaskFlow الأسبوعي
========================

## ملخص عام
- إجمالي المهام: ${summary.totalTasks}
- المكتملة: ${summary.completedTasks}
- قيد التنفيذ: ${summary.inProgressTasks}
- المعلقة: ${summary.pendingTasks}
- نسبة الإنجاز: ${summary.completionRate}%

## توزيع المهام حسب الفئة
${Object.entries(summary.tasksByCategory).map(([cat, count]) => 
    `- ${TASK_CATEGORIES.find(c => c.id === cat)?.name || cat}: ${count}`
).join('\n')}

## نشاط الفريق
- حجم الفريق: ${summary.teamSize}

---
تم إنشاء هذا التقرير في: ${new Date().toLocaleString('ar-EG')}
    `.trim();
    
    // Create and download file
    const blob = new Blob([reportContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `taskflow-report-${new Date().toISOString().split('T')[0]}.md`;
    a.click();
    URL.revokeObjectURL(url);
}

// Initialize Reports Page
document.addEventListener('DOMContentLoaded', function() {
    if (!requireAuth()) return;
    
    renderWeeklySummary();
    renderTeamPerformanceChart();
});
