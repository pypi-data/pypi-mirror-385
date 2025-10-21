# Project Design

Genie Bottle is split into a few main parts that work together. Here's how it all fits together:

![Project Design](images/Project%20code%20design.svg)

## How It All Works

When you use Genie Bottle, here's what happens:

1. You pick a Python script with spells or make a new one
2. Run `bottle serve your_script.py` to start your `Magic` API server and `Scroll` User Interface (UI)
3. The `Scroll` UI connects to the `Magic` server and lets you cast spells
4. Results come back either as normal responses or streamed in real-time

Some spells (like agent spells) stream their results back as they run using Server-Sent Events. Others just return a normal response.

## The Main Parts

### Magic (Python)

This is where all the ML magic happens. The `magic/` folder contains Python code that:

- Runs your AI models (ChatGPT, Stable Diffusion, etc.)
- Turns your Python functions into REST APIs automatically (with FastAPI under the hood)
- Streams responses back in real-time when needed

Basically, you write Python functions and turn them into spells with the `@spell` decorator, then the `Magic` class turns them into a working REST API. No FastAPI boilerplate needed!

### Scrolls (Node.js UIs)

The `scrolls/` folder is for user interfaces. Right now there's a terminal UI (TUI) that lets you chat with your agent in real-time.

The cool part is you can add whatever interface you want here - web apps, desktop apps, mobile apps. They all just talk to the Magic API.

### Docs (MkDocs)

Pretty straightforward - the `docs/` folder has all the documentation you're reading right now. Built with MkDocs and the Material theme.

Run `mkdocs serve` to preview locally, `mkdocs build` to build it.

### Tests (pytest)

The `tests/` folder has all the tests. We use pytest for testing the Python stuff.

Run with `pytest` or `pytest -v` for verbose output.

## The Folders

```
geniebottle/
├── magic/              # Python backend
│   ├── fastapi_generator.py  # Auto-generates APIs
│   └── spellbooks/            # Collections of spells
├── scrolls/            # User interfaces
│   └── tui/           # Terminal UI
├── docs/              # This documentation
├── tests/             # pytest tests
├── examples/          # Example scripts
└── bottle.py          # CLI tool
```

## Making Changes

**For Magic (backend):**

- Write Python functions
- Add `@spell` decorator
- Run `bottle serve your_script.py`

**For Scrolls (frontend):**

- `npm install` to get dependencies
- `npm run dev` to develop with hot reload
- `npm run build` to build for production

**For Docs:**

- Edit markdown files in `docs/`
- Run `mkdocs serve` to preview

That's pretty much it! The whole idea is to keep things simple and separated - Python handles the AI stuff, Node.js handles the UI, and they talk via a clean API.
