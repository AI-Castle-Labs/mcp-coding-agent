# 🔍 Codebase Analysis Report

## 📦 Repository: `ashcastelinocs124/VentureBot`

| Property | Value |
|----------|-------|
| **Branch** | `main` |
| **Analyzed** | 2025-12-29 07:08:20 |
| **Files** | 20 |
| **Classes** | 23 |
| **Functions** | 17 |
| **Imports** | 242 |

---

## 📊 Summary Statistics

```
📁 Total Files Analyzed:        20
🏛️  Total Classes:               23
⚡ Total Functions:              17
📦 Total Imports:               242
```

---

## 📁 File Analysis

### 📊 `services/api_gateway/app/schemas.py`

| Metric | Count |
|--------|-------|
| Classes | 6 |
| Functions | 0 |
| Imports | 12 |

#### 📝 Code Summary

> This Python file defines data models for managing chat sessions and messages using Pydantic, which facilitates data validation and serialization. Its main purpose is to structure and validate the data related to chat sessions, including session creation, message handling, and session responses. Key behaviors include defining optional and required fields for chat sessions and messages, as well as providing configurations for attribute mapping in the response models.

#### 🔗 Dependencies

> The Python file relies on several external dependencies, including the `datetime` module for date and time manipulation, and the `pydantic` library for data validation and settings management through its `BaseModel` and `Field` classes. It also utilizes features from the `__future__` module to enable forward compatibility with type annotations and employs custom models from a `models` module, specifically `JourneyStage` and `MessageRole`. Notably, there are no outward dependencies, indicating that no other code directly relies on this file.

#### 🏛️ Classes

<details>
<summary><strong>ChatSessionCreate</strong> (0 methods)</summary>

**Summary:** The `ChatSessionCreate` class is a data model that represents the creation of a chat session, inheriting from `BaseModel`. Its main purpose is to encapsulate the properties of a chat session, specifically an optional title and a boolean flag indicating whether the onboarding agent should start automatically. The key behavior includes defining these attributes with default values and descriptions for clarity in usage.

**Dependencies:** The `ChatSessionCreate` class relies on the external dependency `Field`, which is likely used for defining data attributes or validation within the class. There are no outward dependencies identified, indicating that no other code directly utilizes the `ChatSessionCreate` class. The nature of the inward dependency suggests that it may be involved in data processing or schema definition within the context of the class.

</details>

<details>
<summary><strong>ChatSessionRead</strong> (0 methods)</summary>

**Summary:** The `ChatSessionRead` class is a data model that represents a chat session, encapsulating attributes such as an identifier, optional title, current stage, and timestamps for creation and updates. Its main purpose is to serve as a structured representation of chat session data, likely for reading or displaying information about ongoing or past sessions. The key behavior includes the use of Pydantic's `BaseModel` for data validation and serialization, with the configuration allowing attributes to be populated from various sources.

**Dependencies:** The `ChatSessionRead` class has no inward dependencies, meaning it does not rely on any external libraries or other classes for its functionality. Additionally, there are no outward dependencies, indicating that no other code or classes utilize `ChatSessionRead`. This suggests that `ChatSessionRead` is either a standalone component or not yet integrated into a broader codebase.

</details>

<details>
<summary><strong>ChatMessageCreate</strong> (0 methods)</summary>

**Summary:** The `ChatMessageCreate` class is a data model that represents a chat message, inheriting from `BaseModel`. Its main purpose is to encapsulate the properties of a chat message, specifically the role of the sender (defined by `MessageRole`) and the message content as a string. The key behavior of this class is to provide a structured way to create and validate chat messages within an application, ensuring that each message has an associated role and content.

**Dependencies:** The `ChatMessageCreate` class has no inward dependencies, meaning it does not rely on any external libraries or modules for its functionality. Additionally, there are no outward dependencies, indicating that no other classes or modules utilize `ChatMessageCreate`. This suggests that `ChatMessageCreate` may serve as a standalone component, potentially designed for future integration or expansion within a larger codebase.

</details>

<details>
<summary><strong>ChatMessageRead</strong> (0 methods)</summary>

**Summary:** The `ChatMessageRead` class is a data model that represents a chat message that has been read, encapsulating attributes such as the message ID, session ID, sender role, content of the message, and the timestamp of its creation. Its main purpose is to serve as a structured representation of read chat messages, facilitating data handling and manipulation in chat applications. Key behavior includes leveraging the `BaseModel` for validation and serialization, with a configuration that allows initialization from attributes directly.

**Dependencies:** The `ChatMessageRead` class has no external dependencies, meaning it does not rely on any other modules, libraries, or classes for its functionality. Additionally, there are no other pieces of code that depend on `ChatMessageRead`, indicating that it stands alone without being utilized elsewhere in the codebase. This isolation suggests that the class may serve a specific purpose or is in a preliminary state of development.

</details>

<details>
<summary><strong>ChatTurnResponse</strong> (0 methods)</summary>

**Summary:** The `ChatTurnResponse` class is a data model that encapsulates the components of a single turn in a chat session, including the session details, the user's message, and the assistant's response. Its main purpose is to structure and represent the data exchanged during a chat interaction, facilitating the management and retrieval of chat-related information. The key behavior of this class is to serve as a container for the relevant messages and session data, likely intended for use in APIs or data processing related to chat applications.

**Dependencies:** The `ChatTurnResponse` class has no external dependencies, meaning it does not rely on any other modules, libraries, or classes for its functionality. Additionally, there are no outward dependencies, indicating that no other code or classes utilize `ChatTurnResponse`. As a result, this class operates independently without any interactions or integrations with other components in the codebase.

</details>

<details>
<summary><strong>SessionStartResponse</strong> (0 methods)</summary>

**Summary:** The `SessionStartResponse` class represents the response returned when initiating a new session that includes auto-onboarding features. Its main purpose is to encapsulate the session details, specifically a `ChatSessionRead` object and an optional onboarding message of type `ChatMessageRead`. The key behavior of this class is to provide structured data for the response, facilitating the management of session information and onboarding communication in a chat application.

**Dependencies:** The `SessionStartResponse` class has no external dependencies, meaning it does not rely on any other modules, libraries, or classes for its functionality. Additionally, there are no outward dependencies, indicating that no other code or classes utilize `SessionStartResponse`. This suggests that the class is self-contained and does not interact with other components in the codebase.

</details>

---

### 🌐 `services/api_gateway/app/routers/chat.py`

| Metric | Count |
|--------|-------|
| Classes | 0 |
| Functions | 5 |
| Imports | 33 |

#### 📝 Code Summary

> This Python file implements a FastAPI router for managing chat sessions, allowing users to create sessions, send messages, and receive responses from an assistant in a structured journey. Its main responsibility is to facilitate real-time chat interactions, track the current stage of the conversation, and manage session state, including onboarding and message handling. Key behaviors include creating sessions with optional auto-start onboarding, processing user messages to generate assistant replies based on the current stage, and providing a WebSocket interface for real-time communication and updates on session status.

#### 🔗 Dependencies

> The Python file relies on several external dependencies primarily from the FastAPI framework for building web applications, as well as database interaction and date/time handling through the `datetime` module. It utilizes various FastAPI components such as APIRouter, HTTPException, and WebSocket for handling web requests and real-time communication, alongside database session management and models for data representation. Notably, there are no outward dependencies, indicating that this file is self-contained and not used by any other code.

#### ⚡ Functions

<details>
<summary><strong>_fetch_session()</strong></summary>

**Summary:** The `_fetch_session` function retrieves a `ChatSession` object from a database using a provided `session_id`. Its main responsibility is to ensure that the session exists; if not, it raises an `HTTPException` with a 404 status code, indicating that the session was not found. The key behavior is the conditional check for the existence of the session, which enforces error handling for missing data.

**Uses:** `HTTPException`, `db`, `status`, `HTTP_404_NOT_FOUND`, `get`

</details>

<details>
<summary><strong>_list_messages()</strong></summary>

**Summary:** The `_list_messages` function retrieves a list of `ChatMessage` objects from a database session, filtered by a specific `session_id`. Its main purpose is to return all chat messages associated with a given session, ordered by their creation time in ascending order. The key behavior involves executing a SQL query using SQLAlchemy to select and order the messages, then converting the result into a list.

**Uses:** `list`, `select`, `ChatMessage`, `db`, `asc`, `created_at`, `order_by`, `scalars`, `session_id`, `where`

</details>

<details>
<summary><strong>_chunk_text()</strong></summary>

**Summary:** The `_chunk_text` function takes a string `text` and an optional integer `size` (defaulting to 128) and yields chunks of the text, each of the specified size. Its main purpose is to break down a potentially large string into smaller, manageable segments for easier processing or analysis. The key behavior involves iterating over the text in increments of `size`, ensuring that each chunk is returned until the entire string has been processed.

**Uses:** `len`, `range`

</details>

<details>
<summary><strong>get_session_info()</strong></summary>

**Summary:** The `get_session_info` function retrieves information about a chat session based on a provided `session_id`, utilizing a database session obtained through dependency injection. Its main responsibility is to fetch and validate the session data, returning it in a structured format defined by `schemas.ChatSessionRead`. The key behavior involves calling the helper function `_fetch_session` to obtain the session details and then validating the data model before returning it.

**Uses:** `Depends`, `_fetch_session`, `router`, `schemas`, `ChatSessionRead`, `get`, `model_validate`

</details>

<details>
<summary><strong>list_messages()</strong></summary>

**Summary:** The `list_messages` function retrieves chat messages associated with a specific session ID from a database. Its main purpose is to validate and return a list of chat messages in a structured format using the `schemas.ChatMessageRead` model. Key behavior includes fetching the session to ensure its validity and then mapping the retrieved messages to the specified schema for consistent output.

**Uses:** `Depends`, `_fetch_session`, `_list_messages`, `router`, `schemas`, `ChatMessageRead`, `get`, `model_validate`

</details>

---

### ⚡ `services/orchestrator/flows/staged_journey_flow.py`

| Metric | Count |
|--------|-------|
| Classes | 4 |
| Functions | 1 |
| Imports | 22 |

#### 📝 Code Summary

> The provided Python module implements a staged execution flow for a human-in-the-loop system designed for VentureBots, guiding users through various entrepreneurial stages such as onboarding, idea generation, and validation. Its main responsibility is to manage the progression through these stages, allowing user input to dictate when to move to the next stage while accumulating context and outputs from previous stages. Key behaviors include dynamically building agents and tasks based on the current stage, handling user messages to determine readiness for progression, and maintaining a structured context to ensure continuity throughout the journey.

#### 🔗 Dependencies

> The Python file relies on several external dependencies, including the `crewai` library for agent and task management, as well as standard libraries like `json`, `logging`, and `pathlib` for data handling and file operations. It does not have any outward dependencies, meaning no other code directly utilizes this file. The nature of these dependencies primarily involves data processing and utility functions, facilitating structured data management and logging capabilities within the application.

#### 🏛️ Classes

<details>
<summary><strong>JourneyStage</strong> (0 methods)</summary>

**Summary:** The `JourneyStage` class defines a set of string constants representing different stages in a journey, such as onboarding, idea generation, and validation. Its main purpose is to provide a centralized and organized way to reference these stages throughout an application, enhancing code readability and maintainability. The key behavior is the encapsulation of stage names as class attributes, allowing for easy access and reducing the risk of typos in string literals.

**Dependencies:** The `JourneyStage` class has no external dependencies, meaning it does not rely on any external libraries or modules for its functionality. Additionally, there are no outward dependencies, indicating that no other classes or modules utilize `JourneyStage`. This suggests that `JourneyStage` is a standalone component, potentially serving a specific purpose within a larger application without interacting with other code.

</details>

<details>
<summary><strong>StageContext</strong> (4 methods)</summary>

**Summary:** The `StageContext` class serves as a container for accumulating context-related information across various stages of a startup development process. Its main responsibility is to manage and serialize user-specific data, such as the user's name, industry focus, startup idea, and outputs from different stages, facilitating easy storage and retrieval. Key behaviors include converting the context to and from dictionary and JSON formats, allowing for seamless integration with data storage systems.

**Dependencies:** The `StageContext` class relies on several external dependencies, including standard libraries such as `json` for data serialization and deserialization, as well as various utility functions and attributes like `dumps`, `loads`, `from_dict`, and `to_dict` for data processing. It also utilizes specific fields and attributes such as `idea_slate`, `industry_focus`, and `onboarding_summary` for managing contextual information. Notably, there are no outward dependencies, indicating that this class is self-contained and does not serve as a base or utility for other code components.

**Methods:**
- `to_dict()` - The `to_dict` method in the `StageContext` class serializes the instance's attributes into a diction...
- `from_dict()` - The `from_dict` method in the `StageContext` class is a class method that deserializes a dictionary ...
- `to_json()` - The `to_json` method in the `StageContext` class serializes the object's data into a JSON string for...
- `from_json()` - The `from_json` method in the `StageContext` class deserializes a JSON string into an instance of `S...

</details>

<details>
<summary><strong>StageResult</strong> (0 methods)</summary>

**Summary:** The `StageResult` class represents the outcome of executing a single stage in a process, encapsulating details such as the stage name, output generated, the subsequent stage to be executed, and the context in which the stage ran. Its main purpose is to store and manage the results and state of a stage, including whether it has been completed. Key behaviors include tracking the progression through stages and maintaining relevant context for further processing.

**Dependencies:** The `StageResult` class has no external dependencies, meaning it does not rely on any external libraries, modules, or other classes for its functionality. Additionally, there are no outward dependencies, indicating that no other code or classes utilize `StageResult`. This suggests that `StageResult` is a standalone component, potentially serving as a data structure or placeholder without any integration with other parts of the codebase.

</details>

<details>
<summary><strong>StagedJourneyExecutor</strong> (9 methods)</summary>

**Summary:** The `StagedJourneyExecutor` class orchestrates the execution of various stages in a venture coaching journey, allowing for the sequential processing of tasks while maintaining context between stages. Its primary responsibility is to manage the flow of tasks, build necessary agents and tasks from a blueprint, and handle user interactions to ensure a coherent experience throughout the journey. Key behaviors include dynamically constructing context from previous stages, executing tasks with appropriate agents, and determining the next stage based on user input and accumulated context.

**Dependencies:** The `StagedJourneyExecutor` class relies on various external dependencies, including data structures like `Crew` and `StageResult`, exception handling with `ValueError`, and several utility functions such as `getattr`, `hasattr`, and `isinstance`. It also utilizes constants and logging mechanisms like `LOGGER`, `STAGE_ORDER`, and `STAGE_TO_TASK` for managing stages and tasks within a journey. Notably, there are no outward dependencies, indicating that no other code directly utilizes the `StagedJourneyExecutor` class.

**Methods:**
- `__init__()` - The `__init__` method in the `StagedJourneyExecutor` class initializes the instance by creating a bl...
- `_build_agent()` - The `_build_agent` method in the `StagedJourneyExecutor` class constructs an `Agent` instance using ...
- `_build_task()` - The `_build_task` method in the `StagedJourneyExecutor` class constructs a `Task` object using a reg...
- `_get_base_inputs()` - The `_get_base_inputs` method retrieves essential input data from a `StageContext` object, specifica...
- `_build_context_text()` - The `_build_context_text` method constructs a string that consolidates relevant information from a u...
- `_run_task()` - The `_run_task` method in the `StagedJourneyExecutor` class executes a specified task by building th...
- `get_next_stage()` - The `get_next_stage` method retrieves the next stage in a predefined sequence (STAGE_ORDER) based on...
- `run_stage()` - The `run_stage` method in the `StagedJourneyExecutor` class executes a specified stage of a user jou...
- `run_onboarding_auto()` - The `run_onboarding_auto` method in the `StagedJourneyExecutor` class automatically initiates the on...

</details>

#### ⚡ Functions

<details>
<summary><strong>get_executor()</strong></summary>

**Summary:** The `get_executor` function retrieves a global instance of `StagedJourneyExecutor`, creating it if it does not already exist. Its main responsibility is to ensure that there is a single, shared instance of the executor throughout the application. The key behavior is the use of a global variable to store the executor, allowing for lazy initialization only when it is first needed.

**Uses:** `StagedJourneyExecutor`

</details>

---

### 🚀 `crewai-agents/src/venturebot_crew/main.py`

| Metric | Count |
|--------|-------|
| Classes | 0 |
| Functions | 4 |
| Imports | 3 |

#### 📝 Code Summary

> The Python file serves as a command-line interface for managing a crew of AI agents focused on entrepreneurship coaching. Its main purpose is to facilitate the execution of various operations such as running, training, replaying, and testing the crew using specified inputs related to user information and startup ideas. Key behaviors include handling command-line arguments to determine the operation to perform, executing the respective methods of the `VenturebotsAiEntrepreneurshipCoachingPlatformCrew` class, and managing exceptions during these operations.

#### 🔗 Dependencies

> The Python file relies on the external dependencies `sys` for system-specific parameters and functions, and `venturebot_crew` which includes the `VenturebotsAiEntrepreneurshipCoachingPlatformCrew` class, likely for functionality related to AI entrepreneurship coaching. There are no outward dependencies, indicating that no other code directly relies on this file. The nature of these dependencies suggests a focus on utility functions for system operations and specific classes for business coaching applications.

#### ⚡ Functions

<details>
<summary><strong>run()</strong></summary>

**Summary:** The `run` function initializes a dictionary of sample input values related to a user, including their name, industry focus, and startup idea. Its main purpose is to kick off a process within the `VenturebotsAiEntrepreneurshipCoachingPlatformCrew` class, which likely involves providing coaching or support for entrepreneurship. The key behavior of the function is the invocation of the `kickoff` method with the prepared inputs, suggesting it serves as a starting point for the crew's operations.

**Uses:** `VenturebotsAiEntrepreneurshipCoachingPlatformCrew`, `crew`, `kickoff`

</details>

<details>
<summary><strong>train()</strong></summary>

**Summary:** The `train` function is designed to initiate the training process for a crew within a venture coaching platform, using a specified number of iterations and an input filename provided via command-line arguments. Its main responsibility is to call the `train` method of the `VenturebotsAiEntrepreneurshipCoachingPlatformCrew` class, passing in necessary parameters for training. Key behavior includes error handling that raises a custom exception if any issues occur during the training process.

**Uses:** `Exception`, `VenturebotsAiEntrepreneurshipCoachingPlatformCrew`, `int`, `sys`, `argv`, `crew`, `train`

</details>

<details>
<summary><strong>replay()</strong></summary>

**Summary:** The `replay` function is designed to replay the execution of a crew task identified by a task ID passed as a command-line argument. Its main responsibility is to invoke the `replay` method of the `crew` object from the `VenturebotsAiEntrepreneurshipCoachingPlatformCrew` class, facilitating the re-execution of a specific task. Key behavior includes error handling, where any exceptions raised during the replay process are caught and re-raised with a descriptive message.

**Uses:** `Exception`, `VenturebotsAiEntrepreneurshipCoachingPlatformCrew`, `sys`, `argv`, `crew`, `replay`

</details>

<details>
<summary><strong>test()</strong></summary>

**Summary:** The `test` function is designed to execute a test on a crew from the `VenturebotsAiEntrepreneurshipCoachingPlatformCrew` class, using specified input parameters and command-line arguments for iterations and model name. Its main purpose is to facilitate the testing of the crew's performance in an entrepreneurship coaching context. Key behavior includes handling exceptions that may arise during the testing process and providing a clear error message if an issue occurs.

**Uses:** `Exception`, `VenturebotsAiEntrepreneurshipCoachingPlatformCrew`, `int`, `sys`, `argv`, `crew`, `test`

</details>

---

### 📊 `services/api_gateway/app/models.py`

| Metric | Count |
|--------|-------|
| Classes | 4 |
| Functions | 0 |
| Imports | 17 |

#### 📝 Code Summary

> This Python file defines a data model for a chat application using SQLAlchemy, focusing on managing chat sessions and messages within an entrepreneurship journey framework. Its main purpose is to facilitate the storage and retrieval of chat sessions, including their stages and associated messages, while maintaining relationships between sessions and messages. Key behaviors include tracking the current stage of the entrepreneurship journey, storing contextual information in JSON format, and automatically managing timestamps for creation and updates of chat sessions and messages.

#### 🔗 Dependencies

> The Python file relies on several external dependencies, including the `sqlalchemy` library for ORM functionality and database interactions, as well as `datetime` for handling date and time data. It does not have any outward dependencies, meaning no other code directly relies on this file. The nature of these dependencies primarily involves data modeling and database schema definitions, with a focus on managing relationships and data types within a database context.

#### 🏛️ Classes

<details>
<summary><strong>MessageRole</strong> (0 methods)</summary>

**Summary:** The `MessageRole` class is an enumeration that defines three distinct roles as string constants: `USER`, `ASSISTANT`, and `SYSTEM`. Its main purpose is to categorize different participants in a messaging context, likely for applications involving chatbots or interactive systems. The key behavior is that it extends both `str` and `enum.Enum`, allowing instances of `MessageRole` to be used as both string values and enumerated types, enhancing type safety and readability in the code.

**Dependencies:** The `MessageRole` class relies on the `enum` module, specifically the `Enum` class, to define enumerated constants. There are no outward dependencies, meaning no other code directly utilizes the `MessageRole` class. The nature of the inward dependency is primarily for creating a structured set of named values, which can facilitate clearer code and improve data handling.

</details>

<details>
<summary><strong>JourneyStage</strong> (0 methods)</summary>

**Summary:** The `JourneyStage` class defines an enumeration for various stages in the VentureBot entrepreneurship journey, such as onboarding, idea generation, and validation. Its main purpose is to provide a structured way to represent and manage the different phases of the entrepreneurial process. The key behavior is that it inherits from both `str` and `enum.Enum`, allowing instances to be used as strings while benefiting from enumeration features, ensuring type safety and clarity in stage representation.

**Dependencies:** The `JourneyStage` class relies on the `enum` module and the `Enum` class from it, which are used to define enumerations for the journey stages. There are no outward dependencies, indicating that no other code directly utilizes the `JourneyStage` class. The nature of the inward dependency is primarily for data representation, allowing for structured and readable definitions of the journey stages.

</details>

<details>
<summary><strong>ChatSession</strong> (0 methods)</summary>

**Summary:** The `ChatSession` class represents a database model for managing chat sessions in an application, specifically tracking the progress of users through various stages of an entrepreneurship journey. Its main responsibility is to store session-related data, including a unique identifier, title, current stage, accumulated context, and timestamps for creation and updates. Key behaviors include maintaining a relationship with associated chat messages and automatically handling the creation and deletion of these messages in relation to the session.

**Dependencies:** The `ChatSession` class relies on several external dependencies, including SQLAlchemy components like `Column`, `String`, and `relationship` for ORM functionality, as well as standard library modules such as `datetime` and `uuid` for date management and unique identifier generation. It also utilizes constants like `ONBOARDING` and functions like `now` and `utc` for time-related operations. Notably, there are no outward dependencies, indicating that no other code directly relies on the `ChatSession` class.

</details>

<details>
<summary><strong>ChatMessage</strong> (0 methods)</summary>

**Summary:** The `ChatMessage` class represents a database model for storing chat messages in a chat application. Its main purpose is to manage the attributes of individual messages, including a unique identifier, associated session ID, sender role, message content, and timestamp of creation. Key behaviors include establishing a relationship with the `ChatSession` class to facilitate access to related messages and ensuring data integrity through foreign key constraints.

**Dependencies:** The `ChatMessage` class relies on several external dependencies for its functionality, including SQLAlchemy components like `Column`, `ForeignKey`, `relationship` for ORM capabilities, and standard Python libraries such as `str`, `datetime`, `timezone`, and `uuid` for data handling and unique identifier generation. Notably, it utilizes `now` and `utc` for timestamp management, indicating a focus on time-sensitive data processing. There are no outward dependencies, meaning no other code directly relies on this class, suggesting it may serve as a standalone component within a larger application.

</details>

---

### 📊 `services/api_gateway/app/database.py`

| Metric | Count |
|--------|-------|
| Classes | 0 |
| Functions | 3 |
| Imports | 17 |

#### 📝 Code Summary

> This Python file is responsible for setting up and managing a SQLAlchemy database connection, specifically for use with a FastAPI application. Its main purpose is to initialize the database, create necessary tables, and provide session management for database interactions. Key behaviors include ensuring the SQLite directory exists, creating tables based on defined models, and offering session management through context managers for both API routes and background jobs, ensuring proper transaction handling.

#### 🔗 Dependencies

> The Python file relies on several external dependencies, including the `sqlalchemy` library for database interactions, `logging` for logging functionality, and `contextlib` for context management. It uses `config` to access settings and `models` for data models, while also leveraging `__future__` for forward compatibility with type annotations. Notably, there are no outward dependencies, indicating that this file is standalone and does not serve as a module for other code.

#### ⚡ Functions

<details>
<summary><strong>init_db()</strong></summary>

**Summary:** The `init_db` function initializes a SQLite database by ensuring that the necessary directory exists and creating the required tables. Its main responsibility is to set up the database environment and structure, specifically for SQLite connections. Key behavior includes checking the database URL, creating the directory if it doesn't exist, and invoking `create_all` on the SQLAlchemy `Base` to generate the tables defined in the models.

**Uses:** `models`, `Base`, `LOGGER`, `database_url`, `os`, `create_all`, `debug`, `dirname`, `info`, `makedirs` +4 more

</details>

<details>
<summary><strong>get_session()</strong></summary>

**Summary:** The `get_session` function is a generator that provides a SQLAlchemy session for use in FastAPI routes. Its main responsibility is to create a new session instance from `SessionLocal`, yield it for database operations, and ensure that the session is properly closed after use. The key behavior is the use of a `try` block to manage the session lifecycle, ensuring resources are released even if an error occurs during the session's use.

**Uses:** `SessionLocal`, `session`, `close`

</details>

<details>
<summary><strong>session_scope()</strong></summary>

**Summary:** The `session_scope` function is a context manager that provides a transactional scope for database operations using SQLAlchemy sessions. Its main purpose is to manage the lifecycle of a database session, ensuring that changes are committed if successful, or rolled back in case of an exception. Key behavior includes yielding a session for use within a block, committing the transaction upon successful completion, and handling exceptions by rolling back any changes before closing the session.

**Uses:** `SessionLocal`, `session`, `close`, `commit`, `rollback`

</details>

---

### 🤖 `crewai-agents/src/venturebot_crew/crew.py`

| Metric | Count |
|--------|-------|
| Classes | 1 |
| Functions | 1 |
| Imports | 22 |

#### 📝 Code Summary

> The provided Python file defines a framework for an entrepreneurship coaching platform called "VenturebotsAi," utilizing various agents and tasks to assist users in the entrepreneurial process. Its main responsibility is to create and manage agents for onboarding, idea generation, market validation, and product management, as well as to define tasks related to user onboarding and market awareness. Key behaviors include dynamic tool instantiation based on available dependencies, configuration loading from environment variables, and the orchestration of agents and tasks into a cohesive crew for sequential processing.

#### 🔗 Dependencies

> The Python file relies on several external dependencies primarily from the `crewai` and `crewai_tools` libraries, which provide functionalities for agent management, task processing, and various utility tools for data retrieval and manipulation. It also utilizes the `dotenv` library for environment variable management and standard libraries like `os` and `pathlib` for file and path handling. Notably, there are no outward dependencies, indicating that this file is not directly used by any other code.

#### 🏛️ Classes

<details>
<summary><strong>VenturebotsAiEntrepreneurshipCoachingPlatformCrew</strong> (12 methods)</summary>

**Summary:** The `VenturebotsAiEntrepreneurshipCoachingPlatformCrew` class is designed to facilitate the creation and management of a crew of AI agents and tasks focused on entrepreneurship coaching. Its main responsibility is to onboard users, generate business ideas, validate markets, and manage product development through a series of defined agents and tasks. Key behaviors include the initialization of various agents with specific configurations and tools, as well as the orchestration of tasks that guide users through the entrepreneurship process in a structured manner.

**Dependencies:** The `VenturebotsAiEntrepreneurshipCoachingPlatformCrew` class relies on a variety of external dependencies, including classes like `Agent`, `Crew`, and `LLM`, as well as utility functions for data processing and file handling, such as `json`, `os`, and `path`. Notably, it does not have any outward dependencies, meaning no other code directly relies on this class. The nature of these inward dependencies suggests a focus on task management, data serialization, and interaction with external resources, likely for AI-driven entrepreneurship coaching functionalities.

**Methods:**
- `venturebot_onboarding_agent()` - The `venturebot_onboarding_agent` method creates and returns an instance of the `Agent` class, confi...
- `venturebot_idea_generator()` - The `venturebot_idea_generator` method creates and returns an instance of the `Agent` class configur...
- `market_validator_agent()` - The `market_validator_agent` method creates and returns an instance of the `Agent` class, configured...
- `venturebot_product_manager()` - The `venturebot_product_manager` method creates and returns an instance of the `Agent` class, config...
- `venturebot_technical_prompt_engineer()` - The `venturebot_technical_prompt_engineer` method creates and returns an instance of the `Agent` cla...
- `venturebot_user_onboarding_and_pain_point_discovery()` - The `venturebot_user_onboarding_and_pain_point_discovery` method initializes and returns a `Task` ob...
- `venturebot_market_aware_idea_generation()` - The `venturebot_market_aware_idea_generation` method creates and returns a `Task` object configured ...
- `comprehensive_market_validation()` - The `comprehensive_market_validation` method in the `VenturebotsAiEntrepreneurshipCoachingPlatformCr...
- `venturebot_product_requirements_and_mvp_development()` - The `venturebot_product_requirements_and_mvp_development` method creates and returns a `Task` object...
- `venturebot_no_code_builder_prompt_generation()` - The `venturebot_no_code_builder_prompt_generation` method creates and returns a `Task` object config...
- `crew()` - The `crew` method in the `VenturebotsAiEntrepreneurshipCoachingPlatformCrew` class creates and retur...
- `_load_response_format()` - The `_load_response_format` method reads a JSON configuration file from a specified directory and co...

</details>

#### ⚡ Functions

<details>
<summary><strong>_available_tools()</strong></summary>

**Summary:** The function `_available_tools` takes a variable number of tool class arguments and instantiates them, provided they are callable. Its main purpose is to create a list of available tool instances while gracefully ignoring any classes that may not be callable, which could indicate missing optional dependencies. The key behavior is the use of a list comprehension to filter and instantiate only the valid tool classes, ensuring robustness in the presence of potential errors.

**Uses:** `callable`, `tool_cls`

</details>

---

### 🤖 `crewai-agents/src/venturebot_crew/tools/custom_tool.py`

| Metric | Count |
|--------|-------|
| Classes | 2 |
| Functions | 0 |
| Imports | 7 |

#### 📝 Code Summary

> This Python file defines a custom tool for a framework, inheriting from `BaseTool`. Its main purpose is to provide a structured input schema using Pydantic for the tool's arguments and to implement a method that simulates a tool's output. The key behavior includes defining an input model with a required string argument and a `_run` method that returns a placeholder output string.

#### 🔗 Dependencies

> The Python file relies on external dependencies from the `crewai.tools` library, specifically `BaseTool`, and utilizes the `pydantic` library for data validation and settings management through `BaseModel` and `Field`. It also employs standard Python typing features for type hinting. Notably, there are no outward dependencies, indicating that this file is not utilized by any other code.

#### 🏛️ Classes

<details>
<summary><strong>MyCustomToolInput</strong> (0 methods)</summary>

**Summary:** The `MyCustomToolInput` class is a data model that defines the input schema for a tool named MyCustomTool, inheriting from `BaseModel`. Its main purpose is to enforce structure and validation for input data by requiring a single string argument, which is described in the field documentation. The key behavior is the use of Pydantic's `Field` to specify that the `argument` is mandatory and to provide a description for clarity.

**Dependencies:** The `MyCustomToolInput` class relies on the external dependency `Field`, which is typically used for defining data structures or validating input data in frameworks like Pydantic or Marshmallow. There are no outward dependencies, indicating that no other code directly utilizes this class. The nature of the inward dependency suggests that `MyCustomToolInput` is likely focused on data validation or serialization.

</details>

<details>
<summary><strong>MyCustomTool</strong> (1 methods)</summary>

**Summary:** The `MyCustomTool` class is a specialized tool that extends the functionality of `BaseTool`, providing a defined name, description, and input schema for its operation. Its main responsibility is to execute a specific task defined in the `_run` method, which currently returns a placeholder string as output. The key behavior of this class lies in its structured approach to tool definition, allowing for clear documentation and input validation through the use of an argument schema.

**Dependencies:** The class `MyCustomTool` has no external dependencies, meaning it does not rely on any external libraries or modules for its functionality. Additionally, there are no other code components that depend on `MyCustomTool`, indicating that it is not utilized or referenced elsewhere in the codebase. This isolation suggests that the class may serve as a standalone utility or prototype without integration into a larger system.

**Methods:**
- `_run()` - The `_run` method in the `MyCustomTool` class takes a string argument and returns a hardcoded string...

</details>

---

### ⚙️ `services/api_gateway/app/config.py`

| Metric | Count |
|--------|-------|
| Classes | 1 |
| Functions | 1 |
| Imports | 7 |

#### 📝 Code Summary

> This Python file defines a configuration management system for an API gateway service using Pydantic, which allows for structured settings with type validation. Its main purpose is to provide runtime configuration options such as application name, database connection string, timeout settings, and CORS policies, while also supporting environment variable loading. The key behavior includes the use of an LRU cache to optimize the retrieval of the settings instance, ensuring that the configuration is only loaded once and reused throughout the application.

#### 🔗 Dependencies

> The Python file relies on external dependencies such as `functools` for caching functionalities and `pydantic` for data validation and settings management, utilizing specific components like `Field` and `BaseSettings`. It does not have any outward dependencies, meaning no other code directly utilizes this file. The nature of these dependencies primarily focuses on data processing and configuration management through validation and caching mechanisms.

#### 🏛️ Classes

<details>
<summary><strong>Settings</strong> (0 methods)</summary>

**Summary:** The `Settings` class is a configuration handler for an API gateway service, inheriting from `BaseSettings`. Its main responsibility is to define and manage runtime settings such as the application name, database connection URL, timeout for orchestrator operations, and allowed CORS origins. Key behaviors include loading environment variables from a specified `.env` file with a defined prefix, while allowing additional fields not explicitly defined in the class.

**Dependencies:** The `Settings` class relies on external dependencies such as `Field` and `SettingsConfigDict`, which are likely used for defining configuration fields and managing settings data structures, respectively. There are no outward dependencies, indicating that no other code directly utilizes the `Settings` class. The nature of these inward dependencies suggests a focus on data processing and configuration management within the application.

</details>

#### ⚡ Functions

<details>
<summary><strong>get_settings()</strong></summary>

**Summary:** The `get_settings` function creates and returns a new instance of the `Settings` class. Its main purpose is to provide access to a settings configuration, presumably for application-wide settings management. The key behavior is that it does not check for an existing cached instance; instead, it always creates a new `Settings` object each time it is called.

**Uses:** `Settings`

</details>

---

### ⚡ `services/orchestrator/flows/startup_journey_flow.py`

| Metric | Count |
|--------|-------|
| Classes | 2 |
| Functions | 0 |
| Imports | 24 |

#### 📝 Code Summary

> The provided Python file implements a flow-based system for guiding users through an entrepreneurship coaching process using the CrewAI framework. Its main purpose is to facilitate the startup journey by managing various stages such as user onboarding, idea generation, market validation, product requirement development, and no-code prompt generation, ultimately synthesizing an entrepreneurship plan. Key behaviors include orchestrating tasks based on user input, maintaining state across different stages, and conditionally executing tasks while ensuring that previously completed stages are not repeated.

#### 🔗 Dependencies

> The Python file relies on several external dependencies primarily from the `crewai` library, which includes components for agent and task management, as well as flow control, indicating a focus on orchestrating workflows. It also utilizes standard libraries such as `pathlib` for file system operations, `pydantic` for data validation, and `typing` for type annotations, suggesting a structured approach to data handling and type safety. Notably, there are no outward dependencies, indicating that this file is self-contained and not utilized by other code.

#### 🏛️ Classes

<details>
<summary><strong>StartupJourneyState</strong> (0 methods)</summary>

**Summary:** The `StartupJourneyState` class is designed to track the various artifacts and stages of a startup's development journey within a flow-based application. Its main responsibility is to maintain user-specific information, such as the founder's name, industry focus, and details about the startup idea, while also recording completed stages and relevant reports. Key behaviors include managing user inputs and summarizing onboarding and validation processes, which facilitate the progression of the startup journey.

**Dependencies:** The `StartupJourneyState` class relies on the external dependency `Field`, which is likely used for defining attributes or data fields within the class, suggesting a focus on data modeling or validation. There are no outward dependencies, indicating that no other code currently utilizes the `StartupJourneyState` class, which may limit its integration within a larger application context. Overall, the dependency on `Field` suggests a potential role in data processing or configuration within a startup journey framework.

</details>

<details>
<summary><strong>StartupJourneyFlow</strong> (12 methods)</summary>

**Summary:** The `StartupJourneyFlow` class orchestrates a structured entrepreneurship coaching pipeline, guiding users through various stages of startup development. Its main responsibility is to manage the flow of tasks and agents that assist users in onboarding, idea generation, market validation, product requirements, and no-code prompt generation, ultimately synthesizing a comprehensive entrepreneurship plan. Key behaviors include dynamically building agents and tasks based on user input and state, executing tasks sequentially while managing state transitions, and providing feedback at each stage of the journey.

**Dependencies:** The `StartupJourneyFlow` class relies on a variety of external dependencies, including built-in Python exceptions like `ValueError`, standard functions such as `getattr`, `isinstance`, and `str`, as well as specific classes like `VenturebotsAiEntrepreneurshipCoachingPlatformCrew`. It does not have any outward dependencies, meaning no other code directly utilizes this class. The nature of its inward dependencies suggests a focus on data processing and object-oriented programming, with potential interactions involving AI coaching and task management functionalities.

**Methods:**
- `__init__()` - The `__init__` method in the `StartupJourneyFlow` class initializes an instance of the class by call...
- `_base_inputs()` - The `_base_inputs` method in the `StartupJourneyFlow` class collects essential user input data from ...
- `_build_agent()` - The `_build_agent` method in the `StartupJourneyFlow` class is responsible for creating an instance ...
- `_build_task()` - The `_build_task` method in the `StartupJourneyFlow` class retrieves a task builder function associa...
- `_context_payload()` - The `_context_payload` method in the `StartupJourneyFlow` class generates a formatted string contain...
- `_run_task()` - The `_run_task` method in the `StartupJourneyFlow` class is responsible for executing a specified ta...
- `onboarding()` - The `onboarding` method in the `StartupJourneyFlow` class collects information about the founder's c...
- `idea_generation()` - The `idea_generation` method in the `StartupJourneyFlow` class generates a market-aware idea slate b...
- `market_validation()` - The `market_validation` method in the `StartupJourneyFlow` class validates the feasibility of a sele...
- `product_requirements()` - The `product_requirements` method in the `StartupJourneyFlow` class generates detailed product requi...
- `no_code_prompt()` - The `no_code_prompt` method in the `StartupJourneyFlow` class translates user requirements into a pr...
- `entrepreneurship_plan()` - The `entrepreneurship_plan` method synthesizes the entrepreneurship journey and outlines the next st...

</details>

---

### ⚡ `services/tools/openai_web_search.py`

| Metric | Count |
|--------|-------|
| Classes | 2 |
| Functions | 0 |
| Imports | 10 |

#### 📝 Code Summary

> The provided Python file implements an OpenAI Web Search Tool designed for real-time market validation and research, specifically tailored for use with CrewAI. Its main responsibility is to facilitate web searches for competitive analysis, market trends, and industry insights by leveraging OpenAI's Responses API. Key behaviors include executing a web search based on user queries, handling API responses, and formatting the results along with relevant sources into a user-friendly output.

#### 🔗 Dependencies

> The Python file relies on several external dependencies, including the `crewai.tools` library for tool functionalities, `json` and `os` for data handling and operating system interactions, and `pydantic` for data validation and settings management. It also uses the `requests` library for making HTTP requests and `typing` for type hinting. Notably, there are no outward dependencies, indicating that this file is not utilized by any other code.

#### 🏛️ Classes

<details>
<summary><strong>OpenAIWebSearchInput</strong> (0 methods)</summary>

**Summary:** The `OpenAIWebSearchInput` class is a data model that defines the input schema for an OpenAI Web Search tool, specifically focusing on the search query parameter. Its main purpose is to ensure that the input provided for web searches is structured and validated, requiring a string that describes the search intent, such as market research or competitive analysis. The key behavior is the use of the `Field` function to enforce the presence and description of the `query` attribute, ensuring that it meets the expected criteria for effective search functionality.

**Dependencies:** The `OpenAIWebSearchInput` class relies on the `Field` dependency, which is typically used for data validation or serialization in frameworks like Pydantic or Marshmallow. There are currently no outward dependencies, indicating that no other code directly utilizes this class. The nature of the inward dependency suggests that it may be involved in defining structured data inputs, potentially for API calls or data processing tasks.

</details>

<details>
<summary><strong>OpenAIWebSearchTool</strong> (2 methods)</summary>

**Summary:** The `OpenAIWebSearchTool` class is designed to facilitate real-time web searches using OpenAI's Responses API, primarily for market research and competitive analysis. Its main responsibility is to execute search queries and return formatted results that include insights on market trends, competitive landscapes, and industry news. Key behaviors include handling API requests, managing errors, and formatting the response to present relevant information and sources in a user-friendly manner.

**Dependencies:** The `OpenAIWebSearchTool` class relies on several external dependencies, including libraries for HTTP requests (`requests`), JSON handling (`json`), and various exception handling classes (`JSONDecodeError`, `RequestException`, `Timeout`). It does not have any outward dependencies, meaning no other code directly utilizes this class. The nature of these dependencies primarily involves making API calls, processing JSON data, and handling exceptions related to network requests.

**Methods:**
- `_run()` - The `_run` method in the `OpenAIWebSearchTool` class executes a web search by sending a query to Ope...
- `_format_response()` - The `_format_response` method in the `OpenAIWebSearchTool` class formats an API response dictionary ...

</details>

---

### ⚙️ `services/api_gateway/app/logging_config.py`

| Metric | Count |
|--------|-------|
| Classes | 0 |
| Functions | 1 |
| Imports | 8 |

#### 📝 Code Summary

> This Python file sets up a centralized logging configuration for the VentureBot backend, allowing for both file and console logging. Its main responsibility is to configure logging behavior based on an environment variable for log level, ensuring logs are stored in a specified file with rotation and backups. Key behaviors include creating the necessary log directory, configuring a rotating file handler for detailed logs, and a console handler for less verbose output, while also preventing duplicate log handlers on reconfiguration.

#### 🔗 Dependencies

> The Python file relies on several external dependencies, including the `logging` module for logging functionality, `os` for operating system interactions, and `pathlib` for filesystem path manipulations. It does not have any outward dependencies, meaning no other code directly relies on this file. The nature of these dependencies primarily involves data processing and utility functions for managing file paths and logging events.

#### ⚡ Functions

<details>
<summary><strong>setup_logging()</strong></summary>

**Summary:** The `setup_logging` function configures a logging system that outputs logs to both a file and the console, with the log level adjustable via the `LOG_LEVEL` environment variable. Its main responsibility is to ensure that logs are captured efficiently, with a file handler that supports rotation (5MB max size and 3 backups) and a console handler that displays logs at the INFO level. Key behaviors include creating the necessary directory for log files, setting up log formatting, and clearing existing handlers to prevent duplicates when the function is called multiple times.

**Uses:** `Path`, `RotatingFileHandler`, `getattr`, `console_handler`, `file_handler`, `log_dir`, `logger`, `logging`, `os`, `root_logger` +14 more

</details>

---

### 🚀 `services/api_gateway/app/main.py`

| Metric | Count |
|--------|-------|
| Classes | 0 |
| Functions | 1 |
| Imports | 17 |

#### 📝 Code Summary

> This Python file defines a FastAPI application that serves as a web server with a health check endpoint and a router for chat functionalities. Its main responsibility is to initialize the database during startup and manage CORS settings for cross-origin requests. Key behaviors include logging application lifecycle events and providing a simple health check endpoint (`/healthz`) to verify the server's operational status.

#### 🔗 Dependencies

> The Python file relies on several external dependencies, including FastAPI for building web applications, contextlib for asynchronous context management, and logging for application logging. It also utilizes a configuration module for settings management and a database module for initialization. There are no outward dependencies, indicating that no other code directly relies on this file.

#### ⚡ Functions

<details>
<summary><strong>healthcheck()</strong></summary>

**Summary:** The `healthcheck` function returns a dictionary with a single key-value pair indicating the system's status as "ok." Its main purpose is to provide a simple health check response, typically used in web applications to verify that the service is running correctly. The key behavior is the straightforward return of a status message, which can be utilized by monitoring tools or health check endpoints.

**Uses:** `app`, `get`

</details>

---

### ⚡ `services/orchestrator/chat_orchestrator.py`

| Metric | Count |
|--------|-------|
| Classes | 1 |
| Functions | 0 |
| Imports | 12 |

#### 📝 Code Summary

> The provided Python file defines a `ChatOrchestrator` class that facilitates a stage-aware interaction for users navigating an entrepreneurship journey with VentureBots. Its main responsibility is to manage user input and context between various stages of the journey, allowing for a human-in-the-loop experience by inferring user details and startup ideas from conversation history. Key behaviors include formatting messages, inferring user information, and executing the next stage based on user responses, while logging important events and handling errors gracefully.

#### 🔗 Dependencies

> The Python file relies on several external dependencies, including standard libraries such as `logging`, `re`, and `typing`, as well as specific components from the `flows.staged_journey_flow` module, which provides functionality for managing journey stages and contexts. Notably, there are no outward dependencies, indicating that this file is self-contained and does not serve as a dependency for any other code. The nature of these inward dependencies suggests a focus on data processing and structured typing, likely aimed at orchestrating complex workflows or journeys.

#### 🏛️ Classes

<details>
<summary><strong>ChatOrchestrator</strong> (9 methods)</summary>

**Summary:** The `ChatOrchestrator` class manages a stage-aware interaction for users on their entrepreneurship journey, facilitating a human-in-the-loop experience by processing user inputs between stages. Its main responsibility is to build and maintain context throughout the conversation, inferring user details such as name, industry focus, and startup ideas based on the dialogue history. Key behaviors include formatting messages, inferring user information, and executing the next stage in the journey while handling errors gracefully.

**Dependencies:** The `ChatOrchestrator` class relies on a variety of external dependencies, including utility functions (e.g., `get_executor`, `reversed`, `re`), logging mechanisms (`LOGGER`), and data structures or constants (e.g., `JourneyStage`, `StageContext`, `COMPLETE`, `IGNORECASE`, `ONBOARDING`). It does not have any outward dependencies, meaning no other code directly relies on it. The nature of these inward dependencies suggests a focus on data processing, state management, and possibly interaction with user input or messaging systems.

**Methods:**
- `__init__()` - The `__init__` method in the `ChatOrchestrator` class initializes an instance of the class by settin...
- `_format_conversation()` - The `_format_conversation` method processes a list of message dictionaries, formatting each message ...
- `_infer_user_name()` - The `_infer_user_name` method analyzes a list of messages to extract and infer the user's name based...
- `_infer_industry_focus()` - The `_infer_industry_focus` method analyzes a list of conversation messages to identify the industry...
- `_infer_startup_idea()` - The `_infer_startup_idea` method analyzes a list of user messages to determine a startup idea based ...
- `_build_stage_context()` - The `_build_stage_context` method constructs a `StageContext` object by integrating information from...
- `run_onboarding()` - The `run_onboarding` method in the `ChatOrchestrator` class automates the onboarding process for a n...
- `run_next_stage()` - The `run_next_stage` method in the `ChatOrchestrator` class manages the progression of a user throug...
- `generate_response()` - The `generate_response` method in the `ChatOrchestrator` class processes user messages to generate a...

</details>

---

### 🚀 `main.py`

| Metric | Count |
|--------|-------|
| Classes | 0 |
| Functions | 0 |
| Imports | 2 |

#### 📝 Code Summary

> The provided Python file imports the `app` object from the `services.api_gateway.app.main` module. Its main purpose is to serve as an entry point for a web application, likely utilizing a framework such as FastAPI or Flask. The key behavior is that it sets up the application instance, which can be used to define routes and handle HTTP requests.

#### 🔗 Dependencies

> The Python file relies on external dependencies from the `services.api_gateway.app.main` module, specifically utilizing its `main` and `app` components. There are no outward dependencies, indicating that no other code directly relies on this file. The nature of these dependencies suggests that the file is likely involved in setting up or managing an API gateway, potentially handling data processing or routing requests through the `app` component.

---

### 🌐 `services/api_gateway/app/orchestrator_client.py`

| Metric | Count |
|--------|-------|
| Classes | 0 |
| Functions | 0 |
| Imports | 12 |

#### 📝 Code Summary

> The provided Python file defines an asynchronous module for generating replies from a chat assistant, specifically designed for onboarding users in a conversational flow. Its main responsibility is to interact with a `ChatOrchestrator` to generate responses based on the current conversation context and stage, while also handling errors gracefully. Key behaviors include invoking the orchestrator in a non-blocking manner using asyncio, logging relevant information, and providing default error messages when exceptions occur during response generation or onboarding execution.

#### 🔗 Dependencies

> The Python file relies on several external dependencies, including standard libraries such as `asyncio` and `logging`, as well as type hinting from `typing`. It also utilizes specific components from the `services.orchestrator` module, including `ChatOrchestrator` and `JourneyStage`, indicating a focus on orchestrating chat flows and managing journey stages. Notably, there are no outward dependencies, meaning no other code directly relies on this file.

---

### ⚡ `services/orchestrator/__init__.py`

| Metric | Count |
|--------|-------|
| Classes | 0 |
| Functions | 0 |
| Imports | 4 |

#### 📝 Code Summary

> This Python file serves as an orchestrator service for the CrewAI application, specifically for managing interactions within the VentureBots framework. Its main purpose is to expose the `ChatOrchestrator` and `StartupJourneyFlow` classes for use in other parts of the application. The key behavior is the organization and encapsulation of these components, allowing for streamlined access and integration within the broader system.

#### 🔗 Dependencies

> The Python file relies on external dependencies from the `chat_orchestrator` module, specifically utilizing the `ChatOrchestrator` class, as well as components from the `flows` module, particularly the `StartupJourneyFlow` class. There are no outward dependencies, indicating that no other code directly relies on this file. The nature of these dependencies suggests a focus on orchestrating chat functionalities and managing startup journey flows, likely involving data processing and workflow management.

---

### ⚡ `services/orchestrator/flows/__init__.py`

| Metric | Count |
|--------|-------|
| Classes | 0 |
| Functions | 0 |
| Imports | 9 |

#### 📝 Code Summary

> This Python file defines an orchestrator for flows related to an entrepreneurship journey, encapsulating various components necessary for managing different stages of this journey. Its main responsibility is to provide a structured interface for executing and managing the flow of stages in the entrepreneurial process, utilizing classes and functions from related modules. Key behaviors include the importation of essential classes and functions that facilitate the execution and context management of the journey stages, as well as the organization of these components for ease of access.

#### 🔗 Dependencies

> The Python file relies on several components from the `staged_journey_flow` module, including classes and functions for managing journey stages, execution, and context, as well as the `startup_journey_flow` module for handling startup processes. There are no outward dependencies, indicating that this file is not utilized by any other code. The nature of these dependencies primarily revolves around orchestrating data flow and managing the execution of various stages in a journey workflow.

---

### ⚡ `services/tools/__init__.py`

| Metric | Count |
|--------|-------|
| Classes | 0 |
| Functions | 0 |
| Imports | 0 |

#### 📝 Code Summary

> The provided Python file is a placeholder for a "Tools" module intended for a project called VentureBots. Its main purpose is likely to encapsulate utility functions or classes that support the core functionality of the VentureBots application. However, since the file contains no actual code or logic, it currently does not exhibit any behavior or functionality.

#### 🔗 Dependencies

> The Python file has no external dependencies, meaning it does not rely on any external libraries or modules. Additionally, there are no other code files that depend on this file, indicating it is standalone with no outward dependencies. As a result, the file does not engage in data processing, API calls, or provide utility functions for other code.

---

### 🧪 `test_ws.py`

| Metric | Count |
|--------|-------|
| Classes | 0 |
| Functions | 0 |
| Imports | 4 |

#### 📝 Code Summary

> This Python file implements an asynchronous chat client that interacts with a chat API and a WebSocket server. Its main purpose is to create a chat session and facilitate communication by sending a message to the server and listening for responses. The key behavior includes creating a session via an HTTP POST request, connecting to a WebSocket using the session ID, sending a predefined message, and continuously receiving messages until an "assistant_message" event is detected.

#### 🔗 Dependencies

> The Python file relies on external dependencies such as `asyncio` for asynchronous programming, `httpx` for making HTTP requests, `json` for data serialization and deserialization, and `websockets` for handling WebSocket connections. There are no outward dependencies, indicating that no other code directly relies on this file. The nature of these dependencies primarily involves data processing and network communication, facilitating asynchronous API calls and real-time data exchange.

---


---

*Generated by GitHub Codebase Analyzer*