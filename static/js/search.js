document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('drink_search');
    const suggestionsDiv = document.getElementById('drink_suggestions');

    if (searchInput && suggestionsDiv) {
        searchInput.addEventListener('input', function() {
            const query = searchInput.value;
            if (query.length > 2) {
                fetch(`/search_drinks/?query=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        suggestionsDiv.innerHTML = '';
                        if (data.length > 0) {
                            data.forEach(drink => {
                                const suggestion = document.createElement('div');
                                suggestion.textContent = drink.name;
                                suggestion.className = 'suggestion-item';
                                suggestion.dataset.drinkId = drink.id;
                                suggestion.addEventListener('click', function() {
                                    searchInput.value = drink.name;
                                    suggestionsDiv.innerHTML = '';
                                });
                                suggestionsDiv.appendChild(suggestion);
                            });
                        }
                    })
                    .catch(error => console.error('Error:', error));
            } else {
                suggestionsDiv.innerHTML = '';
            }
        });

        // Close suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
                suggestionsDiv.innerHTML = '';
            }
        });
    }
}); 