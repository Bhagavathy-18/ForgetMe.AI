# Updated Project Prompt — ForgetMe.AI

Role: You are an expert Full-Stack AI Engineer and UX/UI Developer building a hackathon-winning project called "ForgetMe.AI - The Privacy-First Mental Health Assistant".

Task: Generate/update the complete project codebase and provide it as a downloadable ZIP file. Include a Windows Batch file (`run_project.bat`) at the root directory so the project can be set up and started with one click.

## Core Problem & Proposed Solution

AI therapy and companion bots can collect sensitive personal data such as name, age, salary, and life events. A user may want the assistant to forget one sensitive detail without losing the rest of the conversation and useful memories.

ForgetMe.AI demonstrates selective machine unlearning for NLP. A chat interface is paired with a transparent Memory Vault. When a user requests that a specific entity be forgotten, the application isolates that memory, removes it from the explicit memory store, redacts the forgotten value from future LLM context, and runs a mock PyTorch Gradient Ascent routine to demonstrate a targeted reverse-learning operation.

## Architecture

1. Named Entity Recognition (NER) & Explicit Memory Vault
2. Selective Unlearn Trigger
3. Explicit memory/context purge
4. Targeted neural-erasure demonstration using Gradient Ascent
5. Retrieval verification

## UI / UX

Use the existing ForgetMe.AI minimalist black/white visual language and Tailwind CSS.

- Fully responsive.
- Desktop: persistent Memory Vault on the left and chatbot on the right.
- Mobile: adaptive collapsible Memory Vault.
- High contrast, clean typography, large touch targets.
- Hover lift and shimmer effects.
- Animated entrances and status indicators.
- Interactive flip cards for inspecting memory details.
- Press/tap feedback.
- Reduced-motion accessibility support.
- Export My Data JSON action.
- Keep the UI polished and hackathon-demo friendly.

## Tech Stack

- Frontend: Next.js + React + Tailwind CSS.
- Backend: FastAPI.
- ML core: PyTorch mock unlearning engine.
- NLP: lightweight transparent NER-style extraction.
- LLM: Groq API, with API key entered in the Windows terminal and kept in the backend process.

## Required Features

1. Mental Health Chat UI.
2. Memory Vault with Name, Age, Salary and other extracted facts.
3. Export My Data JSON.
4. Selective Amnesia: forget a single memory.
5. `/api/unlearn` route triggering the PyTorch Gradient Ascent demonstration.
6. Verification route and UI.
7. Windows `run_project.bat`.
8. Extensive code comments for hackathon judges.
9. Clear disclaimer that the neural unlearning implementation is a mock educational demonstration, not a production irreversible erasure guarantee.

## Groq terminal setup

`run_project.bat` must prompt:

`Groq API key:`

The entered key must be provided only to the FastAPI process as `GROQ_API_KEY`. It must not be hard-coded into source files, frontend JavaScript, localStorage, or committed configuration.

## Deliverable

A complete ZIP containing `frontend`, `backend`, `requirements.txt`, `README.md`, `UPDATED_PROMPT.md`, and `run_project.bat`, without generated build caches such as `.next`, `node_modules`, or `__pycache__`.
