# Tank Battle — Complete Feature Checklist

---

## 1. Game Flow & Scenes

- [ ] **Main Menu** — Play and Quit buttons with click sound effects
- [ ] **Map Selection Screen** — Grid of 10 maps with PNG preview thumbnails, hover/press animations, and a styled back button
- [ ] **Game Scene** — Procedurally generated arena with HUD, pause menu, and end screen
- [ ] **Scene transitions** — Main Menu → Map Selection → Gameplay, with Restart / Choose Map / Main Menu options after game-over

---

## 2. Level Generation

- [ ] **10 text-based maps** (map1.txt–map10.txt) of varying sizes (13×13 up to 36×18)
- [ ] **Procedural map loading** — `LevelManager` reads tile data (`W`, `P1`, `P2`, `.`) and spawns walls + player spawns
- [ ] **Auto camera setup** — Camera position and orthographic size adjust dynamically to fit any map
- [ ] **Border walls** — Indestructible outer edges
- [ ] **Inner walls** — Destructible (5 HP each), darken as they take damage, explode on destruction
- [ ] **Map preview generator** — Editor tool that creates color-coded 256×256 PNG previews

---

## 3. Tank Movement

- [ ] **Player 1 controls** — WASD (keyboard) / left stick (gamepad)
- [ ] **Player 2 controls** — Arrow Keys (keyboard) / left stick (gamepad)
- [ ] **360° rotation** at 180°/sec
- [ ] **Bidirectional movement** at 5 units/sec
- [ ] **Axis-aligned wall collision** — X and Y axes resolved independently to prevent wall clipping
- [ ] **Engine audio** — Looping move sound while moving

---

## 4. Tank Shooting

- [ ] **Player 1 fire** — Space / F key / gamepad west button
- [ ] **Player 2 fire** — Enter / M key / gamepad west button
- [ ] **Fire cooldown** — 0.5 seconds between shots
- [ ] **Muzzle flash** particle effect on each shot
- [ ] **Fire sound effect**

---

## 5. Bullet Physics

- [ ] **Raycast-based movement** at 10 units/sec
- [ ] **Elastic wall reflection** — Bullets bounce off walls up to 3 times
- [ ] **Bounce particle effect** + bounce sound on each wall collision
- [ ] **Friendly fire immunity** — Bullets pass through the tank that fired them
- [ ] **Damage on enemy hit** — 1 damage per bullet, with hit particle effect
- [ ] **Auto-destroy** after max bounces

---

## 6. Tank Health

- [ ] **3 hearts** starting health
- [ ] **Heart UI display** — Hearts shown/hidden in HUD (top-left for P1, top-right for P2)
- [ ] **Hurt sound** when taking damage
- [ ] **Death sequence** — Explosion particles + sound, sprites hidden, collider/scripts disabled, 1-second delay before object destruction
- [ ] **Game-over trigger** — Notifies `GameManager` to show end screen and freeze game

---

## 7. Power-Up System

- [ ] **4 power-up types:**
  - [ ] **Speed Boost** — 1.5× movement speed for 5 seconds, trail visual effect
  - [ ] **Triple Shot** — 3-bullet cone (15° spread) for 5 seconds, aura visual effect
  - [ ] **Shield** — Blocks all damage for 5 seconds, bubble visual effect
  - [ ] **Health Boost** — Instant +1 HP, heal particle effect (no timer bar)
- [ ] **Floating bob animation** — Sine wave on all pickups
- [ ] **Pickup sound effect**
- [ ] **Refreshable** — Picking up the same type resets the timer
- [ ] **Spawn system** — 3 initial, then 3 every 5 seconds, max 5 on map
- [ ] **Smart tile tracking** — Power-ups only spawn on empty tiles, tiles freed when power-up is collected/destroyed

---

## 8. Power-Up Bar UI (HUD)

- [ ] **Depleting timer bar** for each active timed power-up
- [ ] **Color-coded** — Orange (Speed), Blue (Triple Shot), Green (Shield)
- [ ] **3D styled bar** — Dark border with drop shadow, inner track, highlight overlay
- [ ] **Bold text label** with outline for readability
- [ ] **Elastic pop-in animation** on spawn
- [ ] **Breathing color effect** while active
- [ ] **Red danger flash** when below 25% remaining
- [ ] **Pop-out shrink** animation before disappearing
- [ ] **Vertical stacking** — Multiple bars stack with spacing
- [ ] **No bar for instant effects** — Health Boost does not show a bar

---

## 9. Pause Menu

- [ ] **Escape key** to toggle pause (New Input System)
- [ ] **Time freeze** — `Time.timeScale = 0` while paused
- [ ] **Buttons** — Resume, Restart, Main Menu
- [ ] **Disabled after game-over** — Prevents unpausing a finished game

---

## 10. End Screen

- [ ] **Winner announcement** — Shows winner name with auto-sizing text
- [ ] **Game freeze** — `Time.timeScale = 0` on tank destruction
- [ ] **Parent canvas activation** — End Screen Canvas properly enabled on game-over
- [ ] **Buttons** — Restart, Choose Map, Main Menu

---

## 11. Audio System

- [ ] **Singleton AudioManager** — Persists across scenes (`DontDestroyOnLoad`)
- [ ] **Music tracks:**
  - [ ] Intro/menu music (0.5 volume)
  - [ ] Gameplay music (0.2 volume)
  - [ ] End screen music
- [ ] **Sound effects (8):** Click, Fire, Bounce, Explode, Move (loop), Hurt, Pickup, End
