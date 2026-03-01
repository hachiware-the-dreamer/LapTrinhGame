# Tank Battle

A 2-player local multiplayer tank combat game built with Unity. Battle your friend in strategic tank warfare with bouncing bullets and power-ups.

---

## Features

- **Local Multiplayer**: 2-player competitive gameplay on the same keyboard
- **Bouncing Bullets**: Bullets ricochet off walls up to 3 times for strategic shots
- **Power-Up System**: Collect power-ups to gain temporary advantages
- **10 Maps**: Various battlefield layouts to master
- **Destructible Walls**: Some walls can be destroyed by bullets
- **Health System**: Each tank has 3 HP - last one standing wins

---

## How to Play

1. Launch the game and select **Play** from the main menu
2. Choose a map from the selection screen
3. Battle your opponent until one tank is destroyed
4. The last tank standing wins!

### Controls

| Action | Player 1 (Orange) | Player 2 (Blue) |
|--------|-------------------|-----------------|
| Move Forward | W | Up Arrow |
| Move Backward | S | Down Arrow |
| Rotate Left | A | Left Arrow |
| Rotate Right | D | Right Arrow |
| Fire | Space | Enter |

---

## Power-Ups

Power-ups spawn randomly on the battlefield. Drive over them to collect:

| Power-Up | Effect | Duration |
|----------|--------|----------|
| Speed Boost | Increases movement speed by 50% | 5 seconds |
| Triple Shot | Fires 3 bullets in a spread pattern | 5 seconds |
| Shield | Blocks all incoming damage | 5 seconds |
| Health Boost | Restores 1 HP (instant) | - |

---

## Combat Mechanics

### Bullet Physics

- Bullets travel in a straight line until hitting a surface
- **Maximum bounces**: 3 times off walls
- After 3 bounces, the bullet is destroyed
- Bullets cannot damage the tank that fired them

### Health System

- Each tank starts with **3 HP**
- Taking a bullet hit reduces HP by 1
- When HP reaches 0, the tank explodes
- Shield power-up temporarily blocks all damage

### Destructible Walls

Some walls on the map can be destroyed by shooting them, opening new pathways and angles of attack.

---

## Map Selection

The game features 10 unique maps with different layouts:
- Various wall configurations for different strategies
- Open areas and tight corridors
- Strategic power-up spawn locations

---

## Requirements

- Unity 2022.3 LTS or newer
- Windows / macOS / Linux

### Running the Game

1. Open the project in Unity
2. Open `Scenes/MainMenuScene`
3. Press Play in the Unity Editor

Or build the project:
1. Go to **File > Build Settings**
2. Add all scenes in the `Scenes` folder
3. Select your target platform and build

---

## File Structure

```
Tank Battle/
├── Assets/
│   ├── Audio/           # Sound effects and music
│   ├── Fonts/           # Game fonts (Armalite, Open Sans)
│   ├── Maps/            # Map layout files (map1-10.txt)
│   ├── Prefabs/         # Tank, bullet, power-up prefabs
│   ├── Resources/       # Runtime-loaded assets
│   ├── Scenes/          # Game scenes
│   ├── Scripts/         # C# game scripts
│   │   ├── AudioManager.cs
│   │   ├── BulletPhysics.cs
│   │   ├── GameManager.cs
│   │   ├── LevelManager.cs
│   │   ├── MainMenu.cs
│   │   ├── MapSelectionManager.cs
│   │   ├── PowerUp.cs
│   │   ├── PowerUpSpawner.cs
│   │   ├── TankHealth.cs
│   │   ├── TankMovement.cs
│   │   ├── TankShooting.cs
│   │   ├── UIManager.cs
│   │   └── WallHealth.cs
│   ├── Settings/        # Render pipeline settings
│   └── Sprites/         # Tank, block, and UI sprites
├── Packages/
├── ProjectSettings/
└── README.md            # This file
```

---

## Tips for Winning

1. **Use bounces** - Ricochet shots around corners to hit enemies
2. **Collect power-ups** - They can turn the tide of battle
3. **Shield wisely** - Save shield for critical moments
4. **Control the map** - Position yourself near power-up spawns
5. **Destroy walls** - Create new angles to catch your opponent off guard

---

## Credits

### Audio

#### Sound Effects
- **Click Sound**: [Breviceps - Freesound](https://freesound.org/people/Breviceps/sounds/448086/)
- **Move Sound**: [KVV_Audio - Freesound](https://freesound.org/people/KVV_Audio/sounds/803256/)
- **Fire Sound**: [qubodup - Freesound](https://freesound.org/people/qubodup/sounds/168707/)
- **Bounce Sound**: [minerjr - Freesound](https://freesound.org/people/minerjr/sounds/89977/)
- **Explode Sound**: [rendensh - Freesound](https://freesound.org/people/rendensh/sounds/105412/)
- **Hit Sound**: [MrEchobot - Freesound](https://freesound.org/people/MrEchobot/sounds/745185/)

#### Music
- **Intro Music**: [irazoki - Freesound](https://freesound.org/people/irazoki/sounds/719030/)
- **Game Music**: [Seth_Makes_Sounds - Freesound](https://freesound.org/people/Seth_Makes_Sounds/sounds/699618/)
- **End Music**: [Victor_Natas - Freesound](https://freesound.org/people/Victor_Natas/sounds/741118/)

### Fonts
- **Armalite**: [placeholder]
- **Open Sans**: [Google Fonts](https://fonts.google.com/specimen/Open+Sans)

### Sprites
- **Tank Sprites**: [Kenney.nl - Top Down Tanks](https://kenney.nl/assets/top-down-tanks)
- **Block/Wall Sprites**: [Kenney.nl - Pixel Platformer Blocks](https://kenney.nl/assets/pixel-platformer-blocks)
- **Power-Up Icons**: [placeholder]
- **Heart Icon**: [Medium](https://medium.com/@250509/adding-a-health-power-up-in-unity-step-by-step-0fbf15351acd)
- **Shield Icon**: [Pngtree](https://pngtree.com/freepng/pixel-art-sci-fi-shield-orb-glowing-blue-transparent-sphere-retro-style_21805236.html)

### Particle
- **Heal Effect**: [Freeiconspng](https://www.freeiconspng.com/img/13072)
