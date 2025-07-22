document.addEventListener('DOMContentLoaded', async function () {
    const wrapper = document.getElementById('live-poll-results');
    const resultsDiv = document.getElementById('poll-results-content');

    // Guard: Make sure the live results container is found
    if (!wrapper || !resultsDiv) return;

    const pollId = wrapper.dataset.pollId;
    if (!pollId) {
        resultsDiv.innerHTML = "<p>Error: No poll ID found.</p>";
        return;
    }

    async function fetchPollResults() {
        try {
            const response = await fetch(`/api/polls/${pollId}/result`);
            const data = await response.json();

            if (data.results && data.options) {
                let html = "<ul>";
                for (const option of data.options) {
                    const count = data.results[option.id] || 0;
                    html += `<li><strong>${option.text}:</strong> ${count} vote(s)</li>`;
                }
                html += "</ul>";
                html += `<p><strong>Total Votes:</strong> ${data.total_votes}</p>`;

                if ('unique_voters' in data) {
                    html += `<p><strong>Unique Voters:</strong> ${data.unique_voters}</p>`;
                }

                resultsDiv.innerHTML = html;
            } else {
                resultsDiv.innerHTML = "<p>No results yet.</p>";
            }
        } catch (error) {
            console.error("Error fetching results:", error);
            resultsDiv.innerHTML = `<p>Error loading results: ${error.message}</p>`;
        }
    }

    // Load results initially
    fetchPollResults();

    // Optional: Auto-refresh every 30 seconds
    setInterval(fetchPollResults, 30000);
});


// document.addEventListener('DOMContentLoaded', async function () {
//     // ✅ Locate the wrapper and content elements
//     const wrapper = document.getElementById('live-poll-results');
//     const resultsDiv = document.getElementById('poll-results-content');

//     // ✅ Exit early if required elements aren’t found
//     if (!wrapper || !resultsDiv) return;

//     const pollId = wrapper.dataset.pollid;

//     // ✅ Show error if poll ID is missing
//     if (!pollId) {
//         resultsDiv.innerHTML = "<p>Error: No poll ID found.</p>";
//         return;
//     }

//     // ✅ Fetch poll results from the API
//     async function fetchPollResults() {
//         try {
//             const response = await fetch(`/api/polls/${pollId}/result`);
//             const data = await response.json();

//             if (data.results && data.options) {
//                 let html = "<ul>";
//                 for (const option of data.options) {
//                     const count = data.results[option.id] || 0;
//                     html += `<li>${option.text}: ${count} vote(s)</li>`;
//                 }
//                 html += "</ul>";
//                 resultsDiv.innerHTML = html;
//             } else {
//                 resultsDiv.innerHTML = "<p>Unexpected response format.</p>";
//             }
//         } catch (error) {
//             resultsDiv.innerHTML = `<p>Error fetching results: ${error.message}</p>`;
//         }
//     }

//     // ✅ Run the fetch on page load
//     fetchPollResults();
//     setInterval(fetchPollResults, 5000)
// })