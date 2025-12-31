# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
# Install dependencies
pip install -r requirement.txt

# Run the game
python script.py
```

## Project Overview

Dodge the Tejecks is a Pygame-based arcade game where players dodge falling objects (displayed as images) to earn points. The game features:

- **Main menu system** with keyboard navigation (number keys 1-5)
- **Difficulty levels**: Easy (5), Medium (10), Hard (15), Impossible (30), God Mode (100), Creator Mode (150) - values represent falling object speed
- **Shop system** for equipping different player characters
- **Persistent save system** using JSON (`save_progress.json`)

## Code Architecture

The entire game is contained in `script.py` as a single-file Pygame application:

- **Global state**: Points, shop items, equipped item, and screen are managed as module-level globals
- **Screen functions**: Each game screen (`main_menu()`, `shop()`, `game_loop()`, `game_over()`, etc.) runs its own event loop
- **Difficulty parameter**: The `game_loop(difficulty)` function takes a speed value that determines how fast objects fall
- **Image assets**: Character images (`.jpeg` files) are loaded at module initialization into `shop_items` dictionary

## Controls

- **Menus**: Number keys (1-5) to select options, B to go back
- **Shop**: UP/DOWN arrows to navigate, ENTER to purchase/equip
- **Gameplay**: LEFT/RIGHT arrows to move player

## Assets Required

The game expects these image files in the root directory:
- `tejeck.jpeg`, `babytejeck.jpeg`, `amelia.jpeg`, `me.jpeg`, `babes.jpeg`, `alvin.jpeg` (player characters)
- `adeline.jpeg` (falling objects)
- `game_over.jpeg` (game over screen)
