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
    
    const isTokenExpired = (token) => {
        if (!token) return true;
        const payload = JSON.parse(atob(token.split('.')[1]));
        const exp = payload.exp;
        const now = Math.floor(Date.now() / 1000);
        return exp < now;
    };
    
    const refreshToken = () => {
        const refreshToken = sessionStorage.getItem('refresh_token');
        if (!refreshToken) {
            console.warn('No refresh token found in sessionStorage.');
            return;
        }
        fetch('/api/accounts/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to refresh token');
            }
            return response.json();
        })
        .then(data => {
            sessionStorage.setItem('access_token', data.access);
            return data.access;
        })
        .catch(error => {
            console.error('Error refreshing token:', error);
            return;
        });
    };
    
    const validateToken = () => {
        const accessToken = sessionStorage.getItem('access_token');
        if (!accessToken || isTokenExpired(accessToken)) {
            console.warn('No access token found in sessionStorage.');
            refreshToken();
            return;
        }
        fetch('/api/accounts/token/verify/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token: accessToken }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to validate token');
            }
            return response.json();
        })
        .then(data => {
            console.log('Token validation successful!');
        })
        .catch(error => {
            console.error('Error validating token:', error);
            return;
        });
    };
    
    const renderPage = () => {
        validateToken();
        let path = window.location.pathname;
        console.log(path);
        if (path.localeCompare("/") == 0) {
            path = "/login";
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
            if (anchor.target != '_blank') {
                anchor.addEventListener('click', (event) => {
                    event.preventDefault();
                    navigateTo(anchor.href);
                });
            }
        });
        
        document.querySelectorAll('form').forEach(form => {
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
                    if (data.status == 'Authentication successful!') {
                        sessionStorage.setItem('access_token', data.access);
                        sessionStorage.setItem('refresh_token', data.refresh);
                        if (data.redirect) {
                            navigateTo(data.redirect);
                        }
                    } else {
                        sessionStorage.removeItem('access_token');
                        sessionStorage.removeItem('refresh_token');
                        if (data.html) {
                            appDiv.innerHTML = data.html;
                            attachHandlers();
                        }
                    }
                })
                .catch(error => console.error('Error submitting form:', error));
            });
        });
    };

    window.addEventListener('popstate', renderPage);
    window.addEventListener('pushState', renderPage);
    window.addEventListener('replaceState', renderPage);

    renderPage();
    attachHandlers();
});