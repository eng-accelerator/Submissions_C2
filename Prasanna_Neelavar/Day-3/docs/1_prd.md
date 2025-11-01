# Chat Interface Requirements (Streamlit)

Based on the provided image and subsequent enhancements, here are the requirements for a Streamlit-based chat interface:

## 1. General Overview
*   The application should provide a conversational AI assistant interface.
*   The UI should support both **light and dark themes**, with the ability for the user to switch between them.
*   A "Deploy" button should be present in the top right corner (functionality TBD).
*   A "Talking:" indicator should be visible.

## 2. Core Chat Functionality
*   **Assistant Display:** Display the assistant's name and a customizable emoji/icon (e.g., rocket emoji).
*   **Chat History:** Display a history of messages between the user and the assistant.
*   **User Input:** A text input field at the bottom for users to type messages, with a send button.
*   **Assistant Responses:** The assistant should generate and display responses, with **varying content based on the selected response style**.
*   **Response Style:** The assistant's response style should be configurable (e.g., "Friendly").
*   **Timestamps:** Each message should display a timestamp.
*   **Expandable Sections:** Implement expandable/collapsible sections within the chat area for additional information (e.g., "About This Demo", "Instructor Notes", "Show Development Info").

## 3. Configuration Options (Sidebar)
*   **Display Settings:**
    *   **Theme Selection:** A control (e.g., radio buttons) to switch between light and dark themes.
*   **Assistant Settings:**
    *   **Assistant Name:** A text input field to set the assistant's display name.
    *   **Response Style:** A dropdown selector to choose the assistant's response style.
*   **Chat Settings:**
    *   **Max Chat History:** A slider or numerical input to control the maximum number of messages to retain in the chat history.
    *   **Show Timestamps:** A checkbox to toggle the visibility of message timestamps.
*   **Actions:**
    *   **Clear Chat:** A button (with a relevant icon) to clear the current chat history.
    *   **Export Chat:** A button (with a relevant icon) to export the chat history as a text file.

## 4. Session Statistics
*   Display real-time session statistics in the sidebar, including:
    *   **Session Duration:** Elapsed time since the session started.
    *   **Messages Sent:** Number of messages sent by the user.
    *   **Total Messages:** Total number of messages in the conversation (user + assistant).

## 5. UI/UX Considerations
*   The layout should be split into a main chat area and a sidebar for configuration and statistics.
*   The sidebar should be collapsible.
*   Clear visual separation between user and assistant messages.
*   Intuitive controls for configuration settings.
*   Responsive design for various screen sizes (implied by Streamlit).

## 6. Next Iteration Features

The following features are proposed for future iterations of the chat interface:

### 6.1. General Enhancements
*   **"Talking:" Indicator:** Implement actual functionality for the "Talking:" indicator. It should activate when the assistant is generating a response and deactivate when finished.

### 6.2. Advanced Chat Management
*   **Chat History Operations:** Implement functionality to manage multiple chat sessions. This includes:
    *   **UI:** An expandable section on the sidebar titled "Chat History" to list available chat sessions.
    *   **Selection:** Allow users to select a chat session from the list.
    *   **Deletion:** Provide a delete action for chat sessions, with a confirmation pop-up dialog.
    *   **Storage:** Chat history should be stored in the local file system within a `/chat_history` folder as individual JSON files.
    *   **Naming Convention:** The first user message in a session should be used as the title for the chat session. New sessions should be saved in `chat_<timestamp>.json` format.
    *   **Saving Mechanism:** The chat session should be updated and saved on every assistant response.
    *   **Session State Management:** Utilize Streamlit's session state intelligently to manage user refresh/rerun within the session.
*   **Chat Session Data Structure:** Each chat session will be stored as a JSON object with the following minimum fields:
    *   `chat_id` (string): A unique identifier for the chat session.
    *   `title` (string): The title of the chat session, derived from the first user message.
    *   `messages` (list of objects): A chronological list of message objects within the session. Each message object will contain:
        *   `role` (string): Either "user" or "assistant".
        *   `content` (string): The text content of the message.
        *   `timestamp` (string): The time the message was created, in ISO 8601 format.
        *   `feedback` (string, optional): "liked", "disliked", or null, indicating user feedback on assistant messages.
    *   `created_at` (string): The timestamp for when the chat session was initially created, in ISO 8601 format.
    *   `updated_at` (string): The timestamp for when the chat session was last updated (e.g., a new message was added or feedback was given), in ISO 8601 format.

### 6.3. AI Features
*   **Session Summarization:** Add a feature to summarize the entire chat session.
    *   **Trigger:** A "Summarize" button should be visible once the assistant provides its first response.
    *   **Display:** The summary should be shown as a pop-up.
    *   **Save Option:** Offer the user an option to save the summary as a Markdown file.
*   **Model Integration:** Integrate with the OpenRouter platform, specifically using a `gpt-oss` model.
    *   **API Key Management:** The OpenRouter API key will be saved as a Streamlit secret in `.streamlit/secrets.toml`.
    *   **Implementation Deferral:** This feature's implementation is deferred until all UI work is complete and thoroughly tested.
*   **Response Post-processing:** Implement logic for general cleanup of extraneous start and ending tags (e.g., `<imend><eos><im_start>`) from LLM responses.

### 6.4. Data Management
*   **ISO 8601 Datetime Formatting:** Ensure all datetime objects saved within the chat history are stored in ISO 8601 format for consistency and ease of parsing. This applies only to the internal data structure, not the displayed timestamps.

### 6.5. User Feedback
*   **Assistant Response Feedback:** Add "like" (thumbs up) and "dislike" (thumbs down) buttons for each assistant response.
    *   **Placement:** Buttons should be placed relative to each assistant message.
    *   **Visual Feedback:** The selected button should be highlighted upon click.
    *   **Storage:** The feedback (e.g., `liked` or `disliked` status) should be saved as part of the chat object within the chat history.
    *   **Purpose:** This feedback will help in re-drafting responses when a chat session from history is selected to continue.