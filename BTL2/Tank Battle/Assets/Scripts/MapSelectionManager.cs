using UnityEngine;
using UnityEngine.SceneManagement;
using TMPro;
using UnityEngine.UI;
using System;

public class MapSelectionManager : MonoBehaviour
{
    public static int TotalMaps = 10;

    [Header("UI References")]
    [SerializeField] Button[] mapButtons;   // 10 buttons, assigned in Inspector
    [SerializeField] RectTransform mapGridRoot;
    [SerializeField] Button backButton;
    [SerializeField] string gameSceneName = "SampleScene";

    void Start()
    {
        ConfigureGrid();

        int buttonCount = Mathf.Min(TotalMaps, mapButtons.Length);
        for (int i = 0; i < buttonCount; i++)
        {
            int mapIndex = i + 1;
            ConfigureMapButton(mapButtons[i], mapIndex);
        }

        if (backButton != null)
        {
            backButton.onClick.RemoveAllListeners();
            backButton.onClick.AddListener(BackToTitle);
        }
    }

    void ConfigureGrid()
    {
        if (mapGridRoot == null && mapButtons != null && mapButtons.Length > 0 && mapButtons[0] != null)
            mapGridRoot = mapButtons[0].transform.parent as RectTransform;

        if (mapGridRoot == null)
            return;

        GridLayoutGroup grid = mapGridRoot.GetComponent<GridLayoutGroup>();
        if (grid == null)
            grid = mapGridRoot.gameObject.AddComponent<GridLayoutGroup>();

        grid.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
        grid.constraintCount = 5;
        grid.cellSize = new Vector2(170f, 100f);
        grid.spacing = new Vector2(16f, 16f);
        grid.childAlignment = TextAnchor.UpperCenter;
        grid.padding = new RectOffset(24, 24, 24, 24);
    }

    void ConfigureMapButton(Button button, int mapIndex)
    {
        if (button == null)
            return;

        TextMeshProUGUI tmpLabel = button.GetComponentInChildren<TextMeshProUGUI>(true);
        if (tmpLabel != null)
        {
            tmpLabel.text = "Map " + mapIndex;
            tmpLabel.fontSize = 24;
            tmpLabel.textWrappingMode = TextWrappingModes.NoWrap;
            tmpLabel.alignment = TextAlignmentOptions.Bottom;
        }

        Text legacyLabel = button.GetComponentInChildren<Text>(true);
        if (legacyLabel != null)
            legacyLabel.text = "Map " + mapIndex;

        Image buttonImage = button.GetComponent<Image>();
        if (buttonImage != null)
        {
            Sprite previewSprite = LoadPreviewSprite(mapIndex);
            if (previewSprite != null)
            {
                buttonImage.sprite = previewSprite;
                buttonImage.type = Image.Type.Simple;
                buttonImage.preserveAspect = true;
                buttonImage.color = Color.white;
            }
            else
            {
                buttonImage.sprite = null;
                buttonImage.color = new Color(0.9f, 0.9f, 0.9f, 1f);
            }
        }

        button.onClick.RemoveAllListeners();
        button.onClick.AddListener(() => SelectMap(mapIndex));
    }

    Sprite LoadPreviewSprite(int mapIndex)
    {
        Sprite previewSprite = Resources.Load<Sprite>("MapPreviews/map" + mapIndex);
        if (previewSprite != null)
            return previewSprite;

        TextAsset mapFile = Resources.Load<TextAsset>("Maps/map" + mapIndex);
        if (mapFile == null)
            return null;

        Texture2D generatedTexture = GenerateMapTexture(mapFile, 256, 256);
        if (generatedTexture == null)
            return null;

        return Sprite.Create(generatedTexture, new Rect(0, 0, generatedTexture.width, generatedTexture.height), new Vector2(0.5f, 0.5f), 100f);
    }

    Texture2D GenerateMapTexture(TextAsset mapFile, int width, int height)
    {
        string[] rows = mapFile.text.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
        if (rows.Length == 0)
            return null;

        int mapWidth = rows[0].Length;
        int mapHeight = rows.Length;

        Texture2D texture = new Texture2D(width, height);
        Color bgColor = new Color(0.70f, 0.73f, 0.80f, 1f);
        Color wallColor = new Color(0.83f, 0.62f, 0.40f, 1f);
        Color player1Color = new Color(0.28f, 0.62f, 0.98f, 1f);
        Color player2Color = new Color(0.96f, 0.38f, 0.36f, 1f);

        for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
                texture.SetPixel(x, y, bgColor);

        float cellWidth = (float)width / mapWidth;
        float cellHeight = (float)height / mapHeight;

        for (int row = 0; row < mapHeight; row++)
        {
            string line = rows[row];
            for (int col = 0; col < line.Length; col++)
            {
                char tile = line[col];
                Color drawColor;
                bool shouldDraw = true;

                switch (tile)
                {
                    case 'W':
                        drawColor = wallColor;
                        break;
                    case '1':
                    case 'P':
                        drawColor = player1Color;
                        break;
                    case '2':
                        drawColor = player2Color;
                        break;
                    default:
                        drawColor = bgColor;
                        shouldDraw = false;
                        break;
                }

                if (!shouldDraw)
                    continue;

                int startX = Mathf.RoundToInt(col * cellWidth);
                int endX = Mathf.RoundToInt((col + 1) * cellWidth);
                int startY = Mathf.RoundToInt((mapHeight - row - 1) * cellHeight);
                int endY = Mathf.RoundToInt((mapHeight - row) * cellHeight);

                for (int y = startY; y < endY; y++)
                {
                    for (int x = startX; x < endX; x++)
                    {
                        if (x >= 0 && x < width && y >= 0 && y < height)
                            texture.SetPixel(x, y, drawColor);
                    }
                }
            }
        }

        texture.Apply();
        return texture;
    }

    public void SelectMap(int mapNumber)
    {
        PlayerPrefs.SetInt("SelectedMap", mapNumber);
        PlayerPrefs.Save();
        SceneManager.LoadScene(gameSceneName);
    }

    public void BackToTitle()
    {
        SceneManager.LoadScene("MainMenuScene");
    }
}
