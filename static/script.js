document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/news')
        .then(response => response.json())
        .then(news => {
            const newsList = document.querySelector('.news-list');
            news.forEach(item => {
                const listItem = document.createElement('li');
                listItem.classList.add('news-item');

                const image = document.createElement('img');
                image.src = item.relate_image_link;
                image.alt = 'News Image';
                image.classList.add('news-image');

                const container = document.createElement('div');
                container.classList.add('news-container');

                const title = document.createElement('p');
                title.classList.add('news-title');
                title.textContent = item.title;

                const text = document.createElement('div');
                text.classList.add('news-text');
                text.textContent = item.description;

                listItem.appendChild(image);
                listItem.appendChild(container);
                container.appendChild(title);
                container.appendChild(text);

                newsList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching news:', error));
})


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
