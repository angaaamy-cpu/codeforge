/**
 * CodeForge UI - JavaScript
 * Phase 4: Phone Interface
 */

// ============================================================
// DOM Elements
// ============================================================

const taskStatus = document.getElementById("task-status");
const activeAgent = document.getElementById("active-agent");
const completedTasks = document.getElementById("completed-tasks");
const phase = document.getElementById("phase");
const taskForm = document.getElementById("task-form");
const taskInput = document.getElementById("task-input");
const btnText = document.getElementById("btn-text");
const btnLoader = document.getElementById("btn-loader");
const taskResult = document.getElementById("task-result");
const historyList = document.getElementById("history-list");
const errorSection = document.getElementById("error-section");
const errorLog = document.getElementById("error-log");

// ============================================================
// API Functions
// ============================================================

async function getState() {
    try {
        const response = await fetch("/api/state");
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("خطأ في جلب الحالة:", error);
        return null;
    }
}

async function getHistory() {
    try {
        const response = await fetch("/api/history");
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("خطأ في جلب السجل:", error);
        return null;
    }
}

async function createTask(description) {
    try {
        const response = await fetch("/api/tasks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ description })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
}

async function checkHealth() {
    try {
        const response = await fetch("/api/health");
        const data = await response.json();
        return data;
    } catch (error) {
        return null;
    }
}

// ============================================================
// UI Functions
// ============================================================

function updateStatus(data) {
    if (!data) {
        taskStatus.textContent = "غير متصل";
        return;
    }
    
    taskStatus.textContent = data.task_status || "غير معروف";
    activeAgent.textContent = data.active_agent || "-";
    completedTasks.textContent = `${data.completed_tasks || 0} / ${data.task_count || 0}`;
    phase.textContent = `Phase ${(data.phase || "4").replace("phase", "")}`;
}

function formatTime(isoString) {
    if (!isoString) return "";
    const date = new Date(isoString);
    return date.toLocaleString("ar-SA", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });
}

function getStatusIcon(status) {
    const icons = {
        "مكتمل": "✅",
        "completed": "✅",
        "فشل": "❌",
        "failed": "❌",
        "قيد التنفيذ": "🔄",
        "executing": "🔄",
        "قيد التخطيط": "⏳",
        "planning": "⏳",
        "blocked": "🔴"
    };
    return icons[status] || "📋";
}

function updateHistory(data) {
    if (!data || !data.history || data.history.length === 0) {
        historyList.innerHTML = '<p class="loading">لا توجد مهام سابقة</p>';
        return;
    }
    
    const items = data.history
        .slice()  // copy
        .reverse() // newest first
        .map(item => {
            const icon = getStatusIcon(item.status);
            const statusClass = item.status === "completed" || item.status === "مكتمل" 
                ? "completed" 
                : item.status === "failed" || item.status === "فشل" 
                    ? "failed" 
                    : "";
            
            return `
                <div class="history-item ${statusClass}">
                    <div class="task-id">${item.task_id}</div>
                    <div class="task-desc">${item.description}</div>
                    <div class="task-status">${icon} ${item.status}</div>
                    <div class="task-time">${formatTime(item.timestamp)}</div>
                </div>
            `;
        })
        .join("");
    
    historyList.innerHTML = items;
}

function showResult(data) {
    taskResult.classList.remove("success", "error");
    
    if (data.success) {
        taskResult.classList.add("success");
        taskResult.innerHTML = `
            <strong>✅ ${data.message}</strong>
            <br>المعرف: ${data.task_id}
            ${data.files && data.files.length > 0 
                ? `<br>الملفات: ${data.files.slice(0, 3).join(", ")}${data.files.length > 3 ? "..." : ""}`
                : ""}
        `;
    } else {
        taskResult.classList.add("error");
        taskResult.innerHTML = `
            <strong>❌ فشل!</strong>
            <br>${data.error || data.message}
        `;
        
        // Show in error log
        showError(data.error || data.message);
    }
    
    // Clear after 10 seconds
    setTimeout(() => {
        taskResult.classList.remove("success", "error");
        taskResult.style.display = "none";
    }, 10000);
}

function showError(message) {
    errorSection.style.display = "block";
    errorLog.textContent = `[${new Date().toISOString()}]\n${message}\n\n${errorLog.textContent}`;
}

function setLoading(loading) {
    taskInput.disabled = loading;
    btnText.style.display = loading ? "none" : "inline";
    btnLoader.style.display = loading ? "inline-block" : "none";
}

// ============================================================
// Event Handlers
// ============================================================

taskForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const description = taskInput.value.trim();
    if (!description) return;
    
    setLoading(true);
    taskResult.style.display = "block";
    
    const data = await createTask(description);
    
    setLoading(false);
    showResult(data);
    
    // Refresh status and history
    await refreshUI();
});

taskInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        taskForm.dispatchEvent(new Event("submit"));
    }
});

// ============================================================
// Initialization
// ============================================================

async function refreshUI() {
    const state = await getState();
    updateStatus(state);
    
    const history = await getHistory();
    updateHistory(history);
}

// Initial load
document.addEventListener("DOMContentLoaded", async () => {
    // Check health
    const health = await checkHealth();
    if (!health) {
        taskStatus.textContent = "خطأ في الاتصال";
        return;
    }
    
    // Load data
    await refreshUI();
    
    // Refresh every 5 seconds
    setInterval(refreshUI, 5000);
});

// Handle visibility change
document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
        refreshUI();
    }
});
