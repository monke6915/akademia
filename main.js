let playerScore = 0;
let computerScore = 0;
let gameHistory = [];
let moveCounter = { K: 0, P: 0, N: 0 };


function zacni() {
    alert("Klikni ok Pre zacatie hry");
    console.log("Hra zacala");
    let userInput = prompt("Zadaj K, P, alebo N:").toUpperCase();
    console.log("Hrac zadal: ", userInput);

    if (!["K", "P", "N"].includes(userInput)) {
        console.log("Hrac zadal zly znak");
        alert("Zadal si zly znak Zadaj K, P, alebo N");
        return;
    }

    let playerPick = ["K", "P", "N"];
    let pcPick = playerPick[Math.floor(Math.random() * playerPick.length)];
    console.log("Vyber PC: ",  pcPick);

    var winner = "";
    if (userInput === pcPick) {
        winner = "Remiza";
    }
    else if (
        (userInput === "K" && pcPick === "N") ||
        (userInput === "P" && pcPick === "K") ||
        (userInput === "N" && pcPick === "P")
    ) {
        winner = "Ty";
        playerScore++;
    } else {
        winner = "PC";
        computerScore++;
    }
    
    gameHistory.push({ userInput, pcPick, winner });
    moveCounter[userInput]++;
    
    console.log("Skore hraca: ", playerScore);
    console.log("Skore PC: ", computerScore);
    console.log("Vyherca: ", winner);

    document.getElementById("score").innerText = `Skore Ty: ${playerScore} - Skore PC: ${computerScore}`;

    
    alert("PC si vybral: " + pcPick + "\n" + winner + " vyhral tuto hru");
    console.log("Hra skoncila");
    console.log("Historia Hier:", gameHistory);
    console.log("Pocitanie Hraca:", moveCounter);
}
