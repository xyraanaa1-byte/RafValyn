// ===========================
// DARK / LIGHT MODE
// ===========================
const html = document.documentElement;
const savedTheme = localStorage.getItem('theme') || 'dark';
html.setAttribute('data-theme', savedTheme);
updateThemeUI(savedTheme);

function toggleTheme() {
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeUI(next);
}

function updateThemeUI(theme) {
    const label = document.getElementById('themeLabel');
    const icon = document.getElementById('themeIcon');
    if (!label || !icon) return;

    if (theme === 'light') {
        label.textContent = 'Mode Gelap';
        icon.innerHTML = `<path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" fill="none" stroke="currentColor" stroke-width="2"/>`;
    } else {
        label.textContent = 'Mode Terang';
        icon.innerHTML = `<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>`;
    }
}

// ===========================
// PROFILE DROPDOWN
// ===========================
function toggleDropdown() {
    const menu = document.getElementById('dropdownMenu');
    if (menu) menu.classList.toggle('show');
}

document.addEventListener('click', function(e) {
    const dropdown = document.getElementById('profileDropdown');
    const menu = document.getElementById('dropdownMenu');
    if (dropdown && menu && !dropdown.contains(e.target)) {
        menu.classList.remove('show');
    }
});

// ===========================
// MOBILE MENU
// ===========================
function toggleMobileMenu() {
    const menu = document.getElementById('navbarMenu');
    const hamburger = document.getElementById('hamburger');
    const icon = document.getElementById('hamburgerIcon');
    const isOpen = menu.classList.contains('show');

    if (isOpen) {
        // Tutup menu
        menu.classList.remove('show');
        hamburger.classList.remove('active');
        icon.innerHTML = `
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
        `;
    } else {
        // Buka menu
        menu.classList.add('show');
        hamburger.classList.add('active');
        icon.innerHTML = `
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
        `;
    }
}

// Klik di luar menu → otomatis tutup
document.addEventListener('click', function(e) {
    const menu = document.getElementById('navbarMenu');
    const hamburger = document.getElementById('hamburger');
    const icon = document.getElementById('hamburgerIcon');

    if (menu && hamburger && !hamburger.contains(e.target) && !menu.contains(e.target)) {
        if (menu.classList.contains('show')) {
            menu.classList.remove('show');
            hamburger.classList.remove('active');
            if (icon) icon.innerHTML = `
                <line x1="3" y1="6" x2="21" y2="6"/>
                <line x1="3" y1="12" x2="21" y2="12"/>
                <line x1="3" y1="18" x2="21" y2="18"/>
            `;
        }
    }

    // Tutup dropdown profil juga kalau klik di luar
    const dropdown = document.getElementById('profileDropdown');
    const dropdownMenu = document.getElementById('dropdownMenu');
    if (dropdown && dropdownMenu && !dropdown.contains(e.target)) {
        dropdownMenu.classList.remove('show');
    }
});

// ===========================
// NAVBAR SCROLL EFFECT
// ===========================
window.addEventListener('scroll', function() {
    const navbar = document.getElementById('navbar');
    if (navbar) {
        if (window.scrollY > 20) {
            navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.3)';
        } else {
            navbar.style.boxShadow = 'none';
        }
    }
});

// ===========================
// AUTO HIDE FLASH MESSAGES
// ===========================
setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateX(20px)';
        el.style.transition = 'all 0.3s ease';
        setTimeout(() => el.remove(), 300);
    });
}, 4000);

// Join personal room untuk notifikasi realtime
if (typeof socket !== 'undefined') {
    socket.emit('join_user_room');
}

// Load notif count
function loadNotifCount() {
    fetch('/notifications/count')
    .then(r => r.json())
    .then(d => {
        const badge = document.getElementById('notifBadge');
        const dmBadge = document.getElementById('dmBadge');
        if (badge) {
            badge.textContent = d.count;
            badge.classList.toggle('show', d.count > 0);
        }
    });
}

loadNotifCount();
setInterval(loadNotifCount, 30000);

// ===========================
// NOTIFIKASI REALTIME
// ===========================
function initNotifications() {
    // Cek apakah SocketIO tersedia di halaman ini
    if (typeof io === 'undefined') return;

    const notifSocket = io();
    notifSocket.emit('join_user_room');

    notifSocket.on('new_notification', function(data) {
        showNotifToast(data);
        loadNotifCount();
        // Update badge DM kalau notif chat
        if (data.type === 'chat') {
            loadChatUnread();
        }
    });
}

function showNotifToast(data) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        right: 1rem;
        z-index: 9999;
        background: var(--bg);
        border: 1px solid var(--border);
        border-left: 4px solid var(--pink);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        min-width: 280px;
        max-width: 350px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        animation: slideInRight 0.3s ease;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    `;

    const icon = data.type === 'chat' ? '💬' : data.type === 'valentine' ? '💌' : '🔔';

    toast.innerHTML = `
        <span style="font-size:1.5rem;flex-shrink:0;">${icon}</span>
        <div style="flex:1;overflow:hidden;">
            <p style="font-size:0.88rem;font-weight:700;color:var(--text);margin-bottom:0.2rem;">${data.title}</p>
            <p style="font-size:0.78rem;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${data.message}</p>
        </div>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:1rem;padding:0;flex-shrink:0;">×</button>
    `;

    toast.addEventListener('click', function(e) {
        if (e.target.tagName !== 'BUTTON') {
            window.location.href = data.link;
        }
    });

    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function loadNotifCount() {
    fetch('/notifications/count')
    .then(r => r.json())
    .then(d => {
        const badge = document.getElementById('notifBadge');
        if (badge) {
            badge.textContent = d.count;
            badge.classList.toggle('show', d.count > 0);
        }
    }).catch(() => {});
}

function loadChatUnread() {
    fetch('/chat/unread')
    .then(r => r.json())
    .then(d => {
        const badge = document.getElementById('dmBadge');
        if (badge) {
            badge.textContent = d.count;
            badge.classList.toggle('show', d.count > 0);
        }
    }).catch(() => {});
}

// Tambahkan CSS animasi
const notifStyle = document.createElement('style');
notifStyle.textContent = `
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideOutRight {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(20px); }
    }
`;
document.head.appendChild(notifStyle);

// Init
loadNotifCount();
loadChatUnread();
setInterval(loadNotifCount, 30000);
setInterval(loadChatUnread, 15000);
initNotifications();