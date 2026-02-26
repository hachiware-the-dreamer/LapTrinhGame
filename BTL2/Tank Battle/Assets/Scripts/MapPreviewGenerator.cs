using UnityEngine;
using UnityEngine.UI;

#if UNITY_EDITOR
using UnityEditor;
using System.IO;
#endif

public class MapPreviewGenerator : MonoBehaviour
{
#if UNITY_EDITOR
    [MenuItem("Tools/Generate Map Previews")]
    public static void GenerateAllPreviews()
    {
        string outputFolder = "Assets/Resources/MapPreviews";
        if (!Directory.Exists(outputFolder))
            Directory.CreateDirectory(outputFolder);

        for (int i = 1; i <= 10; i++)
        {
            TextAsset mapFile = Resources.Load<TextAsset>("Maps/map" + i);
            if (mapFile == null)
            {
                Debug.LogError("Map file not found: Maps/map" + i);
                continue;
            }

            Texture2D preview = GenerateMapPreview(mapFile, 256, 256);
            byte[] pngData = preview.EncodeToPNG();
            string filePath = outputFolder + "/map" + i + ".png";
            File.WriteAllBytes(filePath, pngData);
            Debug.Log("Generated preview: " + filePath);
        }

        AssetDatabase.Refresh();
        Debug.Log("All map previews generated!");
    }

    static Texture2D GenerateMapPreview(TextAsset mapFile, int width, int height)
    {
        string[] rows = mapFile.text.Split(new[] { '\r', '\n' }, System.StringSplitOptions.RemoveEmptyEntries);
        int mapWidth = rows[0].Length;
        int mapHeight = rows.Length;

        Texture2D texture = new Texture2D(width, height);
        Color bgColor = new Color(0.7f, 0.7f, 0.8f); // Light gray background
        Color wallColor = new Color(0.8f, 0.6f, 0.4f); // Brown wall
        Color player1Color = new Color(0.2f, 0.6f, 1f); // Blue
        Color player2Color = new Color(1f, 0.3f, 0.3f); // Red

        // Fill background
        for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
                texture.SetPixel(x, y, bgColor);

        // Draw map
        float cellWidth = (float)width / mapWidth;
        float cellHeight = (float)height / mapHeight;

        for (int row = 0; row < mapHeight; row++)
        {
            for (int col = 0; col < rows[row].Length; col++)
            {
                char tile = rows[row][col];
                Color color = bgColor;

                if (tile == 'W') color = wallColor;
                else if (tile == 'P' || tile == '1') color = player1Color;
                else if (tile == '2') color = player2Color;

                if (tile != '.')
                {
                    int startX = Mathf.RoundToInt(col * cellWidth);
                    int startY = Mathf.RoundToInt((mapHeight - row - 1) * cellHeight);
                    int endX = Mathf.RoundToInt((col + 1) * cellWidth);
                    int endY = Mathf.RoundToInt((mapHeight - row) * cellHeight);

                    for (int y = startY; y < endY; y++)
                        for (int x = startX; x < endX; x++)
                            if (x >= 0 && x < width && y >= 0 && y < height)
                                texture.SetPixel(x, y, color);
                }
            }
        }

        texture.Apply();
        return texture;
    }
#endif
}
