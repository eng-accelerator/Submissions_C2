# Plan for Challenge 3: Export Functionality

This document outlines the plan to implement a comprehensive, multi-format export feature in the `chat-challenge-3.py` file.

### Primary Goal

The objective is to allow users to download the current conversation history in three different formats: TXT, JSON, and CSV. Each format will be tailored for a specific use case (readability, data interchange, and analysis) and will include relevant metadata and statistics as specified in the challenge brief.

---

### Prerequisite: Add Timestamps to Messages

The current message objects in `chat-challenge-3.py` only store `role` and `content`. The export requirements, particularly for JSON and CSV, necessitate a timestamp for each message. 

- **Action**: The first step is to modify the message creation logic. When a user or assistant message is generated, it will be stored with a timestamp.
- **Example Structure**: `{"role": "user", "content": prompt, "timestamp": datetime.now().isoformat()}`

### Step 1: Create Modular Export Helper Functions

To keep the code clean and maintainable, the logic for each format will be encapsulated in its own function. These functions will be defined near the top of the script.

- **`export_as_txt(messages, metadata)`**
    1.  Generate a text header using the `metadata` (e.g., total messages, export date).
    2.  Iterate through the `messages` list.
    3.  For each message, format a human-readable string, such as `[HH:MM:SS] Role: Content`.
    4.  Combine the header and formatted messages into a single string and return it.

- **`export_as_json(messages, metadata)`**
    1.  Define the top-level dictionary structure: `{"export_metadata": {}, "conversation": [], "statistics": {}}`.
    2.  Populate the `export_metadata` object.
    3.  Iterate through the `messages` list to build the `conversation` array. For each message, calculate per-message stats like `character_count`.
    4.  Calculate the aggregate `statistics` for the entire conversation (e.g., total user/assistant messages).
    5.  Use `json.dumps()` with an indent to convert the final dictionary into a well-formatted JSON string for return.

- **`export_as_csv(messages, metadata)`**
    1.  This function will use Python's built-in `csv` module and the `io.StringIO` class to build the CSV file in memory.
    2.  A `csv.writer` will be created.
    3.  The specified header row will be written first: `['Message_ID', 'Timestamp', 'Role', 'Content', 'Character_Count', 'Word_Count']`.
    4.  Iterate through the `messages` list, and for each message, calculate the required stats (`Character_Count`, `Word_Count`).
    5.  Write the data for each message as a new row.
    6.  Return the complete CSV string from the `StringIO` object.

### Step 2: Implement Sidebar UI for Exporting

- **Location**: A new section will be added to the sidebar (`with st.sidebar:`).
- **Controls**:
    1.  Add a new subheader: `st.subheader("📤 Export Conversation")`.
    2.  Add a `st.selectbox` to allow the user to choose their desired format from a list: `["TXT", "JSON", "CSV"]`.
- **Download Logic**:
    1.  Add an `st.button` labeled "Prepare Export". When clicked, the appropriate helper function from Step 1 will be called based on the user's format selection.
    2.  The generated content will be stored in a temporary session state variable.
    3.  An `st.download_button` will be conditionally displayed, allowing the user to download the prepared content. The `file_name` and `mime` type for the download button will be set dynamically based on the selected format.

### Summary of Implementation Flow

1.  **Prerequisite**: Augment the message data model to include timestamps.
2.  **Backend Logic**: Implement the three distinct data transformation functions (`export_as_txt`, `export_as_json`, `export_as_csv`).
3.  **Frontend UI**: Add the necessary controls to the sidebar for format selection and download initiation.
4.  **Integration**: Connect the UI controls to the backend logic to generate and deliver the correct file to the user.
