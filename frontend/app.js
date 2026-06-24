// API Configuration
const API_BASE_URL = window.location.origin;

// DOM Elements
const statusBadge = document.getElementById('status-badge');
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const typingIndicator = document.getElementById('typing-indicator');
const quickRepliesContainer = document.getElementById('quick-replies');
const lastMsgTimeEl = document.getElementById('last-msg-time');

// State
let isServerOnline = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (window.lucide) {
        window.lucide.createIcons();
    }
    
    // Load initial health status
    checkHealth();
    
    // Polling health check every 10 seconds
    setInterval(checkHealth, 10000);

    // Add default greeting message
    addChatMessage('incoming', '¡Hola! Soy tu asistente virtual de la clínica. ¿En qué puedo ayudarte hoy?\n\nPuedes consultarme sobre:\n- Horarios de atención 🕒\n- Servicios y precios 💰\n- Agendar una cita 🗓️\n- Políticas de cancelación ❌');
});

// Health check function
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (response.ok && data.status === 'ok') {
            isServerOnline = true;
            statusBadge.className = 'status-indicator online';
            statusBadge.querySelector('.status-text').innerText = 'API online';
        } else {
            throw new Error('Server unhealthy');
        }
    } catch (error) {
        isServerOnline = false;
        statusBadge.className = 'status-indicator offline';
        statusBadge.querySelector('.status-text').innerText = 'API offline';
    }
}

// Add Chat Message to UI (WhatsApp Style)
function addChatMessage(type, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;
    
    // Format text: convert newlines to <br> and bold tags **text** to <strong>text</strong>
    let formattedText = text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
    const p = document.createElement('p');
    p.innerHTML = formattedText;
    messageDiv.appendChild(p);
    
    // Create WhatsApp metadata (Time + Checkmarks)
    const metaSpan = document.createElement('span');
    metaSpan.className = 'bubble-meta';
    
    const now = new Date();
    const timeString = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    metaSpan.innerText = timeString;
    
    // Update the last message time in the sidebar
    if (lastMsgTimeEl) {
        lastMsgTimeEl.innerText = timeString;
    }
    
    if (type === 'outgoing') {
        // Add double blue checks for outgoing messages
        const ticksSpan = document.createElement('span');
        ticksSpan.className = 'ticks-icon';
        ticksSpan.innerHTML = '<i data-lucide="check-check"></i>';
        metaSpan.appendChild(ticksSpan);
    }
    
    messageDiv.appendChild(metaSpan);
    chatMessages.appendChild(messageDiv);
    
    // Re-create icons to render the checkmarks
    if (window.lucide) {
        window.lucide.createIcons();
    }
    
    // Auto scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message handler
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;
    
    chatInput.value = '';
    sendMessageToAgent(message);
});

// Quick reply buttons click handler
quickRepliesContainer.addEventListener('click', (e) => {
    const btn = e.target.closest('.quick-reply-chip');
    if (!btn) return;
    
    const message = btn.getAttribute('data-msg');
    sendMessageToAgent(message);
});

async function sendMessageToAgent(messageText) {
    // Render user message in UI
    addChatMessage('outgoing', messageText);
    
    // Show typing indicator
    typingIndicator.style.display = 'flex';
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    try {
        if (!isServerOnline) {
            await checkHealth();
            if (!isServerOnline) {
                throw new Error('Servidor offline');
            }
        }

        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: messageText })
        });
        
        if (!response.ok) {
            throw new Error('Error en respuesta del servidor');
        }
        
        const data = await response.json();
        
        // Hide typing indicator
        typingIndicator.style.display = 'none';
        
        // Render agent response
        addChatMessage('incoming', data.response);
    } catch (error) {
        typingIndicator.style.display = 'none';
        addChatMessage('incoming', '⚠️ No se pudo enviar el mensaje al servidor. Asegúrate de iniciar el backend (`python run.py`) y tener configurado tu GEMINI_API_KEY en el archivo `.env`.');
        console.error(error);
    }
}
