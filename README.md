# ForgetMe.AI — Privacy-First Mental Health Assistant

Hackathon-ready full-stack demo for **selective memory deletion** and a **mock machine-unlearning workflow**.

## What this build demonstrates

1. **Chat UI** — responsive Next.js + Tailwind interface.
2. **Memory Vault** — explicit personal facts are extracted into atomic memory records.
3. **Selective Amnesia** — forget one item without clearing unrelated memories.
4. **Vector/RAG boundary simulation** — the active memory list is the only persistent context injected into the chatbot.
5. **PyTorch Gradient Ascent** — `/api/unlearn` runs a tiny, deterministic gradient-ascent demonstration that increases the selected forget-set loss.
6. **Verification** — the UI can test whether a forgotten category is still available.
7. **Export** — download the Memory Vault as JSON.
8. **Groq** — enter your Groq API key directly in the Windows launcher terminal. The key stays in the backend process and is never embedded in frontend code.
9. **Motion UX** — hover lift, shimmer, staggered entrance, floating status, flip-to-inspect memory cards, adaptive mobile vault drawer, reduced-motion support.

## Important technical note

The PyTorch operation is a **mock educational unlearning engine**. It does not prove irreversible deletion from a production LLM's neural weights. Real machine unlearning requires model-specific methods and formal evaluation. The demo intentionally separates:

- **Explicit memory deletion:** remove the selected memory from the app's active memory store.
- **Contextual erasure:** forgotten values are redacted before conversation context is sent to Groq.
- **Neural unlearning simulation:** gradient ascent is demonstrated on a tiny synthetic model.

## Windows one-click start

1. Install Python 3.11+ and Node.js 18+.
2. Double-click `run_project.bat`.
3. Paste your Groq API key when prompted, or press Enter to use local demo fallback.
4. Open `http://localhost:3000`.

The batch file creates `venv`, installs `fastapi`, `uvicorn`, `torch`, and other backend requirements, runs `npm install`, then starts both servers.

## Suggested hackathon demo

Paste:

> My name is Alex, I am 28 years old, and my salary is $80,000.

Then:

- Open **Chat**.
- Watch the Memory Vault extract Name, Age, and Salary.
- Flip the Salary card.
- Click **Forget**.
- Watch the unlearning status.
- Ask **What is my age?** → Age remains available.
- Ask **What is my salary?** → The assistant should say it no longer has that information.
- Open **Verify** for a visual verification record.
- Export the vault JSON.

## Groq configuration

The launcher sets:

`GROQ_API_KEY=<your key>`

and defaults to:

`GROQ_MODEL=llama-3.3-70b-versatile`

You can change the model inside `run_project.bat` or set `GROQ_MODEL` in the backend process.

## Safety

ForgetMe.AI is a demonstration and general wellbeing assistant, not a medical or emergency service. Do not use the hackathon demo as a substitute for professional care.
