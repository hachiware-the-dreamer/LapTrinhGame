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
