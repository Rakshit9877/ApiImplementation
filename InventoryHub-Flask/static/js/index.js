// Utility Functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 100);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-IN').format(num);
}

// Navigation Handling
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        this.classList.add('active');
        showNotification(`Navigated to ${this.textContent.trim()}`);
        
        const content = document.querySelector('.content');
        content.classList.add('loading');
        setTimeout(() => content.classList.remove('loading'), 1000);
    });
});

// Stats Interaction
document.querySelectorAll('.stat-item').forEach(stat => {
    stat.addEventListener('click', function() {
        this.classList.toggle('active');
        const label = this.querySelector('.stat-label').textContent;
        const value = this.querySelector('.stat-value').textContent;
        showNotification(`Selected ${label}: ${value}`);
    });
});

// Simulate Real-time Updates
function updateRandomStat() {
    const stats = document.querySelectorAll('.stat-value');
    const randomStat = stats[Math.floor(Math.random() * stats.length)];
    const currentValue = parseInt(randomStat.textContent.replace(/,/g, ''));
    const change = Math.floor(Math.random() * 20) - 10;
    const newValue = currentValue + change;
    
    randomStat.textContent = formatNumber(newValue);
    
    const trend = randomStat.nextElementSibling;
    if (trend) {
        const percentage = ((change / currentValue) * 100).toFixed(1);
        trend.textContent = `${percentage > 0 ? '↑' : '↓'} ${Math.abs(percentage)}% vs last week`;
        trend.style.color = percentage > 0 ? '#16a34a' : '#dc2626';
    }
}
setInterval(updateRandomStat, 5000);

// Button Interactions
document.querySelectorAll('.button').forEach(button => {
    button.addEventListener('click', function(e) {
        if (this.tagName.toLowerCase() !== 'a') {  
            e.preventDefault();  // Prevent default only if it's NOT a link
        }
        const isSignup = this.textContent.includes('Started');
        showNotification(isSignup ? 'Starting sign up process...' : 'Loading Your Account...', 'Success');
    });
});


// Rating Interactions
document.querySelectorAll('.rating-item').forEach(rating => {
    rating.addEventListener('mouseenter', () => rating.style.transform = 'scale(1.05)');
    rating.addEventListener('mouseleave', () => rating.style.transform = 'scale(1)');
    rating.addEventListener('click', function() {
        const source = this.textContent.split(' ').pop();
        showNotification(`Viewing ${source} reviews...`);
    });
});

// Initialize with Loading Animation
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.opacity = '1';
        document.body.style.transition = 'opacity 0.3s ease';
        showNotification('Welcome to InvenTrack!', 'success');
    }, 100);
});

// Mobile Navigation Handling
if (window.innerWidth <= 768) {
    const navList = document.querySelector('.nav-list');
    let isScrolling = false;
    
    navList.addEventListener('scroll', () => {
        if (!isScrolling) navList.classList.add('scrolling');
        isScrolling = true;
        clearTimeout(window.scrollTimeout);
        
        window.scrollTimeout = setTimeout(() => {
            navList.classList.remove('scrolling');
            isScrolling = false;
        }, 150);
    });
}

// Keyboard Navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.stat-item.active').forEach(stat => stat.classList.remove('active'));
    }
});


// Number Animation Function
function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        element.textContent = Math.floor(progress * (end - start) + start).toLocaleString();
        if (progress < 1) window.requestAnimationFrame(step);
    };
    window.requestAnimationFrame(step);
}

// Start Number Animations
function startNumberAnimations() {
    document.querySelectorAll('.stat-value').forEach(element => {
        const finalValue = parseInt(element.textContent.replace(/,/g, ''));
        element.textContent = '0';
        animateValue(element, 0, finalValue, 2000);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const items = document.querySelectorAll(".integration-item");
    const middleIndex = Math.floor(items.length / 2);

    items.forEach((item, index) => {
        setTimeout(() => {
            if (index < middleIndex) {
                item.classList.add("move-left");
            } else if (index > middleIndex) {
                item.classList.add("move-right");
            } else {
                item.classList.add("center");
            }
        }, index * 100);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const observerOptions = {
        root: null,
        rootMargin: '-50px',
        threshold: 0.2
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Calculate delay based on distance from center
                const items = entry.target.parentNode.children;
                const centerIndex = Math.floor(items.length / 2);
                const currentIndex = Array.from(items).indexOf(entry.target);
                const distanceFromCenter = Math.abs(currentIndex - centerIndex);
                
                // Stagger delay increases as items get further from center
                entry.target.style.animationDelay = `${distanceFromCenter * 0.1}s`;
                entry.target.classList.add('animate');
            }
        });
    }, observerOptions);

    // Observe all integration items
    document.querySelectorAll('.integration-item').forEach(item => {
        observer.observe(item);
    });
});

// Mobile menu toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const navItems = document.getElementById('nav-items');
    
    if (mobileMenuToggle && navItems) {
      mobileMenuToggle.addEventListener('click', function() {
        navItems.classList.toggle('active');
      });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
      if (!event.target.closest('.nav-container') && navItems.classList.contains('active')) {
        navItems.classList.remove('active');
      }
    });
    
    // Sidebar toggle functionality for mobile
    const createSidebarToggle = function() {
      if (window.innerWidth <= 768) {
        const sidebar = document.querySelector('.sidebar');
        
        if (sidebar) {
          // Create toggle button if it doesn't exist
          if (!document.getElementById('sidebar-toggle')) {
            const sidebarToggle = document.createElement('button');
            sidebarToggle.id = 'sidebar-toggle';
            sidebarToggle.classList.add('sidebar-toggle');
            sidebarToggle.innerHTML = '☰ Menu';
            
            const content = document.querySelector('.content');
            if (content) {
              content.prepend(sidebarToggle);
              
              sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('active');
              });
              
              // Close sidebar when clicking outside
              document.addEventListener('click', function(event) {
                if (!event.target.closest('.sidebar') && 
                    event.target !== sidebarToggle && 
                    sidebar.classList.contains('active')) {
                  sidebar.classList.remove('active');
                }
              });
            }
          }
        }
      }
    };
    
    createSidebarToggle();
    
    // Recalculate on resize
    window.addEventListener('resize', function() {
      createSidebarToggle();
    });
  });
