const apiUrl = "http://localhost:8000"; // Change if your API runs elsewhere

document.getElementById("createTaskBtn").addEventListener("click", async function() {
    const sleepTime = document.getElementById("sleepTime").value;

    if (!sleepTime || sleepTime < 1) {
        alert("Please enter a valid sleep time (minimum 1 second).");
        return;
    }

    const response = await fetch(`${apiUrl}/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sleep_time: parseInt(sleepTime, 10) })
    });

    const data = await response.json();
    if (data.task_id) {
        addTaskToTable(data.task_id, sleepTime, "Queued");
    }
});

function addTaskToTable(taskId, sleepTime, status) {
    const tableBody = document.getElementById("taskTableBody");
    const row = document.createElement("tr");
    row.setAttribute("data-task-id", taskId);
    row.innerHTML = `
        <td class="border border-gray-300 px-4 py-2">${taskId}</td>
        <td class="border border-gray-300 px-4 py-2">${sleepTime} sec</td>
        <td class="border border-gray-300 px-4 py-2 task-status transition-colors duration-500 text-yellow-500 font-bold">${status}</td>
    `;
    tableBody.appendChild(row);
}

async function updateTaskStatuses() {
    const rows = document.querySelectorAll("#taskTableBody tr");
    for (const row of rows) {
        const taskId = row.getAttribute("data-task-id");
        const statusCell = row.querySelector(".task-status");

        const response = await fetch(`${apiUrl}/tasks/${taskId}`);
        if (response.ok) {
            const data = await response.json();
            const newStatus = data.status || "Unknown";

            if (statusCell.textContent !== newStatus) { // Update only if different
                statusCell.textContent = newStatus;
                
                // Remove previous status color classes
                statusCell.classList.remove("text-yellow-500", "text-blue-500", "text-green-500", "text-red-500");

                // Apply color based on status
                if (newStatus === "Queued") {
                    statusCell.classList.add("text-yellow-500");
                } else if (newStatus === "In Progress") {
                    statusCell.classList.add("text-blue-500");
                } else if (newStatus === "Completed") {
                    statusCell.classList.add("text-green-500");
                } else {
                    statusCell.classList.add("text-red-500");
                }
            }
        } else {
            statusCell.textContent = "Failed";
            statusCell.classList.add("text-red-500");
        }
    }
}

setInterval(updateTaskStatuses, 1000); // Refresh status every second
