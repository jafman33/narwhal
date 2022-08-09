    // // list of div elements whose immediate parent element is of class .msg_history
    let msgH = document.querySelectorAll(".msg_history > div");
    let CurrentLen;

    let init = () => {
        CurrentLen = msgH.length;
    };

    init();

    // Validate Position
    let validatePosition = () => {
        if (msgH.length === CurrentLen && msgH.length != 0) {
            msgH[msgH.length - 1].setAttribute("id", "last_message");
            for (var i; i < msgH.length; i++) {
                if (msgH[i].id === "last_message" && msgH[i] !== msgH.length - 1) {
                    msgH[i].removeAttribute("id");
                    msgH[msgH.length - 1].setAttribute("id", "last_message");
                }
            }
        }
    };

    // ScrollDown
    let scrollDown = () => {
        validatePosition();
        location.href = "#last_message";
        init();
    };

    // socket
    var socket = io.connect(document.domain + ':' + location.port + '/?rid=' + '{{ room_id }}');

    scrollDown();

    socket.on('connect', function() {
        socket.emit('join-chat', {
            rid: '{{ room_id }}'
        })
    })

    socket.on('joined-chat', function(msg) {
        // console.log(msg)
    })


    var time = new Date();


    // on Submit
    var form = $('#chat_form').on('submit', function(e) {

        e.preventDefault();
        let user_input = $('input.message').val();

        socket.emit('outgoing', {
            timestamp: Date.now() / 1000,
            sender_username: "{{ user_data['username'] }}",
            sender_id: "{{ user_data['id'] }}",
            message: user_input,
            rid: "{{ room_id }}"
        });

        $('div.msg_history').append(`
        <div class="outgoing_msg">
          <div class="sent_msg">
            <p>${user_input}</p>
            <span class="time_date">
              ${time.toLocaleString('en-US', {
                  hour: 'numeric',
                  minute: 'numeric',
                  hour12: true
                })} 
            </span> 
          </div>
        </div>
        `);

        document.getElementById("last-message").innerHTML = user_input;
        $('input.message').val('').focus();
        console.log('here')
        scrollDown();

    });

    // on message
    socket.on('message', function(msg) {
        $('div.msg_history').append(`<div class="incoming_msg">
          <div class="incoming_msg_img"> <img src="https://ptetutorials.com/images/user-profile.png" alt="sunil"></div>
          <div class="received_msg">
            <div class="received_withd_msg">
              <p>${msg.message}</p>
              <span class="time_date"> 
                ${time.toLocaleString('en-US', {
                  hour: 'numeric',
                  minute: 'numeric',
                  hour12: true
                })} 
              </span>
            </div>
          </div>
        `)
        scrollDown();
        document.getElementById("last-message").innerHTML = msg.message
    });