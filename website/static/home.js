//sends and acts on socket messages 

$(document).ready(function() {

    const socket = io.connect('http://127.0.0.1:5000');
    socket.emit('join')

    //sends message when button clicked; emits message content via socket to the server
    $('#send-message').on('click', function() {
        if (document.getElementById("message-content") != null) {
            const msgContent = document.getElementById("message-content").value
            document.getElementById("message-content").value = ""
            socket.emit('send_message', msgContent)
        }
    })

    $('#close-chatroom').on('click', function() {
        socket.emit('leave')
    })

    //defines how the client reacts to a socket message; displays received message
    socket.on('msg_data', function(msg_data) {
        const content = document.createTextNode(msg_data.msg_content)
        const date = document.createTextNode(msg_data.msg_date)
        const sender = document.createTextNode(msg_data.msg_sender)

        container = document.getElementById("messages")

        const li = document.createElement("li")
        li.classList.add("list-group-item", "border")
        container.appendChild(li)

        const div1 = document.createElement("div")
        li.appendChild(div1)

        const span1 = document.createElement("span")
        span1.classList.add("pull-left")
        span1.style.cssText += "max-width: 80%"
        span1.appendChild(content)
        div1.appendChild(span1)

        const span2 = document.createElement("span")
        span2.classList.add("pull-right")
        span2.classList.add("font-weight-bold")
        span2.style.cssText += "max-width: 15%"
        span2.appendChild(sender)
        div1.appendChild(span2)

        const br = document.createElement("br")
        li.appendChild(br)

        const div2 = document.createElement("div")
        div2.setAttribute("align", "right")
        div2.appendChild(date)
        li.appendChild(div2)
    })
});