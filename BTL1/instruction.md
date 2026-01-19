# Assignment 1 Assessment Criteria - “Whack-a-Zombie” 

## Required Features (10 pts total) 

### Background with multiple zombie spawn locations (2 pts) 

* Provide a background scene with several distinct positions where zombies can appear.
* **Recommendation:** at least 6 clearly separated spawn points distributed across the playfield.

### Zombie design (sprite/art) (1 pt) 

* Include a distinct zombie visual (head or full body).
* Ensure consistent art style; credit sources if you use third-party assets.

### Zombie head display and lifetime (1–2 pts) 

* **1 pt:** The zombie head appears and persists until hit (no auto-disappear).
* **2 pts:** The zombie head has a timer and automatically disappears after a set duration.
* **Recommendation:** lifetime between **800–1500 ms**; use different durations to vary difficulty.

### Mouse interaction / hit detection (3 pts) 

* Capture mouse click events at coordinates (x, y).
* Determine whether the click hits the zombie's head (use a hitbox or pixel-perfect test).
* Prevent double-counting on a single click; ignore clicks while animations are finishing.

### Score output (HUD) (1–2 pts) 

* **1 pt:** Display either hits or misses.
* **2 pts:** Display both hits and misses, and show a differential or ratio (for example, accuracy percent).
* **Accuracy formula:** `accuracy = hits / (hits + misses) x 100 percent`.

## Bonus (Extra Credit) 

### Audio 

* Add background music and a distinct sound effect when a zombie is hit.
* Provide a mute/unmute toggle and reasonable volume levels.

### Hit Effects 

* Show immediate visual feedback (for example, flash, particles, squash/stretch) when a hit is registered.

### Spawn/Despawn Animation 

* Animate zombies appearing and disappearing (fade, pop, slide, or scale).

## Notes and Clarifications 

* Display the HUD (hits, misses, accuracy) in a readable corner (for example, top-left).
* Keep the frame rate stable; keep spawn timing independent of animation speed if possible.
* Use a game loop to manage spawn timing and ensure only one head is counted per click.
* Prepare assets at appropriate resolutions to avoid blurring; test on common screen sizes.
* Include a short README on how to run the game and the control scheme.
