# � Aim Trainer Game

A progressive difficulty aim trainer built with Pygame to test and improve your reflexes and accuracy.

---

## ✨ Features

- **60-Second Sessions**: Fixed duration gameplay with progressive difficulty
- **Reaction Time Tracking**: Measures your response time from target spawn to click
- **Progressive Difficulty**: Targets get smaller and disappear faster over time
- **Comprehensive Stats**: Tracks score, hits, misses, accuracy, and reaction times
- **Visual Feedback**: Green flash for hits, red flash for misses, floating score text

---

## 🕹️ How to Play

1. **Click "START GAME"** from the main menu
2. **Click on targets** as quickly as possible before they disappear
3. **Avoid missing** - both clicking empty space and letting targets expire count as misses
4. **Complete 60 seconds** to see your results

### Controls

- **Left Mouse Button**: Click targets
- **ESC**: Pause/Resume during gameplay

---

## 📊 Scoring System

The scoring system rewards both accuracy and speed:

### Formula

```python
score += BASE_POINTS + REFLEX_BONUS
```

Where:
- **BASE_POINTS** = 100 (constant)
- **REFLEX_BONUS** = `(TTL - Reaction Time) / TTL * BONUS_CAP`
  - TTL = Target's time-to-live (how long it stays visible)
  - Reaction Time = Time from target spawn to successful click
  - BONUS_CAP = 50 (maximum bonus points)

### Example

If a target has a TTL of 2000ms and you click it in 500ms:

$$bonus = \frac{max(0, 2000 - 500)}{2000} \times 50 = 37.5$$

$$score = 100 + 37.5 = 137.5 \text{ points}$$

**Key Points:**
- Faster clicks = higher bonus
- Click immediately = maximum 150 points
- Click at the last moment = minimum 100 points
- Misses = 0 points (and counted as a miss)

---

## 📈 Progressive Difficulty

The game becomes progressively harder over time to maintain challenge:

### Difficulty Mechanics

- **Every 5 seconds**, the difficulty increases:
  - **TTL decreases** by 100ms (targets disappear faster)
  - **Radius decreases** by 3px (targets become smaller)

### Difficulty Bounds

- **Initial Settings:**
  - TTL: 2000ms
  - Radius: 50px

- **Minimum Settings:**
  - TTL: 800ms
  - Radius: 20px

This ensures the game remains challenging but not impossible.

---

## 📋 Statistics Tracked

### During Gameplay
- **Time Remaining**: Countdown timer (60 seconds)
- **Score**: Cumulative points earned
- **Hits**: Successful target clicks
- **Misses**: Failed clicks + expired targets
- **Current TTL**: Target lifetime (ms)
- **Current Size**: Target radius (px)

### Results Screen
- **Final Score**: Total points earned
- **Hits**: Number of successful clicks
- **Misses**: Number of missed targets/clicks
- **Accuracy**: Hit percentage (Hits / Total Clicks * 100)
- **Average Reaction Time**: Mean reaction time across all hits
- **Best Reaction Time**: Fastest reaction time achieved

---

## 🎨 Target Design

Targets are circular with concentric red and white rings:
- **Outer ring** (100%): Red
- **Ring 2** (80%): White
- **Ring 3** (60%): Red
- **Ring 4** (40%): White
- **Center** (20%): Red

The entire circle is clickable - you don't need to hit the center specifically.

---

## ⚙️ Configuration

Game settings can be adjusted in `config.py`:

```python
# Game duration
GAME_DURATION = 60000  # 60 seconds

# Initial target settings
INITIAL_TARGET_RADIUS = 50
INITIAL_TTL = 2000

# Difficulty progression
DIFFICULTY_RAMP_INTERVAL = 5000  # Increase every 5 seconds
TTL_DECREASE_AMOUNT = 100
RADIUS_DECREASE_AMOUNT = 3

# Scoring
BASE_POINTS = 100
REFLEX_BONUS_CAP = 50
```

---

## 💻 Requirements

- Python 3.7+
- Pygame 2.0+

### Installation

```bash
pip install pygame
```

### Running the Game

```bash
python main.py
```

---

## 📁 File Structure

```
BTL1/
├── main.py           # Main game loop and logic
├── target.py         # Target class (concentric circles)
├── screens.py        # All screen classes (Start, Results, Pause, etc.)
├── config.py         # Game configuration and constants
├── readme.md         # This file
├── assets/
│   ├── crosshair.png # Cursor image
│   └── sound/        # Sound effects
└── font/
    └── Pixeltype.ttf # Game font
```

---

## 💡 Tips for High Scores

1. **Focus on accuracy first** - misses don't give any points
2. **Click quickly** - faster clicks = higher reflex bonus
3. **Stay calm as difficulty increases** - panic leads to misses
4. **Warm up** - your reaction time improves with practice
5. **Find your rhythm** - consistent clicking beats frantic clicking

---

## 🎨 Asset References

### Audio:
* **Hit Sound:**  https://elevenlabs.io/sound-effects/pistol
* **Miss Sound:**  https://minecraft.wiki/w/File:Player_hurt1.ogg
* **Open Sans Font:** https://fonts.google.com/specimen/Open+Sans
* **Crosshair:** https://www.flaticon.com/free-icon/crosshair_1545215?term=crosshair&page=1&position=10&origin=tag&related_id=1545215

---

**Good luck improving your aim!** 🎯
 