using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class PowerUpSpawner : MonoBehaviour
{
    [Header("Power-Up Prefabs")]
    [SerializeField] GameObject speedBoostPrefab;   // Wind-like power-up
    [SerializeField] GameObject tripleShotPrefab;   // Triple shot power-up
    [SerializeField] GameObject shieldPrefab;       // Shield power-up

    [Header("Spawn Settings")]
    [SerializeField] float spawnInterval = 5f;       // Seconds between spawns
    [SerializeField] float firstSpawnDelay = 2f;     // Delay before the first spawn
    [SerializeField] int maxPowerUpsOnMap = 5;       // Limit active power-ups
    [SerializeField] int initialSpawnCount = 3;      // How many to spawn at the start
    [SerializeField] float tileSize = 1f;
    [SerializeField] float powerUpScale = 0.5f;      // Scale to match tile/tank size

    private List<Vector2> emptyTiles = new List<Vector2>();
    private int activePowerUps = 0;

    void Start()
    {
        FindEmptyTiles();
        StartCoroutine(SpawnLoop());
    }

    /// <summary>
    /// Reads the same map the LevelManager used to find all empty '.' tiles.
    /// </summary>
    void FindEmptyTiles()
    {
        int mapNumber = PlayerPrefs.GetInt("SelectedMap", 1);
        TextAsset mapFile = Resources.Load<TextAsset>("Maps/map" + mapNumber);
        if (mapFile == null)
        {
            Debug.LogError("PowerUpSpawner: Map file not found!");
            return;
        }

        string[] rows = mapFile.text.Split(new[] { '\r', '\n' }, System.StringSplitOptions.RemoveEmptyEntries);
        for (int y = 0; y < rows.Length; y++)
        {
            string currentRow = rows[y];
            for (int x = 0; x < currentRow.Length; x++)
            {
                if (currentRow[x] == '.')
                {
                    // Same coordinate system as LevelManager
                    emptyTiles.Add(new Vector2(x * tileSize, -y * tileSize));
                }
            }
        }

        Debug.Log("PowerUpSpawner: Found " + emptyTiles.Count + " empty tiles for spawning.");
    }

    IEnumerator SpawnLoop()
    {
        yield return new WaitForSeconds(firstSpawnDelay);

        // Spawn multiple power-ups at the start to populate the map
        for (int i = 0; i < initialSpawnCount && activePowerUps < maxPowerUpsOnMap; i++)
        {
            SpawnRandomPowerUp();
        }

        while (true)
        {
            yield return new WaitForSeconds(spawnInterval);

            if (activePowerUps < maxPowerUpsOnMap && emptyTiles.Count > 0)
            {
                SpawnRandomPowerUp();
            }
        }
    }

    void SpawnRandomPowerUp()
    {
        if (emptyTiles.Count == 0)
        {
            Debug.LogWarning("PowerUpSpawner: No empty tiles available for spawning!");
            return;
        }

        // Pick a random empty tile
        int randomIndex = Random.Range(0, emptyTiles.Count);
        Vector2 spawnPos = emptyTiles[randomIndex];
        
        // Remove this tile from available positions
        emptyTiles.RemoveAt(randomIndex);

        // Pick a random power-up type (equal chance for all 3)
        GameObject prefab;
        int roll = Random.Range(0, 3);
        if (roll == 0) prefab = speedBoostPrefab;
        else if (roll == 1) prefab = tripleShotPrefab;
        else prefab = shieldPrefab;

        if (prefab == null)
        {
            Debug.LogWarning("PowerUpSpawner: A power-up prefab is not assigned!");
            // Return the tile back to the list since we couldn't spawn
            emptyTiles.Add(spawnPos);
            return;
        }

        GameObject powerUp = Instantiate(prefab, spawnPos, Quaternion.identity);
        
        // Scale down to match tile/tank size
        powerUp.transform.localScale = new Vector3(powerUpScale, powerUpScale, 1f);
        
        activePowerUps++;

        // Track when it gets picked up or destroyed
        PowerUpTracker tracker = powerUp.AddComponent<PowerUpTracker>();
        tracker.spawner = this;
        tracker.occupiedPosition = spawnPos;
    }

    /// <summary>
    /// Called by PowerUpTracker when a power-up is destroyed (picked up or expired).
    /// </summary>
    public void OnPowerUpDestroyed(Vector2 position)
    {
        activePowerUps = Mathf.Max(0, activePowerUps - 1);
        
        // Return the tile to the available spawn positions
        emptyTiles.Add(position);
    }
}

/// <summary>
/// Helper component that notifies the spawner when a power-up is removed from the map.
/// </summary>
public class PowerUpTracker : MonoBehaviour
{
    [HideInInspector] public PowerUpSpawner spawner;
    [HideInInspector] public Vector2 occupiedPosition;

    void OnDestroy()
    {
        // Only run if the scene is still active and the spawner exists
        if (gameObject.scene.isLoaded && spawner != null)
        {
            spawner.OnPowerUpDestroyed(occupiedPosition);
        }
    }
}
