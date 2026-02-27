using UnityEngine;
using UnityEngine.SceneManagement;
using TMPro;
using UnityEngine.UI;
using System;

public class MapSelectionManager : MonoBehaviour
{
    public static int TotalMaps = 10;

    [Header("UI References")]
    [SerializeField] TextMeshProUGUI headerText;
    [SerializeField] Button[] mapButtons;   // 10 buttons, assigned in Inspector
    [SerializeField] RectTransform mapGridRoot;
    [SerializeField] Button backButton;
    [SerializeField] string gameSceneName = "GameScene";

    void Start()
    {
        ConfigureHeader();
        ConfigureGrid();

        int buttonCount = Mathf.Min(TotalMaps, mapButtons.Length);
        for (int i = 0; i < buttonCount; i++)
        {
            int mapIndex = i + 1;
            ConfigureMapButton(mapButtons[i], mapIndex);
        }

        ConfigureBackButton();
    }

    void ConfigureHeader()
    {
        if (headerText != null)
        {
            headerText.text = "<color=#3388FF>MAP</color> <color=#FF3333>SELECTION</color>";
            headerText.fontSize = 80;
            headerText.fontStyle = FontStyles.Bold;
            headerText.alignment = TextAlignmentOptions.Center;
        }
    }

    void ConfigureBackButton()
    {
        if (backButton != null)
        {
            backButton.onClick.RemoveAllListeners();
            backButton.onClick.AddListener(BackToTitle);

            // Ignore layout group
            LayoutElement layoutElement = backButton.GetComponent<LayoutElement>();
            if (layoutElement == null)
                layoutElement = backButton.gameObject.AddComponent<LayoutElement>();
            layoutElement.ignoreLayout = true;

            // Position at bottom left corner
            RectTransform rectTransform = backButton.GetComponent<RectTransform>();
            if (rectTransform != null)
            {
                rectTransform.anchorMin = new Vector2(0, 0);
                rectTransform.anchorMax = new Vector2(0, 0);
                rectTransform.pivot = new Vector2(0, 0);
                rectTransform.anchoredPosition = new Vector2(30, 30);
                rectTransform.sizeDelta = new Vector2(200, 80);
            }

            TextMeshProUGUI buttonText = backButton.GetComponentInChildren<TextMeshProUGUI>();
            if (buttonText != null)
            {
                buttonText.fontSize = 32;
                buttonText.fontStyle = FontStyles.Bold;
            }

            Text legacyText = backButton.GetComponentInChildren<Text>();
            if (legacyText != null)
            {
                legacyText.fontSize = 32;
                legacyText.fontStyle = UnityEngine.FontStyle.Bold;
            }
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
        grid.cellSize = new Vector2(300f, 240f);
        grid.spacing = new Vector2(20f, 40f);
        grid.childAlignment = TextAnchor.MiddleCenter;
        grid.padding = new RectOffset(40, 40, 40, 40);
    }

    void ConfigureMapButton(Button button, int mapIndex)
    {
        if (button == null)
            return;

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

        TextMeshProUGUI tmpLabel = button.GetComponentInChildren<TextMeshProUGUI>(true);
        if (tmpLabel != null)
        {
            RectTransform labelRect = tmpLabel.GetComponent<RectTransform>();
            if (labelRect != null)
            {
                // Position text below the image
                labelRect.anchorMin = new Vector2(0, 0);
                labelRect.anchorMax = new Vector2(1, 0);
                labelRect.pivot = new Vector2(0.5f, 1);
                labelRect.anchoredPosition = new Vector2(0, -5);
                labelRect.sizeDelta = new Vector2(0, 30);
            }
            
            tmpLabel.text = "Map " + mapIndex;
            tmpLabel.fontSize = 28;
            tmpLabel.fontStyle = FontStyles.Bold;
            tmpLabel.textWrappingMode = TextWrappingModes.NoWrap;
            tmpLabel.alignment = TextAlignmentOptions.Center;
            tmpLabel.color = Color.black;
        }

        Text legacyLabel = button.GetComponentInChildren<Text>(true);
        if (legacyLabel != null)
        {
            legacyLabel.text = "Map " + mapIndex;
            legacyLabel.fontStyle = UnityEngine.FontStyle.Bold;
            legacyLabel.alignment = TextAnchor.UpperCenter;
            legacyLabel.color = Color.black;
        }

        button.onClick.RemoveAllListeners();
        button.onClick.AddListener(() => SelectMap(mapIndex));

        // Hover scale effect
        if (button.GetComponent<ButtonHoverScale>() == null)
            button.gameObject.AddComponent<ButtonHoverScale>();
    }

    Sprite LoadPreviewSprite(int mapIndex)
    {
        // Always generate from map file to ensure colors are up to date
        TextAsset mapFile = Resources.Load<TextAsset>("Maps/map" + mapIndex);
        if (mapFile == null)
        {
            // Fallback to pre-made preview if map file doesn't exist
            Sprite previewSprite = Resources.Load<Sprite>("MapPreviews/map" + mapIndex);
            return previewSprite;
        }

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
                if (tile == 'W')
                {
                    DrawRect(texture, col * cellWidth, (mapHeight - row - 1) * cellHeight, cellWidth, cellHeight, wallColor, width, height);
                }
                else if (tile == '1') // Found Player 1
                {
                    DrawRect(texture, (col - 1) * cellWidth, (mapHeight - row - 1) * cellHeight, cellWidth * 2f, cellHeight, player1Color, width, height);
                }
                else if (tile == '2') // Found Player 2
                {
                    DrawRect(texture, (col - 1) * cellWidth, (mapHeight - row - 1) * cellHeight, cellWidth * 2f, cellHeight, player2Color, width, height);
                }
            }
        }

        texture.Apply();
        return texture;
    }

    // --- HELPER METHOD ---
    void DrawRect(Texture2D tex, float startX, float startY, float w, float h, Color color, int maxWidth, int maxHeight)
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

    public void SelectMap(int mapNumber)
    {
        // Play click sound
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayClick();
        }
        
        PlayerPrefs.SetInt("SelectedMap", mapNumber);
        PlayerPrefs.Save();
        SceneManager.LoadScene(gameSceneName);
    }

    public void BackToTitle()
    {
        // Play click sound
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayClick();
        }
        
        SceneManager.LoadScene("MainMenuScene");
    }
}
