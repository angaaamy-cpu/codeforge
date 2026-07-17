/**
 * TaskFlow Pro - Team Module
 * ==========================
 * Team management functionality
 */

// Render Team Grid
function renderTeamGrid() {
    const container = document.getElementById('team-grid');
    if (!container) return;
    
    clearChildren(container);
    
    const users = getUsers();
    
    users.forEach(user => {
        const tasks = getTasks().filter(t => t.assignee === user.email);
        const completedTasks = tasks.filter(t => t.status === 'completed').length;
        const inProgressTasks = tasks.filter(t => t.status === 'in-progress').length;
        
        const card = document.createElement('div');
        card.className = 'team-member-card';
        
        // Avatar
        const avatar = document.createElement('div');
        avatar.className = 'member-avatar';
        avatar.textContent = user.avatar;
        card.appendChild(avatar);
        
        // Info
        const info = document.createElement('div');
        info.className = 'member-info';
        
        const name = document.createElement('div');
        name.className = 'member-name';
        name.textContent = user.name;
        
        const role = document.createElement('div');
        role.className = 'member-role';
        role.textContent = getRoleDisplay(user.role);
        
        const dept = document.createElement('div');
        dept.className = 'member-department text-muted';
        dept.style.cssText = 'font-size: 0.8rem;';
        dept.textContent = user.department;
        
        info.appendChild(name);
        info.appendChild(role);
        info.appendChild(dept);
        card.appendChild(info);
        
        // Status
        const status = document.createElement('div');
        status.className = 'member-status';
        const dot = document.createElement('span');
        dot.className = 'status-dot status-' + user.status;
        status.appendChild(dot);
        card.appendChild(status);
        
        // Stats
        const stats = document.createElement('div');
        stats.className = 'member-stats mt-2';
        
        const miniStats = document.createElement('div');
        miniStats.className = 'mini-stats';
        miniStats.style.cssText = 'margin-top: 0.5rem;';
        
        miniStats.innerHTML = `
            <div class="mini-stat">
                <div class="mini-stat-value">${tasks.length}</div>
                <div class="mini-stat-label">المهام</div>
            </div>
            <div class="mini-stat">
                <div class="mini-stat-value text-success">${completedTasks}</div>
                <div class="mini-stat-label">مكتمل</div>
            </div>
            <div class="mini-stat">
                <div class="mini-stat-value text-warning">${inProgressTasks}</div>
                <div class="mini-stat-label">قيد التنفيذ</div>
            </div>
        `;
        
        stats.appendChild(miniStats);
        card.appendChild(stats);
        
        // Actions (manager only)
        if (hasPermission('manager')) {
            const actions = document.createElement('div');
            actions.className = 'member-actions mt-2';
            
            const btn = document.createElement('button');
            btn.className = 'btn btn-sm btn-secondary';
            btn.textContent = 'تعديل';
            btn.onclick = function() { showEditMemberModal(user.email); };
            
            actions.appendChild(btn);
            card.appendChild(actions);
        }
        
        container.appendChild(card);
    });
}

// Render Team Table
function renderTeamTable() {
    const tbody = document.getElementById('team-tbody');
    if (!tbody) return;
    
    clearChildren(tbody);
    
    const users = getUsers();
    
    users.forEach(user => {
        const tasks = getTasks().filter(t => t.assignee === user.email);
        const completedTasks = tasks.filter(t => t.status === 'completed').length;
        
        const tr = document.createElement('tr');
        
        // Name cell
        const nameTd = document.createElement('td');
        const nameDiv = document.createElement('div');
        nameDiv.className = 'flex items-center gap-2';
        
        const dot = document.createElement('span');
        dot.className = 'status-dot status-' + user.status;
        
        const avatar = document.createElement('span');
        avatar.textContent = user.avatar;
        
        const name = document.createElement('span');
        name.textContent = user.name;
        
        nameDiv.appendChild(dot);
        nameDiv.appendChild(avatar);
        nameDiv.appendChild(name);
        nameTd.appendChild(nameDiv);
        tr.appendChild(nameTd);
        
        // Email
        const emailTd = document.createElement('td');
        emailTd.textContent = user.email;
        tr.appendChild(emailTd);
        
        // Role
        const roleTd = document.createElement('td');
        const roleBadge = document.createElement('span');
        roleBadge.className = 'badge badge-purple';
        roleBadge.textContent = getRoleDisplay(user.role);
        roleTd.appendChild(roleBadge);
        tr.appendChild(roleTd);
        
        // Department
        const deptTd = document.createElement('td');
        deptTd.textContent = user.department;
        tr.appendChild(deptTd);
        
        // Tasks count
        const tasksTd = document.createElement('td');
        tasksTd.textContent = tasks.length;
        tr.appendChild(tasksTd);
        
        // Completed count
        const completedTd = document.createElement('td');
        completedTd.textContent = completedTasks;
        tr.appendChild(completedTd);
        
        // Joined date
        const dateTd = document.createElement('td');
        dateTd.textContent = formatDate(user.joinedAt);
        tr.appendChild(dateTd);
        
        // Actions
        const actionsTd = document.createElement('td');
        if (hasPermission('manager')) {
            const btn = document.createElement('button');
            btn.className = 'btn btn-sm btn-secondary';
            btn.textContent = 'تعديل';
            btn.onclick = function() { showEditMemberModal(user.email); };
            actionsTd.appendChild(btn);
        } else {
            actionsTd.textContent = '-';
        }
        tr.appendChild(actionsTd);
        
        tbody.appendChild(tr);
    });
}

// Show Edit Member Modal
function showEditMemberModal(email) {
    if (!hasPermission('manager')) return;
    
    const user = getUserByEmail(email);
    if (!user) return;
    
    document.getElementById('edit-member-email').value = user.email;
    document.getElementById('edit-member-name').value = user.name;
    document.getElementById('edit-member-role').value = user.role;
    document.getElementById('edit-member-status').value = user.status;
    
    showModal('edit-member-modal');
}

// Handle Edit Member Submit
function handleEditMemberSubmit(event) {
    event.preventDefault();
    
    const email = document.getElementById('edit-member-email').value;
    const newRole = document.getElementById('edit-member-role').value;
    const newStatus = document.getElementById('edit-member-status').value;
    
    updateUserRole(email, newRole);
    updateUserStatus(email, newStatus);
    
    hideModal('edit-member-modal');
    renderTeamGrid();
    renderTeamTable();
}

// Update Team Stats
function updateTeamStats() {
    const stats = getStats();
    
    const totalEl = document.getElementById('total-members');
    const onlineEl = document.getElementById('online-members');
    
    if (totalEl) totalEl.textContent = stats.totalUsers;
    if (onlineEl) onlineEl.textContent = stats.onlineUsers;
}

// Initialize Team Page
document.addEventListener('DOMContentLoaded', function() {
    if (!requireAuth()) return;
    
    renderTeamGrid();
    renderTeamTable();
    updateTeamStats();
});
