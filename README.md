# Dungeon Crawler Game

A procedural dungeon crawler built with Pygame. Objective is to clear rooms, fight enemies, defeat the boss, and escape.

## Controls

| Key | Action |
|-----|--------|
| W/A/S/D | Move |
| Mouse click | Shoot |
| I | Open inventory |

## How to Run

```bash
pip install pygame
python3 main.py
```

## Gameplay

1. **Lobby** — Start here. Head to the portal to enter the dungeon.
2. **Dungeon** — Procedurally generated rooms connected by doors. Each room spawns 1-3 enemies. Clear all rooms to unlock the boss.
3. **Boss Fight** — A multi-phase boss encounter (walking, aiming, firing, charging).
4. **Escape** — After defeating the boss, a portal appears. Head back to the lobby to play again.

## What I Learned

- Game state management (state machine pattern)
- Collision detection and resolution
- Procedural room generation with door placement
- Entity-component design
- Pygame rendering and camera system
