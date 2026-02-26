using UnityEngine;
using UnityEditor;
using System.IO;

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
            if (mapFile == null) continue;

            Texture2D preview = GenerateMapPreview(mapFile, 256, 256);
            byte[] pngData = preview.EncodeToPNG();
            string filePath = outputFolder + "/map" + i + ".png";
            File.WriteAllBytes(filePath, pngData);
            
            // Force Unity to recognize the new file immediately
            AssetDatabase.ImportAsset(filePath, ImportAssetOptions.ForceUpdate);
            
            // Automatically set it to 'Sprite' so it looks correct on your UI Canvas!
            TextureImporter importer = AssetImporter.GetAtPath(filePath) as TextureImporter;
            if (importer != null)
            {
                importer.textureType = TextureImporterType.Sprite;
                importer.spritePixelsPerUnit = 100f;
                importer.filterMode = FilterMode.Point; // Keeps the edges crisp!
                importer.SaveAndReimport();
            }
        }

        AssetDatabase.Refresh();
        Debug.Log("All map previews generated successfully!");
    }

    static Texture2D GenerateMapPreview(TextAsset mapFile, int width, int height)
    {
        string[] rows = mapFile.text.Split(new[] { '\r', '\n' }, System.StringSplitOptions.RemoveEmptyEntries);
        int mapWidth = rows[0].Length;
        int mapHeight = rows.Length;

        Texture2D texture = new Texture2D(width, height);
        Color bgColor = new Color(0.7f, 0.7f, 0.8f); 
        Color wallColor = new Color(0.8f, 0.6f, 0.4f); 
        Color player1Color = new Color(0.2f, 0.6f, 1f); 
        Color player2Color = new Color(1f, 0.3f, 0.3f); 

        // Fill background
        for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
                texture.SetPixel(x, y, bgColor);

        float cellWidth = (float)width / mapWidth;
        float cellHeight = (float)height / mapHeight;

        for (int row = 0; row < mapHeight; row++)
        {
            for (int col = 0; col < rows[row].Length; col++)
            {
                char tile = rows[row][col];
                
                if (tile == 'W')
                {
                    DrawRect(texture, col * cellWidth, (mapHeight - row - 1) * cellHeight, cellWidth, cellHeight, wallColor, width, height);
                }
                else if (tile == '1') // Found Player 1
                {
                    // Draw a BLUE box spanning BOTH the 'P' (col - 1) and '1' (col)
                    DrawRect(texture, (col - 1) * cellWidth, (mapHeight - row - 1) * cellHeight, cellWidth * 2f, cellHeight, player1Color, width, height);
                }
                else if (tile == '2') // Found Player 2
                {
                    // Draw a RED box spanning BOTH the 'P' (col - 1) and '2' (col)
                    DrawRect(texture, (col - 1) * cellWidth, (mapHeight - row - 1) * cellHeight, cellWidth * 2f, cellHeight, player2Color, width, height);
                }
                // Notice there is no "else if (tile == 'P')". We just ignore it!
            }
        }

        texture.Apply();
        return texture;
    }
    
    // A helper function to make drawing the blocks much cleaner
    static void DrawRect(Texture2D tex, float startX, float startY, float w, float h, Color color, int maxWidth, int maxHeight)
    {
        int xMin = Mathf.RoundToInt(startX);
        int yMin = Mathf.RoundToInt(startY);
        int xMax = Mathf.RoundToInt(startX + w);
        int yMax = Mathf.RoundToInt(startY + h);

        for (int y = yMin; y < yMax; y++)
        {
            for (int x = xMin; x < xMax; x++)
            {
                if (x >= 0 && x < maxWidth && y >= 0 && y < maxHeight)
                {
                    tex.SetPixel(x, y, color);
                }
            }
        }
    }
#endif
}