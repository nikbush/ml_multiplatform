async function fetchData() {
    try {
        const response = await fetch("http://localhost:8000/table/list");
        if (!response.ok) {
            throw new Error("Error loading data");
        }
        const data = await response.json();
        const list = document.getElementById("data-list");
        list.innerHTML = ""; // Очистка списка перед обновлением
        data.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item.join(", ");
            list.appendChild(li);
        });
        document.getElementById("error").textContent = "";
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("error").textContent = "Failed to load data!";
    }
}
