document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-bs-toggle='tooltip']").forEach((el) => {
    if (window.bootstrap) new bootstrap.Tooltip(el);
  });
  
  // Force sidebar text color to black
  const sidebar = document.querySelector('.main-sidebar') || document.querySelector('.sidebar');
  if (sidebar) {
    sidebar.style.setProperty('background', '#ffffff', 'important');
    sidebar.style.setProperty('color', '#334155', 'important');
    
    // Force all text elements in sidebar to black
    const allElements = sidebar.querySelectorAll('*');
    allElements.forEach(el => {
      el.style.setProperty('color', '#334155', 'important');
    });
    
    // Set nav links specifically
    const navLinks = sidebar.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.style.setProperty('color', '#334155', 'important');
      link.style.setProperty('background', '#ffffff', 'important');
    });
    
    // Set icons
    const icons = sidebar.querySelectorAll('i, .fas, .far, .fab');
    icons.forEach(icon => {
      icon.style.setProperty('color', '#334155', 'important');
    });
  }
  
  // Also try with sidebar-dark classes
  const sidebarDark = document.querySelector('.sidebar-dark-primary') || document.querySelector('.sidebar-dark');
  if (sidebarDark) {
    sidebarDark.style.setProperty('background', '#ffffff', 'important');
    const allElements = sidebarDark.querySelectorAll('*');
    allElements.forEach(el => {
      el.style.setProperty('color', '#334155', 'important');
    });
  }
});
