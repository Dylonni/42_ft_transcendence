document.addEventListener("DOMContentLoaded", () => {
    const contentDiv = document.getElementById('content');
    let errorModal = null;
    let errorBsModal = null;
    let errorModalMsg = null;
    let notifSocket = null;
    let friendListSocket = null;
    let friendChatSocket = null;
    let gameChatSocket = null;
    let gamePlaySocket = null;

    let showCanvas = false;
    let lastState = null;
    let currentState = null;
    let lastTimestamp = 0;
    let currentTimestamp = 0;

    let player = null;
    let direction = 0;
    let keyDown = 0;
    let isMouseDown = false;
    let mouseDown = 0;
    let mouseY = 0;
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
        let search = window.location.search;
        fetch(`${path}${search}`, {
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
                if (node.nodeName.toLowerCase() !== 'script') {
                    contentDiv.appendChild(node.cloneNode(true));
                }
            });
            document.title = newDocument.title;
            attachHandlers();
            initializeBsElements();
        })
        .catch(error => console.error('Error fetching content:', error));
    };

    const initializeBsElements = () => {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl,  {trigger: 'hover'}));
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
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
            if (data.element) {
                const notifList = document.getElementById('notifList');
                if (notifList) {
                    notifList.innerHTML += data.element;
                    setNotifHandlers(); // MAYBE: optimize
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
            } else if (data.notif_list) {
                const notifList = document.getElementById('notifList');
                if (notifList) {
                    notifList.innerHTML = data.notif_list;
                    setNotifHandlers(); // MAYBE: optimize
                }
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
            if (data.friend_list) {
                const friendList = document.getElementById('friendList');
                if (friendList) {
                    friendList.innerHTML = data.friend_list;
                    document.querySelectorAll('a').forEach(anchor => {
                        if (anchor.id.startsWith('navFriendChat')) {
                            anchor.addEventListener('click', (event) => {
                                event.preventDefault();
                                navigateTo(anchor.href);
                            });
                        }
                    });
                }
            }
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
            if (data.element) {
                const sayHiMessage = document.getElementById('templateSayHi');
                if (sayHiMessage) {
                    sayHiMessage.remove();
                }
                const messageSection = document.getElementById('messageSection');
                if (messageSection) {
                    messageSection.innerHTML += data.element;
                    messageSection.scrollTop = messageSection.scrollHeight;
                }
                friendChatSocket.send(JSON.stringify({'read': true}));
            }
            if (data.friend_header) {
                const friendHeaderDiv = document.getElementById('friendHeaderDiv');
                if (friendHeaderDiv) {
                    friendHeaderDiv.innerHTML = data.friend_header;
                }
            }
            if (data.section) {
                const messageSection = document.getElementById('messageSection');
                if (messageSection) {
                    messageSection.innerHTML = data.section;
                }
            }
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
            if (data.header) {
                const playerSection = document.getElementById('playerSection');
                if (playerSection) {
                    playerSection.innerHTML = data.header;
                }
            }
            if (data.message) {
                const gameMsgDiv = document.getElementById('gameMsgDiv');
                if (gameMsgDiv) {
                    gameMsgDiv.innerHTML += data.message;
                    gameMsgDiv.scrollTop = gameMsgDiv.scrollHeight;
                }
            }
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
            if (data.game_state) {
                lastState = currentState;
                lastTimestamp = currentTimestamp;
                currentState = data.game_state;
                currentTimestamp = performance.now();
                if (!showCanvas && currentState.game_running) {
                    const pongDiv = document.getElementById('pongDiv');
                    if (pongDiv) {
                        pongDiv.classList.remove('d-none', 'd-xxl-none');
                    }
                    const gameInfoDiv = document.getElementById('gameInfoDiv');
                    if (gameInfoDiv) {
                        gameInfoDiv.classList.add('d-none', 'd-xxl-none');
                    }
                    gameLoop();
                    showCanvas = true;
                }
                if (showCanvas && !currentState.game_running) {
                    ctx.clearRect(0, 0, playCanvas.width, playCanvas.height);
                    const pongDiv = document.getElementById('pongDiv');
                    if (pongDiv) {
                        pongDiv.classList.add('d-none', 'd-xxl-none');
                    }
                    const gameInfoDiv = document.getElementById('gameInfoDiv');
                    if (gameInfoDiv) {
                        gameInfoDiv.classList.remove('d-none', 'd-xxl-none');
                    }
                    showCanvas = false;
                }
            } else if (data.countdown) {
                const countdownSpan = document.getElementById('countdownSpan');
                if (countdownSpan) {
                    countdownSpan.textContent = data.countdown + ' seconds';
                }
            } else if (data.ready) {
                const readyDiv = document.getElementById('readyDiv');
                if (readyDiv) {
                    readyDiv.innerHTML = data.ready;
                }
            } else if (data.redirect) {
                navigateTo(data.redirect);
            } else if (data.header) {
                const playerSection = document.getElementById('playerSection');
                if (playerSection) {
                    playerSection.innerHTML = data.header;
                }
            }
        };

        gamePlaySocket.onclose = () => {
            console.log('Game Play WebSocket connection closed.');
        };

        gamePlaySocket.onerror = (error) => {
            console.error('Game Play WebSocket error:', error);
        };

        const interpolateState = (state1, state2, t) => {
            return {
                player1_y: state1.player1_y + (state2.player1_y - state1.player1_y) * t,
                player2_y: state1.player2_y + (state2.player2_y - state1.player2_y) * t,
                ball_x: state1.ball_x + (state2.ball_x - state1.ball_x) * t,
                ball_y: state1.ball_y + (state2.ball_y - state1.ball_y) * t,
                player1_score: state1.player1_score,
                player2_score: state1.player2_score,
                // Any other game state variables
                game_running: state1.game_running,
                paddle_height: state1.paddle_height,
                ball_size: state1.ball_size,
                countdown: state1.countdown,
            };
        };

        const gameLoop = () => {
            if (currentTimestamp && lastTimestamp && (currentTimestamp !== lastTimestamp)) {
                const now = performance.now();
                const interpolationFactor = Math.min(1, (now - lastTimestamp) / (currentTimestamp - lastTimestamp));
                let stateToRender;
                if (lastState && currentState) {
                    stateToRender = interpolateState(lastState, currentState, interpolationFactor);
                } else {
                    stateToRender = currentState || lastState;
                }
                renderGame(stateToRender);
            } else {
                renderGame(currentState || lastState);
            }
            requestAnimationFrame(gameLoop);
        };

        const renderGame = (stateToRender) => {
            if (!stateToRender || !playCanvas || !ctx) return;

            ctx.clearRect(0, 0, playCanvas.width, playCanvas.height);

            ctx.fillStyle = 'white';
            ctx.fillRect(0, stateToRender.player1_y, 10, stateToRender.paddle_height);
            ctx.fillRect(playCanvas.width - 10, stateToRender.player2_y, 10, stateToRender.paddle_height);

            ctx.fillRect(stateToRender.ball_x, stateToRender.ball_y, stateToRender.ball_size, stateToRender.ball_size);

            for (let i = 0; i < playCanvas.height; i += 20) {
                ctx.fillRect(playCanvas.width / 2 - 1, i, 2, 10);
            }

            ctx.font = '20px Arial';
            ctx.fillText(stateToRender.player1_score, playCanvas.width / 4, 30);
            ctx.fillText(stateToRender.player2_score, 3 * playCanvas.width / 4, 30);

            if (stateToRender.countdown) {
                ctx.font = '50px Arial';
                ctx.fillStyle = 'white';
                ctx.textAlign = 'center';
                ctx.fillText(stateToRender.countdown, playCanvas.width / 2, playCanvas.height / 2);
            }
        };
    };

    const attachHandlers = () => {
        const path = window.location.pathname;
        errorModal = document.getElementById('errorModal');
        errorBsModal = new bootstrap.Modal(errorModal);
        errorModalMsg = document.getElementById('errorModalMsg');
        const subdirectory = path.split('/')[1];
        if (subdirectory !== 'friends') {
            closeWebSocket(friendListSocket);
        }
        closeWebSocket(friendChatSocket);
        closeWebSocket(gameChatSocket);
        closeWebSocket(gamePlaySocket);
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
        }

        setNotifHandlers();
        authPages();
        
        const inputs = document.querySelectorAll(".otp-field > input");
        const button = document.getElementById("verifyBtn"); 
        if (inputs.length > 0) {
            window.addEventListener("load", () => inputs[0].focus());  
            if (button) {
                button.setAttribute("disabled", "disabled");
            }
            inputs[0].addEventListener("paste", function (event) {
                event.preventDefault();
                const pastedValue = (event.clipboardData || window.clipboardData).getData(
                    "text"
                );
                const otpLength = inputs.length;
    
                for (let i = 0; i < otpLength; i++) {
                    if (i < pastedValue.length) {
                        inputs[i].value = pastedValue[i];
                        inputs[i].removeAttribute("disabled");
                        inputs[i].focus;
                    } else {
                        inputs[i].value = ""; // Clear any remaining inputs
                        inputs[i].focus;
                    }
                }
            });
    
            inputs[inputs.length - 1].addEventListener("keyup", (event) => {
                if (event.key === "Enter") {
                    button.click();
                }
            });
    
            inputs.forEach((input, index1) => {
            input.addEventListener("keyup", (e) => {
                    const currentInput = input;
                    const nextInput = input.nextElementSibling;
                    const prevInput = input.previousElementSibling;
    
                    if (currentInput.value.length > 1) {
                        currentInput.value = "";
                        return;
                    }
    
                    if ( nextInput && nextInput.hasAttribute("disabled") && currentInput.value !== "") {
                        nextInput.removeAttribute("disabled");
                        nextInput.focus();
                    }
    
                    if (e.key === "Backspace") {
                        inputs.forEach((input, index2) => {
                            if (index1 <= index2 && prevInput) {
                                input.setAttribute("disabled", true);
                                input.value = "";
                                prevInput.focus();
                            }
                        });
                    }
    
                    button.classList.remove("active");
                    button.setAttribute("disabled", "disabled");
    
                    const inputsNo = inputs.length;
                    if (!inputs[inputsNo - 1].disabled && inputs[inputsNo - 1].value !== "") {
                        button.classList.add("active");
                        button.removeAttribute("disabled");
    
                        return;
                    }
                });
            });
        }

        const enableTwoFaBtn = document.getElementById('enableTwoFaBtn');
        if (enableTwoFaBtn) {
            enableTwoFaBtn.addEventListener('click', (event) => {
                event.preventDefault();
                fetch('/api/profiles/me/twofa/', {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error(`Error disabling 2FA:`, error));
            });
        }

        const disableTwoFaBtn = document.getElementById('disableTwoFaBtn');
        if (disableTwoFaBtn) {
            disableTwoFaBtn.addEventListener('click', (event) => {
                event.preventDefault();
                fetch('/api/profiles/me/twofa/', {
                    method: 'PUT',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error(`Error disabling 2FA:`, error));
            });
        }

        const pongCanvas = document.getElementById('pongCanvas');
        if (pongCanvas) {
            pongGame();
        }

        document.querySelectorAll('a').forEach(anchor => {
            if (anchor.id.startsWith('nav')) {
                anchor.addEventListener('click', (event) => {
                    event.preventDefault();
                    navigateTo(anchor.href);
                });
            } else if (anchor.id.startsWith('changeLang')) {
                anchor.addEventListener('click', (event) => {
                    event.preventDefault();
                    const idParts = anchor.id.split('_');
                    if (idParts.length > 1) {
                        const lang = idParts[1];
                        langReload(lang);
                    }
                });
            }
        });

        const verifyBtn = document.getElementById('verifyBtn');
        if (verifyBtn) {
            verifyBtn.addEventListener('click', (event) => {
                event.preventDefault();
                let code = '';
                document.querySelectorAll(".otp-field > input").forEach(inputField => {
                    code += inputField.value;
                });
                fetch(verifyBtn.dataset.target, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({'code': code}),
                })
                .then(response => response.json())
                .then(data => {
                    if ('error' in data) {
                        if (errorBsModal) {
                            errorModalMsg.textContent = data.error;
                            errorBsModal.show();
                        }
                    }
                    if ('redirect' in data) {
                        if (data.redirect === '/home/') {
                            openNotifWebSocket();
                            navigateTo(data.redirect);
                        }
                    }
                })
                .catch(error => console.error(`Error with request to ${event.target.action}:`, error));
            })
        }

        const resetPasswordForm = document.getElementById('resetPasswordForm');
        if (resetPasswordForm) {
            resetPasswordForm.addEventListener('submit', (event) => {
                event.preventDefault();
                const formData = new FormData(event.target);
                fetch(event.target.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error('Error resetting password:', error));
            });
        }

        const changePasswordForm = document.getElementById('changePasswordForm');
        if (changePasswordForm) {
            changePasswordForm.addEventListener('submit', (event) => {
                event.preventDefault();
                const formData = new FormData(event.target);
                fetch(event.target.action, {
                    method: 'PUT',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error('Error changing password:', error));
            });
        }

        const changeEmailForm = document.getElementById('changeEmailForm');
        if (changeEmailForm) {
            changeEmailForm.addEventListener('submit', (event) => {
                event.preventDefault();
                const formData = new FormData(event.target);
                fetch(event.target.action, {
                    method: 'PUT',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error('Error changing email:', error));
            });
        }

        const logoutBtn = document.getElementById('logoutBtn');
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

        const playerLimitInput = document.getElementById('playerLimitInput');
        if (playerLimitInput) {
            playerLimitInput.addEventListener('input', (event) => {
                const playerLimitSpan = document.getElementById('playerLimitSpan');
                if (playerLimitSpan) {
                    playerLimitSpan.textContent = event.target.value;
                }
            });
        }

        const winScoreInput = document.getElementById('winScoreInput');
        if (winScoreInput) {
            winScoreInput.addEventListener('input', (event) => {
                const winScoreSpan = document.getElementById('winScoreSpan');
                if (winScoreSpan) {
                    winScoreSpan.textContent = event.target.value;
                }
            });
        }

        const createGameForm = document.getElementById('createGameForm');
        if (createGameForm) {
            createGameForm.addEventListener('submit', (event) => {
                event.preventDefault();
                const formData = new FormData(event.target);
                if (createGameForm.hasAttribute('data-game-type')) {
                    saveGameSettings(formData);
                    navigateTo('/play/');
                } else {
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
                            navigateTo(data.redirect);
                        }
                    })
                    .catch(error => console.error('Error creating game:', error));
                }
            });
        }
    };

    const setNotifHandlers = () => {
        const notifBtn = document.getElementById('notiftoggle');
        if (notifBtn) {
            if (!notifBtn.dataset.hasListener) {
                notifBtn.addEventListener('change', (event) => {
                    if (notifBtn.checked && notifSocket) {
                        const message = {
                            notification: {
                                command: 'notifs_read'
                            }
                        };
                        notifSocket.send(JSON.stringify(message));
                        const showNotifDot = document.getElementById('showNotifDot');
                        if (showNotifDot) {
                            showNotifDot.classList.add('d-none', 'd-xxl-none');
                        }
                    }
                });
            }
            notifBtn.dataset.hasListener = 'true';
        }

        document.querySelectorAll('.accept-friend-btn').forEach(acceptFriendBtn => {
            if (!acceptFriendBtn.dataset.hasListener) {
                acceptFriendBtn.addEventListener('click', (event) => {
                    const requestId = acceptFriendBtn.dataset.objectId;
                    if (requestId) {
                        fetch(`/api/profiles/me/requests/${requestId}/`, {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            acceptFriendBtn.parentElement.parentElement.remove();
                        })
                        .catch(error => console.error('Error accepting friend request:', error));
                    }
                });
                acceptFriendBtn.dataset.hasListener = 'true';
            }
        });

        document.querySelectorAll('.decline-friend-btn').forEach(declineFriendBtn => {
            if (!declineFriendBtn.dataset.hasListener) {
                declineFriendBtn.addEventListener('click', (event) => {
                    const requestId = declineFriendBtn.dataset.objectId;
                    if (requestId) {
                        fetch(`/api/profiles/me/requests/${requestId}/`, {
                            method: 'DELETE',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            declineFriendBtn.parentElement.parentElement.remove();
                        })
                        .catch(error => console.error('Error declining friend request:', error));
                    }
                });
                declineFriendBtn.dataset.hasListener = 'true';
            }
        });

        document.querySelectorAll('.accept-game-btn').forEach(acceptGameBtn => {
            if (!acceptGameBtn.dataset.hasListener) {
                acceptGameBtn.addEventListener('click', (event) => {
                    const inviteId = acceptGameBtn.dataset.objectId;
                    if (inviteId) {
                        fetch(`/api/profiles/me/invites/${inviteId}/`, {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            acceptGameBtn.parentElement.parentElement.remove();
                            if ('redirect' in data) {
                                navigateTo(data.redirect);
                            }
                        })
                        .catch(error => console.error('Error accepting game invite:', error));
                    }
                });
                acceptGameBtn.dataset.hasListener = 'true';
            }
        });

        document.querySelectorAll('.decline-game-btn').forEach(declineGameBtn => {
            if (!declineGameBtn.dataset.hasListener) {
                declineGameBtn.addEventListener('click', (event) => {
                    const inviteId = declineGameBtn.dataset.objectId;
                    if (inviteId) {
                        fetch(`/api/profiles/me/invites/${inviteId}/`, {
                            method: 'DELETE',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            declineGameBtn.parentElement.parentElement.remove();
                        })
                        .catch(error => console.error('Error declining game invite:', error));
                    }
                });
                declineGameBtn.dataset.hasListener = 'true';
            }
        });
    };

    const authPages = () => {
        const showPasswordBtn = document.getElementById('showPassword');
        if (showPasswordBtn) {
            showPasswordBtn.addEventListener('click', (event) => {
                const showInput = document.getElementById('floatingPassword-register');
                if (showInput) {
                    if (showInput.type == 'password'){
                        showInput.type = 'text';
                    } else {
                        showInput.type = 'password';
                    }
                }
            });
        }

        const acceptTerms = document.getElementById('tosAccept');
        const registerBtn = document.getElementById('registerBtn');
        if (registerBtn && acceptTerms){
            acceptTerms.addEventListener('change', (event) => {  
                    registerBtn.classList.toggle("disabled");
            });
        }

        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (event) => {
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
                    if ('error' in data) {
                        if (errorBsModal) {
                            errorModalMsg.textContent = data.error;
                            errorBsModal.show();
                        }
                    }
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error(`Error with request to ${event.target.action}:`, error));
            });
        }

        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (event) => {
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
                    if ('error' in data) {
                        if (errorBsModal) {
                            errorModalMsg.textContent = data.error;
                            errorBsModal.show();
                        }
                    }
                    if ('redirect' in data) {
                        if (data.redirect === '/home/') {
                            openNotifWebSocket();
                        }
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error(`Error with request to ${event.target.action}:`, error));
            });
        }
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
                            if ('error' in data) {
                                if (errorBsModal) {
                                    errorModalMsg.textContent = data.error;
                                    errorBsModal.show();
                                }
                            }
                            if ('data' in data) {
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
                const gameId = joinGameBtn.dataset.gameId;
                if (gameId) {
                    fetch(`/api/games/${gameId}/join/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        if ('error' in data) {
                            if (errorBsModal) {
                                errorModalMsg.textContent = data.error;
                                errorBsModal.show();
                            }
                        }
                        if ('redirect' in data) {
                            navigateTo(data.redirect);
                        }
                    })
                    .catch(error => console.error('Error searching game:', error));
                }
            });
        });
    }

    const gamesPage = () => {
        const path = window.location.pathname;
        const pathParts = path.split('/');
        if (pathParts.length > 2 && pathParts[2].length == 36) {
            const gameId = pathParts[2];
            openGameChatWebSocket(gameId);
            openGamePlayWebSocket(gameId);

            new EmojiPicker({
                trigger: [
                    {
                        selector: ['.emojiPickerBtn'],
                        insertInto: '.gameChatInput'
                    },
                ],
                closeButton: true,
                closeOnSelect: true,
            });

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

            document.querySelectorAll('.invite-friend-btn').forEach(inviteFriendBtn => {
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
                        navigateTo('/home/');
                    })
                    .catch(error => console.error('Error leaving game:', error));
                });
            }

            const startGameBtn = document.getElementById('startGameBtn');
            if (startGameBtn) {
                startGameBtn.addEventListener('click', (event) => {
                    event.preventDefault();
                    fetch(`/api/games/${gameId}/start/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (gamePlaySocket) {
                            const message = {action: 'next_round'};
                            gamePlaySocket.send(JSON.stringify(message));
                        }
                    })
                    .catch(error => console.error('Error starting game:', error));
                });
            }

            playCanvas = document.getElementById('playCanvas');
            if (playCanvas) {
                ctx = playCanvas.getContext('2d');
                document.addEventListener('keydown', (event) => {
                    if (playCanvas) {
                        if (event.key === 'z' || event.key === 'ArrowUp') {
                            direction = -1;
                            sendKeyDirection();
                        } else if (event.key === 's' || event.key === 'ArrowDown') {
                            direction = 1;
                            sendKeyDirection();
                        }
                    }
                });

                playCanvas.addEventListener('mousedown', (event) => {
                    const rect = playCanvas.getBoundingClientRect();
                    mouseY = event.clientY - rect.top;
                    isMouseDown = true;
                    mouseDown = setInterval(sendMousePosition, 16);
                });

                playCanvas.addEventListener('mousemove', (event) => {
                    if (isMouseDown) {
                        const rect = playCanvas.getBoundingClientRect();
                        mouseY = event.clientY - rect.top;
                    }
                });

                playCanvas.addEventListener('mouseup', () => {
                    isMouseDown = false;
                    clearInterval(mouseDown);
                });

                playCanvas.addEventListener('mouseleave', () => {
                    isMouseDown = false;
                    clearInterval(mouseDown);
                });

                const sendKeyDirection = () => {
                    if (gamePlaySocket) {
                        gamePlaySocket.send(JSON.stringify({
                            action: 'move_key',
                            direction: direction,
                            player: player,
                        }));
                    }
                };

                const sendMousePosition = () => {
                    if (gamePlaySocket) {
                        gamePlaySocket.send(JSON.stringify({
                            action: 'move_mouse',
                            position: mouseY,
                            player: player,
                        }));
                    }
                };

                playCanvas.addEventListener('touchmove', (event) => {
                    event.preventDefault();
                    const touch = event.touches[0];
                    const rect = playCanvas.getBoundingClientRect();
                    mouseY = touch.clientY - rect.top;
                    sendMousePosition();
                });
            }

            const gameChatForm = document.getElementById('gameChatForm');
            if (gameChatForm) {
                gameChatForm.addEventListener('submit', (event) => {
                    event.preventDefault();
                    const gameId = gameChatForm.dataset.gameId;
                    if (gameId) {
                        const formData = new FormData(event.target);
                        fetch(`/api/games/${gameId}/messages/`, {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                            body: formData,
                        })
                        .then(response => response.json())
                        .then(data => {
                            const gameChatInput = document.getElementById('gameChatInput');
                            if (gameChatInput) {
                                gameChatInput.value = '';
                            }
                        })
                        .catch(error => console.error(`Error sending message to game:`, error));
                    }
                });

                const gameChatBtn = document.getElementById('gameChatBtn');
                if (gameChatBtn) {
                    gameChatBtn.addEventListener('click', (event) => {
                        event.preventDefault();
                        const gameId = gameChatForm.dataset.gameId;
                        if (gameId) {
                            const formData = new FormData(gameChatForm);
                            fetch(`/api/games/${gameId}/messages/`, {
                                method: 'POST',
                                headers: {
                                    'X-Requested-With': 'XMLHttpRequest',
                                },
                                body: formData,
                            })
                            .then(response => response.json())
                            .then(data => {
                                const gameChatInput = document.getElementById('gameChatInput');
                                if (gameChatInput) {
                                    gameChatInput.value = '';
                                }
                            })
                            .catch(error => console.error(`Error sending message to game:`, error));
                        }
                    });
                }
            }
        }
    };

    const profilesPage = () => {
        const winrateCanvas = document.getElementById('winRate');
        if (winrateCanvas) {
            const data = [winrateCanvas.dataset.won, winrateCanvas.dataset.lost];
            new Chart(
                winrateCanvas,
                {
                    type: 'pie',
                    data: {
                        labels: [
                            'Won',
                            'Lost',
                        ],
                        datasets: [{
                            label: 'Winrate',
                            data: data,
                        }],
                    },
                }
            );
        }

        let points;
        let path = window.location.pathname;
        if (path.endsWith('/')) {
            path = '/api' + path + 'elos/';
        } else {
            path = '/api' + path + '/elos/';
        }
        fetch(`${path}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => response.json())
        .then(data => {
            if ('points' in data) {
                points = data.points;
                new Chart(
                    document.getElementById('lastElos'),
                    {
                        type: 'line',
                        data: {
                            labels: points.map(row => row.index),
                            datasets: [{
                                label: "Elo",
                                data: points.map(row => row.elo),
                            }],
                        },
                    }
                );
            }
        })
        .catch(error => console.error('Error getting last elos:', error));
        
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
                        // if ('error' in data) {
                        //     if (errorBsModal) {
                        //         errorModalMsg.textContent = data.error;
                        //         errorBsModal.show();
                        //     }
                        // }
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
        
        new EmojiPicker({
            trigger: [
                {
                    selector: ['.emojiPick'],
                    insertInto: '.chatInput' // If there is only one '.selector', than it can be used without array
                },
            ],
            closeButton: true,
            closeOnSelect: true,
        });

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
                    const friendshipId = chatForm.dataset.friendshipId;
                    if (friendshipId) {
                        const formData = new FormData(event.target);
                        fetch(`/api/profiles/me/friends/${friendshipId}/messages/`, {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                            body: formData,
                        })
                        .then(response => response.json())
                        .then(data => {
                            const chatInput = document.getElementById('chatInput');
                            if (chatInput) {
                                chatInput.value = '';
                            }
                        })
                        .catch(error => console.error(`Error sending message to friend:`, error));
                    }
                });

                const chatBtn = document.getElementById('chatBtn');
                if (chatBtn) {
                    chatBtn.addEventListener('click', (event) => {
                        event.preventDefault();
                        const friendshipId = chatForm.dataset.friendshipId;
                        if (friendshipId) {
                            const formData = new FormData(chatForm);
                            fetch(`/api/profiles/me/friends/${friendshipId}/messages/`, {
                                method: 'POST',
                                headers: {
                                    'X-Requested-With': 'XMLHttpRequest',
                                },
                                body: formData,
                            })
                            .then(response => response.json())
                            .then(data => {
                                const chatInput = document.getElementById('chatInput');
                                if (chatInput) {
                                    chatInput.value = '';
                                }
                            })
                            .catch(error => console.error(`Error sending message to friend:`, error));
                        }
                    });
                }
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
                    if ('error' in data) {
                        if (errorBsModal) {
                            errorModalMsg.textContent = data.error;
                            errorBsModal.show();
                        }
                    }
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
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
                    .then(response => response.json())
                    .then(data => {
                        if ('error' in data) {
                            if (errorBsModal) {
                                errorModalMsg.textContent = data.error;
                                errorBsModal.show();
                            }
                        }
                        if ('redirect' in data) {
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
                fetch('/api/profiles/me/email/', {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error('Error changing email:', error));
            });
        }

        const changePasswordBtn = document.getElementById('changePasswordBtn');
        if (changePasswordBtn) {
            changePasswordBtn.addEventListener('click', (event) => {
                event.preventDefault();
                fetch('/api/profiles/me/password/', {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if ('redirect' in data) {
                        navigateTo(data.redirect);
                    }
                })
                .catch(error => console.error('Error changing password:', error));
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

const saveGameSettings = (formData) => {
    const formDataObj = {};
    formData.forEach((value, key) => {
        formDataObj[key] = value;
    });
    localStorage.setItem('winScore', formDataObj.win_score);
    localStorage.setItem('ballSize', formDataObj.ball_size);
    localStorage.setItem('ballSpeed', formDataObj.ball_speed);
    localStorage.setItem('paddleSize', formDataObj.paddle_size);
    localStorage.setItem('aiDifficulty', formDataObj.ai_difficulty);
};

const loadGameSettings = () => {
    const settings = {};
    settings.winScore = parseInt(localStorage.getItem('winScore')) || 5;
    const ballSize = localStorage.getItem('ballSize');
    settings.ballSize = 10;
    if (ballSize === 'Small') settings.ballSize = 10;
    if (ballSize === 'Medium') settings.ballSize = 15;
    if (ballSize === 'Large') settings.ballSize = 20;
    const ballSpeed = localStorage.getItem('ballSpeed');
    settings.ballSpeed = 4;
    if (ballSpeed === 'Slow') settings.ballSpeed = 4;
    if (ballSpeed === 'Normal') settings.ballSpeed = 6;
    if (ballSpeed === 'Fast') settings.ballSpeed = 8;
    const paddleSize = localStorage.getItem('paddleSize');
    settings.paddleSize = 70;
    if (paddleSize === 'Small') settings.paddleSize = 70;
    if (paddleSize === 'Medium') settings.paddleSize = 85;
    if (paddleSize === 'Large') settings.paddleSize = 100;
    settings.aiDifficulty = localStorage.getItem('aiDifficulty') || 'Easy';
    return settings;
};

const pongGame = () => {
	const canvas = document.getElementById('pongCanvas');
	const ctx = canvas.getContext('2d');
    const settings = loadGameSettings();

	// Constants
	const WIDTH = canvas.width;
	const HEIGHT = canvas.height;
    const HALFWIDTH = canvas.width / 2;
    const HALFHEIGHT = canvas.height / 2;
    const BALLSPEED = settings.ballSpeed;

	// Paddle properties
	let paddleWidth = 10;
	let paddleHeight = settings.paddleSize;
	let paddleSpeed = 8;

	// Ball properties
	let ballSize = settings.ballSize;
    let ballSpeed = BALLSPEED;
	let ballSpeedX = BALLSPEED;
	let ballSpeedY = BALLSPEED;

    let winScore = settings.winScore;

	// Paddle positions
	let player1Y = (HEIGHT - paddleHeight) / 2;
	let player2Y = (HEIGHT - paddleHeight) / 2;

	// Ball position
	let ballX = (WIDTH - ballSize) / 2;
	let ballY = (HEIGHT - ballSize) / 2;

	// Player scores
	let player1Score = 0;
	let player2Score = 0;

    let gameRunning = true;
    let message = null;
    let countdown = 3;

	// Key state
	let zPressed = false;
	let sPressed = false;
    let upArrowPressed = false;
	let downArrowPressed = false;

    let mouseX = null;
    let mouseY = null;
    let mouseClickActive = false;
    let isBot = true;
    let aiDifficulty = settings.aiDifficulty;

    let hasDelay = true;
    let lastHitTime = 0;
    let moveDelay = 100;

    let isHit = null;
    let lastHitPosX = null;
    let lastHitPosY = null;
    let lastHitSpdX = null;
    let lastHitSpdY = null;
    let predictionY = HALFHEIGHT;

	document.addEventListener('keydown', (event) => {
        if (event.key === 'z') zPressed = true;
		if (event.key === 's') sPressed = true;

		if (event.key === 'ArrowUp') upArrowPressed = true;
		if (event.key === 'ArrowDown') downArrowPressed = true;
	});

	document.addEventListener('keyup', (event) => {
		if (event.key === 'z') zPressed = false;
		if (event.key === 's') sPressed = false;

        if (event.key === 'ArrowUp') upArrowPressed = false;
		if (event.key === 'ArrowDown') downArrowPressed = false;
	});

    canvas.addEventListener('mousemove', (event) => {
        const rect = canvas.getBoundingClientRect();
        mouseX = event.clientX - rect.left;
        mouseY = event.clientY - rect.top - paddleHeight / 2;
    });

    canvas.addEventListener('mousedown', () => {
        mouseClickActive = true;
    });
    
    canvas.addEventListener('mouseup', () => {
        mouseClickActive = false;
    });

    function pressEnter(event) {
        if (event.key === 'Enter') {
            resetGame();
        }
    }

    function setDifficulty() {
        switch (aiDifficulty) {
            case 'Easy':
                hasDelay = true;
                moveDelay = 1000;
                break;
            case 'Normal':
                hasDelay = true;
                moveDelay = 300;
                break;
            case 'Hard':
                hasDelay = false;
                moveDelay = 0;
                break;
            default:
                hasDelay = true;
                moveDelay = 1000;
        }
    }

    function resetGame() {
        player1Score = 0;
        player2Score = 0;
        resetBall();
    
        gameRunning = true;
        message = null;
        document.removeEventListener('keydown', pressEnter);
    }

    function predict() {
        if (isHit) {
            let predPosX = lastHitPosX;
            let predPosY = lastHitPosY;
            let predSpdX = lastHitSpdX;
            let predSpdY = lastHitSpdY;
            isHit = false;
            while (predPosX < WIDTH) {
                predPosX += predSpdX;
                predPosY += predSpdY;
                if (predPosY <= 0 || predPosY >= HEIGHT - ballSize) predSpdY = -predSpdY;
            }
            predictionY = predPosY - (paddleHeight / 2);
        }
        if (hasDelay) {
            const currentTime = Date.now();
            if (currentTime - lastHitTime < moveDelay) return;
        }
        if (player2Y < predictionY) {
            player2Y += paddleSpeed;
            if (player2Y > predictionY) player2Y = predictionY;
        } else if (player2Y > predictionY) {
            player2Y -= paddleSpeed;
            if (player2Y < predictionY) player2Y = predictionY;
        }
    }

	// Game loop
	function gameLoop() {
		update();
		draw();
		requestAnimationFrame(gameLoop);
	}

	// Update positions
	function update() {
        if (!gameRunning) return;

		// Move paddles
		if (zPressed && player1Y > 0) {
            player1Y -= paddleSpeed;
        } else if (sPressed && player1Y < HEIGHT - paddleHeight) {
            player1Y += paddleSpeed;
        } else if (mouseClickActive && mouseY !== null && mouseX < HALFWIDTH) {
            if (player1Y < mouseY) {
                player1Y += paddleSpeed;
                if (player1Y > mouseY) player1Y = mouseY;
            } else if (player1Y > mouseY) {
                player1Y -= paddleSpeed;
                if (player1Y < mouseY) player1Y = mouseY;
            }
        }

        if (!isBot) {
            if (upArrowPressed && player2Y > 0) {
                player2Y -= paddleSpeed;
            } else if (downArrowPressed && player2Y < HEIGHT - paddleHeight) {
                player2Y += paddleSpeed;
            } else if (mouseClickActive && mouseY !== null && mouseX > HALFWIDTH) {
                if (player2Y < mouseY) {
                    player2Y += paddleSpeed;
                    if (player2Y > mouseY) player2Y = mouseY;
                } else if (player2Y > mouseY) {
                    player2Y -= paddleSpeed;
                    if (player2Y < mouseY) player2Y = mouseY;
                }
            }
        }

		// Move ball
		ballX += ballSpeedX;
		ballY += ballSpeedY;

		// Ball collision with top and bottom
		if (ballY <= 0 || ballY >= HEIGHT - ballSize) ballSpeedY = -ballSpeedY;

		// Ball collision with paddles
		if (ballX <= paddleWidth && ballY >= player1Y && ballY <= player1Y + paddleHeight) {
			ballX = paddleWidth;
            ballSpeedX = -ballSpeedX;
            const angle = Math.atan2(ballSpeedY, ballSpeedX);
            ballSpeed += 1;
            ballSpeedX = ballSpeed * Math.cos(angle);
            ballSpeedY = ballSpeed * Math.sin(angle);
            setBallAsHit();
		}
		if (ballX >= WIDTH - paddleWidth - ballSize && ballY >= player2Y && ballY <= player2Y + paddleHeight) {
			ballX = WIDTH - paddleWidth - ballSize;
            ballSpeedX = -ballSpeedX;
            const angle = Math.atan2(ballSpeedY, ballSpeedX);
            ballSpeed += 1;
            ballSpeedX = ballSpeed * Math.cos(angle);
            ballSpeedY = ballSpeed * Math.sin(angle);
		}

		// AI paddle movement
        if (isBot) {
            predict();
        }

		// Score and reset ball
		if (ballX <= 0) {
			player2Score++;
			if (player2Score >= winScore) {
                gameRunning = false;
                message = 'Player 2 Wins! Press Enter to Retry';
                document.addEventListener('keydown', pressEnter);
            } else {
                resetBall();
            }
		} else if (ballX >= WIDTH - ballSize) {
			player1Score++;
			if (player1Score >= winScore) {
                gameRunning = false;
                message = 'Player 1 Wins! Press Enter to Retry';
                document.addEventListener('keydown', pressEnter);
            } else {
                resetBall();
            }
		}
	}

	// Draw everything
	function draw() {
		ctx.clearRect(0, 0, WIDTH, HEIGHT);

		// Draw paddles
		ctx.fillStyle = 'white';
		ctx.fillRect(0, player1Y, paddleWidth, paddleHeight); // Left paddle (Player 1)
		ctx.fillRect(WIDTH - paddleWidth, player2Y, paddleWidth, paddleHeight); // Right paddle (AI)

		// Draw ball
		ctx.fillRect(ballX, ballY, ballSize, ballSize);

		// Draw net
		for (let i = 0; i < HEIGHT; i += 20) {
			ctx.fillRect(WIDTH / 2 - 1, i, 2, 10);
		}

		// Draw scores
		ctx.font = '20px Arial';
		ctx.fillText(player1Score, WIDTH / 4, 30);
		ctx.fillText(player2Score, 3 * WIDTH / 4, 30);

        if (message) {
            ctx.font = '30px Arial';
            ctx.fillStyle = 'white';
            ctx.textAlign = 'center';
            ctx.fillText(message, WIDTH / 2, HEIGHT / 2);
        }

        if (countdown > 0) {
            ctx.font = '50px Arial';
            ctx.fillStyle = 'white';
            ctx.textAlign = 'center';
            ctx.fillText(countdown, WIDTH / 2, HEIGHT / 2);
        }
	}

    function setBallAsHit() {
        lastHitPosX = ballX;
        lastHitPosY = ballY;
        lastHitSpdX = ballSpeedX;
        lastHitSpdY = ballSpeedY;
        isHit = true;
        lastHitTime = Date.now();
    }

	// Reset ball to the center
	function resetBall() {
		ballX = (WIDTH - ballSize) / 2;
        ballY = (HEIGHT - ballSize) / 2;

		let tempSpeedX = ballSpeedX;
        ballSpeedX = 0;
        ballSpeedY = 0;

        countdown = 4;

        function doCountdown() {
            countdown--;
            if (countdown <= 0) {
                const angle = Math.random() * Math.PI / 2 - Math.PI / 4;
                const direction = tempSpeedX < 0 ? 1 : -1;
                ballSpeed = BALLSPEED;
                ballSpeedX = direction * ballSpeed * Math.cos(angle);
                ballSpeedY = ballSpeed * Math.sin(angle);
                if (ballSpeedX > 0) {
                    setBallAsHit();
                }
            } else {
                setTimeout(doCountdown, 1000);
            }
        }

        doCountdown();
	}

	// Start the game loop
    setDifficulty();
    resetGame();
	gameLoop();
};