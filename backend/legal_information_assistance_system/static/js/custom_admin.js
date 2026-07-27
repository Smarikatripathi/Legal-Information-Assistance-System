// Custom Admin JavaScript for Legal Information Assistance System

document.addEventListener('DOMContentLoaded', function() {
    // Notification bell functionality
    const notificationBell = document.querySelector('.notification-bell');
    if (notificationBell) {
        notificationBell.addEventListener('click', function(e) {
            e.preventDefault();
            toggleNotificationDropdown();
        });
    }

    // Close notification dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const dropdown = document.querySelector('.notification-dropdown');
        if (dropdown && !dropdown.contains(e.target) && !notificationBell?.contains(e.target)) {
            dropdown.classList.add('d-none');
        }
    });

    // Confirm destructive actions
    const destructiveButtons = document.querySelectorAll('[data-confirm]');
    destructiveButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (message && !confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Keyboard shortcut for search (Ctrl+K)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.search-input');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });

    // Sidebar toggle for mobile
    const sidebarToggle = document.querySelector('.topbar-icon[aria-label="Toggle navigation"]');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            const sidebar = document.querySelector('.legal-admin-sidebar');
            if (sidebar) {
                sidebar.classList.toggle('sidebar-collapsed');
                document.body.classList.toggle('sidebar-collapsed');
            }
        });
    }

    // Also handle any sidebar-toggle class
    const sidebarToggleAlt = document.querySelector('.sidebar-toggle');
    if (sidebarToggleAlt) {
        sidebarToggleAlt.addEventListener('click', function() {
            const sidebar = document.querySelector('.legal-admin-sidebar');
            if (sidebar) {
                sidebar.classList.toggle('sidebar-collapsed');
                document.body.classList.toggle('sidebar-collapsed');
            }
        });
    }

    // Initialize tooltips
    const tooltipElements = document.querySelectorAll('[data-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        element.setAttribute('title', element.getAttribute('data-original-title') || element.title);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Table row actions improvements
    const actionButtons = document.querySelectorAll('.action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Mark notification as read
    const markAsReadButtons = document.querySelectorAll('.mark-as-read');
    markAsReadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const notificationId = this.getAttribute('data-notification-id');
            markNotificationAsRead(notificationId);
        });
    });

    // Mark all notifications as read
    const markAllAsReadButton = document.querySelector('.mark-all-as-read');
    if (markAllAsReadButton) {
        markAllAsReadButton.addEventListener('click', function(e) {
            e.preventDefault();
            markAllNotificationsAsRead();
        });
    }
});

function toggleNotificationDropdown() {
    const dropdown = document.querySelector('.notification-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('d-none');
        
        // Load notifications if dropdown is opened
        if (!dropdown.classList.contains('d-none') && dropdown.children.length === 0) {
            loadNotifications();
        }
    }
}

async function loadNotifications() {
    const dropdown = document.querySelector('.notification-dropdown');
    if (!dropdown) return;

    try {
        const response = await fetch('/admin/legal_ai/notifications/');
        if (response.ok) {
            const data = await response.json();
            renderNotifications(data.notifications, dropdown);
        }
    } catch (error) {
        console.error('Failed to load notifications:', error);
        dropdown.innerHTML = '<div class="p-3 text-muted">Failed to load notifications</div>';
    }
}

function renderNotifications(notifications, container) {
    if (!notifications || notifications.length === 0) {
        container.innerHTML = '<div class="p-3 text-muted">No new notifications</div>';
        return;
    }

    let html = '<div class="notification-list">';
    notifications.forEach(notification => {
        html += `
            <div class="notification-item ${notification.status === 'unread' ? 'unread' : ''}" data-id="${notification.id}">
                <div class="notification-content">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message}</div>
                    <div class="notification-time">${notification.created_at}</div>
                </div>
                <button class="btn btn-sm btn-link mark-as-read" data-notification-id="${notification.id}">
                    <i class="fas fa-check"></i>
                </button>
            </div>
        `;
    });
    html += `
        <div class="notification-footer">
            <a href="/admin/legal_ai/adminnotification/" class="btn btn-sm btn-primary">View All</a>
            <button class="btn btn-sm btn-secondary mark-all-as-read">Mark All Read</button>
        </div>
    </div>`;
    
    container.innerHTML = html;

    // Add event listeners to new elements
    container.querySelectorAll('.mark-as-read').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const notificationId = this.getAttribute('data-notification-id');
            markNotificationAsRead(notificationId);
        });
    });

    container.querySelector('.mark-all-as-read')?.addEventListener('click', function(e) {
        e.preventDefault();
        markAllNotificationsAsRead();
    });
}

async function markNotificationAsRead(notificationId) {
    try {
        const response = await fetch(`/admin/legal_ai/notifications/${notificationId}/mark-read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
            },
        });
        if (response.ok) {
            const notificationItem = document.querySelector(`.notification-item[data-id="${notificationId}"]`);
            if (notificationItem) {
                notificationItem.classList.remove('unread');
            }
            updateNotificationBadge();
        }
    } catch (error) {
        console.error('Failed to mark notification as read:', error);
    }
}

async function markAllNotificationsAsRead() {
    try {
        const response = await fetch('/admin/legal_ai/mark-all-read/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
            },
        });
        if (response.ok) {
            document.querySelectorAll('.notification-item.unread').forEach(item => {
                item.classList.remove('unread');
            });
            updateNotificationBadge();
        }
    } catch (error) {
        console.error('Failed to mark all notifications as read:', error);
    }
}

function updateNotificationBadge() {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        const currentCount = parseInt(badge.textContent);
        if (currentCount > 0) {
            badge.textContent = Math.max(0, currentCount - 1);
            if (badge.textContent === '0') {
                badge.classList.add('d-none');
            }
        }
    }
}

function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// PDF Preview functionality
function openPdfPreview(documentId) {
    const url = `/admin/legal_ai/legaldocument/${documentId}/preview/`;
    window.open(url, '_blank');
}

// Utility function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Utility function to truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Initialize any dynamic content
function initializeDynamicContent() {
    // Load dashboard stats
    const dashboardStats = document.querySelector('[data-dashboard-stats]');
    if (dashboardStats) {
        loadDashboardStats();
    }
}

async function loadDashboardStats() {
    try {
        const response = await fetch('/admin/legal_ai/dashboard-stats/');
        if (response.ok) {
            const stats = await response.json();
            updateDashboardStats(stats);
        }
    } catch (error) {
        console.error('Failed to load dashboard stats:', error);
    }
}

function updateDashboardStats(stats) {
    // Update KPI cards with real data
    const statElements = document.querySelectorAll('[data-stat]');
    statElements.forEach(element => {
        const statKey = element.getAttribute('data-stat');
        if (stats[statKey] !== undefined) {
            element.textContent = stats[statKey];
        }
    });
}

// Call initialization
initializeDynamicContent();
