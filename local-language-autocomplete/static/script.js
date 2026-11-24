
const searchInput = document.getElementById("searchInput");
const suggestionsBox = document.getElementById("suggestions");
const statusText = document.getElementById("status");
const clearBtn = document.getElementById("clearBtn");

let debounceTimer;
let requestNumber = 0;

async function searchWords(query) {
    const currentRequest = ++requestNumber;

    if (!query.trim()) {
        suggestionsBox.replaceChildren();
        statusText.textContent = "Start typing to see suggestions.";
        return;
    }

    statusText.textContent = "Finding suggestions...";

    try {
        const response = await fetch(
            `/api/suggest?q=${encodeURIComponent(query)}&limit=8`
        );

        if (!response.ok) {
            throw new Error("Search request failed");
        }

        const data = await response.json();

        // Ignore an older response if the user has typed again.
        if (currentRequest !== requestNumber) return;

        renderSuggestions(data.suggestions);
    } catch (error) {
        if (currentRequest !== requestNumber) return;

        suggestionsBox.replaceChildren();
        statusText.textContent =
            "Could not load suggestions. Please try again.";
    }
}

function renderSuggestions(suggestions) {
    suggestionsBox.replaceChildren();

    if (!suggestions.length) {
        statusText.textContent = "No matching words found.";
        return;
    }

    statusText.textContent =
        `${suggestions.length} suggestion(s) found`;

    suggestions.forEach((item) => {
        const li = document.createElement("li");
        li.className = "suggestion";
        li.setAttribute("role", "option");
        li.tabIndex = 0;

        const word = document.createElement("span");
        word.className = "word";
        word.textContent = item.word;

        const meta = document.createElement("span");
        meta.className = "word-meta";
        meta.textContent = `Frequency: ${item.frequency}`;

        li.append(word, meta);

        li.addEventListener("click", () => chooseWord(item.word));
        li.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                chooseWord(item.word);
            }
        });

        suggestionsBox.appendChild(li);
    });
}

async function chooseWord(word) {
    searchInput.value = word;
    suggestionsBox.replaceChildren();
    statusText.textContent = `Selected: ${word}`;

    try {
        const response = await fetch("/api/select", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ word })
        });

        if (!response.ok) {
            throw new Error("Could not update frequency");
        }
    } catch (error) {
        statusText.textContent =
            "Word selected, but its frequency could not be updated.";
    }
}

searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);

    const query = searchInput.value;
    debounceTimer = setTimeout(() => searchWords(query), 150);
});

clearBtn.addEventListener("click", () => {
    clearTimeout(debounceTimer);
    requestNumber++;
    searchInput.value = "";
    suggestionsBox.replaceChildren();
    statusText.textContent = "Start typing to see suggestions.";
    searchInput.focus();
});

document.querySelectorAll(".example").forEach((button) => {
    button.addEventListener("click", () => {
        searchInput.value = button.textContent.trim();
        searchWords(searchInput.value);
        searchInput.focus();
    });
});
