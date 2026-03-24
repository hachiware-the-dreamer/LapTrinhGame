# Infinite Flyer
Institution: Ho Chi Minh City University of Technology (HCMUT)

> Infinite Flyer is a 2D endless arcade game built with Python and Pygame. The player controls a flying character, avoids obstacles, collects coins, and experiences multi-layer parallax scrolling.

## 1) Introduction

- **Genre**: Endless Arcade / Flappy Bird-inspired
- **Language / Engine**: Python + Pygame
- **Project Goals**:
  - Build a complete 2D game loop with clear states (menu -> play -> pause -> game over).
  - Implement parallax scrolling with deltaTime-based movement.
  - Manage assets, audio, and collision systems in a modular code architecture.

## 2) Features

- [x] Full screen/state flow: Main Menu, Instructions, Settings, Pause, Game Over, High Score.
- [x] Multiple selectable backgrounds with parallax effects.
- [x] Procedural obstacle spawning with score zones and collectible coins.
- [x] Local high score save/load system.
- [x] Adjustable Music/SFX volume and difficulty settings.
- [x] Multiple gameplay modes (Flappy / Swing).

## 3) System Requirements

- Python: 3.10+
- OS: Windows/macOS/Linux
- Dependencies: see [requirements.txt](requirements.txt)

## 4) Installation

```bash
# (Recommended) create a virtual environment
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 5) Run the Game

```bash
python main.py
```

## 6) Controls (Game Manual)

- **Space**: flap upward (Flappy mode)
- **Left Mouse Click**: flap upward
- **P or Esc**:
  - During gameplay: pause game
  - In pause menu: resume game
- **In Settings**:
  - Change game mode
  - Select background
  - Adjust music/sfx volume
  - Tune difficulty parameters

Notes:
- In Swing mode, flap input flips gravity direction.
- UI buttons include hover and active visual states for better usability.

## 7) Gameplay Rules / Scoring

- Pass each obstacle pair: +1 point
- Collect coins:
  - Small coin: +2 points
  - Big coin: +5 points
- Game over conditions:
  - Colliding with obstacles
  - Hitting the ceiling or ground

## 8) Project Structure

```text
.
├─ main.py
├─ requirements.txt
├─ highscore.txt
├─ assets/
│  ├─ backgrounds/
│  │  ├─ bg1/
│  │  ├─ bg2/
│  │  └─ bg3/
│  ├─ obstacles/
│  ├─ musics/
│  ├─ sfx/
│  └─ sprites/
│     └─ coin/
└─ scripts/
   ├─ __init__.py
   ├─ background.py
   ├─ coin_anim.py
   ├─ entities.py
   ├─ screens.py
   ├─ settings.py
   └─ utils.py
```

## 9) Configuration

- Main configuration file: [scripts/settings.py](scripts/settings.py)
- Important tunable values:
  - Target FPS
  - Window size
  - Obstacle start gap / min gap / shrink rate
  - Music and SFX volume

## 10) Technical Explanation: Parallax Scrolling

The parallax system is designed to create depth and a continuous sense of movement.

Implementation details:

1. **At least 3 layers with different relative speeds**
- Each background uses multiple depth layers (far/mid/near).
- Distant layers move slower; closer layers move faster.
- Speeds are defined in pixels per second.

2. **deltaTime-based updates**
- In the main loop, deltaTime is computed as:
  - dt = clock.tick(FPS) / 1000.0
- Each layer updates horizontal offset with:
  - offset += speed * dt
- This keeps movement consistent across different frame rates.

3. **Seamless horizontal looping**
- To avoid gaps or visible seams, each moving layer is drawn twice side-by-side:
  - First draw at x = -offset
  - Second draw at x = -offset + image_width
- Offset is wrapped with modulo image_width for infinite scrolling.

4. **Painter's Algorithm for depth ordering**
- Layers are rendered from far to near:
  - Sky (if present)
  - Far layer
  - Mid layer
  - Foreground layer
- Nearest layers are drawn last, correctly covering farther layers.

Outcome:
- Smooth visual motion
- Stronger depth perception
- Easy extensibility for additional environment themes

## 11) Assets & References

- Background 1 (Mountains): https://opengameart.org/content/seamless-hd-landscape-in-parts
- Background 2 (Seaview): https://opengameart.org/content/background-seaview-parallax
- Background 3 (Forest): https://opengameart.org/content/parallax-background-forest-pixel-art
- Obstacles/Tiles: https://kenney.nl/assets/pixel-platformer
- Background Music: https://opengameart.org/content/happy-arcade-tune
- Coin Sprite: https://opengameart.org/content/spinning-pixel-coin-0
- Game Over SFX: https://pixabay.com/sound-effects/search/game-over/
- Coin Pick-up SFX: https://pixabay.com/sound-effects/search/8-bit%20coin/

