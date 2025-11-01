function shake(){
    var ball = document.getElementById("ball")
    var messageText = document.getElementById("message")

    if(messageText != null){
        messageText.parentNode.removeChild(messageText)

    }

    ball.classList.add("shake")

    setTimeout(function(){ball.classList.remove("shake");},1000)
}