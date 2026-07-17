/**
 * Todo App - CodeForge Demo Project
 * Phase 4: First Complete Project
 */

// ============================================================
// State
// ============================================================

let todos = [];
let nextId = 1;

// ============================================================
// DOM Elements
// ============================================================

const taskInput = document.getElementById("task-input");
const addBtn = document.getElementById("add-btn");
const tasksList = document.getElementById("tasks-list");
const emptyState = document.getElementById("empty-state");
const totalCount = document.getElementById("total-count");
const completedCount = document.getElementById("completed-count");
const pendingCount = document.getElementById("pending-count");
const clearCompletedBtn = document.getElementById("clear-completed");
const clearAllBtn = document.getElementById("clear-all");

// ============================================================
// Storage
// ============================================================

function saveToStorage() {
    const data = {
        todos: todos,
        nextId: nextId
    };
    localStorage.setItem("codeforge_todos", JSON.stringify(data));
}

function loadFromStorage() {
    const data = localStorage.getItem("codeforge_todos");
    if (data) {
        try {
            const parsed = JSON.parse(data);
            todos = parsed.todos || [];
            nextId = parsed.nextId || 1;
        } catch (e) {
            console.error("خطأ في تحميل البيانات:", e);
            todos = [];
            nextId = 1;
        }
    }
}

// ============================================================
// Todo Operations
// ============================================================

function addTodo(text) {
    if (!text.trim()) return;
    
    const todo = {
        id: nextId++,
        text: text.trim(),
        done: false,
        createdAt: new Date().toISOString()
    };
    
    todos.push(todo);
    saveToStorage();
    render();
}

function toggleTodo(id) {
    const todo = todos.find(t => t.id === id);
    if (todo) {
        todo.done = !todo.done;
        saveToStorage();
        render();
    }
}

function deleteTodo(id) {
    todos = todos.filter(t => t.id !== id);
    saveToStorage();
    render();
}

function clearCompleted() {
    todos = todos.filter(t => !t.done);
    saveToStorage();
    render();
}

function clearAll() {
    todos = [];
    saveToStorage();
    render();
}

// ============================================================
// Render
// ============================================================

function render() {
    // Update stats
    const total = todos.length;
    const completed = todos.filter(t => t.done).length;
    const pending = total - completed;
    
    totalCount.textContent = total;
    completedCount.textContent = completed;
    pendingCount.textContent = pending;
    
    // Render list
    if (todos.length === 0) {
        tasksList.innerHTML = "";
        emptyState.style.display = "block";
        return;
    }
    
    emptyState.style.display = "none";
    
    tasksList.innerHTML = todos.map(todo => `
        <li class="task-item ${todo.done ? "completed" : ""}" data-id="${todo.id}">
            <input 
                type="checkbox" 
                class="task-checkbox" 
                ${todo.done ? "checked" : ""}
                onchange="toggleTodo(${todo.id})"
            >
            <span class="task-text">${escapeHtml(todo.text)}</span>
            <button class="task-delete" onclick="deleteTodo(${todo.id})">🗑️</button>
        </li>
    `).join("");
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================
// Event Listeners
// ============================================================

addBtn.addEventListener("click", () => {
    addTodo(taskInput.value);
    taskInput.value = "";
    taskInput.focus();
});

taskInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        addTodo(taskInput.value);
        taskInput.value = "";
    }
});

clearCompletedBtn.addEventListener("click", clearCompleted);
clearAllBtn.addEventListener("click", clearAll);

// ============================================================
// Initialize
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    loadFromStorage();
    render();
});
