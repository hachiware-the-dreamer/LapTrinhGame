using UnityEngine;

public class LevelManager : MonoBehaviour
{
    [Header("Map Settings")]
    [SerializeField] GameObject wallPrefab;
    [SerializeField] float tileSize = 1f;

    [Header("Player Prefabs")]
    [SerializeField] GameObject player1Prefab;
    [SerializeField] GameObject player2Prefab;

    void Start()
    {
        int mapNumber = PlayerPrefs.GetInt("SelectedMap", 1);
        TextAsset mapFile = Resources.Load<TextAsset>("Maps/map" + mapNumber);
        if (mapFile == null)
        {
            Debug.LogError("Map file not found: Maps/map" + mapNumber + ". Make sure map files are inside Assets/Resources/Maps/");
            return;
        }
        GenerateMap(mapFile);
    }

    void GenerateMap(TextAsset mapFile)
    {
        // Splits the .txt file into rows -> removes '\r', '\n' and blank lines
        string[] rows = mapFile.text.Split(new[] { '\r', '\n' }, System.StringSplitOptions.RemoveEmptyEntries);
        float mapHeight = rows.Length;
        float mapWidth = rows.Length > 0 ? rows[0].Length : 0;

        for (int y = 0; y < rows.Length; y++)
        {
            string currentRow = rows[y];
            for (int x = 0; x < currentRow.Length; x++)
            {
                char tile = currentRow[x];
                Vector2 spawnPos = new Vector2(x * tileSize, -y * tileSize); // Use -y -> map draws top-to-bottom

                if (tile == 'W') // Wall
                {
                    // Have transform -> all walls are child of level manager
                    GameObject wall = Instantiate(wallPrefab, spawnPos, Quaternion.identity, transform);

                    // Check if this is a border wall (first/last row or column)
                    bool isBorder = (x == 0 || x == currentRow.Length - 1 || y == 0 || y == mapHeight - 1);

                    if (!isBorder)
                    {
                        // Add destructible component to inner walls
                        wall.AddComponent<WallHealth>();
                    }
                }
                else if (tile == 'P') // Player
                {
                    if (x + 1 < currentRow.Length)
                    {
                        char nextChar = currentRow[x + 1];
                        
                        // Pos = middle point of P and 1 (or P, 2)
                        Vector2 playerSpawnPos = new Vector2((x + 0.5f) * tileSize, -y * tileSize);

                        // No transform
                        if (nextChar == '1')
                        {
                            Instantiate(player1Prefab, playerSpawnPos, Quaternion.identity);
                            x++; // Skip '1' in next iteration
                        }
                        else if (nextChar == '2')
                        {
                            Instantiate(player2Prefab, playerSpawnPos, Quaternion.identity);
                            x++; // Skip '2' in next iteration
                        }
                    }
                }
            }
        }

        // Camera auto-focus
        // float mapWidth = rows[0].Length * tileSize;
        // float mapHeight = rows.Length * tileSize;

        // Account for center of tile
        float centerX = (mapWidth / 2f) - (tileSize / 2f);
        float centerY = -(mapHeight / 2f) + (tileSize / 2f);

        float hudPadding = 4f;
        float adjustedCenterY = centerY + (hudPadding / 2f);

        // Keep Z at -10 so it stays behind the 2D sprites
        Camera.main.transform.position = new Vector3(centerX, adjustedCenterY, -10f);
        
        // Automatically adjust the camera size to fit the map width
        float screenAspect = (float)Screen.width / (float)Screen.height;
        float baseSize = (mapWidth / 2f) / screenAspect;
        Camera.main.orthographicSize = baseSize + 0.5f + (hudPadding / 2f); // +0.5f adds a small padding
    }
}
