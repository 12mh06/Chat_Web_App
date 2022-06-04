// functions that send needed variables to functions in backend and (if needed) reload or redirect

function deleteMessage(messageId) {
    fetch('/delete-message', {
        method: 'POST',
        body: JSON.stringify({ messageId: messageId })
    }).then((_res) => {
        window.location.href = '/';
    })
}

function addMessage(msgContent, chatroomId) {
    fetch('/add-message', {
        method: 'POST',
        body: JSON.stringify({ msgContent: msgContent, chatroomId: chatroomId })
    })
}

function deleteFriend(friendId) {
    fetch('/delete-friend', {
        method: 'POST',
        body: JSON.stringify({ friendId: friendId })
    }).then((_res) => {
        window.location.href = '/friends';
    })
}

function addToChatroom(friendEmail, chatroomId) {
    fetch('/add-to-chatroom', {
        method: 'POST',
        body: JSON.stringify({ friendEmail: friendEmail, chatroomId: chatroomId })
    }).then((_res) => {
        window.location.href = '/';
    })
}

function closeChatroom(chatroomId) {
    fetch('/close-chatroom', {
        method: 'POST',
        body: JSON.stringify({ chatroomId: chatroomId })
    }).then((_res) => {
        window.location.href = '/';
    })
}

function leaveChatroom(chatroomId) {
    fetch('/leave-chatroom', {
        method: 'POST',
        body: JSON.stringify({ chatroomId: chatroomId })
    }).then((_res) => {
        window.location.href = '/';
    })
}

function enterChatroom(chatroomId) {
    fetch('/enter-chatroom', {
        method: 'POST',
        body: JSON.stringify({ chatroomId: chatroomId })
    }).then((_res) => {
        window.location.href = '/';
    })
}

function acceptFriendRequest(friendId) {
    respondFriendRequest(friendId, true)
}

function denyFriendRequest(friendId) {
    respondFriendRequest(friendId, false)
}

function respondFriendRequest(friendId, answer) {
    fetch('/respond-friend-request', {
        method: 'POST',
        body: JSON.stringify({ friendId: friendId, answer: answer })
    }).then((_res) => {
        window.location.href = '/friends'
    })
}