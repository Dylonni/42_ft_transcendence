document.addEventListener("DOMContentLoaded", () => {
    const appDiv = document.getElementById('content');
    
    const originalPushState = history.pushState;
    history.pushState = function () {
        originalPushState.apply(history, arguments);
        fireStateEvent('pushState', arguments);
    };
    
    const originalReplaceState = history.replaceState;
    history.replaceState = function () {
        originalReplaceState.apply(history, arguments);
        fireStateEvent('replaceState', arguments);
    };
    
    const fireStateEvent = (type, args) => {
        const event = new Event(type);
        event.arguments = args;
        window.dispatchEvent(event);
    };
    
    const navigateTo = (url) => {
        history.pushState(null, null, url);
    };
    
    const renderPage = () => {
        let path = window.location.pathname;
        console.log(path);
        if (path.localeCompare("/") == 0) {
            path = '/login/';
        }
        fetch(`${path}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => response.text())
        .then(html => {
            appDiv.innerHTML = html;
            attachHandlers();
        })
        .catch(error => console.error('Error fetching content:', error));
    };
    
    const attachHandlers = () => {
        document.querySelectorAll('a').forEach(anchor => {
            if (anchor.id != 'login-42') {
                anchor.addEventListener('click', (event) => {
                    event.preventDefault();
                    navigateTo(anchor.href);
                });
            } else {
                anchor.addEventListener('click', function() {
                    const loginWindow = window.open('/api/oauth/42/login/', '42 Login', 'width=600,height=600');
                    
                    // window.location.reload();
                });
            }
        });
        
        document.querySelectorAll('.auth-form').forEach(form => {
            form.addEventListener('submit', (event) => {
                event.preventDefault();
                const formData = new FormData(event.target);
                fetch(event.target.action, {
                    method: event.target.method,
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    if (data.redirect) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error('Error submitting form:', error));
            });
        });

        let logoutBtn = document.querySelector('.logout-btn')
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (event) => {
            event.preventDefault();
            fetch(`/api/auth/logout/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.redirect) {
                    navigateTo(data.redirect);
                }
            })
            .catch(error => console.error('Error logging out:', error));
        });
        }
    };

    window.addEventListener('popstate', renderPage);
    window.addEventListener('pushState', renderPage);
    window.addEventListener('replaceState', renderPage);

    renderPage();
    attachHandlers();
});