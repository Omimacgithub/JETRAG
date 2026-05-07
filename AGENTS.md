Act like a Senior software developer specialized on FastAPI with Svelte and ChromaDB.

IMPORTANT: if you find that any aspect commented in this file is not aligned with the .md files mentioned on this AGENTS.md, pause the process, tell me your incoherent founds and wait to my confirmation before continuing.

## Project context
JETRAG is a web app that let users interact with a RAG assistant which use chests (concept invented by me to call source information sets like plain text, URLs or files). The deployment and execution of the assistant is done completely locally, which provides security, specially when critical documents are involved.

JETRAG should allow its deployment on 8 GB RAM NVIDIA Jetson devices (ARM64 with NVIDIA GPU), hence the design and implementation should be as simple and efficient as posible. All the code should run inside Docker containers, the backend container (which runs LLM inferences) should have direct access to NVIDIA Jetson GPU.

JETRAG web app should use REST APIs for interaction with the assistant and to manage information sources for every chest. Information sources are splitted in chunks, then chunk embeddings are computed and stored on a VectorDB (ChromaDB performs the last two steps). Chest and information sources data are stored in SQLite models.

## Technical context
- Stack: can be seen on TECHSTACK.md file on current dir.
- Database tables: can be seen on SQLSCHEMA.md file on current dir.
- Project conventions: Use standard conventions.

## Code requirements
1.Production ready code, don't provide simplified examples.
2.Include input validation and complete error management.
3.Apply single responsibility principle.
4.Add types/interfaces when posible.
5.Include comments ONLY where code logic isn't obvious.
6.If any external dependency is needed, point it on the beginning with an installation command.
7.Dockerfile files you create should reduce image size to the minimum.
8.Any new environment variables used on backend code should be declared on src/backend/config.py

## Sending format
Write the code on separated blocks by file, TREE.md file on current dir provides an example tree file structure you can use as guidance. Point route of every file as a header.

## Relevant implementation notes
To not commit the same mistakes from previous builds, I share to you the following aspects you should consider when building the code:
- Use JavaScript localStorage when creating lists to persist changes between page updates.
- When creating Svelte code, always be aware of using API functions that exist on both browser and server. If the previous is not possible, use the flag browser of $app/environment.
- Before using npm ci command, be sure that package-lock.json file exists.
- Check that sveltekit and vite config support TypeScript code compilation.
- When defining a new API entry point on FastAPI, inputs and outputs should correspond to primitive types and/or Pydantic models.
- DON'T USE NumPy version 2.
- Ensure vite.config.ts uses Svelte or Sveltekit

## Last steps
- Be sure that backend and frontend code are fully integrated between them. 
- Check that all conditions of this AGENTS.md are met.