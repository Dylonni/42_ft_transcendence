document.addEventListener("DOMContentLoaded", () => {
    const contentDiv = document.getElementById('content');
    const loadedScripts = new Set();
    let chatSocket;
    let notifSocket = null;
    let friendSocket = null;
    let gameSocket = null;

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
        if (url) {
            history.pushState(null, null, url);
        }
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
            const newDocument = new DOMParser().parseFromString(html, 'text/html');
            const newContent = newDocument.querySelector('#content').childNodes;
            while (contentDiv.firstChild) {
                contentDiv.removeChild(contentDiv.firstChild);
            }
            newContent.forEach(node => {
                contentDiv.appendChild(node.cloneNode(true));
            });
            loadPageScripts(newDocument);
            attachHandlers();
        })
        .catch(error => console.error('Error fetching content:', error));
    };

    const loadPageScripts = (newDocument) => {
        const scriptElements = newDocument.querySelectorAll('script');
        scriptElements.forEach(scriptElement => {
            const src = scriptElement.src;
            if (!loadedScripts.has(src)) {
                const newScript = document.createElement('script');
                newScript.src = src;
                document.body.appendChild(newScript);
                loadedScripts.add(src);
            }
        });
    }

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

    const makeAPIRequest = (url, method, headers = {}, body = null, callback) => {
        fetch(url, {
            method: method,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                ...headers,
            },
            body: body,
        })
        .then(response => response.json())
        .then(data => {
            if ('redirect' in data) {
                navigateTo(data.redirect);
            }
            else if (callback) {
                callback(data);
            }
        })
        .catch(error => console.error(`Error with request to ${url}:`, error));
    };

    const langReload = (lang) => {
        makeAPIRequest(
            `/api/lang/${lang}/`,
            'POST',
            {'Content-Type': 'application/json'},
            JSON.stringify({'path': window.location.pathname}),
        );
    };

    const closeWebSocket = (socket) => {
        if (socket) {
            socket.close();
            socket = null;
        }
    };

    const openNotifWebSocket = () => {
        if (notifSocket && notifSocket.readyState !== WebSocket.CLOSED) {
            return;
        }

        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
        const wsUrl = `${wsScheme}://${window.location.host}/ws/notifs/`;
        notifSocket = new WebSocket(wsUrl);

        notifSocket.onopen = () => {
            console.log('Notif WebSocket connection established.');
        };

        notifSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const message = data['message'];
            console.log(message);
        };

        notifSocket.onclose = () => {
            console.log('Notif WebSocket connection closed.');
        };

        notifSocket.onerror = (error) => {
            console.error('Notif WebSocket error:', error);
        };
    };

    const openFriendWebSocket = (uuid) => {
        if (friendSocket && friendSocket.readyState !== WebSocket.CLOSED) {
            return;
        }

        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
        const wsUrl = `${wsScheme}://${window.location.host}/ws/friends/${uuid}/`;
        friendSocket = new WebSocket(wsUrl);

        friendSocket.onopen = () => {
            console.log('Friend WebSocket connection established.');
        };

        friendSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const message = data['message'];
            console.log(message);
        };

        friendSocket.onclose = () => {
            console.log('Friend WebSocket connection closed.');
        };

        friendSocket.onerror = (error) => {
            console.error('Friend WebSocket error:', error);
        };
    };

    const openGameWebSocket = (uuid) => {
        if (gameSocket && gameSocket.readyState !== WebSocket.CLOSED) {
            return;
        }

        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
        const wsUrl = `${wsScheme}://${window.location.host}/ws/games/${uuid}/`;
        gameSocket = new WebSocket(wsUrl);

        gameSocket.onopen = () => {
            console.log('Game WebSocket connection established.');
        };

        gameSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const message = data['message'];
            console.log(message);
        };

        gameSocket.onclose = () => {
            console.log('Game WebSocket connection closed.');
        };

        gameSocket.onerror = (error) => {
            console.error('Game WebSocket error:', error);
        };
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
                fetch(event.target.action, {
                    method: event.target.method,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    openNotifWebSocket();
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error(`Error with request to ${url}:`, error));
            });
        });
        
        let logoutBtn = document.querySelector('.logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (event) => {
                event.preventDefault();
                makeAPIRequest(
                    '/api/auth/logout/',
                    'POST',
                );
                closeWebSocket(notifSocket);
                closeWebSocket(friendSocket);
                closeWebSocket(gameSocket);
            });
        }
        
        let avatarBtn = document.querySelector('#avatar-upload');
        if (avatarBtn) {
            avatarBtn.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    const formData = new FormData();
                    const imageFile = e.target.files[0];
                    formData.append('avatar', imageFile);
                    makeAPIRequest(
                        '/api/profiles/me/avatar/',
                        'POST',
                        {},
                        formData,
                    );
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
                fetch(e.target.action, {
                    method: e.target.method,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    openGameWebSocket(data.id);
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error('Error creating game:', error));
            });
        }
        
        const friendChatBtn = document.getElementById('friend-chat-btn');
        const friendChatInput = document.getElementById('chatInput');
        const messageList = document.getElementById('message-list');
        if (friendChatBtn && friendChatInput && messageList) {
            const currentUrl = window.location.pathname;
            const uuidRegex = /\/friends\/([0-9a-fA-F-]{36})\/?/;
            const match = currentUrl.match(uuidRegex);
            if (match) {
                const uuid = match[1];
                chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/${uuid}/`);
                
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

        var toastTriggers = document.querySelectorAll('[data-bs-toggle="toast"]');
        for (let toastTrigger of toastTriggers) {
            toastTrigger.addEventListener('click', function () {
                var toastSelector = toastTrigger.getAttribute('data-bs-target');
                if (!toastSelector) return;
                try {
                    var toastEl = document.querySelector(toastSelector);
                    if (!toastEl) return;
                    var toast = new bootstrap.Toast(toastEl);
                    toast.show();
                }
                catch(e) {
                    console.error(e);
                }
            })
        }

        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl,  {trigger: 'hover'}));

        if (window.innerWidth < 768) {
            [].slice.call(document.querySelectorAll('[data-bss-disabled-mobile]')).forEach(function (elem) {
                elem.classList.remove('animated');
                elem.removeAttribute('data-bss-hover-animate');
                elem.removeAttribute('data-aos');
                elem.removeAttribute('data-bss-parallax-bg');
                elem.removeAttribute('data-bss-scroll-zoom');
            });
        }
    };
    
    window.addEventListener('popstate', renderPage);
    window.addEventListener('pushState', renderPage);
    window.addEventListener('replaceState', renderPage);
    
    attachHandlers();
});