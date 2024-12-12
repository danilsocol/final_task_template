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

                    const title = document.createElement('p');
                    title.classList.add('news-title');
                    title.textContent = item.title;

                    const text = document.createElement('div');
                    text.classList.add('news-text');
                    text.textContent = item.description;

                    listItem.appendChild(title); // Затем заголовок
                    listItem.appendChild(image);  // Картинка сверху
                    listItem.appendChild(text);  // Затем описание

                    newsList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching news:', error));
})


const chatHistory = document.getElementById('chat-history');
const chatInput = document.getElementById('chat-text-area');
const sendButton = document.getElementById('send-button');

let currentSessionId = null;

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
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: message,
                    session_id: currentSessionId
                })
            });
            
        // // Задержка для имитации ответа от сервера
        // setTimeout(() => {
        //     // Добавляем ответ от бота в историю чата (заглушка)
        //     addMessage('bot', `Ответ от бота: Вы сказали "${message}"`);
            if (!response.ok) {
                throw new Error('Ошибка сети');
            }

            const data = await response.json();
            currentSessionId = data.session_id;
            addMessage('bot', data.response);
        } catch (error) {
            console.error('Ошибка при отправке сообщения:', error);
            addMessage('system', 'Произошла ошибка при отправке сообщения');
        } finally {
            sendButton.disabled = false;
        }
    }
});

function addMessage(sender, message) {
    const messageElement = document.createElement('div');
    if (sender === 'system') {
        return;
    }

    // Определяем, кто отправил сообщение
    let ownerMessage = "Вы: ";
    if (sender === 'bot') {
        ownerMessage = "ЧелгуБот: ";
    }

    // Заменяем символы новой строки на <br>
    const formattedMessage = message.replace(/\n/g, '<br>');

    // Добавляем сообщение в элемент
    messageElement.innerHTML = ownerMessage + formattedMessage;
    messageElement.className = `message ${sender}-message`;
    chatHistory.appendChild(messageElement);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Очищаем текстовое поле после отправки
    document.getElementById('chat-text-area').value = '';
}


const searchButton = document.getElementById('search-button');
const searchInput = document.getElementById('search-input');
const searchResultsDiv = document.getElementById('search-results');

searchButton.addEventListener('click', async () => {
    const query = searchInput.value;

    // Отправляем запрос на бэкэнд
    try {
        const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error('Ошибка сети');
        }

        const results = await response.json();

        // Отображаем результаты в блоке searchResultsDiv
             let resultsHTML = '';
        results.forEach(result => {
            resultsHTML += `
                <div class="result-item">
                    <a href="${result.url}" target="_blank">${result.title}</a>
                    ${result.headline ? `<p class="headline">${result.headline}</p>` : ''}
                </div>
            `;
        });

        searchResultsDiv.innerHTML = resultsHTML || '<p>Ничего не найдено.</p>';
    } catch (error) {
        console.error('Ошибка при получении результатов поиска:', error);
        searchResultsDiv.innerHTML = '<p>Произошла ошибка при получении результатов поиска.</p>';
    }
});