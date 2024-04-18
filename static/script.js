window.onload = function() {
    fetch('/data')
    .then(response => response.json())
    .then(data => {
        const totalEarned = document.getElementById('totalEarned');
        const users24Hours = document.getElementById('users24Hours');
        const totalParticipants = document.getElementById('totalParticipants');
        const tbody = document.querySelector('#data tbody');

        // Сортировка данных по id_blockchain
        data.sort((a, b) => parseInt(a.id_blockchain) - parseInt(b.id_blockchain));

        if (data.length > 0) {
            totalEarned.textContent = data[0].total_earned;
            users24Hours.textContent = data[0].users_last_24_hours;
            totalParticipants.textContent = data[0].total_participants;
        }

        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.id}</td>
                <td>${item.wallet_address}</td>
                <td>${item.date_registration}</td>
                <td>${item.earned}</td>
                <td>${item.id_blockchain}</td>
                <td>${item.queue_position}</td>
                <td>${item.activations}</td>
                <td>${item.partners}</td>
                <td>${item.reload}</td>
                <td>${item.user_level}</td>
                <td>${item.tokens_balance}</td>
            `;
            tbody.appendChild(tr);
        });
    })
    .catch(error => console.error('Error loading the data:', error));
};
