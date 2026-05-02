# UNO tay` Tasks

## Task 5:
- them asset hoac sua gameplay cho dep hon

## Task 6: Multiplayer - Lobby & Room System
- [x] **Lobby Interface:** Create a menu screen that displays a list of active, joinable rooms.
- [x] **Room Creation:** Allow a host to create a room with specific parameters: Room Name, Password, and Player Capacity (2 or 4 players).
- [x] **Room Visibility:** Dynamically update the lobby list to hide rooms that are currently full.
- [x] **Room Re-listing:** Re-add a room to the visible lobby list if a player leaves and a slot opens up.
- [x] **Room Deletion:** Automatically destroy and remove the room from the list if all human players leave (resulting in an all-AI room).

## Task 7: Multiplayer - Architecture & AI Backfill
- [x] **Host-Authoritative Server:** Implement the client-server architecture where the room creator's machine acts as the central server/host for that match.
- [x] **AI Substitution:** When the host presses "Start Match," check the current player count. Automatically spawn AI bot instances to fill any vacant slots up to the chosen capacity (2 or 4).
- [x] **Action Validation:** Ensure the host validates all moves (legal cards, valid targets for Rule 7, stacking legality) before broadcasting to clients.

## Task 8: Multiplayer - State Synchronization
- [x] **Simultaneous Broadcasting:** Send updated game states from the host to all clients simultaneously whenever an action occurs.
- [x] **Sync Card Plays:** Synchronize the action of a card being played, ensuring the visual animation translates correctly for each player's local directional perspective.
- [x] **Sync Card Draws:** Broadcast when a player draws a card so all clients update that opponent's visible card count.
- [x] **Sync Custom Rules:** Broadcast the exact state changes for the Rule of 0 (directional hand shift) and Rule of 7 (target hand swap) so the visual clump-and-distribute animations trigger for everyone at the same time.

## Task 9: Multiplayer Visuals - Read Server Events
*Note: Animations must be decoupled from local mouse clicks and instead driven by the `event` dict inside the `match_sync` payloads returned by `MultiplayerClient.poll_messages()`.*

- [x] **Relative Player Mapping:** The `match_sync` payload contains `seat_names` and `game["current_player"]`. Map the server's `actor_id` to the local client's screen anchors (Local Client = Bottom, Next = Left, etc.) based on their seat index relative to the local player's seat.
- [x] **Play/Draw Animations via Events:** - Loop through messages from `client.poll_messages()`. If the message `type` is `"match_sync"` and an `event` exists:
  - If `event["action"] == "play"`, animate the `event["played_card"]` flying from the mapped `actor_id`'s anchor to the center discard pile.
  - If `event["action"] == "draw"`, animate a card flying from the center draw pile to the mapped `actor_id`'s anchor.
- [x] **Custom Rule Animations via Events:**
  - If `event["action"] == "rule_0"` or `event["action"] == "rule_7"`, trigger Phase 1 (The Clump) of the hand-swapping animation.
  - Wait for the *next* `match_sync` packet containing the updated `game["player_hands"]` before triggering Phase 2 (distributing the cards to their new anchors).
- [x] **Sync Directional Arrows:** Tie the rotation of the center play arrows directly to `game["turn_direction"]` from the `match_sync` payload, so it instantly reverses for all clients when the server updates the state.

## Task 10: Server-Side AI Pacing & Local Debounce
*Note: The server currently computes AI turns instantly via a `while` loop in `_auto_resolve_ai_pending`, which breaks client animations. We must implement a timestamp-based cooldown.*

- [x] **Modify `HostAuthoritativeMatch` Initialization:**
  - Open `multiplayer.py`.
  - In `HostAuthoritativeMatch.__init__`, add a new variable to track the cooldown: `self.next_ai_action_time_ms = 0`.
- [x] **Refactor `_auto_resolve_ai_pending`:**
  - Remove the `while safety > 0 and self.game.winner is None:` loop. The method should only process *one* AI action per call.
  - Add a check at the top of the method: `if now_ms < self.next_ai_action_time_ms: return []`.
  - At the end of the method, right before returning the `events` list, set the cooldown for the next AI turn: `self.next_ai_action_time_ms = now_ms + 1500` (adds a 1.5-second delay).
- [x] **Restore Local Input Debounce:** - In the Pygame frontend, re-implement the local `is_animating` flag.
  - While `is_animating == True`, ignore all local mouse clicks to prevent the player from sending a `"submit_action"` payload to the server while the client is still rendering a previous `match_sync` event.

### Implementation Notes (Task 9/10)
- Hand-transfer choices in multiplayer (`choose_zero_direction` / `choose_seven_target`) were decoupled from local click animations: local click now only submits to host, and visuals are driven by `match_sync.event`.
- Rule 0/7 now runs as two-phase remote animation: clump on `event["action"] in {"rule_0","rule_7"}`, then distribute only after a later `match_sync` arrives with changed `player_hands`.
- Added server-side AI pacing regression tests (`tests/test_multiplayer_security.py`) to ensure one AI action per call and cooldown gating.
- Timing consistency fix: multiplayer host-submitted actions now use host wall-clock milliseconds, preventing mixed timestamp domains from prematurely resolving timed effects.
- Crash fix: normalized card-signature sorting for hand-swap sync detection so mixed `None`/string fields no longer raise `TypeError` during Rule 7 swaps.
- Freeze fix: Rule 7 client no longer waits forever for a second sync packet; if the resolving packet already contains post-swap state, that snapshot is queued immediately for phase-2 distribution.

## Task 11: Polish UNO Call Mechanics & Visual Effects
*Note: The UNO button logic needs refinement to prevent false activations, and we need to add the specific Vietnamese text popups and screen flashes.*

- [ ] **Smart UNO Button Activation:**
  - Update the local UI logic: The "UNO" button should *only* light up and become interactable if the local player's hand size is exactly 2 AND at least one of those 2 cards is a legal play (matches current color, number, action, or is a Wild).
  - Ensure the button remains dimmed/disabled if the player has 2 cards but no legal moves (meaning their only option is to draw).
- [ ] **Success Visuals ("tao tay` roi"):**
  - Create a visual event that triggers when a player successfully calls UNO.
  - Draw a screen-wide, semi-transparent green overlay (e.g., using `pygame.Surface` with alpha) that flashes and quickly fades out.
  - Render large, bold text in the exact center of the screen that says: **"tao tay` roi"**.
- [ ] **Catch/Penalty Visuals ("chua tay` dau"):**
  - Create a visual event that triggers when a player is caught failing to call UNO and receives the +2 penalty.
  - Draw a screen-wide, semi-transparent red flash overlay that quickly fades out.
  - Render large, bold text in the exact center of the screen that says: **"chua tay` dau"**.
- [ ] **Multiplayer Sync for Visuals:**
  - Hook these new visual effects into the multiplayer event listener (Task 9). 
  - When `client.poll_messages()` receives an `event["action"] == "uno"`, trigger the green flash. 
  - If you implement a "caught" event, trigger the red flash globally so everyone in the lobby sees the text and flash when someone gets penalized.
