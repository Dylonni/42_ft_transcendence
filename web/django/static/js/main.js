document.addEventListener("DOMContentLoaded", () => {
    const contentDiv = document.getElementById('content');
    let chatSocket;
    
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
    
    const langReload = (lang) => {
        console.log(lang);
        fetch(`/api/lang/${lang}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'path': window.location.pathname,
            }),
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
                    if (anchor.id.startsWith('lang')) {
                        const lang = anchor.id.split('-')[1];
                        langReload(lang);
                    } else {
                        navigateTo(anchor.href);
                    }
                });
            }
        });
        
        document.querySelectorAll('.auth-form').forEach(form => {
            form.addEventListener('submit', (event) => {
                event.preventDefault();
                const formData = new FormData(event.target);
                console.log(...formData);
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
        
        const profileSearchBtn = document.getElementById('profile-search-btn');
        const profileSearchInput = document.getElementById('inputsearch');
        if (profileSearchBtn && profileSearchInput) {
            profileSearchBtn.addEventListener('click', (e) => {
                const alias = profileSearchInput.value;
                if (alias) {
                    fetch(`/api/profiles/search/?alias=${alias}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data) {
                            console.log(data);
                            navigateTo(`/profiles/${data[0].id}`);
                        }
                    })
                    .catch(error => console.error('Error searching profile:', error));
                }
            });
            profileSearchInput.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    profileSearchBtn.click();
                }
            });
        }        
        
        const addFriendBtn = document.getElementById('add-friend-btn');
        if (addFriendBtn) {
            addFriendBtn.addEventListener('click', (e) => {
                let currentUrl = window.location.pathname;
                if (!currentUrl.endsWith('/')) {
                    currentUrl += '/';
                }
                const csrfToken = getCookie('csrftoken');
                fetch(`/api${currentUrl}requests/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                })
                .catch(error => console.error('Error adding friend:', error));
            });
        }
        const createGameForm = document.getElementById('createGameForm');
        if (createGameForm) {
            createGameForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                console.log(...formData);
            });
        }
        const friendChatBtn = document.getElementById('friend-chat-btn');
        const friendChatInput = document.getElementById('chatInput');
        const messageList = document.getElementById('message-list');
        if (friendChatBtn && friendChatInput && messageList) {
            console.log('CHAT SYSTEM');
            const currentUrl = window.location.pathname;
            const uuidRegex = /\/friends\/([0-9a-fA-F-]{36})\/?/;
            const match = currentUrl.match(uuidRegex);
            if (match) {
                const uuid = match[1];
                chatSocket = new WebSocket(
                    `ws://${window.location.host}/ws/chat/${uuid}/`
                );
                
                chatSocket.addEventListener('open', (e) => {
                    console.log('Chat socket connection established');
                });
                
                chatSocket.addEventListener('message', (e) => {
                    const data = JSON.parse(e.data);
                    const message = data['message'];
                    console.log(message);
                    messageList.innerHTML += message;
                });
                
                chatSocket.addEventListener('close', (e) => {
                    console.error('Chat socket closed unexpectedly');
                });
                
                friendChatBtn.addEventListener('click', (e) => {
                    const message = friendChatInput.value;
                    if (message) {
                        chatSocket.send(JSON.stringify({
                            'message': message
                        }));
                        console.log(`Sent: ${message}`);
                        friendChatInput.value = '';
                    }
                });
                
                friendChatInput.focus();
                friendChatInput.addEventListener('keyup', (e) => {
                    if (e.key === 'Enter') {
                        friendChatBtn.click();
                    }
                });
            }
        }
    };
    
    window.addEventListener('popstate', renderPage);
    window.addEventListener('pushState', renderPage);
    window.addEventListener('replaceState', renderPage);
    
    attachHandlers();
});