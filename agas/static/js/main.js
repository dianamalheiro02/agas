document.getElementById("editButton").addEventListener("click", () => {
    fetch('/edit_ontology')
        .then(response => response.text())
        .then(data => {
            console.log(data); // Log success or error
        })
        .catch(error => console.error('Error:', error));
});

document.addEventListener('DOMContentLoaded', () => {
    const convertButton = document.getElementById('convertButton');

    function fetchAndDisplayContentConvert() {
        fetch('/convert_ontology')
            .then(response => response.text())
            .then(data => {
                if (window.editor) {
                    window.editor.setValue(data); // Monaco update
                    //document.getElementById('rdf').value = data; // Optional: update hidden field
                }
            })
            .catch(error => console.error('Error fetching converted ontology:', error));
            // Reload the page
            location.reload();
    }

    // Button to re-fetch and refresh content on demand
    convertButton.addEventListener('click', fetchAndDisplayContentConvert);
});

document.addEventListener('DOMContentLoaded', () => {
    const syncButton = document.getElementById('syncButton');

    // Fetch RDF content and update Monaco Editor
    function fetchAndDisplayContent() {
        fetch('/sync_ontology')
            .then(response => response.text())
            .then(data => {
                if (window.editor) {
                    window.editor.setValue(data); // Update Monaco content
                    //document.getElementById('rdf').value = data; // (Optional) Keep hidden input in sync
                }
            })
            .catch(error => console.error('Error fetching ontology:', error));
    }

    // Fetch content on page load
    fetchAndDisplayContent();

    // Sync button re-fetches content
    syncButton.addEventListener('click', fetchAndDisplayContent);
});

/*
document.getElementById("saveButton").addEventListener("click", function() {

    let currentSection = "full";  // default

    document.getElementById("B0").addEventListener("click", () => currentSection = "full");
    document.getElementById("B1").addEventListener("click", () => currentSection = "classes");
    document.getElementById("B2").addEventListener("click", () => currentSection = "dataproperties");
    document.getElementById("B3").addEventListener("click", () => currentSection = "objectproperties");
    document.getElementById("B4").addEventListener("click", () => currentSection = "individuals");

    const content = document.getElementById("rdf").value;

    fetch("/save_ontology", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
            content: content,
            section: currentSection
        })
    })
    .then(res => {
        if (res.ok) {
            alert("Ontology saved successfully!");
            location.reload();  // Optional: Reload page after save
        } else {
            alert("Failed to save ontology.");
        }
    });
});*/

/*
document.getElementById("rdfForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const form = event.target;
    const method = document.querySelector('input[name="method"]:checked').value;
    const action = form.getAttribute("action");
    const rdfContent = document.getElementById("rdf").value;

    console.log("Submitting RDF data:", rdfContent);
    console.log("Method:", method);
    console.log("Action URL:", action);

    if (method === "GET") {
        // Send as URL parameters
        const params = new URLSearchParams();
        params.append("rdf", rdfContent);
        window.location.href = `${action}?${params.toString()}`;
    } else {
        try {
            // Option 1: Send as plain text (if server expects raw RDF)
            const response = await fetch(action, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/pdf, application/xml, text/html, application/xhtml+xml" // Adjust as needed
                },
                body: rdfContent,
                // mode: "no-cors" //can't see result
            });


            // Option 2: Send as form-data (if needed)
            // const formData = new FormData();
            // formData.append("rdf", rdfContent);
            // const response = await fetch(action, {
            //     method: "POST",
            //     body: formData
            // });

            if (!response.ok) {
                console.error("Server responded with error:", response.status, response.statusText);
                alert("Error: " + response.statusText);
                return;
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            window.open(url);

        } catch (error) {
            console.error("Fetch error:", error);
            alert("An error occurred while processing your request.");
        }
    }
});
*/

