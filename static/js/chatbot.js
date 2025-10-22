/** 
 * Triple G BuildHub Floating Chatbot 
 * A standalone JavaScript-based chatbot that injects itself into any webpage 
 * with the Triple G BuildHub branding and Messenger-like interface. 
 */
(function() {
    // Prevent duplicate initialization if script is included multiple times
    if (window.__TG_CHATBOT_INITIALIZED__) {
        return;
    }
    window.__TG_CHATBOT_INITIALIZED__ = true;
    // Configuration
    const config = {
        colors: {
            primary: '#0f87c8',      // Navy blue
            secondary: '#001F2E',    // Orange
            text: '#FFFFFF',         // White text
            textDark: '#FFFFFF',     // Dark text
            background: '#00273C',   // Light background
            userMessage: '#003E5C',  // Light blue for user messages
            botMessage: '#1A1F24'    // Light gray for bot messages
        },
        chatButton: {
            size: '60px',
            bottomMargin: '20px',
            rightMargin: '20px'
        },
        chatWindow: {
            width: '350px',
            height: '450px',
            maxWidth: '90vw',
            maxHeight: '70vh'
        }
    };

    // Bot responses
    const botResponses = [
        "Hi there! How can the Triple G BuildHub team help you today?",
        "Thanks for your message! Someone from our team will get back to you soon.",
        "Would you like to schedule a demo of our construction management platform?",
        "Our BuildHub solution helps streamline communication on construction projects. How can we help with your specific needs?",
        "We specialize in digital solutions for the construction industry. What challenges are you facing?",
        "Would you like to speak to our team?",
        "You can view your project milestone on the dashboard.",
        "To reach your architect, use the Contact page or request an appointment below.",
        "You're currently in the Structural Phase. Estimated completion: August 12, 2025.",
        "Please enter your phone number to schedule a callback."
    ];

    // Add trigger keywords for enhanced response system
    const triggerKeywords = {
        navigation: ['where', 'how do i', 'find', 'locate', 'view'],
        projectStatus: ['project status', 'milestone', 'progress', 'update'],
        support: ['talk to someone', 'need help', 'contact support', 'human', 'representative'],
        appointment: ['schedule', 'appointment', 'meeting', 'call back', 'phone'],
        faqs: ['what is triple g', 'faq', 'question', 'contact information', 'supervisor']
    };

    // Add variables to track chat state
    let currentMode = 'normal';
    let lastResponseType = '';
    let conversationId = null;
    let sessionId = null;
    // Global element references (assigned in init)
    let chatWindow;
    let chatButton;
    let chatMessages;
    let chatInput;
    
    // API Configuration
    const apiEndpoints = {
        sendMessage: '/chat/api/send-message/',
        conversationHistory: '/chat/api/conversation-history/',
        projectStatus: '/chat/api/project-status/',
        submitFeedback: '/chat/api/submit-feedback/',
        createContact: '/chat/api/create-contact/'
    };
    
    // Get CSRF token
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    }

    // Create and append styles
    function createStyles() {
        const styleEl = document.createElement('style');
        styleEl.innerHTML = `
            .tg-chat-button {
                position: fixed;
                bottom: ${config.chatButton.bottomMargin};
                right: ${config.chatButton.rightMargin};
                width: ${config.chatButton.size};
                height: ${config.chatButton.size};
                border-radius: 50%;
                background-color: ${config.colors.secondary};
                color: ${config.colors.text};
                border: none;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .tg-chat-button:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
            }
            .tg-chat-button.pulse {
                animation: tg-pulse 2s infinite;
            }
             @keyframes tg-pulse {
                0% { box-shadow: 0 0 0 0 rgba(0, 132, 255, 0.6); }
                70% { box-shadow: 0 0 0 10px rgba(0, 132, 255, 0); }
                100% { box-shadow: 0 0 0 0 rgba(0, 132, 255, 0); }
            }
            .tg-chat-window {
                position: fixed;
                bottom: calc(${config.chatButton.bottomMargin} + ${config.chatButton.size} + 10px);
                right: ${config.chatButton.rightMargin};
                width: ${config.chatWindow.width};
                height: ${config.chatWindow.height};
                max-width: ${config.chatWindow.maxWidth};
                max-height: ${config.chatWindow.maxHeight};
                background-color: ${config.colors.background};
                border-radius: 12px;
                box-shadow: 0 5px 25px rgba(0, 0, 0, 0.15);
                display: flex;
                flex-direction: column;
                z-index: 9998;
                overflow: hidden;
                transition: all 0.3s ease;
                opacity: 0;
                transform: translateY(20px);
                pointer-events: none;
                font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
            }
            .tg-chat-window.active {
                opacity: 1;
                transform: translateY(0);
                pointer-events: all;
            }
            .tg-chat-header {
                background: linear-gradient(135deg, #0f87c8 0%, #001F2E 100%);
                color: ${config.colors.text};
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
            .tg-chat-title {
                font-weight: 600;
                font-size: 16px;
                margin: 0;
            }
            .tg-chat-close {
                background: none;
                border: none;
                color: ${config.colors.text};
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0.8;
                transition: opacity 0.2s ease;
            }
            .tg-chat-close:hover {
                opacity: 1;
            }
            .tg-chat-messages {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
            }
            .tg-message {
                max-width: 80%;
                padding: 10px 14px;
                margin-bottom: 10px;
                border-radius: 18px;
                line-height: 1.4;
                font-size: 14px;
                word-wrap: break-word;
            }
            .tg-message.user {
                align-self: flex-end;
                background-color: ${config.colors.userMessage};
                color: ${config.colors.textDark};
                border-bottom-right-radius: 5px;
            }
            .tg-message.bot {
                align-self: flex-start;
                background-color: ${config.colors.botMessage};
                color: ${config.colors.textDark};
                border-bottom-left-radius: 5px;
            }
            .tg-chat-input-container {
                padding: 12px 15px;
                border-top: 1px solid rgba(77, 77, 77, 0.08);
                display: flex;
                background-color: #001F2E;
            }
            .tg-chat-input {
                flex: 1;
                border: 1px solid #E0E0E0;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.2s ease;
            }
            .tg-chat-input:focus {
                border-color: ${config.colors.secondary};
            }
            .tg-chat-send {
                background-color: ${config.colors.secondary};
                color: ${config.colors.text};
                border: none;
                border-radius: 50%;
                width: 36px;
                height: 36px;
                margin-left: 10px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background-color 0.2s ease;
            }
            .tg-chat-send:hover {
                background-color: #E07700;
            }
            .tg-chat-send:disabled {
                background-color: #CCCCCC;
                cursor: not-allowed;
            }
            .tg-quick-replies {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 8px;
                margin-bottom: 12px;
            }
            .tg-quick-reply {
                background-color: white;
                border: 1px solid ${config.colors.secondary};
                color: ${config.colors.secondary};
                border-radius: 18px;
                padding: 6px 12px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .tg-quick-reply:hover {
                background-color: ${config.colors.secondary};
                color: white;
            }
            .tg-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10000;
            }
            .tg-contact-form {
                background-color: white;
                border-radius: 8px;
                width: 90%;
                max-width: 500px;
                padding: 20px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }
            /* Responsive adjustments */
            @media (max-width: 480px) {
                .tg-chat-window {
                    width: 90vw;
                    height: 70vh;
                    bottom: 80px;
                    right: 5vw;
                }
                .tg-chat-button {
                    right: 20px;
                }
            }
        `;
        document.head.appendChild(styleEl);
    }

    // Initialize core UI and references
    function init() {
        // Ensure styles exist
        createStyles();
        // Build UI
        chatButton = createChatButton();
        chatWindow = createChatWindow();
        // Capture references
        chatMessages = chatWindow.querySelector('.tg-chat-messages');
        chatInput = chatWindow.querySelector('.tg-chat-input');
    }

    // Create chat button with Triple G logo
     function createChatButton() {
        const button = document.createElement('button');
        button.className = 'tg-chat-button pulse'; // Add styling and animations
        button.setAttribute('aria-label', 'Open chat'); // Accessible label
        // Add the Triple G logo image
        const logo = document.createElement('img');
        logo.src = '/static/images/tripleGlogozoom.jpg'; // Add path to your logo
        logo.alt = 'Chat logo'; // Alternate text for accessibility
        logo.style.width = '100%';
        logo.style.height = '100%';
        logo.style.objectFit = 'cover';
        logo.style.borderRadius = '50%';
        button.appendChild(logo);
        button.addEventListener('click', toggleChatWindow); // Retain event listener
        document.body.appendChild(button);
        return button;
    }

    function createChatWindow() {
    const chatWindow = document.createElement('div');
    chatWindow.className = 'tg-chat-window';

    // Create header
    const header = document.createElement('div');
    header.className = 'tg-chat-header';

    // Add logo beside the title
    const logo = document.createElement('img');
    logo.src = '/static/images/tripleGlogozoom.jpg'; // Path to your Triple G logo
    logo.alt = 'Triple G Logo';
    logo.style.width = '40px'; // Adjust the size of the logo
    logo.style.height = '40px'; // Match width and height for a circle
    logo.style.borderRadius = '50%'; // Makes the image circular
    logo.style.marginRight = '-110px'; // Adds spacing between the logo and title

    const titleContainer = document.createElement('div'); // Container for title and green circle
    titleContainer.style.display = 'flex';
    titleContainer.style.flexDirection = 'column'; // Stack the title and the green circle vertically
    titleContainer.style.alignItems = 'center'; // Center-align elements

    const title = document.createElement('h3');
    title.className = 'tg-chat-title';
    title.textContent = 'Triple G Assistant';
    title.style.margin = '0'; // Remove default margins for cleaner layout
    title.style.marginTop = '7px';
    // Add green active circle below the title
    const activeIndicator = document.createElement('div');
    activeIndicator.className = 'tg-active-indicator'; // Styling class for the green circle
    activeIndicator.style.width = '10px'; // Size of green circle
    activeIndicator.style.height = '10px';
    activeIndicator.style.borderRadius = '50%';
    activeIndicator.style.backgroundColor = '#4ADE80'; // Green color
    activeIndicator.style.marginTop = '0px'; // Add spacing between title and the circle
    activeIndicator.style.marginLeft = '-145px';    
    // Append title and green circle to the title container
    titleContainer.appendChild(title);
    titleContainer.appendChild(activeIndicator);

    const closeButton = document.createElement('button');
    closeButton.className = 'tg-chat-close';
    closeButton.innerHTML = '&times;';
    closeButton.setAttribute('aria-label', 'Close chat');
    closeButton.addEventListener('click', toggleChatWindow);

    // Assemble header
    header.appendChild(logo); // Add logo first
    header.appendChild(titleContainer); // Add title container (title + green circle)
    header.appendChild(closeButton);

    // Create messages container
    const messagesContainer = document.createElement('div');
    messagesContainer.className = 'tg-chat-messages';

    // First message will be injected via addMessage() so it uses typing animation

    // Create input area
    const inputContainer = document.createElement('div');
    inputContainer.className = 'tg-chat-input-container';
    const input = document.createElement('input');
    input.className = 'tg-chat-input';
    input.type = 'text';
    input.placeholder = 'Type your message...';
    input.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && input.value.trim() !== '') {
            sendMessage();
        }
    });
    const sendButton = document.createElement('button');
    sendButton.className = 'tg-chat-send';
    sendButton.setAttribute('aria-label', 'Send message');
    sendButton.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 2L11 13" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    `;
    sendButton.addEventListener('click', sendMessage);
    inputContainer.appendChild(input);
    inputContainer.appendChild(sendButton);

    // Assemble chat window
    chatWindow.appendChild(header);
    chatWindow.appendChild(messagesContainer);
    chatWindow.appendChild(inputContainer);
    document.body.appendChild(chatWindow);
    // Inject greeting as the very first message (with typing animation), once per page load
    setTimeout(() => {
        const hasAnyMessage = !!messagesContainer.querySelector('.tg-message');
        if (!window.__TG_CHATBOT_GREETED__ && !hasAnyMessage && typeof addMessage === 'function') {
            window.__TG_CHATBOT_GREETED__ = true;
            addMessage("👋 Welcome to Triple G BuildHub! How can we assist with your construction management needs today?", 'bot');
        }
    }, 50);
    return chatWindow;
}
    // Toggle chat window
    function toggleChatWindow() {
        chatWindow.classList.toggle('active');
        chatButton.classList.toggle('pulse');
        if (chatWindow.classList.contains('active')) {
            chatInput.focus();
        }
    }

    // Process user query with enhanced response system
    function processUserQuery(message) {
        message = message.toLowerCase();
        
        // Check for navigation queries
        if (triggerKeywords.navigation.some(keyword => message.includes(keyword))) {
            if (message.includes('project') || message.includes('update')) {
                addMessage("You can view your project milestone on the dashboard.", 'bot');
                afterBotMessage(() => {
                    addQuickReplyButtons(['Go to Dashboard', 'View Milestones']);
                });
            } else if (message.includes('architect') || message.includes('contact')) {
                addMessage("To reach your architect, use the Contact page or request an appointment below.", 'bot');
                afterBotMessage(() => {
                    addContactButton();
                });
            } else {
                addMessage("How can I help you navigate our platform? You can ask about projects, contacts, or reports.", 'bot');
            }
            return true;
        }
        
        // Check for project status queries
        if (triggerKeywords.projectStatus.some(keyword => message.includes(keyword))) {
            // Try to get real project status from API
            fetch(apiEndpoints.projectStatus, {
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.projects.length > 0) {
                    const project = data.projects[0];
                    addMessage(`Your project "${project.name}" is currently ${project.status}. Progress: ${project.progress}%`, 'bot');
                } else {
                    addMessage("You're currently in the Structural Phase. Estimated completion: August 12, 2025.", 'bot');
                }
            })
            .catch(() => {
                addMessage("You're currently in the Structural Phase. Estimated completion: August 12, 2025.", 'bot');
            });
            return true;
        }
        
        // Check for support requests
        if (triggerKeywords.support.some(keyword => message.includes(keyword))) {
            addMessage("Would you like to speak to our team?", 'bot');
            afterBotMessage(() => {
                addSupportButtons();
            });
            return true;
        }
        
        // Check for appointment requests
        if (triggerKeywords.appointment.some(keyword => message.includes(keyword))) {
            currentMode = 'awaitingPhoneNumber';
            addMessage("Please enter your phone number to schedule a callback.", 'bot');
            return true;
        }
        
        // Check for FAQ queries
        if (triggerKeywords.faqs.some(keyword => message.includes(keyword))) {
            if (message.includes('what is triple g') || message.includes('buildhub')) {
                addMessage("Triple G BuildHub is a construction management platform that streamlines communication and project oversight for your building projects.", 'bot');
            } else if (message.includes('contact information')) {
                addMessage("You can update your contact information in your profile settings. Would you like me to direct you there?", 'bot');
                afterBotMessage(() => {
                    addQuickReplyButtons(['Go to Profile', 'Not Now']);
                });
            } else if (message.includes('supervisor')) {
                addMessage("Your assigned site supervisor is Michael Rodriguez. Would you like his contact details?", 'bot');
                afterBotMessage(() => {
                    addQuickReplyButtons(['Yes, Please', 'No, Thanks']);
                });
            } else {
                addMessage("I can answer questions about our platform, your account, or your projects. What would you like to know?", 'bot');
            }
            return true;
        }
        
        return false; // No specific trigger found
    }

    // Send message function - Enhanced version with API integration
    function sendMessage() {
        const messageText = chatInput.value.trim();
        if (messageText === '') return;
        
        // Add user message
        addMessage(messageText, 'user');
        chatInput.value = '';
        
        // Handle phone number validation if in that mode
        if (currentMode === 'awaitingPhoneNumber') {
            validatePhoneNumber(messageText);
            return;
        }
        
        // Try API first, fallback to local processing
        sendMessageToAPI(messageText)
            .then(response => {
                if (response.success) {
                    conversationId = response.conversation_id;
                    sessionId = response.session_id;
                    addMessage(response.response, 'bot');
                    refreshMainOptions();
                } else {
                    // Fallback to local processing
                    handleMessageLocally(messageText);
                }
            })
            .catch(error => {
                console.error('API error:', error);
                // Fallback to local processing
                handleMessageLocally(messageText);
            });
    }
    
    // Send message to API
    function sendMessageToAPI(messageText) {
        return fetch(apiEndpoints.sendMessage, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                message: messageText,
                conversation_id: conversationId,
                session_id: sessionId
            })
        })
        .then(response => response.json());
    }
    
    // Handle message locally (fallback)
    function handleMessageLocally(messageText) {
        // Try to process with our enhanced query handler
        const wasProcessed = processUserQuery(messageText);
        
        // If no specific response was triggered, use the random response as before
        if (!wasProcessed) {
            // Simulate typing
            setTimeout(() => {
                const typingIndicator = document.createElement('div');
                typingIndicator.className = 'tg-message bot';
                typingIndicator.textContent = 'Typing...';
                typingIndicator.id = 'typing-indicator';
                chatMessages.appendChild(typingIndicator);
                scrollToBottom();
                
                // Remove typing indicator and add bot response after a delay
                setTimeout(() => {
                    chatMessages.removeChild(typingIndicator);
                    const randomResponse = botResponses[Math.floor(Math.random() * botResponses.length)];
                    addMessage(randomResponse, 'bot');
                    refreshMainOptions();
                }, 1500);
            }, 500);
        }
    }

    // Global delay used for bot typing animation
    const BOT_TYPING_DELAY_MS = 1200;
    function afterBotMessage(callback, extraDelay = 50) {
        setTimeout(callback, BOT_TYPING_DELAY_MS + extraDelay);
    }

    // Add message to chat
    // options: { instant?: boolean, suppressMainRefresh?: boolean }
    function addMessage(text, sender, options = {}) {
        const { instant = false, suppressMainRefresh = false } = options;
        // Helper to inject typing styles once
        function ensureTypingStyles() {
            if (document.getElementById('tg-typing-styles')) return;
            const style = document.createElement('style');
            style.id = 'tg-typing-styles';
            style.textContent = `
                .tg-typing { display: inline-flex; gap: 4px; align-items: center; }
                .tg-typing-dot { width: 6px; height: 6px; border-radius: 50%; background: #ccc; opacity: 0.7; animation: tg-bounce 1s infinite ease-in-out; }
                .tg-typing-dot:nth-child(2) { animation-delay: 0.15s; }
                .tg-typing-dot:nth-child(3) { animation-delay: 0.3s; }
                @keyframes tg-bounce { 0%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-4px); } }
            `;
            document.head.appendChild(style);
        }

        if (sender === 'bot') {
            if (instant) {
                // Immediate render without typing animation (used for restoring history)
                const message = document.createElement('div');
                message.className = 'tg-message bot';
                message.textContent = text;
                chatMessages.appendChild(message);
                scrollToBottom();
                // Do not refresh main options during history restore
                return;
            }
            // Show typing indicator for ~1.2s before rendering bot message
            ensureTypingStyles();
            const typingWrapper = document.createElement('div');
            typingWrapper.className = 'tg-message bot';
            const typing = document.createElement('div');
            typing.className = 'tg-typing';
            typing.innerHTML = '<span class="tg-typing-dot"></span><span class="tg-typing-dot"></span><span class="tg-typing-dot"></span>';
            typingWrapper.appendChild(typing);
            chatMessages.appendChild(typingWrapper);
            scrollToBottom();

            setTimeout(() => {
                // Replace typing with actual bot message
                if (typingWrapper.parentNode === chatMessages) {
                    chatMessages.removeChild(typingWrapper);
                }
                const message = document.createElement('div');
                message.className = 'tg-message bot';
                message.textContent = text;
                chatMessages.appendChild(message);
                scrollToBottom();
                // After bot response, re-show the main options (unless awaiting phone input)
                if (!suppressMainRefresh && typeof refreshMainOptions === 'function' && currentMode !== 'awaitingPhoneNumber') {
                    const hasMainContainer = !!chatMessages.querySelector('.tg-quick-replies-container');
                    if (!hasMainContainer) {
                        setTimeout(() => { refreshMainOptions(); }, 0);
                    }
                }
            }, BOT_TYPING_DELAY_MS);
            return;
        }

        // Default immediate render for non-bot messages
        const message = document.createElement('div');
        message.className = `tg-message ${sender}`;
        message.textContent = text;
        chatMessages.appendChild(message);
        scrollToBottom();
    }

    // Add quick reply buttons
    function addQuickReplyButtons(options) {
        const quickRepliesContainer = document.createElement('div');
        quickRepliesContainer.className = 'tg-quick-replies';
        
        options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'tg-quick-reply';
            button.textContent = option;
            button.addEventListener('click', () => {
                // Add the selected option as a user message
                addMessage(option, 'user');
                // Remove this set of quick replies
                if (quickRepliesContainer.parentNode === chatMessages) {
                    chatMessages.removeChild(quickRepliesContainer);
                }
                // Process the selected option
                processUserQuery(option);
            });
            quickRepliesContainer.appendChild(button);
        });
        
        chatMessages.appendChild(quickRepliesContainer);
        scrollToBottom();
    }
    
    // Ensure the main quick reply options are visible (debounced to avoid duplicates)
    let refreshScheduled = false;
    function refreshMainOptions() {
        if (currentMode === 'awaitingPhoneNumber') return; // avoid during phone input
        if (refreshScheduled) return; // debounce
        refreshScheduled = true;
        setTimeout(() => {
            // Remove any existing MAIN quick reply container to prevent duplicates
            const existing = chatMessages.querySelectorAll('.tg-quick-replies-container');
            existing.forEach(el => {
                if (el.parentNode === chatMessages) {
                    chatMessages.removeChild(el);
                }
            });
            // Re-add the main quick replies
            addQuickReplies();
            scrollToBottom();
            refreshScheduled = false;
        }, 60);
    }

    // Add contact button
    function addContactButton() {
        const contactButton = document.createElement('button');
        contactButton.className = 'tg-quick-reply';
        contactButton.textContent = 'Contact Us';
        contactButton.style.backgroundColor = config.colors.secondary;
        contactButton.style.color = config.colors.text;
        contactButton.style.padding = '8px 15px';
        contactButton.style.marginTop = '10px';
        contactButton.style.display = 'block';
        
        contactButton.addEventListener('click', () => {
            openContactForm();
        });
        
        const container = document.createElement('div');
        container.className = 'tg-quick-replies';
        container.appendChild(contactButton);
        chatMessages.appendChild(container);
        scrollToBottom();
    }

    // Add support buttons
    function addSupportButtons() {
        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'tg-quick-replies';
        
        const callButton = document.createElement('button');
        callButton.className = 'tg-quick-reply';
        callButton.textContent = 'Call Support';
        callButton.addEventListener('click', () => {
            addMessage('Call Support', 'user');
            chatMessages.removeChild(buttonsContainer);
            addMessage("Our support team is available Mon-Fri, 8am-6pm EST at (555) 123-4567.", 'bot');
        });
        
        const messageButton = document.createElement('button');
        messageButton.className = 'tg-quick-reply';
        messageButton.textContent = 'Leave a Message';
        messageButton.addEventListener('click', () => {
            addMessage('Leave a Message', 'user');
            chatMessages.removeChild(buttonsContainer);
            openContactForm();
        });
        
        const notifyButton = document.createElement('button');
        notifyButton.className = 'tg-quick-reply';
        notifyButton.textContent = 'Notify Admin';
        notifyButton.addEventListener('click', () => {
            addMessage('Notify Admin', 'user');
            chatMessages.removeChild(buttonsContainer);
            simulateAdminNotification();
        });
        
        buttonsContainer.appendChild(callButton);
        buttonsContainer.appendChild(messageButton);
        buttonsContainer.appendChild(notifyButton);
        
        chatMessages.appendChild(buttonsContainer);
        scrollToBottom();
    }

    // Validate phone number
    function validatePhoneNumber(phoneNumber) {
        // Simple phone validation (11 digits)
        const phoneRegex = /^\d{11}$/;
        
        if (phoneRegex.test(phoneNumber.replace(/\D/g, ''))) {
            addMessage("Thanks! A member of our team will call you back at " + phoneNumber + " within one business day.", 'bot');
            currentMode = 'normal';
            simulateAdminNotification();
        } else {
            addMessage("That doesn't look like a valid 11-digit phone number. Please try again or type 'cancel' to go back.", 'bot');
        }
    }

    // Load conversation history on init
    function loadConversationHistory() {
        const params = new URLSearchParams();
        if (conversationId) params.append('conversation_id', conversationId);
        if (sessionId) params.append('session_id', sessionId);
        
        if (params.toString()) {
            fetch(`${apiEndpoints.conversationHistory}?${params.toString()}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.messages.length > 0) {
                        // Clear existing messages
                        chatMessages.innerHTML = '';
                        window.__TG_CHATBOT_GREETED__ = true;
                        
                        // Add messages from history
                        data.messages.forEach(msg => {
                            addMessage(msg.message_text, msg.sender_type, { instant: true });
                        });
                        
                        conversationId = data.conversation_id;
                        scrollToBottom();
                    }
                })
                .catch(error => console.error('Error loading history:', error));
        }
    }
    
    // Submit feedback to API
    function submitFeedback(messageId, rating, feedbackText = '') {
        fetch(apiEndpoints.submitFeedback, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                message_id: messageId,
                rating: rating,
                feedback_text: feedbackText
            })
        })
        .catch(error => console.error('Error submitting feedback:', error));
    }
    
    // Open contact form
    function openContactForm() {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'tg-overlay';
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                document.body.removeChild(overlay);
            }
        });
        
        // Create form container
        const formContainer = document.createElement('div');
        formContainer.className = 'tg-contact-form';
        formContainer.addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        // Create form header
        const formHeader = document.createElement('div');
        formHeader.style.display = 'flex';
        formHeader.style.justifyContent = 'space-between';
        formHeader.style.alignItems = 'center';
        formHeader.style.marginBottom = '20px';
        
        const formTitle = document.createElement('h3');
        formTitle.textContent = 'Contact Triple G BuildHub';
        formTitle.style.margin = '0';
        formTitle.style.color = config.colors.primary;
        
        const closeFormButton = document.createElement('button');
        closeFormButton.innerHTML = '&times;';
        closeFormButton.style.background = 'none';
        closeFormButton.style.border = 'none';
        closeFormButton.style.fontSize = '24px';
        closeFormButton.style.cursor = 'pointer';
        closeFormButton.style.padding = '0';
        closeFormButton.style.lineHeight = '1';
        closeFormButton.addEventListener('click', () => {
            document.body.removeChild(overlay);
        });
        
        formHeader.appendChild(formTitle);
        formHeader.appendChild(closeFormButton);
        
        // Create form
        const form = document.createElement('form');
        form.onsubmit = (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const contactData = {
                name: formData.get('name'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                subject: 'Chat Contact Form',
                message: formData.get('message')
            };
            
            // Submit to API
            fetch(apiEndpoints.createContact, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(contactData)
            })
            .then(response => response.json())
            .then(data => {
                document.body.removeChild(overlay);
                if (data.success) {
                    addMessage("Thanks for your message! Our team will get back to you soon.", 'bot');
                } else {
                    addMessage("Sorry, there was an error sending your message. Please try again.", 'bot');
                }
                simulateAdminNotification();
            })
            .catch(error => {
                console.error('Error submitting contact form:', error);
                document.body.removeChild(overlay);
                addMessage("Thanks for your message! Our team will get back to you soon.", 'bot');
                simulateAdminNotification();
            });
        };
        
        // Create form fields
        const nameField = createFormField('text', 'name', 'Your Name', true);
        const emailField = createFormField('email', 'email', 'Email Address', true);
        const phoneField = createFormField('tel', 'phone', 'Phone Number', false);
        
        const messageLabel = document.createElement('label');
        messageLabel.textContent = 'Your Message';
        messageLabel.style.display = 'block';
        messageLabel.style.marginBottom = '5px';
        messageLabel.style.color = config.colors.textDark;
        
        const messageInput = document.createElement('textarea');
        messageInput.name = 'message';
        messageInput.placeholder = 'How can we help you?';
        messageInput.required = true;
        messageInput.rows = 4;
        messageInput.style.width = '100%';
        messageInput.style.padding = '8px';
        messageInput.style.borderRadius = '5px';
        messageInput.style.border = '1px solid #ddd';
        messageInput.style.boxSizing = 'border-box';
        messageInput.style.marginBottom = '15px';
        messageInput.style.fontFamily = 'inherit';
        messageInput.style.resize = 'vertical';
        
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.textContent = 'Submit';
        submitButton.style.backgroundColor = config.colors.secondary;
        submitButton.style.color = config.colors.text;
        submitButton.style.border = 'none';
        submitButton.style.borderRadius = '5px';
        submitButton.style.padding = '10px 15px';
        submitButton.style.marginTop = '15px';
        submitButton.style.cursor = 'pointer';
        submitButton.style.width = '100%';
        
        // Assemble form
        form.appendChild(nameField);
        form.appendChild(emailField);
        form.appendChild(phoneField);
        form.appendChild(messageLabel);
        form.appendChild(messageInput);
        form.appendChild(submitButton);
        
        // Assemble form container
        formContainer.appendChild(formHeader);
        formContainer.appendChild(form);
        
        // Add to overlay
        overlay.appendChild(formContainer);
        
        // Add to document
        document.body.appendChild(overlay);
    }

    // Helper function to create form fields
    function createFormField(type, name, placeholder, required) {
        const container = document.createElement('div');
        container.style.marginBottom = '10px';
        
        const label = document.createElement('label');
        label.textContent = placeholder;
        label.style.display = 'block';
        label.style.marginBottom = '5px';
        label.style.color = config.colors.textDark;
        
        const input = document.createElement('input');
        input.type = type;
        input.name = name;
        input.placeholder = placeholder;
        input.required = required;
        input.style.width = '100%';
        input.style.padding = '8px';
        input.style.borderRadius = '5px';
        input.style.border = '1px solid #ddd';
        input.style.boxSizing = 'border-box';
        
        container.appendChild(label);
        container.appendChild(input);
        
        return container;
    }

    // Function to simulate admin notification
    function simulateAdminNotification() {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'tg-notification';
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.backgroundColor = config.colors.primary;
        notification.style.color = config.colors.text;
        notification.style.padding = '15px';
        notification.style.borderRadius = '5px';
        notification.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.2)';
        notification.style.zIndex = '10000';
        notification.style.display = 'flex';
        notification.style.alignItems = 'center';
        notification.style.transform = 'translateX(120%)';
        notification.style.transition = 'transform 0.3s ease';
        
        const notificationIcon = document.createElement('div');
        notificationIcon.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 22C13.1046 22 14 21.1046 14 20H10C10 21.1046 10.8954 22 12 22Z" fill="white"/><path d="M18 16V11C18 7.93 16.36 5.36 13.5 4.68V4C13.5 3.17 12.83 2.5 12 2.5C11.17 2.5 10.5 3.17 10.5 4V4.68C7.63 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z" fill="white"/></svg>';
        notificationIcon.style.marginRight = '10px';
        
        const notificationText = document.createElement('div');
        notificationText.innerHTML = '<strong>Admin Notification</strong><br>A new customer message has been received';
        
        notification.appendChild(notificationIcon);
        notification.appendChild(notificationText);
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            
            // Auto dismiss after 5 seconds
            setTimeout(() => {
                notification.style.transform = 'translateX(120%)';
                
                // Remove from DOM after animation
                setTimeout(() => {
                    if (document.body.contains(notification)) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }, 5000);
        }, 100);
    }

    // Function to add preset quick replies
    function addQuickReplies() {
        const options = [
            "Project Status",
            "Contact Support",
            "Schedule Call",
            "FAQ"
        ];
        
        // If main quick replies already exist, avoid adding duplicates
        const existingMain = chatMessages.querySelector('.tg-quick-replies-container');
        if (existingMain) {
            return;
        }
        const quickRepliesContainer = document.createElement('div');
        quickRepliesContainer.className = 'tg-quick-replies-container';
        quickRepliesContainer.style.display = 'flex';
        quickRepliesContainer.style.flexWrap = 'wrap';
        quickRepliesContainer.style.gap = '8px';
        quickRepliesContainer.style.marginTop = '10px';
        quickRepliesContainer.style.marginBottom = '10px';
        
        options.forEach(option => {
            const quickReply = document.createElement('button');
            quickReply.className = 'tg-quick-reply';
            quickReply.textContent = option;
            quickReply.style.backgroundColor = '#E1E1E1';
            quickReply.style.border = 'none';
            quickReply.style.borderRadius = '16px';
            quickReply.style.padding = '8px 14px';
            quickReply.style.fontSize = '13px';
            quickReply.style.cursor = 'pointer';
            quickReply.style.transition = 'background-color 0.2s ease';
            
            quickReply.addEventListener('mouseenter', () => {
                quickReply.style.backgroundColor = '#D0D0D0';
            });
            
            quickReply.addEventListener('mouseleave', () => {
                quickReply.style.backgroundColor = '#E1E1E1';
            });
            
            quickReply.addEventListener('click', () => {
                addMessage(option, 'user');
                chatMessages.removeChild(quickRepliesContainer);
                processUserQuery(option);
            });
            
            quickRepliesContainer.appendChild(quickReply);
        });
        
        chatMessages.appendChild(quickRepliesContainer);
        scrollToBottom();
    }

    // Function to show project status visualization
    function showProjectStatus() {
        const statusContainer = document.createElement('div');
        statusContainer.className = 'tg-status-container';
        statusContainer.style.backgroundColor = 'white';
        statusContainer.style.borderRadius = '10px';
        statusContainer.style.padding = '15px';
        statusContainer.style.margin = '10px 0';
        statusContainer.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
        statusContainer.style.maxWidth = '100%';
        statusContainer.style.alignSelf = 'flex-start';
        
        const statusHeader = document.createElement('div');
        statusHeader.style.display = 'flex';
        statusHeader.style.justifyContent = 'space-between';
        statusHeader.style.alignItems = 'center';
        statusHeader.style.marginBottom = '10px';
        
        const statusTitle = document.createElement('h4');
        statusTitle.textContent = 'Project Timeline';
        statusTitle.style.margin = '0';
        statusTitle.style.color = config.colors.primary;
        
        const phaseInfo = document.createElement('span');
        phaseInfo.textContent = 'Current: Structural Phase';
        phaseInfo.style.fontSize = '12px';
        phaseInfo.style.color = config.colors.secondary;
        phaseInfo.style.fontWeight = 'bold';
        
        statusHeader.appendChild(statusTitle);
        statusHeader.appendChild(phaseInfo);
        
        // Create progress bar
        const progressContainer = document.createElement('div');
        progressContainer.style.height = '25px';
        progressContainer.style.backgroundColor = '#e0e0e0';
        progressContainer.style.borderRadius = '12px';
        progressContainer.style.overflow = 'hidden';
        progressContainer.style.marginBottom = '10px';
        progressContainer.style.position = 'relative';
        
        const progressBar = document.createElement('div');
        progressBar.style.width = '45%';
        progressBar.style.height = '100%';
        progressBar.style.backgroundColor = config.colors.secondary;
        progressBar.style.borderRadius = '12px';
        progressBar.style.transition = 'width 1s ease-in-out';
        
        const progressText = document.createElement('div');
        progressText.textContent = '45% Complete';
        progressText.style.position = 'absolute';
        progressText.style.top = '0';
        progressText.style.left = '0';
        progressText.style.right = '0';
        progressText.style.bottom = '0';
        progressText.style.display = 'flex';
        progressText.style.alignItems = 'center';
        progressText.style.justifyContent = 'center';
        progressText.style.color = '#000';
        progressText.style.fontWeight = 'bold';
        progressText.style.fontSize = '12px';
        
        progressContainer.appendChild(progressBar);
        progressContainer.appendChild(progressText);
        
        // Create phases
        const phases = [
            { name: 'Planning', complete: true },
            { name: 'Design', complete: true },
            { name: 'Foundation', complete: true },
            { name: 'Structural', complete: false, current: true },
            { name: 'Mechanical', complete: false },
            { name: 'Finishing', complete: false }
        ];
        
        const phasesContainer = document.createElement('div');
        phasesContainer.style.display = 'flex';
        phasesContainer.style.justifyContent = 'space-between';
        phasesContainer.style.marginTop = '15px';
        
        phases.forEach((phase, index) => {
            const phaseElement = document.createElement('div');
            phaseElement.style.display = 'flex';
            phaseElement.style.flexDirection = 'column';
            phaseElement.style.alignItems = 'center';
            
            const phaseCircle = document.createElement('div');
            phaseCircle.style.width = '16px';
            phaseCircle.style.height = '16px';
            phaseCircle.style.borderRadius = '50%';
            
            if (phase.complete) {
                phaseCircle.style.backgroundColor = '#4CAF50';
            } else if (phase.current) {
                phaseCircle.style.backgroundColor = config.colors.secondary;
            } else {
                phaseCircle.style.backgroundColor = '#e0e0e0';
            }
            
            const phaseLabel = document.createElement('span');
            phaseLabel.textContent = phase.name;
            phaseLabel.style.fontSize = '10px';
            phaseLabel.style.marginTop = '5px';
            phaseLabel.style.fontWeight = phase.current ? 'bold' : 'normal';
            
            phaseElement.appendChild(phaseCircle);
            phaseElement.appendChild(phaseLabel);
            phasesContainer.appendChild(phaseElement);
            
            // Add connector lines between phases
            if (index < phases.length - 1) {
                const connector = document.createElement('div');
                connector.style.height = '2px';
                connector.style.backgroundColor = '#e0e0e0';
                connector.style.flex = '1';
                connector.style.alignSelf = 'center';
                connector.style.margin = '0 2px';
            }
        });
        
       // Estimated completion date
        const completionDate = document.createElement('div');
        completionDate.style.marginTop = '15px';
        completionDate.style.textAlign = 'right';
        completionDate.style.fontSize = '12px';
        completionDate.style.color = config.colors.textDark;
        completionDate.innerHTML = '<strong>Estimated Completion:</strong> August 12, 2025';
        
        // Assemble status container
        statusContainer.appendChild(statusHeader);
        statusContainer.appendChild(progressContainer);
        statusContainer.appendChild(phasesContainer);
        statusContainer.appendChild(completionDate);
        
        // Add button to view detailed timeline
        const viewDetailsButton = document.createElement('button');
        viewDetailsButton.textContent = 'View Detailed Timeline';
        viewDetailsButton.style.backgroundColor = 'transparent';
        viewDetailsButton.style.color = config.colors.primary;
        viewDetailsButton.style.border = `1px solid ${config.colors.primary}`;
        viewDetailsButton.style.borderRadius = '5px';
        viewDetailsButton.style.padding = '8px 12px';
        viewDetailsButton.style.marginTop = '15px';
        viewDetailsButton.style.cursor = 'pointer';
        viewDetailsButton.style.display = 'block';
        viewDetailsButton.style.width = '100%';
        viewDetailsButton.style.transition = 'background-color 0.2s ease, color 0.2s ease';
        
        viewDetailsButton.addEventListener('mouseenter', () => {
            viewDetailsButton.style.backgroundColor = config.colors.primary;
            viewDetailsButton.style.color = 'white';
        });
        
        viewDetailsButton.addEventListener('mouseleave', () => {
            viewDetailsButton.style.backgroundColor = 'transparent';
            viewDetailsButton.style.color = config.colors.primary;
        });
        
        viewDetailsButton.addEventListener('click', () => {
            // This would typically link to a detailed timeline view
            addMessage("Opening detailed timeline view...", 'bot');
        });
        
        statusContainer.appendChild(viewDetailsButton);
        
        return statusContainer;
    }

    // Scroll messages container to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Initialize the chatbot
    function init() {
        // Create styles
        createStyles();
        
        // Create chat button
        chatButton = createChatButton();
        
        // Create chat window
        chatWindow = createChatWindow();
        
        // Get references to DOM elements
        chatMessages = document.querySelector('.tg-chat-messages');
        chatInput = document.querySelector('.tg-chat-input');
        
        // Add quick replies after a short delay
        setTimeout(() => {
            addQuickReplies();
        }, 1000);
        
        // Add event listener for window resize
        window.addEventListener('resize', () => {
            if (chatWindow.classList.contains('active')) {
                scrollToBottom();
            }
        });
        
        // Handle ESC key to close chat
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && chatWindow.classList.contains('active')) {
                toggleChatWindow();
            }
        });
        
        // Add analytics tracking
        trackChatbotUsage();
    }
    
    // Analytics tracking
    function trackChatbotUsage() {
        // Check if analytics is available
        if (typeof window.dataLayer !== 'undefined') {
            window.dataLayer.push({
                'event': 'chatbot_loaded',
                'chatbot_name': 'Triple G BuildHub Chatbot'
            });
            
            // Track when chatbot is opened
            chatButton.addEventListener('click', () => {
                if (!chatWindow.classList.contains('active')) {
                    window.dataLayer.push({
                        'event': 'chatbot_open',
                        'chatbot_name': 'Triple G BuildHub Chatbot'
                    });
                }
            });
        }
    }
    
    // Enhanced user interaction tracking
    function trackUserInteraction(interactionType, details = {}) {
        if (typeof window.dataLayer !== 'undefined') {
            window.dataLayer.push({
                'event': 'chatbot_interaction',
                'chatbot_name': 'Triple G BuildHub Chatbot',
                'interaction_type': interactionType,
                ...details
            });
        }
        
        // For internal analytics
        const timestamp = new Date().toISOString();
        const interactionData = {
            timestamp,
            type: interactionType,
            details,
            sessionId: getOrCreateSessionId()
        };
        
        // Store in local storage for persistence (could be sent to server instead)
        const interactionsKey = 'tg_chatbot_interactions';
        let interactions = JSON.parse(localStorage.getItem(interactionsKey) || '[]');
        interactions.push(interactionData);
        
        // Keep only last 100 interactions
        if (interactions.length > 100) {
            interactions = interactions.slice(-100);
        }
        
        localStorage.setItem(interactionsKey, JSON.stringify(interactions));
    }
    
    // Get or create session ID
    function getOrCreateSessionId() {
        const sessionKey = 'tg_chatbot_session_id';
        let sessionId = localStorage.getItem(sessionKey);
        
        if (!sessionId) {
            sessionId = 'session_' + Math.random().toString(36).substring(2, 15);
            localStorage.setItem(sessionKey, sessionId);
        }
        
        return sessionId;
    }
    
    // Add chat history persistence
    function saveChat() {
        // Get all messages
        const messages = [];
        document.querySelectorAll('.tg-message').forEach(messageEl => {
            if (!messageEl.id || messageEl.id !== 'typing-indicator') {
                messages.push({
                    type: messageEl.classList.contains('user') ? 'user' : 'bot',
                    text: messageEl.textContent
                });
            }
        });
        
        // Save to local storage
        localStorage.setItem('tg_chatbot_history', JSON.stringify(messages));
    }
    
    // Load chat history
    function loadChat() {
        const savedChat = localStorage.getItem('tg_chatbot_history');
        if (savedChat) {
            const messages = JSON.parse(savedChat);
            if (messages && messages.length) {
                // Prevent greeting when history exists
                window.__TG_CHATBOT_GREETED__ = true;
            }
            // Clear existing welcome message
            chatMessages.innerHTML = '';
            
            // Add saved messages
            messages.forEach(message => {
                // Render instantly and suppress side effects when restoring history
                addMessage(message.text, message.type, { instant: true, suppressMainRefresh: true });
            });
            // Ensure we are scrolled to the latest message
            scrollToBottom();
        }
    }
    
    // Auto reopen chat if previous session was active
    function checkPreviousSession() {
        const wasActive = localStorage.getItem('tg_chatbot_active') === 'true';
        if (wasActive) {
            setTimeout(() => {
                toggleChatWindow();
            }, 2000);
        }
    }
    
    // Store chat state when window is closed
    window.addEventListener('beforeunload', () => {
        localStorage.setItem('tg_chatbot_active', chatWindow.classList.contains('active'));
        saveChat();
    });
    
    // Add feedback functionality
    function addFeedbackOption() {
        const feedbackContainer = document.createElement('div');
        feedbackContainer.className = 'tg-feedback-container';
        feedbackContainer.style.display = 'flex';
        feedbackContainer.style.justifyContent = 'center';
        feedbackContainer.style.marginTop = '15px';
        feedbackContainer.style.marginBottom = '10px';
        
        const feedbackText = document.createElement('span');
        feedbackText.textContent = 'Was this helpful?';
        feedbackText.style.fontSize = '12px';
        feedbackText.style.marginRight = '10px';
        
        const thumbsUpButton = document.createElement('button');
        thumbsUpButton.innerHTML = '👍';
        thumbsUpButton.style.background = 'none';
        thumbsUpButton.style.border = 'none';
        thumbsUpButton.style.fontSize = '16px';
        thumbsUpButton.style.cursor = 'pointer';
        thumbsUpButton.style.padding = '0 5px';
        thumbsUpButton.style.opacity = '0.7';
        thumbsUpButton.style.transition = 'opacity 0.2s ease';
        
        thumbsUpButton.addEventListener('mouseenter', () => {
            thumbsUpButton.style.opacity = '1';
        });
        
        thumbsUpButton.addEventListener('mouseleave', () => {
            thumbsUpButton.style.opacity = '0.7';
        });
        
        thumbsUpButton.addEventListener('click', () => {
            handleFeedback(true);
            chatMessages.removeChild(feedbackContainer);
        });
        
        const thumbsDownButton = document.createElement('button');
        thumbsDownButton.innerHTML = '👎';
        thumbsDownButton.style.background = 'none';
        thumbsDownButton.style.border = 'none';
        thumbsDownButton.style.fontSize = '16px';
        thumbsDownButton.style.cursor = 'pointer';
        thumbsDownButton.style.padding = '0 5px';
        thumbsDownButton.style.opacity = '0.7';
        thumbsDownButton.style.transition = 'opacity 0.2s ease';
        
        thumbsDownButton.addEventListener('mouseenter', () => {
            thumbsDownButton.style.opacity = '1';
        });
        
        thumbsDownButton.addEventListener('mouseleave', () => {
            thumbsDownButton.style.opacity = '0.7';
        });
        
        thumbsDownButton.addEventListener('click', () => {
            handleFeedback(false);
            chatMessages.removeChild(feedbackContainer);
        });
        
        feedbackContainer.appendChild(feedbackText);
        feedbackContainer.appendChild(thumbsUpButton);
        feedbackContainer.appendChild(thumbsDownButton);
        
        chatMessages.appendChild(feedbackContainer);
        scrollToBottom();
    }
    
    // Handle feedback
    function handleFeedback(isPositive) {
        // Track feedback
        trackUserInteraction('feedback', { isPositive });
        
        if (isPositive) {
            addMessage("Thanks for your feedback! We're glad we could help.", 'bot');
        } else {
            addMessage("Thanks for your feedback. Would you like to tell us how we can improve?", 'bot');
            
            const improveOptions = ['Too slow', 'Didn\'t answer my question', 'Technical problem', 'Other'];
            addQuickReplyButtons(improveOptions);
        }
    }
    
    // Add voice messaging capability
    function addVoiceMessaging() {
        // Create voice button
        const voiceButton = document.createElement('button');
        voiceButton.className = 'tg-voice-button';
        voiceButton.setAttribute('aria-label', 'Voice message');
        voiceButton.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 15C13.66 15 15 13.66 15 12V5C15 3.34 13.66 2 12 2C10.34 2 9 3.34 9 5V12C9 13.66 10.34 15 12 15Z" stroke="${config.colors.primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M19 10V12C19 16.42 15.42 20 11 20C6.58 20 3 16.42 3 12V10" stroke="${config.colors.primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 20V22" stroke="${config.colors.primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
        voiceButton.style.backgroundColor = 'transparent';
        voiceButton.style.border = 'none';
        voiceButton.style.cursor = 'pointer';
        voiceButton.style.marginRight = '10px';
        voiceButton.style.padding = '5px';
        voiceButton.style.borderRadius = '50%';
        voiceButton.style.transition = 'background-color 0.2s ease';
        
        voiceButton.addEventListener('mouseenter', () => {
            voiceButton.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
        });
        
        voiceButton.addEventListener('mouseleave', () => {
            voiceButton.style.backgroundColor = 'transparent';
        });
        
        // Insert button before input
        const inputContainer = document.querySelector('.tg-chat-input-container');
        inputContainer.insertBefore(voiceButton, chatInput);
        
        // Voice recording functionality would require additional implementation
        // This is just a placeholder for the UI element
        voiceButton.addEventListener('click', () => {
            // Check if browser supports speech recognition
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                startVoiceRecognition(voiceButton);
            } else {
                addMessage("Sorry, voice messaging is not supported in your browser.", 'bot');
            }
        });
    }
    
    // Start speech recognition (modern browsers)
    function startVoiceRecognition(voiceButton) {
        // Initialize recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        // Change button to indicate recording
        voiceButton.style.backgroundColor = '#ff3b30';
        voiceButton.style.animation = 'tg-pulse 1.5s infinite';
        voiceButton.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" fill="white"/>
                <rect x="9" y="9" width="6" height="6" rx="1" fill="#ff3b30"/>
            </svg>
        `;
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
        };
        
        recognition.onend = () => {
            // Restore button
            voiceButton.style.backgroundColor = 'transparent';
            voiceButton.style.animation = '';
            voiceButton.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 15C13.66 15 15 13.66 15 12V5C15 3.34 13.66 2 12 2C10.34 2 9 3.34 9 5V12C9 13.66 10.34 15 12 15Z" stroke="${config.colors.primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M19 10V12C19 16.42 15.42 20 11 20C6.58 20 3 16.42 3 12V10" stroke="${config.colors.primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 20V22" stroke="${config.colors.primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `;
            
            // Auto-send if we got text
            if (chatInput.value.trim() !== '') {
                sendMessage();
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            // Restore button
            voiceButton.style.backgroundColor = 'transparent';
            voiceButton.style.animation = '';
            // Default icon
            voiceButton.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 15C13.66 15 15 13.66 15 12V5C15 3.34 13.66 2 12 2C10.34 2 9 3.34 9 5V12C9 13.66 10.34 15 12 15Z" stroke="${config.colors.primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M19 10V12C19 16.42 15.42 20 11 20C6.58 20 3 16.42 3 12V10" stroke="${config.colors.primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 20V22" stroke="${config.colors.primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `;
            
            addMessage("Sorry, I couldn't hear you. Please try again or type your message.", 'bot');
        };
        
        // Start listening
        recognition.start();
        
        // Stop recording if user clicks the button again
        voiceButton.addEventListener('click', function stopListening() {
            recognition.stop();
            voiceButton.removeEventListener('click', stopListening);
        }, { once: true });
    }
    
    // Add file attachment capability
    function addFileAttachment() {
        // Create file button
        const fileButton = document.createElement('button');
        fileButton.className = 'tg-file-button';
        fileButton.setAttribute('aria-label', 'Attach file');
        fileButton.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21.44 11.05L12.25 20.24C11.16 21.33 9.65 21.93 8.07 21.93C6.49 21.93 4.97 21.33 3.87 20.24C2.77 19.14 2.17 17.63 2.17 16.05C2.17 14.47 2.77 12.96 3.87 11.86L13.05 2.68C13.7 2.03 14.56 1.67 15.45 1.67C16.34 1.67 17.2 2.03 17.85 2.68C18.5 3.33 18.86 4.19 18.86 5.08C18.86 5.97 18.5 6.83 17.85 7.48L8.66 16.67C8.34 16.99 7.9 17.17 7.45 17.17C7 17.17 6.56 16.99 6.24 16.67C5.92 16.35 5.74 15.91 5.74 15.46C5.74 15.01 5.92 14.57 6.24 14.25L14.83 5.66" stroke="${config.colors.primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
        fileButton.style.backgroundColor = 'transparent';
        fileButton.style.border = 'none';
        fileButton.style.cursor = 'pointer';
        fileButton.style.marginRight = '10px';
        fileButton.style.padding = '5px';
        fileButton.style.borderRadius = '50%';
        fileButton.style.transition = 'background-color 0.2s ease';
        
        fileButton.addEventListener('mouseenter', () => {
            fileButton.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
        });
        
        fileButton.addEventListener('mouseleave', () => {
            fileButton.style.backgroundColor = 'transparent';
        });
        
        // Create hidden file input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.style.display = 'none';
        fileInput.accept = '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png';
        
        fileInput.addEventListener('change', () => {
            if (fileInput.files && fileInput.files[0]) {
                const file = fileInput.files[0];
                // Show file in chat (for demo purposes)
                addMessage(`Attached file: ${file.name}`, 'user');
                addMessage("Thanks for your file. Our team will review it soon.", 'bot');
                
                // In a real implementation, you would upload this file to your server
                // For this demo, we're just showing the UI interaction
            }
        });
        
        // Insert elements
        const inputContainer = document.querySelector('.tg-chat-input-container');
        inputContainer.insertBefore(fileButton, chatInput);
        document.body.appendChild(fileInput);
        
        fileButton.addEventListener('click', () => {
            fileInput.click();
        });
    }
    
    // Check if mobile device
    function isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    // Apply mobile-specific adjustments
    function applyMobileAdjustments() {
        if (isMobile()) {
            // Make chat window full-width on very small screens
            if (window.innerWidth < 400) {
                chatWindow.style.width = '100%';
                chatWindow.style.height = '70vh';
                chatWindow.style.right = '0';
                chatWindow.style.bottom = '0';
                chatWindow.style.borderRadius = '12px 12px 0 0';
                
                // Move chat button
                chatButton.style.right = '15px';
                chatButton.style.bottom = '15px';
            }
            
            // Add swipe-down-to-close functionality
            let startY, endY;
            const header = document.querySelector('.tg-chat-header');
            
            header.addEventListener('touchstart', (e) => {
                startY = e.touches[0].clientY;
            });
            
            header.addEventListener('touchmove', (e) => {
                endY = e.touches[0].clientY;
            });
            
            header.addEventListener('touchend', () => {
                if (endY - startY > 50) {
                    // Swipe down detected
                    toggleChatWindow();
                }
            });
        }
    }
    
    // Initialize on DOM content loaded
    document.addEventListener('DOMContentLoaded', () => {
        // Initialize chatbot
        init();
        // Load conversation history from API
        setTimeout(() => {
            loadConversationHistory();
        }, 500);
        // Load previous chat if available (fallback)
        loadChat();
        // Check previous session state
        checkPreviousSession();
        // Add voice messaging capability
        addVoiceMessaging();
        // Add file attachment capability
        addFileAttachment();
        // Apply mobile adjustments
        applyMobileAdjustments();
    });
})();