function changeScore(step) {
    const rows = document.querySelectorAll("tbody tr");
    rows.forEach(function (row) {
        const cells = row.querySelectorAll("td");
        for (let i = 1; i < cells.length; i++) {
            const value = Number(cells[i].textContent);
            cells[i].textContent = value + step;
        }
    });
    updateAverage();
}

function updateAverage() {
    const rows = document.querySelectorAll("tbody tr");
    const footCells = document.querySelectorAll("tfoot tr td");
    for (let col = 1; col < footCells.length; col++) {
        let sum = 0;
        rows.forEach(function (row) {
            sum += Number(row.querySelectorAll("td")[col].textContent);
        });
        const avg = sum / rows.length;
        footCells[col].textContent = Number.isInteger(avg) ? avg : avg.toFixed(1);
    }
}

document.getElementById("btn-plus").addEventListener("click", function () {
    changeScore(10);
});

document.getElementById("btn-minus").addEventListener("click", function () {
    changeScore(-10);
});

function changeColor(color) {
    document.body.style.backgroundColor = color;
}

document.getElementById("btn-red").addEventListener("click", function () {
    changeColor("red");
});

document.getElementById("btn-yellow").addEventListener("click", function () {
    changeColor("yellow");
});

document.getElementById("btn-blue").addEventListener("click", function () {
    changeColor("blue");
});
