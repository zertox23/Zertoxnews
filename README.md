ZertoxNews

ZertoxNews is a fully automated news distribution system that combines a custom scraping API with a Discord bot. It allows communities to automatically receive fresh articles from any website without manual setup.

Features

Dynamic scraping: supports any website through custom scraping rules passed to the API and stored in JSON.

Discord integration: add new sources, test scrapers, and manage feeds using slash commands.

Background tasks: periodically fetches new articles and posts them into mapped Discord channels.

Media support: handles text, images, and video, with database-backed storage.

Database persistence: MySQL with SQLAlchemy ORM to store articles, media, sources, and channel mappings.

Tech Stack

Python – Discord bot and API client logic

Discord.py – slash commands, embeds, automation

FastAPI (API service) – scraper management and article pipeline

SQLAlchemy + MySQL – persistent storage for articles and sources

Loguru – structured logging

Docker – containerized API service (bot runs standalone)

Project Structure

main.py – entry point, loads cogs and background tasks

commands.py – slash commands for managing sources and channels

background_tasks2_0.py – periodic jobs to fetch and post news

db.py – database models and session manager

funks.py – utility functions (embeds, downloads, etc.)

models.py – Pydantic models for file and media handling

api.py – client wrapper for the ZertoxNews API

Workflow

Admin runs a slash command (for example /add_new_source).

Bot sends configuration to the API, which validates and stores the scraping rules.

The source is linked to a Discord category and channels are created as needed.

Background tasks fetch articles, store them in MySQL, and post them into mapped channels.

Articles are posted with full text and media using Discord embeds.
