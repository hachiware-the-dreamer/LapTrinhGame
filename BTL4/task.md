# UNO tay` Tasks

## Task 1: Fix Player 3 (Top Player) UI Clipping
- [ ] **Adjust P3 Anchor:** Move Player 3's card anchor position further down (increase the Y-coordinate).
- [ ] **Adjust P3 Text:** Move Player 3's status/name text down accordingly.
- [ ] **Verification:** Ensure that when a "+2" or "+4" penalty text appears, there is no overlapping or clipping between the penalty text and P3's cards/UI.

## Task 2: Update Directional Play Arrows
- [ ] **Redesign Asset:** Replace the current center arrow graphic with a design featuring exactly 4 arrows (pointing in a circular sequence).
- [ ] **Center Positioning:** Ensure the center of the 4-arrow graphic aligns perfectly with the center of the draw/discard piles.
- [ ] **Rotation Logic:** Confirm the arrows smoothly rotate clockwise or counter-clockwise based on the active `play_direction` state.

## Task 3: Revamp Wild / +4 Color Selection UI
- [ ] **Simon-Says UI:** Replace the current color selection menu with a circular UI split into 4 equal quarters (Red, Blue, Green, Yellow), resembling a "Simon Says" wheel.
- [ ] **Positioning:** Center this wheel on the screen, popping up when a Wild or +4 card is played.
- [ ] **Mouse Interaction:** Add collision detection so hovering over a quarter highlights it, and clicking selects the color.
- [ ] **Card Visual Update:** Once a color is chosen, update the sprite/surface of the Wild/+4 card currently resting on the top of the discard pile to visually reflect the chosen color (e.g., tinting it or swapping to a specific colored-wild sprite).

## Task 4: Draw Pile "Play or Keep" Decision
- [ ] **Logic Hook:** Intercept the draw logic. When a player clicks the draw pile, check if the drawn card is legal to play immediately.
- [ ] **Decision UI:** If the card *can* be played, pause the turn and display a temporary UI prompt with two buttons: "Play" and "Keep".
- [ ] **Play Option:** If "Play" is clicked, animate the card moving to the discard pile and trigger its effects.
- [ ] **Keep Option:** If "Keep" is clicked (or if the drawn card is illegal), animate the card moving to the player's hand and end their turn.

## Task 5: The "UNO" Call Mechanic
- [ ] **UNO Button UI:** Add an "UNO" button to the game interface that players can click. --> pop up text that says "player {player.num} tay` roi"
- [ ] **UNO Call Logic:** Require a player to click this button when playing their second-to-last card (dropping their hand to exactly 1 card).
- [ ] **Catch/Penalty System:** Implement a "Catch" mechanic (either a button for opponents or an automatic check before the next turn).  --> pop up text that says "chua tay` dau"
- [ ] **Penalty Application:** If a player holds 1 card, hasn't pressed "UNO", and is caught, force them to draw a 2-card penalty.
--> play wow sfx

## Task 6: Multiplayer - Lobby & Room System
- [ ] **Lobby Interface:** Create a menu screen that displays a list of active, joinable rooms.
- [ ] **Room Creation:** Allow a host to create a room with specific parameters: Room Name, Password, and Player Capacity (2 or 4 players).
- [ ] **Room Visibility:** Dynamically update the lobby list to hide rooms that are currently full.
- [ ] **Room Re-listing:** Re-add a room to the visible lobby list if a player leaves and a slot opens up.
- [ ] **Room Deletion:** Automatically destroy and remove the room from the list if all human players leave (resulting in an all-AI room).

## Task 7: Multiplayer - Architecture & AI Backfill
- [ ] **Host-Authoritative Server:** Implement the client-server architecture where the room creator's machine acts as the central server/host for that match.
- [ ] **AI Substitution:** When the host presses "Start Match," check the current player count. Automatically spawn AI bot instances to fill any vacant slots up to the chosen capacity (2 or 4).
- [ ] **Action Validation:** Ensure the host validates all moves (legal cards, valid targets for Rule 7, stacking legality) before broadcasting to clients.

## Task 8: Multiplayer - State Synchronization
- [ ] **Simultaneous Broadcasting:** Send updated game states from the host to all clients simultaneously whenever an action occurs.
- [ ] **Sync Card Plays:** Synchronize the action of a card being played, ensuring the visual animation translates correctly for each player's local directional perspective.
- [ ] **Sync Card Draws:** Broadcast when a player draws a card so all clients update that opponent's visible card count.
- [ ] **Sync Custom Rules:** Broadcast the exact state changes for the Rule of 0 (directional hand shift) and Rule of 7 (target hand swap) so the visual clump-and-distribute animations trigger for everyone at the same time.