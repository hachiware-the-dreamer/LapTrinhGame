# Custom UNO Online

A Python/Pygame UNO game with local play, LAN room discovery, host-authoritative multiplayer, AI backfill, and custom house rules for cards 0, 7, and 8.

## Setup

Use Python 3.12 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Run verification before submitting changes:

```powershell
python -m unittest discover -v
python -m compileall main.py scripts tests
```

## Project Structure

- `main.py` starts Pygame, manages display mode, and owns the main loop.
- `scripts/game_manager.py` contains the authoritative UNO rules and game state.
- `scripts/screens.py` contains menu, settings, local game, lobby, and multiplayer screens.
- `scripts/ui.py`, `scripts/sprites.py`, and `scripts/assets.py` render cards, layout, and assets.
- `scripts/multiplayer.py` implements LAN discovery, room hosting, joining, and match synchronization.
- `scripts/ai.py` provides simple AI turns for local games and multiplayer backfill.
- `tests/` contains regression tests for display behavior, rule settings, and multiplayer security.
- `assets/` stores sprites, fonts, sound effects, and music.

## Gameplay

Start the game with `python main.py`. Use **Game Settings** for local matches: player count, initial cards, Rule 0/7/8 toggles, Rule 8 timer, and two-player Reverse behavior.

The screen shows the current hand, top discard, draw pile, turn direction, active effects, and match messages. If a player cannot play a legal card, they may draw one card. If the drawn card is legal, they can play it or keep it.

## UNO Rules

The base game uses a standard UNO deck: number cards, Skip, Reverse, +2, Wild, and +4. A card is legal when it matches the current color, number, or action kind, or when it is a Wild card.

House rules:

- **Rule 0:** playing a 0 asks the player to choose clockwise or counter-clockwise hand passing.
- **Rule 7:** playing a 7 asks the player to choose another player and swap hands.
- **Rule 8:** playing an 8 starts a timed reaction event. Each player can react once. The last responder draws 2 if everyone reacts; otherwise every non-responder draws 2.
- **No action-card win:** Skip, Reverse, +2, Wild, and +4 cannot be the final winning card.
- **Stacking:** after +2, the next player may stack +2 or +4. After +4, only +4 may be stacked. The first player who cannot or does not stack draws the full penalty and loses the turn.

For two-player games, Reverse behavior is configurable in local settings. `Reverse` flips direction and passes the turn; `Skip` makes Reverse act like Skip, giving the same player another turn.

## Multiplayer

Open **Multiplayer**, enter a player name, then create or join a LAN room. The host advertises rooms over UDP discovery and accepts TCP clients. A room supports 2 or 4 seats; empty seats are filled with AI when the host starts the match.

The host is authoritative. Clients send intended actions, but the host validates turn ownership, card legality, custom-rule targets, draw stacking, reaction state, and win conditions before broadcasting synchronized state.

## Security And Integrity Notes

LAN clients are treated as untrusted. The host issues session tokens, keeps tokens out of shared room state, uses host receive time for action/reaction timing, and caps TCP message buffers to reduce memory abuse from malformed clients.

Room passwords are intended only for casual LAN filtering. Traffic is not encrypted, so do not use sensitive passwords.

## Known Limitations

- Multiplayer game-rule configuration is carried in room state, but the current room creation screen exposes only room name, password, and capacity.
- Multiplayer is designed for trusted classroom/home LANs, not internet matchmaking.
- AI is intentionally simple and prioritizes legal play over advanced strategy.
