# SimpleFeed: A Minimal Web Feed

This is **SimpleFeed**, a minimal RSS reader built with Python and Django that allows users to subscribe and manage custom web feeds. Users can explore, organize, and archive their favorite feeds—all from a clean web interface with automatic daily updates.

## Key Features

- User authentication (register, login, logout)
- Add and manage your own RSS/Atom feeds
- Daily feed updates powered by `schedule` + background threading
- View and delete individual feed items
- Personal user profiles with optional public visibility
- Toggle feeds between public/private and active/inactive
- "Random Feed" explorer to discover public content
- ⚙Admin integration for managing users, feeds, and entries

## Project Structure

- `feeds/models.py` — Defines custom `User`, `Profile`, `Feed`, and `Item` models
- `feeds/util.py` — Fetches/parses feeds using `feedparser` and stores items in the DB
- `feeds/views.py` — Implements all core logic for feed and profile interaction
- `feeds/urls.py` — Maps routes for the main app interface
- `capstone/settings.py` — Configured for local SQLite dev + custom user model
- `templates/feeds/*.html` — Dynamic rendering with Django templates (not included here)
- Background task runner in a dedicated thread for daily refresh (7:30 AM)


