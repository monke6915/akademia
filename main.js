function zacni() {
    alert("Klikni ok Pre zacatie hry");
    var userInput = prompt("Zadaj K, P, alebo N:").toUpperCase();

    if (!["K", "P", "N"].includes(userInput)) {
        alert("Zadal si zly znak Zadaj K, P, alebo N");
        return;
    }

    var vyber = ["K", "P", "N"];
    var vyberpc = vyber[Math.floor(Math.random() * vyber.length)];

    var vyherca = "";
    if (userInput === vyberpc) {
        vyherca = "Remiza";
    }
    else if (
        (userInput === "K" && vyberpc === "N") ||
        (userInput === "P" && vyberpc === "K") ||
        (userInput === "N" && vyberpc === "P")
    ) {
        vyherca = "Ty";
    } else {
        vyherca = "PC";
    }
    alert("PC si vybral: " + vyberpc + "\n" + vyherca);
}