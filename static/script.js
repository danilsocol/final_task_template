const chatHistory = document.getElementById('chat-history');
const chatInput = document.getElementById('chat-input');
const sendButton = document.getElementById('send-button');

sendButton.addEventListener('click', async () => {
    const message = chatInput.value;
    if (message.trim() !== '') {
        // Добавляем сообщение пользователя в историю чата
        addMessage('user', message);
        chatInput.value = '';

        // Блокируем кнопку
        sendButton.disabled = true;

        // Отправляем запрос на сервер (заглушка)
        // Здесь будет асинхронный вызов к вашему FastAPI endpoint для чата
        // Например, fetch('/chat', { method: 'POST', body: JSON.stringify({ message: message }) })

        // Задержка для имитации ответа от сервера
        setTimeout(() => {
            // Добавляем ответ от бота в историю чата (заглушка)
            addMessage('bot', `Ответ от бота: Вы сказали "${message}"`);

            // Разблокируем кнопку
            sendButton.disabled = false;
        }, 1000);
    }
});

function addMessage(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.textContent = `${sender}: ${message}`;
    chatHistory.appendChild(messageElement);
    chatHistory.scrollTop = chatHistory.scrollHeight; // Прокручиваем вниз
}

// Добавляем функциональность для кнопки "Искать" (заглушка)
const searchButton = document.getElementById('search-button');
const searchInput = document.getElementById('search-input');
const searchResultsDiv = document.getElementById('search-results');

searchButton.addEventListener('click', async () => {
    const query = searchInput.value;

    // Заглушка для результатов поиска
    const mockResults = [
        'https://www.chelsu.ru/page-1',
        'https://www.chelsu.ru/page-2',
        'https://www.chelsu.ru/page-3',
        'https://www.chelsu.ru/page-4',
        'https://www.chelsu.ru/page-5',
    ];

    // Отображаем результаты в блоке searchResultsDiv
    let resultsHTML = '<ul>';
    mockResults.forEach(result => {
        resultsHTML += `<li><a href="${result}" target="_blank">${result}</a></li>`;
    });
    resultsHTML += '</ul>';

    searchResultsDiv.innerHTML = resultsHTML;
});