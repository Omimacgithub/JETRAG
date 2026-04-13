Act like a Senior software developer specialized on FastAPI with Svelte and ChromaDB.

IMPORTANT: if you find that any aspect commented in this file is not aligned with the .md files mentioned on this AGENTS.md, pause the process, tell me your incoherent founds and wait to my confirmation before continuing.

## Project context
JETRAG is a web app that let users interact with a RAG chatbot which use chests (concept invented by me to call source information sets like plain text, URLs or files). The deployment and execution of the chatbot is done completely locally, which provides security, specially when critical documents are involved.

JETRAG should allow its deployment on 8 GB RAM NVIDIA Jetson devices (ARM64 with NVIDIA GPU), hence the design and implementation should be as simple and efficient as posible. All the code should run inside Docker containers, the backend container (which runs LLM inferences and embedding model for RAG) should have direct access to NVIDIA Jetson GPU.

JETRAG web app should use REST APIs for interaction with the chatbot and to manage information sources for every chest. Information sources are splitted in chunks, then chunk embeddings are computed and stored on a VectorDB (ChromaDB). Chest and information sources data are stored in SQLite models.

I want you to implement the following:

## Functionality
JETRAG web app consist on two main windows, one for displaying and select existing chests or create new ones (called CHESTS PAGE for now, this is the starting window), and the other for chatting and managing information sources of a specific chest (called CHAT PAGE for now). Every window and between windows flow can be found on APPFLOW.md file on current dir. File ../design/prototypes/MAIN.png shows a CHESTS PAGE concept (its just a concept, you can adapt it according to your needs). Starting on APPFLOW.md STEP 1 (CHESTS PAGE), existing chests list is retrieved from backend (SQLite db) using a GET request. Create new chest button asks the user for new chest name, then it is registered on SQLite db through POST request and app flow changes to STEP 2 with new chest content (initially an empty set of sources). Each listed chest on CHESTS PAGE is an item which, if focused with cursor or keyboard, can be deleted from SQLite db through DELETE request or modify its name with PATCH request. If user clicks on a chest item, app flow changes to STEP 2 with chest sources retrieved from SQLite db with GET request.

File ../design/prototypes/CHAT.png shows a CHAT PAGE concept (its just a concept, you can adapt it according to your needs). APPFLOW.md STEP 2 shows CHAT PAGE window, create new chest button asks the user for new chest name, then it is registered on SQLite db through POST request and app flow remains on STEP 2 with new chest content (initially an empty set of sources). Left panel displays existing chest sources and "add new sources" button that if pressed, user can input data in form of plain text, URL or file (several inputs can be stored using javascript localstorage). When user confirms input data, then app flow changes to STEP 3, which receives user input data on backend through POST request. Because STEP 3 can take quite seconds, the web interface should display a charge circle to tell user that processing is taking place. When STEP 3 finishes, app flow goes back to STEP 2 with updated chest sources list through GET request. Every displayed source is an item which, if focused with cursor or keyboard, can be deleted from SQLite db through DELETE request or enable its use on LLM chat answer through a check box. CHAT PAGE main area shows chat messages where user can ask to the LLM. When user sends a question to the LLM, then app flow changes to STEP 4 (which performs a conventional RAG pipeline). Finally, STEP 5 is reached when LLM returns the answer.

App should run inside Docker containers, DOCKERARCH.md file on current dir shows app container division, how containers are connected and the following persistent volumes used:
- ./data/sqlite/jetrag.db: SQLite db (for models following the schema specified on SQLSCHEMA.md file on current dir).
- ./data/chroma/: ChromaDB vector db.
- ./triton/models/: TensorRT optimized LLM and embeddings models.
When you create docker-compose.yml file, you can follow the configuration on section "docker-compose.yml" from DOCKERARCH.md file on current dir.


## Technical context
- Stack: can be saw on TECHSTACK.md file on current dir.
- Database tables: can be saw on SQLSCHEMA.md file on current dir.
- Proyect conventions: Use standard conventions.

## Code requirements
1.Production ready code, don't provide simplified examples.
2.Include input validation and complete error management.
3.Apply single responsibility principle.
4.Add types/interfaces when posible.
5.Include comments ONLY where code logic isn't obvious.
6.If any external dependency is needed, point it on the beginning with an installation command.
7.Dockerfile files you create should reduce image size to the minimum.

## Sending format
Write the code on separated blocks by file, TREE.md file on current dir provides an example tree file structure you can use as guidance. Point route of every file as a header.

## Relevant implementation notes
To not commit the same mistakes from previous builds, I share to you the following aspects you should consider when building the code:
- Before using npm ci command, be sure that package-lock.json file exists.
- Check that sveltekit and vite config support TypeScript code compilation.
- When defining a new API entry point on FastAPI, inputs and outputs should correspond to primitive types and/or Pydantic models.
- DON'T USE NumPy version 2.
- Ensure vite.config.ts uses Svelte or Sveltekit

## README.md
Create a README.md file with the following:
- Software requirements section.
- Steps to deploy the app locally and in Docker containers (provide steps to create a python3 venv).
- Specify URLs to connect with services.
- Add any other relevant aspect.

## Last steps
- Be sure that backend and frontend code are fully integrated between them. 
- Check that all sections of this AGENTS.md are fulfilled.