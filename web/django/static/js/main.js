document.addEventListener("DOMContentLoaded", () => {
    const contentDiv = document.getElementById('content');
    
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
    
    const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    const navigateTo = (url) => {
        history.pushState(null, null, url);
    };
    
    const renderPage = () => {
        let path = window.location.pathname;
        console.log(path);
        fetch(`${path}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => response.text())
        .then(html => {
            contentDiv.innerHTML = html;
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
            }
        });
        
        document.querySelectorAll('.auth-form').forEach(form => {
            form.addEventListener('submit', (event) => {
                event.preventDefault();
                const formData = new FormData(event.target);
                console.log(formData);
                fetch(event.target.action, {
                    method: event.target.method,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
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
        
        let profileSearchBtn = document.getElementById('profile-search-btn');
        if (profileSearchBtn) {
            profileSearchBtn.addEventListener('click', (e) => {
                const alias = document.getElementById('inputsearch').value;
                fetch(`/api/profiles/search/?alias=${alias}`)
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    if (data.redirect) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error('Error searching profile:', error));
            });
        }
        
        let addFriendBtn = document.getElementById('add-friend-btn');
        if (addFriendBtn) {
            addFriendBtn.addEventListener('click', (e) => {
                const currentUrl = window.location.pathname;
                const uuidRegex = /\/profile\/([0-9a-fA-F-]{36})\/?/;
                const match = currentUrl.match(uuidRegex);
                if (match) {
                    const uuid = match[1];
                    const csrftoken = getCookie('csrftoken');
                    fetch(`/api/profiles/${uuid}/request/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data);
                    })
                    .catch(error => console.error('Error adding friend:', error));
                } else {
                    console.error('UUID not found in the URL');
                }
                let profile_id = window.location.href.substring(window.location.href.lastIndexOf('/') + 1);
            });
        }
    };

    window.addEventListener('popstate', renderPage);
    window.addEventListener('pushState', renderPage);
    window.addEventListener('replaceState', renderPage);

    attachHandlers();
});