$(document).ready(function () {

    let typeWriterInterval;

    // Display Speak Message
    eel.expose(DisplayMessage)
    function DisplayMessage(message) {
        clearInterval(typeWriterInterval);
        $(".siri-message").empty();
        
        let i = 0;
        typeWriterInterval = setInterval(function() {
            if (i < message.length) {
                $(".siri-message").append(message.charAt(i));
                i++;
                var container = $(".siri-message").parent()[0];
                container.scrollTop = container.scrollHeight;
            } else {
                clearInterval(typeWriterInterval);
            }
        }, 20); // 20ms per character
    }

    // Stop Text Animation
    eel.expose(StopTextAnimation)
    function StopTextAnimation() {
        clearInterval(typeWriterInterval);
    }

    // Show User Query Instantly
    eel.expose(ShowUserQuery)
    function ShowUserQuery(message) {
        clearInterval(typeWriterInterval);
        $(".siri-message").text(message);
    }


    // Display hood
    eel.expose(ShowHood)
    function ShowHood() {

        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
        
    }

    eel.expose(ShowStopBtn)
    function ShowStopBtn() {
        $("#StopSpeakingBtn").removeAttr("hidden");
    }

    eel.expose(HideStopBtn)
    function HideStopBtn() {
        $("#StopSpeakingBtn").attr("hidden", true);
    }


    eel.expose(senderText)
    function senderText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (message.trim() !== "") {
            chatBox.innerHTML += `<div class="row justify-content-end mb-4">
            <div class = "width-size">
            <div class="sender_message">${message}</div>
        </div>`; 
    
            // Scroll to the bottom of the chat box
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    eel.expose(receiverText)
    function receiverText(message) {

        var chatBox = document.getElementById("chat-canvas-body");
        if (message.trim() !== "") {
            chatBox.innerHTML += `<div class="row justify-content-start mb-4">
            <div class = "width-size">
            <div class="receiver_message">${message}</div>
            </div>
        </div>`; 
    
            // Scroll to the bottom of the chat box
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
    }

    let currentStreamElement = null;

    eel.expose(receiverTextStreamInit)
    function receiverTextStreamInit() {
        // Clear standard typewriter artifacts
        clearInterval(typeWriterInterval);
        $(".siri-message").empty();

        var chatBox = document.getElementById("chat-canvas-body");
        chatBox.innerHTML += `<div class="row justify-content-start mb-4">
            <div class = "width-size">
            <div class="receiver_message dynamic-stream"></div>
            </div>
        </div>`;
        
        // Target the latest stream bubble
        let streamElements = document.getElementsByClassName("dynamic-stream");
        currentStreamElement = streamElements[streamElements.length - 1];
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    eel.expose(receiverTextStreamChunk)
    function receiverTextStreamChunk(chunk) {
        if (currentStreamElement) {
            // Convert Python newlines into HTML breaks
            let formattedChunk = chunk.replace(/\n/g, '<br>');
            
            // Append to chat bubble
            currentStreamElement.innerHTML += formattedChunk;
            var chatBox = document.getElementById("chat-canvas-body");
            chatBox.scrollTop = chatBox.scrollHeight;

            // Also append to Siri main display area
            $(".siri-message").append(formattedChunk);
            var container = $(".siri-message").parent()[0];
            container.scrollTop = container.scrollHeight;
        }
    }
    // ─── Thinking Animation ───
    let thinkingInterval = null;
    const thinkingMessages = [
        "Analyzing query",
        "Fetching details",
        "Gathering insights",
        "Processing request",
        "Refining response",
        "Preparing answer"
    ];

    eel.expose(ShowThinkingAnimation)
    function ShowThinkingAnimation() {
        let msgIndex = 0;
        let dotCount = 0;
        
        // Show first message immediately
        $(".siri-message").html('<span class="thinking-text">' + thinkingMessages[0] + '</span>');
        
        thinkingInterval = setInterval(function () {
            dotCount++;
            if (dotCount > 3) {
                dotCount = 0;
                msgIndex = (msgIndex + 1) % thinkingMessages.length;
            }
            let dots = ".".repeat(dotCount);
            $(".siri-message").html(
                '<span class="thinking-text">' + thinkingMessages[msgIndex] + dots + '</span>'
            );
        }, 500);
    }

    eel.expose(HideThinkingAnimation)
    function HideThinkingAnimation() {
        if (thinkingInterval) {
            clearInterval(thinkingInterval);
            thinkingInterval = null;
        }
        $(".siri-message").empty();
    }


});