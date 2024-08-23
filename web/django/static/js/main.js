document.addEventListener("DOMContentLoaded", () => {
    const contentDiv = document.getElementById('content');
    const loadedScripts = new Set();
    let notifSocket = null;
    let friendListSocket = null;
    let friendChatSocket = null;
    let gameChatSocket = null;
    let gamePlaySocket = null;
    let gameState = null;
    let playCanvas = null;
    let ctx = null;

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
            document.title = newDocument.title;
            removeExtraScripts();
            loadPageScripts(newDocument);
            attachHandlers();
        })
        .catch(error => console.error('Error fetching content:', error));
    };

    const removeExtraScripts = () => {
        const scriptElements = document.querySelectorAll('script');
        scriptElements.forEach(scriptElement => {
            const src = scriptElement.src;
            if (src && !src.includes('main.js')) {
                scriptElement.parentNode.removeChild(scriptElement);
                loadedScripts.delete(src);
            }
        });
    };

    const loadPageScripts = (newDocument) => {
        const scriptElements = newDocument.querySelectorAll('script');
        scriptElements.forEach(scriptElement => {
            const src = scriptElement.src;
            if (!loadedScripts.has(src) && !src.includes('main.js')) {
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

    const langReload = (lang, isProfileDefault = false) => {
        const endpoint = isProfileDefault 
        ? `/api/profiles/me/lang/${lang}/` 
        : `/api/lang/${lang}/`;

        makeAPIRequest(
            endpoint,
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

    const closeAllWebSockets = () => {
        closeWebSocket(notifSocket);
        closeWebSocket(friendListSocket);
        closeWebSocket(friendChatSocket);
        closeWebSocket(gameChatSocket);
        closeWebSocket(gamePlaySocket);
    };

    const openWebSocket = (path) => {
        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
        const wsUrl = `${wsScheme}://${window.location.host}/ws/${path}`;
        return new WebSocket(wsUrl);
    };

    const openNotifWebSocket = () => {
        notifSocket = openWebSocket('notifs/');

        notifSocket.onopen = () => {
            console.log('Notif WebSocket connection established.');
        };

        notifSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const element = data['element'];
            const notifList = document.getElementById('notifList');
            if (notifList) {
                notifList.innerHTML += element;
            }
            const notifBtn = document.getElementById('notiftoggle');
            if (notifBtn && !notifBtn.checked) {
                const showNotifDot = document.getElementById('showNotifDot');
                if (showNotifDot) {
                    showNotifDot.classList.remove('d-none', 'd-xxl-none');
                }
            }
            const notifDiv = document.getElementById('notifDiv');
            if (notifDiv) {
                notifDiv.classList.remove('rubberBand');
                void notifDiv.offsetWidth;
                notifDiv.classList.add('rubberBand');
            }
        };

        notifSocket.onclose = () => {
            console.log('Notif WebSocket connection closed.');
        };

        notifSocket.onerror = (error) => {
            console.error('Notif WebSocket error:', error);
        };
    };

    const openFriendListWebSocket = () => {
        friendListSocket = openWebSocket(`friends/`);

        friendListSocket.onopen = () => {
            console.log('Friend List WebSocket connection established.');
        };

        friendListSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const element = data['element'];
            // TODO: update friends on status changed
            // const friendList = document.getElementById('friendList');
            // if (friendList) {
            //     friendList.innerHTML += element;
            // }
        };

        friendListSocket.onclose = () => {
            console.log('Friend List WebSocket connection closed.');
        };

        friendListSocket.onerror = (error) => {
            console.error('Friend List WebSocket error:', error);
        };
    };

    const openFriendChatWebSocket = (friendshipId) => {
        friendChatSocket = openWebSocket(`friends/${friendshipId}/`);

        friendChatSocket.onopen = () => {
            console.log('Friend Chat WebSocket connection established.');
        };

        friendChatSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const element = data['element'];
            const sayHiMessage = document.getElementById('templateSayHi');
            if (sayHiMessage) {
                sayHiMessage.remove();
            }
            const messageSection = document.getElementById('messageSection');
            if (messageSection) {
                messageSection.innerHTML += element;
                messageSection.scrollTop = messageSection.scrollHeight;
            }
            // TODO: update last message sent in friend list
        };

        friendChatSocket.onclose = () => {
            console.log('Friend Chat WebSocket connection closed.');
        };

        friendChatSocket.onerror = (error) => {
            console.error('Friend Chat WebSocket error:', error);
        };
    };

    const openGameChatWebSocket = (gameId) => {
        gameChatSocket = openWebSocket(`games/${gameId}/`);

        gameChatSocket.onopen = () => {
            console.log('Game Chat WebSocket connection established.');
        };

        gameChatSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const element = data['element'];
            // TODO: update on player joined/left or message sent/received
            // const playerSection = document.getElementById('playerSection');
            // if (playerSection) {
            //     playerSection.innerHTML += element;
            // }
        };

        gameChatSocket.onclose = () => {
            console.log('Game Chat WebSocket connection closed.');
        };

        gameChatSocket.onerror = (error) => {
            console.error('Game Chat WebSocket error:', error);
        };
    };

    const openGamePlayWebSocket = (gameId) => {
        gamePlaySocket = openWebSocket(`games/${gameId}/play/`);

        gamePlaySocket.onopen = () => {
            console.log('Game Play WebSocket connection established.');
        };

        gamePlaySocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const action = data['action'];
            if (action === 'update_state') {
                gameState = data.game_state;
                renderGame();
            }
        };

        gamePlaySocket.onclose = () => {
            console.log('Game Play WebSocket connection closed.');
        };

        gamePlaySocket.onerror = (error) => {
            console.error('Game Play WebSocket error:', error);
        };
    };

    const renderGame = () => {
        if (!gameState || !playCanvas || !ctx) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#FFFFFF";
        ctx.fillRect(gameState.player1_x, gameState.player1_y, gameState.paddle_width, gameState.paddle_height);
        ctx.fillStyle = "#FFFFFF";
        ctx.fillRect(gameState.player2_x, gameState.player2_y, gameState.paddle_width, gameState.paddle_height);
        ctx.beginPath();
        ctx.arc(gameState.ball_x, gameState.ball_y, gameState.ball_radius, 0, Math.PI * 2);
        ctx.fillStyle = "#FFFFFF";
        ctx.fill();
        ctx.closePath();
    }

    const attachHandlers = () => {
        const path = window.location.pathname;
        const subdirectory = path.split('/')[1];
        if (subdirectory !== 'friends') {
            closeWebSocket(friendListSocket);
        }
        closeWebSocket(friendChatSocket);
        closeWebSocket(gameChatSocket);
        switch (subdirectory) {
            case 'home':
                homePage();
                break;
            case 'games':
                gamesPage();
                break;
            case 'profiles':
                profilesPage();
                break;
            case 'friends':
                friendsPage();
                break;
            case 'settings':
                settingsPage();
                break;
            default:
                console.log(`subdir = ${subdirectory}`);
        }

        setNotifHandlers();

        document.querySelectorAll('a').forEach(anchor => {
            if (anchor.id.startsWith('nav')) {
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
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    if ('redirect' in data) {
                        openNotifWebSocket();
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error(`Error with request to ${event.target.action}:`, error));
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
                closeAllWebSockets();
            });
        }

        const createGameForm = document.getElementById('createGameForm');
        if (createGameForm) {
            createGameForm.addEventListener('submit', (event) => {
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
                    console.log('Game created:', data);
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error('Error creating game:', error));
            });
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
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
        var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl)
        })

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

    const setNotifHandlers = () => {
        const notifBtn = document.getElementById('notiftoggle');
        if (notifBtn) {
            notifBtn.addEventListener('change', (event) => {
                if (notifBtn.checked && notifSocket) {
                    const message = {
                        notification: {
                            command: 'notifs_read'
                        }
                    };
                    notifSocket.send(JSON.stringify(message));
                }
            });
        }

        document.querySelectorAll('.accept-friend-btn').forEach(acceptFriendBtn => {
            acceptFriendBtn.addEventListener('click', (event) => {
                if (notifSocket) {
                    const requestId = acceptFriendBtn.dataset.objectId;
                    fetch(`/api/profiles/me/requests/${requestId}/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Friend request accepted:', data);
                        acceptFriendBtn.parentElement.parentElement.remove();
                    })
                    .catch(error => console.error('Error accepting friend request:', error));
                }
            });
        });

        document.querySelectorAll('.decline-friend-btn').forEach(declineFriendBtn => {
            declineFriendBtn.addEventListener('click', (event) => {
                if (notifSocket) {
                    const requestId = declineFriendBtn.dataset.objectId;
                    fetch(`/api/profiles/me/requests/${requestId}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Friend request declined:', data);
                        declineFriendBtn.parentElement.parentElement.remove();
                    })
                    .catch(error => console.error('Error declining friend request:', error));
                }
            });
        });

        document.querySelectorAll('.accept-game-btn').forEach(acceptGameBtn => {
            acceptGameBtn.addEventListener('click', (event) => {
                if (notifSocket) {
                    const inviteId = acceptGameBtn.dataset.objectId;
                    fetch(`/api/profiles/me/invites/${inviteId}/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Game invite accepted:', data);
                        acceptGameBtn.parentElement.parentElement.remove();
                        if ('redirect' in data) {
                            navigateTo(data.redirect);
                        }
                    })
                    .catch(error => console.error('Error accepting game invite:', error));
                }
            });
        });

        document.querySelectorAll('.decline-game-btn').forEach(declineGameBtn => {
            declineGameBtn.addEventListener('click', (event) => {
                if (notifSocket) {
                    const inviteId = declineGameBtn.dataset.objectId;
                    fetch(`/api/profiles/me/invites/${inviteId}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Game invite declined:', data);
                        declineGameBtn.parentElement.parentElement.remove();
                    })
                    .catch(error => console.error('Error declining game invite:', error));
                }
            });
        });
    };

    const homePage = () => {
        const searchProfileInput = document.getElementById('searchProfileInput');
        if (searchProfileInput) {
            searchProfileInput.addEventListener('keyup', (event) => {
                const profileAlias = searchProfileInput.value;
                if (profileAlias) {
                    // TODO: handle search here -> for example, display dropdown with profiles starting with value
                    // console.log(profileAlias);
                    if (event.key === 'Enter') {
                        fetch(`/api/profiles/search/?alias=${profileAlias}`)
                        .then(response => response.json())
                        .then(data => {
                            console.log('Profiles searched:', data);
                            if (data && 'data' in data) {
                                navigateTo(`/profiles/${data.data[0].id}`);
                            }
                        })
                        .catch(error => console.error('Error searching profile:', error));
                    }
                }
            });
        }

        const searchGameInput = document.getElementById('searchGameInput');
        if (searchGameInput) {
            searchGameInput.addEventListener('keyup', (event) => {
                event.preventDefault();
                const gameName = searchGameInput.value;
                if (gameName) {
                    // TODO: handle search here -> for example, display only games containing value
                    // console.log(gameName);
                    if (event.key === 'Enter') {
                        fetch(`/api/games/search/?name=${alias}`)
                        .then(response => response.json())
                        .then(data => {
                            console.log('Games searched:', data);
                            // TODO: display search result
                        })
                        .catch(error => console.error('Error searching game:', error));
                    }
                }
            });
        }

        document.querySelectorAll('.join-game-btn').forEach(joinGameBtn => {
            joinGameBtn.addEventListener('click', (event) => {
                event.preventDefault();
                fetch(`/api/games/${joinGameBtn.dataset.gameId}/join/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Game joined:', data);
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error('Error searching game:', error));
            });
        });
    }

    const gamesPage = () => {
        const path = window.location.pathname;
        const pathParts = path.split('/');
        if (pathParts.length > 2 && pathParts[2].length == 36) {
            const gameId = pathParts[2];
            openGameChatWebSocket(gameId);

            const inviteRandomBtn = document.getElementById('inviteRandomBtn');
            if (inviteRandomBtn) {
                inviteRandomBtn.addEventListener('click', (event) => {
                    event.preventDefault();
                    fetch('/api/profiles/?excludeself=true')
                    .then(response => response.json())
                    .then(data => {
                        const connectedProfiles = data.filter(profile => profile.status === 'Online');
                        if (connectedProfiles.length === 0) {
                            console.error('No connected profiles available to invite.');
                            return;
                        }
                        const randomIndex = Math.floor(Math.random() * connectedProfiles.length);
                        const profileId = connectedProfiles[randomIndex].id;
                        fetch(`/api/profiles/${profileId}/invites/`, {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Game invite sent:', data);
                        })
                        .catch(error => console.error('Error sending game invite:', error));
                    })
                    .catch(error => console.error('Error getting profiles:', error));
                });
            }

            document.querySelectorAll('.invite-friend-button').forEach(inviteFriendBtn => {
                inviteFriendBtn.addEventListener('click', (event) => {
                    event.preventDefault();
                    const profileId = inviteFriendBtn.dataset.profileId;
                    if (profileId) {
                        fetch(`/api/profiles/${profileId}/invites/`, {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Friend invited:', data);
                            navigateTo(window.location.pathname);
                        })
                        .catch(error => console.error('Error inviting friend:', error));
                    }
                });
            });

            const leaveGameBtn = document.getElementById('leaveGameBtn');
            if (leaveGameBtn) {
                leaveGameBtn.addEventListener('click', (event) => {
                    event.preventDefault();
                    fetch(`/api/games/${gameId}/leave/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Game left:', data);
                        navigateTo('/home/');
                    })
                    .catch(error => console.error('Error leaving game:', error));
                });
            }

            const startGameBtn = document.getElementById('startGameBtn');
            if (startGameBtn) {
                startGameBtn.addEventListener('click', (event) => {
                    event.preventDefault();
                    // TODO
                });
            }

            playCanvas = document.getElementById('playCanvas');
            if (playCanvas) {
                ctx = playCanvas.getContext('2d');
                playCanvas.addEventListener('mousemove', (event) => {
                    const rect = playCanvas.getBoundingClientRect();
                    const y = event.clientY - rect.top;
                    // TODO: send action through websocket
                });

                playCanvas.addEventListener('touchmove', (event) => {
                    event.preventDefault();
                    const touch = event.touches[0];
                    const rect = playCanvas.getBoundingClientRect();
                    const y = touch.clientY - rect.top;
                    // TODO: send action through websocket
                });
            }
        }
    };

    const profilesPage = () => {
        const addFriendBtn = document.getElementById('addFriendBtn');
        if (addFriendBtn) {
            addFriendBtn.addEventListener('click', (event) => {
                event.preventDefault();
                const profileId = addFriendBtn.dataset.profileId;
                if (profileId) {
                    fetch(`/api/profiles/${profileId}/requests/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Friend request sent:', data);
                        navigateTo(window.location.pathname);
                    })
                    .catch(error => console.error('Error sending friend request:', error));
                }
            });
        }

        const removeFriendBtn = document.getElementById('removeFriendBtn');
        if (removeFriendBtn) {
            removeFriendBtn.addEventListener('click', (event) => {
                event.preventDefault();
                const friendshipId = removeFriendBtn.dataset.friendshipId;
                if (friendshipId) {
                    fetch(`/api/profiles/me/friends/${friendshipId}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Friend removed:', data);
                        navigateTo(window.location.pathname);
                    })
                    .catch(error => console.error('Error removing friend:', error));
                }
            });
        }

        const blockProfileBtn = document.getElementById('blockProfileBtn');
        if (blockProfileBtn) {
            blockProfileBtn.addEventListener('click', (event) => {
                event.preventDefault();
                const profileId = blockProfileBtn.dataset.profileId;
                if (profileId) {
                    fetch(`/api/profiles/${profileId}/blocks/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Profile blocked:', data);
                        navigateTo(window.location.pathname);
                    })
                    .catch(error => console.error('Error blocking profile:', error));
                }
            });
        }

        const unblockProfileBtn = document.getElementById('unblockProfileBtn');
        if (unblockProfileBtn) {
            unblockProfileBtn.addEventListener('click', (event) => {
                event.preventDefault();
                const blockId = unblockProfileBtn.dataset.blockId;
                if (blockId) {
                    fetch(`/api/profiles/me/blocks/${blockId}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Profile unblocked:', data);
                        navigateTo(window.location.pathname);
                    })
                    .catch(error => console.error('Error unblocking profile:', error));
                }
            });
        }
    }

    const friendsPage = () => {
        openFriendListWebSocket();

        const searchFriendInput = document.getElementById('searchFriendInput');
        if (searchFriendInput) {
            searchFriendInput.addEventListener('keyup', (event) => {
                const friendAlias = searchFriendInput.value;
                if (friendAlias) {
                    // TODO: handle search here -> for example, scroll to alias starting with value
                    if (event.key === 'Enter') {
                        console.log(friendAlias);
                        searchFriendInput.value = '';
                    }
                }
            });
        }

        const path = window.location.pathname;
        const pathParts = path.split('/');
        if (pathParts.length > 2 && pathParts[2].length == 36) {
            const friendshipId = pathParts[2];
            openFriendChatWebSocket(friendshipId);

            // TODO: remove red dot on friend selected

            const messageSection = document.getElementById('messageSection');
            if (messageSection) {
                messageSection.scrollTop = messageSection.scrollHeight;
            }

            const blockFriendBtn = document.getElementById('blockFriendBtn');
            if (blockFriendBtn) {
                blockFriendBtn.addEventListener('click', (event) => {
                    event.preventDefault();
                    const profileId = blockFriendBtn.dataset.profileId;
                    if (profileId) {
                        fetch(`/api/profiles/${profileId}/blocks/`, {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Friend blocked:', data);
                            navigateTo(window.location.pathname);
                        })
                        .catch(error => console.error('Error blocking friend:', error));
                    }
                });
            }

            const unblockFriendBtn = document.getElementById('unblockFriendBtn');
            if (unblockFriendBtn) {
                unblockFriendBtn.addEventListener('click', (event) => {
                    event.preventDefault();
                    const blockId = unblockFriendBtn.dataset.blockId;
                    if (blockId) {
                        fetch(`/api/profiles/me/blocks/${blockId}/`, {
                            method: 'DELETE',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Friend unblocked:', data);
                            navigateTo(window.location.pathname);
                        })
                        .catch(error => console.error('Error unblocking friend:', error));
                    }
                });
            }

            const removeFriendBtn = document.getElementById('removeFriendBtn');
            if (removeFriendBtn) {
                removeFriendBtn.addEventListener('click', (event) => {
                    event.preventDefault();
                    const friendshipId = removeFriendBtn.dataset.friendshipId;
                    if (friendshipId) {
                        fetch(`/api/profiles/me/friends/${friendshipId}/`, {
                            method: 'DELETE',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Friend removed:', data);
                            navigateTo('/friends/');
                        })
                        .catch(error => console.error('Error removing friend:', error));
                    }
                });
            }

            const inviteFriendBtn = document.getElementById('inviteFriendBtn');
            if (inviteFriendBtn) {
                inviteFriendBtn.addEventListener('click', (event) => {
                    event.preventDefault();
                    const profileId = inviteFriendBtn.dataset.profileId;
                    if (profileId) {
                        fetch(`/api/profiles/${profileId}/invites/`, {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Friend invited:', data);
                            // MAYBE: add something to indicate successful invitation
                        })
                        .catch(error => console.error('Error inviting friend:', error));
                    }
                });
            }

            const chatForm = document.getElementById('chatForm');
            if (chatForm) {
                chatForm.addEventListener('submit', (event) => {
                    event.preventDefault();
                    const formData = new FormData(event.target);
                    const friendshipId = chatForm.dataset.friendshipId;
                    fetch(`/api/profiles/me/friends/${friendshipId}/messages/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                        body: formData,
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data);
                        const chatInput = document.getElementById('chatInput');
                        if (chatInput) {
                            chatInput.value = '';
                        }
                    })
                    .catch(error => console.error(`Error sending message to friend:`, error));
                });
            }
        }
    };

    const settingsPage = () => {
        const changeAliasForm = document.getElementById('changeAliasForm');
        if (changeAliasForm) {
            changeAliasForm.addEventListener('submit', (event) => {
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
                    const changeAliasErrorMsg = document.getElementById('changeAliasErrorMsg');
                    if (data) {
                        if ('error' in data) {
                            if (changeAliasErrorMsg) {
                                changeAliasErrorMsg.classList.remove('d-none', 'd-xxl-none');
                            }
                        }
                        if ('redirect' in data) {
                            if (changeAliasErrorMsg) {
                                changeAliasErrorMsg.classList.add('d-none', 'd-xxl-none');
                            }
                            navigateTo(data.redirect);
                        }
                    }
                })
                .catch(error => console.error('Error changing alias:', error));
            });
        }

        document.querySelectorAll('a').forEach(anchor => {
            if (anchor.id.startsWith('changeAvatar') || anchor.id.startsWith('unlinkFortytwo')) {
                anchor.addEventListener('click', (e) => {
                    e.preventDefault();
                    makeAPIRequest(
                        anchor.href,
                        'POST',
                    );
                });
            } else if (anchor.id.startsWith('changeDefaultLang')) {
                anchor.addEventListener('click', (e) => {
                    const idParts = anchor.id.split('_');
                    if (idParts.length > 1) {
                        const lang = idParts[1];
                        langReload(lang, true);
                    }
                });
            }
        });

        const uploadAvatarInput = document.getElementById('uploadAvatarInput');
        if (uploadAvatarInput) {
            uploadAvatarInput.addEventListener('change', (e) => {
                console.log("HERE");
                if (e.target.files.length > 0) {
                    const formData = new FormData();
                    const imageFile = e.target.files[0];
                    formData.append('avatar', imageFile);
                    fetch('/api/profiles/me/avatar/', {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                        body: formData,
                    })
                    .then(response => {
                        const uploadAvatarErrorMsg = document.getElementById('uploadAvatarErrorMsg');
                        if (uploadAvatarErrorMsg) {
                            if (response.ok) {
                                uploadAvatarErrorMsg.classList.add('d-none', 'd-xxl-none');
                            } else {
                                uploadAvatarErrorMsg.classList.remove('d-none', 'd-xxl-none');
                            }
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data && 'redirect' in data) {
                            navigateTo(data.redirect);
                        }
                    })
                    .catch(error => console.error('Error changing avatar:', error));
                }
            });
        }

        const changeEmailBtn = document.getElementById('changeEmailBtn');
        if (changeEmailBtn) {
            changeEmailBtn.addEventListener('click', (event) => {
                event.preventDefault();
                makeAPIRequest(
                    '/api/profiles/me/email/',
                    'POST',
                );
            });
        }

        const changePasswordBtn = document.getElementById('changePasswordBtn');
        if (changePasswordBtn) {
            changePasswordBtn.addEventListener('click', (event) => {
                event.preventDefault();
                makeAPIRequest(
                    '/api/profiles/me/password/',
                    'POST',
                );
            });
        }

        const deleteAccountForm = document.getElementById('deleteAccountForm');
        if (deleteAccountForm) {
            deleteAccountForm.addEventListener('submit', (event) => {
                event.preventDefault();
                const formData = new FormData(event.target);
                fetch(event.target.action, {
                    method: 'DELETE',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    const deleteAccountErrorMsg = document.getElementById('deleteAccountErrorMsg');
                    if (data) {
                        if ('error' in data) {
                            if (deleteAccountErrorMsg) {
                                deleteAccountErrorMsg.classList.remove('d-none', 'd-xxl-none');
                            }
                        }
                        if ('redirect' in data) {
                            if (deleteAccountErrorMsg) {
                                deleteAccountErrorMsg.classList.add('d-none', 'd-xxl-none');
                            }
                            closeAllWebSockets();
                            navigateTo(data.redirect);
                        }
                    }
                })
                .catch(error => console.error('Error deleting account:', error));
            });
        }

        document.querySelectorAll('.remove-block-btn').forEach(removeBlockBtn => {
            removeBlockBtn.addEventListener('click', (event) => {
                event.preventDefault();
                const blockId = removeBlockBtn.dataset.blockId;
                if (blockId) {
                    fetch(`/api/profiles/me/blocks/${blockId}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Friend unblocked:', data);
                        navigateTo(window.location.pathname);
                    })
                    .catch(error => console.error('Error unblocking friend:', error));
                }
            });
        });
    };
    
    window.addEventListener('popstate', renderPage);
    window.addEventListener('pushState', renderPage);
    window.addEventListener('replaceState', renderPage);
    
    attachHandlers();
});