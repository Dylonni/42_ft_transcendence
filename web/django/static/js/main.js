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
    
    const getCookie = (name) => {
        let value = "; " + document.cookie;
        let parts = value.split("; " + name + "=");
        if (parts.length === 2) {
            return parts.pop().split(";").shift();
        }
    }
    
    const renderPage = () => {
        let path = window.location.pathname;
        console.log(path);
        if (path.localeCompare("/") == 0) {
            var csrftoken = getCookie('csrftoken');
            fetch('/api/token/verify/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.redirect) {
                    navigateTo(data.redirect);
                }
            })
            .catch(error => console.error('Error verifying tokens:', error));
        } else {
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
        }
    };
    
    const attachHandlers = () => {
        document.querySelectorAll('a').forEach(anchor => {
            if (anchor.id != 'login-42') {
                anchor.addEventListener('click', (event) => {
                    event.preventDefault();
                    navigateTo(anchor.href);
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

        let logoutBtn = document.querySelector('.logout-btn');
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

        let avatarBtn = document.querySelector('#avatar-btn');
        if (avatarBtn) {
            avatarBtn.addEventListener('change', (e) => {
                if (e.target.files[0]) {
                    console.log('You selected ' + e.target.files[0].name);
                }
            });
        }
    };

    window.addEventListener('popstate', renderPage);
    window.addEventListener('pushState', renderPage);
    window.addEventListener('replaceState', renderPage);

    // renderPage();
    attachHandlers();
});