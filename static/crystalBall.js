function startshake(){
    var ball = document.getElementById("ball")
    ball.classList.add("shake")
}

function stopshake(){
    var ball = document.getElementById("ball")
    ball.classList.remove("shake")
}

document.addEventListener("DOMContentLoaded", () => {
    const simulateBtn = document.getElementById("simulateBtn");
    const resultsDiv = document.getElementById("results");

    simulateBtn.addEventListener("click", async () => {
        const athlete1 = document.getElementById("player1").value;
        const athlete2 = document.getElementById("player2").value;
        const activity = document.getElementById("event").value;

        startshake();
        resultsDiv.innerText = "Consulting the crystal ball...";

        try {
            const response = await fetch("/compare", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ athlete1, athlete2, activity })
            });

            const result = await response.json();

            if (result.error) {
                resultsDiv.innerText = result.error;
            } else {
                resultsDiv.innerText = `${result.winner} wins!\n\n${result.commentary}`;
            }
        } catch (err) {
            console.error("Error during fetch:", err);
            resultsDiv.innerText = "Something went wrong! Try again.";
        } finally {
            stopshake();
        }
    });
});