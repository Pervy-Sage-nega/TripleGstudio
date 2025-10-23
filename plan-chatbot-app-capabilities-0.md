I have created the following plan after thorough exploration and analysis of the codebase. Follow the below plan verbatim. Trust the files and references. Do not re-verify what's written in the plan. Explore only when absolutely necessary. First implement all the proposed file changes and then I'll review all the changes together at the end.

### Observations

## Current State Analysis

The chatbot app has a **fully functional frontend** (JavaScript-based) with rich features including voice input, file attachments, feedback system, and chat history persistence. However, the **backend is minimal**:

- **No chatbot-specific models** (empty `chatbot/models.py`)
- **Only 2 views**: `chatbot()` renders the UI, `adminmessagecenter()` displays `ContactMessage` objects
- **No API endpoints** for real-time chat communication
- **All responses are hardcoded** in JavaScript with keyword-based triggers
- **Chat history stored only in localStorage** (browser-side)

The project uses:
- **Django 5.2.6** with PostgreSQL
- **JsonResponse** pattern for APIs (seen in `portfolio/api.py`, `blog/views.py`)
- **Role-based access control** via decorators (`@require_admin_role`, `@require_public_role`)
- **Existing models**: `ContactMessage` (core), `Project` (site_diary), `Profile` (accounts)
- **No REST framework** (DRF) - uses plain Django views with JsonResponse

Key integration points:
- **Site Diary app**: Has `Project` model with status, progress, milestones
- **Portfolio app**: Has API endpoints (`portfolio/api.py`) for project data
- **Accounts app**: Has `Profile`, `AdminProfile`, `SiteManagerProfile` models
- **Core app**: Has `ContactMessage` model with status tracking (new, read, reviewed, archived)

### Approach

Build a **backend-integrated chatbot system** that connects the existing JavaScript frontend to Django backend via REST APIs. Create database models for conversation persistence, implement intent detection logic, integrate with existing apps (Site Diary, Portfolio) for real data, and provide admin management interface. Start with rule-based responses, design for future AI integration.

### Reasoning

Explored the chatbot app structure, examined the JavaScript frontend implementation, reviewed existing API patterns in portfolio and blog apps, analyzed the database models in site_diary and accounts apps, checked authentication/authorization patterns, and identified integration points with other modules.

## Mermaid Diagram

sequenceDiagram
    participant User
    participant JS as chatbot.js<br/>(Frontend)
    participant API as chatbot/views.py<br/>(Backend API)
    participant Utils as chatbot/utils.py<br/>(Intent Detection)
    participant DB as Database<br/>(Models)
    participant Apps as Site Diary/Portfolio<br/>(Data Sources)
    
    Note over User,Apps: User Sends Message
    User->>JS: Types message
    JS->>API: POST /chat/api/send-message/<br/>{message, conversation_id}
    API->>DB: Get/Create Conversation
    DB-->>API: Conversation object
    API->>DB: Save ChatMessage (user)
    API->>Utils: detect_intent(message)
    Utils->>DB: Query ChatbotIntent
    DB-->>Utils: Matching intents
    Utils-->>API: Best intent + confidence
    
    alt Intent: Project Status
        API->>Apps: Query user's projects
        Apps-->>API: Project data
        API->>Utils: generate_response(intent, user, context)
        Utils-->>API: Personalized response
    else Intent: General Query
        API->>Utils: generate_response(intent)
        Utils-->>API: Template response
    end
    
    API->>DB: Save ChatMessage (bot)
    API-->>JS: {success, response, conversation_id}
    JS->>User: Display bot response
    
    Note over User,Apps: Load History on Init
    JS->>API: GET /chat/api/conversation-history/
    API->>DB: Query ChatMessage
    DB-->>API: Message list
    API-->>JS: {messages: [...]}
    JS->>User: Restore chat history
    
    Note over User,Apps: Admin Views Conversations
    Admin->>AdminUI: Click Chatbot tab
    AdminUI->>API: GET /chat/api/admin/conversations/
    API->>DB: Query Conversation + counts
    DB-->>API: Conversation list
    API-->>AdminUI: {conversations: [...]}
    AdminUI->>Admin: Display conversations

## Proposed File Changes

### chatbot\models.py(MODIFY)

References: 

- site_diary\models.py
- core\models.py
- accounts\models.py

Create database models for chatbot functionality:

1. **Conversation Model**:
   - Fields: `user` (ForeignKey to User, nullable for anonymous), `session_id` (UUID for anonymous users), `started_at`, `last_message_at`, `status` (active/closed/archived), `user_agent`, `ip_address`
   - Methods: `is_anonymous()`, `get_message_count()`, `close_conversation()`
   - Meta: ordering by `-last_message_at`

2. **ChatMessage Model**:
   - Fields: `conversation` (ForeignKey to Conversation), `sender_type` (user/bot/system), `message_text`, `intent` (nullable), `confidence_score` (nullable), `metadata` (JSONField for attachments/voice data), `created_at`
   - Methods: `is_from_user()`, `is_from_bot()`
   - Meta: ordering by `created_at`

3. **ChatbotIntent Model**:
   - Fields: `name` (unique), `description`, `keywords` (JSONField - list of trigger words), `response_template`, `requires_auth`, `priority`, `is_active`, `created_at`, `updated_at`
   - Methods: `match_keywords(message)`, `get_response(context)`
   - Meta: ordering by `-priority`

4. **ChatFeedback Model**:
   - Fields: `message` (ForeignKey to ChatMessage), `rating` (thumbs_up/thumbs_down), `feedback_text`, `created_at`
   - Meta: ordering by `-created_at`

Follow the pattern from `site_diary/models.py` and `core/models.py` for consistency.

### chatbot\views.py(MODIFY)

References: 

- portfolio\api.py
- core\views.py
- site_diary\models.py
- admin_side\views.py
- admin_side\decorators.py

Expand views to include API endpoints for chatbot functionality:

1. **Keep existing views**: `chatbot()` and `adminmessagecenter()` remain unchanged

2. **Add `send_message` API view**:
   - Decorator: `@require_http_methods(['POST'])`
   - Accept JSON: `message`, `conversation_id` (optional), `session_id` (optional)
   - Logic: Get or create Conversation, save user message, detect intent using `ChatbotIntent.match_keywords()`, generate bot response, save bot message, return JSON with response and conversation_id
   - Handle both authenticated and anonymous users

3. **Add `get_conversation_history` view**:
   - Decorator: `@require_http_methods(['GET'])`
   - Parameters: `conversation_id` or `session_id`
   - Return: List of messages with sender, text, timestamp
   - Security: Verify user owns the conversation

4. **Add `get_project_status` view**:
   - Decorator: `@login_required`, `@require_http_methods(['GET'])`
   - Query `site_diary.models.Project` for user's projects
   - Return: Project name, status, progress percentage, milestones
   - Use pattern from `core/views.py` `clientdashboard()` for querying user projects

5. **Add `submit_feedback` view**:
   - Decorator: `@require_http_methods(['POST'])`
   - Accept: `message_id`, `rating`, `feedback_text`
   - Create `ChatFeedback` record
   - Return success response

6. **Add `create_contact_from_chat` view**:
   - Decorator: `@require_http_methods(['POST'])`
   - Accept: name, email, phone, subject, message
   - Create `ContactMessage` object (reuse from `core.models`)
   - Return success response

Follow the JsonResponse pattern from `portfolio/api.py` and error handling from `core/views.py`.
Add admin-specific API endpoints for conversation management:

1. **Add `admin_get_conversations` view**:
   - Decorator: `@require_admin_role` (from `admin_side.decorators`)
   - Query all `Conversation` objects with message counts
   - Return JSON list with: id, user info, session_id, started_at, last_message_at, message_count, status

2. **Add `admin_get_conversation_messages` view**:
   - Decorator: `@require_admin_role`
   - Parameter: `conversation_id`
   - Query all `ChatMessage` objects for the conversation
   - Return JSON list with: id, sender_type, message_text, intent, created_at

3. **Add `admin_close_conversation` view**:
   - Decorator: `@require_admin_role`, `@require_http_methods(['POST'])`
   - Parameter: `conversation_id`
   - Update conversation status to 'closed'
   - Return success response

4. **Add `admin_archive_conversation` view**:
   - Decorator: `@require_admin_role`, `@require_http_methods(['POST'])`
   - Parameter: `conversation_id`
   - Update conversation status to 'archived'
   - Return success response

Use the decorator pattern from `admin_side/views.py` and `site_diary/views.py` for admin authentication.

### chatbot\urls.py(MODIFY)

References: 

- portfolio\urls.py
- core\urls.py

Add URL patterns for new API endpoints:

1. Keep existing patterns: `''` (chatbot UI), `'adminmessagecenter/'`

2. Add API patterns:
   - `'api/send-message/'` → `views.send_message`
   - `'api/conversation-history/'` → `views.get_conversation_history`
   - `'api/project-status/'` → `views.get_project_status`
   - `'api/submit-feedback/'` → `views.submit_feedback`
   - `'api/create-contact/'` → `views.create_contact_from_chat`

Follow the URL pattern structure from `portfolio/urls.py` and `core/urls.py`.
Add URL patterns for admin API endpoints:

1. Add admin API patterns:
   - `'api/admin/conversations/'` → `views.admin_get_conversations`
   - `'api/admin/conversation/<int:conversation_id>/messages/'` → `views.admin_get_conversation_messages`
   - `'api/admin/conversation/<int:conversation_id>/close/'` → `views.admin_close_conversation`
   - `'api/admin/conversation/<int:conversation_id>/archive/'` → `views.admin_archive_conversation`

Place these after the existing patterns.

### chatbot\admin.py(MODIFY)

References: 

- site_diary\admin.py
- blog\admin.py

Register chatbot models in Django admin:

1. **ConversationAdmin**:
   - List display: user, session_id, started_at, last_message_at, status, message count
   - List filter: status, started_at
   - Search fields: user__username, user__email, session_id
   - Readonly fields: started_at, last_message_at
   - Inline: ChatMessageInline (show messages within conversation)
   - Actions: close_conversations, archive_conversations

2. **ChatMessageAdmin**:
   - List display: conversation, sender_type, message_text (truncated), intent, created_at
   - List filter: sender_type, intent, created_at
   - Search fields: message_text, conversation__user__username
   - Readonly fields: created_at

3. **ChatbotIntentAdmin**:
   - List display: name, priority, is_active, created_at
   - List filter: is_active, requires_auth
   - Search fields: name, description, keywords
   - List editable: priority, is_active
   - Fieldsets: organize by Basic Info, Keywords & Response, Settings

4. **ChatFeedbackAdmin**:
   - List display: message, rating, created_at
   - List filter: rating, created_at
   - Search fields: feedback_text, message__message_text
   - Readonly fields: created_at

Follow the admin configuration pattern from `site_diary/admin.py` and `blog/admin.py`.

### chatbot\utils.py(NEW)

References: 

- site_diary\utils.py
- blog\utils.py

Create utility functions for chatbot logic:

1. **Intent Detection**:
   - `detect_intent(message_text)`: Query `ChatbotIntent` objects, match keywords, return best match with confidence score
   - `calculate_keyword_match_score(message, keywords)`: Calculate match percentage

2. **Response Generation**:
   - `generate_response(intent, user, context)`: Generate response based on intent template, replace placeholders with user data
   - `get_user_context(user)`: Gather user info (name, projects, profile) for personalization
   - `get_project_info(user)`: Query site_diary projects for user

3. **Session Management**:
   - `get_or_create_conversation(user, session_id)`: Get existing or create new conversation
   - `generate_session_id()`: Generate UUID for anonymous users

4. **Data Formatting**:
   - `format_message_for_api(message)`: Convert ChatMessage to JSON-serializable dict
   - `format_conversation_for_api(conversation)`: Convert Conversation with messages to JSON

Use patterns from `site_diary/utils.py` and `blog/utils.py` for consistency.

### static\js\chatbot.js(MODIFY)

References: 

- static\js\adminjs\adminmessagecenter.js(MODIFY)
- static\js\blogindividual.js

Update JavaScript to integrate with backend APIs:

1. **Add API Configuration**:
   - Add `apiEndpoints` object with URLs: `/chat/api/send-message/`, `/chat/api/conversation-history/`, etc.
   - Add `conversationId` and `sessionId` variables to track conversation

2. **Modify `sendMessage()` function**:
   - Replace hardcoded responses with API call to `/chat/api/send-message/`
   - Send: `{ message: messageText, conversation_id: conversationId, session_id: sessionId }`
   - Receive: `{ success: true, response: botMessage, conversation_id: id }`
   - Store `conversationId` for subsequent messages
   - Keep fallback to hardcoded responses if API fails

3. **Add `loadConversationHistory()` function**:
   - Call `/chat/api/conversation-history/` on chatbot init
   - Restore previous messages if conversation exists
   - Use `addMessage(text, sender, { instant: true })` to avoid typing animation for history

4. **Modify `openContactForm()` function**:
   - On form submit, call `/chat/api/create-contact/` instead of just showing success
   - Send form data as JSON
   - Show success/error message based on API response

5. **Add `submitFeedback()` function**:
   - On thumbs up/down click, call `/chat/api/submit-feedback/`
   - Send: `{ message_id: messageId, rating: 'thumbs_up', feedback_text: '' }`

6. **Add CSRF Token Handling**:
   - Get CSRF token from cookie or meta tag
   - Include in all POST requests headers: `'X-CSRFToken': csrfToken`

7. **Update `processUserQuery()` for project status**:
   - When project status query detected, call `/chat/api/project-status/`
   - Display real project data instead of hardcoded response

8. **Error Handling**:
   - Add try-catch blocks for all API calls
   - Show user-friendly error messages
   - Log errors to console for debugging

Keep existing features (voice, file upload, localStorage backup) intact. Follow the AJAX pattern from `static/js/adminjs/adminmessagecenter.js`.

### chatbot\management\commands\seed_chatbot_intents.py(NEW)

References: 

- site_diary\management\commands\setup_sample_data.py
- blog\management\commands\create_blog_posts.py

Create management command to populate initial chatbot intents:

1. **Command Structure**:
   - Class: `Command(BaseCommand)`
   - Method: `handle(self, *args, **options)`

2. **Create Default Intents**:
   - **Navigation Intent**: keywords=['where', 'how do i', 'find', 'locate', 'view'], response='You can find that in your dashboard. Would you like me to guide you?'
   - **Project Status Intent**: keywords=['project status', 'milestone', 'progress', 'update'], response='Let me check your project status...'
   - **Support Intent**: keywords=['talk to someone', 'need help', 'contact support', 'human'], response='I can connect you with our support team. Would you like to leave a message?'
   - **Appointment Intent**: keywords=['schedule', 'appointment', 'meeting', 'call back'], response='I can help you schedule an appointment. Please provide your contact information.'
   - **FAQ Intent**: keywords=['what is triple g', 'faq', 'question', 'about'], response='Triple G BuildHub is a construction management platform. What would you like to know?'
   - **Greeting Intent**: keywords=['hello', 'hi', 'hey', 'good morning'], response='Hello! Welcome to Triple G BuildHub. How can I assist you today?'

3. **Use `get_or_create()`** to avoid duplicates

4. **Print summary** of created intents

Follow the pattern from `site_diary/management/commands/setup_sample_data.py` and `blog/management/commands/create_blog_posts.py`.

### chatbot\management\commands\__init__.py(NEW)

Create empty `__init__.py` file to make the commands directory a Python package.

### chatbot\management\__init__.py(NEW)

Create empty `__init__.py` file to make the management directory a Python package.

### chatbot\templates\admin\adminmessagecenter.html(MODIFY)

Enhance admin message center to include chatbot conversations:

1. **Add Tabs**:
   - Add new tab: 'Chatbot Conversations' alongside existing tabs (All Messages, New, Read, etc.)
   - Tab button: `<button class="tab-btn" data-tab="chatbot">Chatbot</button>`

2. **Add Chatbot Conversations Section**:
   - Create new section: `<div id="chatbot-conversations" style="display: none;">`
   - Display list of `Conversation` objects with user, session_id, message count, last_message_at
   - Each conversation row has 'View Messages' button

3. **Add Conversation Detail Modal**:
   - Modal to display all messages in a conversation
   - Show messages in timeline format (similar to existing message display)
   - Include sender type (user/bot), message text, timestamp
   - Add 'Close Conversation' and 'Archive' buttons

4. **Add JavaScript**:
   - Tab switching logic to show/hide chatbot conversations
   - AJAX call to fetch conversations: `/chat/api/admin/conversations/`
   - AJAX call to fetch conversation messages: `/chat/api/admin/conversation/<id>/messages/`
   - Modal open/close handlers

Follow the existing structure and styling from the current template. Use the same CSS classes and JavaScript patterns.

### static\js\adminjs\adminmessagecenter.js(MODIFY)

Add JavaScript functionality for chatbot conversations tab:

1. **Add Tab Switching**:
   - Listen for click on 'Chatbot' tab button
   - Hide contact messages sections, show chatbot conversations section

2. **Add `loadChatbotConversations()` function**:
   - Fetch conversations from `/chat/api/admin/conversations/`
   - Render conversations in table/timeline format
   - Add 'View Messages' button for each conversation

3. **Add `viewConversationMessages(conversationId)` function**:
   - Fetch messages from `/chat/api/admin/conversation/${conversationId}/messages/`
   - Open modal and display messages
   - Format messages with sender type, text, timestamp

4. **Add `closeConversation(conversationId)` function**:
   - POST to `/chat/api/admin/conversation/${conversationId}/close/`
   - Update UI to reflect closed status
   - Show success message

5. **Add `archiveConversation(conversationId)` function**:
   - POST to `/chat/api/admin/conversation/${conversationId}/archive/`
   - Remove from active list or update status
   - Show success message

6. **Add CSRF Token Handling**:
   - Get CSRF token from cookie
   - Include in all POST requests

Follow the existing code structure and patterns in the file.

### chatbot\migrations\0001_initial.py(NEW)

Create initial migration for chatbot models:

1. Run `python manage.py makemigrations chatbot` after creating models
2. This will auto-generate the migration file
3. Review the migration to ensure all fields, relationships, and constraints are correct
4. Ensure foreign keys to User model are properly configured
5. Ensure JSONField is used for metadata and keywords fields

The migration will be auto-generated by Django, no manual creation needed.