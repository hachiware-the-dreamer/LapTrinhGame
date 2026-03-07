using UnityEngine;
using UnityEngine.SceneManagement;
using TMPro;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance;

    [Header("End Screen UI")]
    [SerializeField] GameObject endScreenPanel;
    private TextMeshProUGUI winnerText;

    public bool IsGameOver { get; private set; }

    void Awake()
    {
        Instance = this;

        // Play game background music
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayGameMusic();
        }

        // Auto-find the TMP text inside the end screen panel
        if (endScreenPanel != null)
        {
            winnerText = endScreenPanel.GetComponentInChildren<TextMeshProUGUI>(true);
            if (winnerText != null)
            {
                winnerText.textWrappingMode = TextWrappingModes.NoWrap;
                winnerText.enableAutoSizing = true;
                winnerText.fontSizeMin = 10;
                winnerText.fontSizeMax = 72;
                winnerText.alignment = TextAlignmentOptions.Center;
                winnerText.overflowMode = TextOverflowModes.Overflow;
            }
        }
    }

    // --- ADD THIS TO HIDE THE MENU WHEN THE GAME STARTS ---
    void Start()
    {
        if (endScreenPanel != null)
        {
            endScreenPanel.SetActive(false);
        }
        
        // Ensure the game runs at normal speed 
        Time.timeScale = 1f; 
    }

    /// Called by TankHealth when a tank is destroyed.
    public void OnTankDestroyed(string destroyedTag)
    {
        // The winner is the OTHER player
        string winner = (destroyedTag == "Player1") ? "Xanh SM Wins!" : "Shopee Wins!";

        // Play end music
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayEndMusic();
        }

        if (winnerText != null)
            winnerText.text = winner;

        if (endScreenPanel != null)
        {
            // Ensure the parent canvas is active (it may start disabled in the scene)
            Transform parent = endScreenPanel.transform.parent;
            if (parent != null) parent.gameObject.SetActive(true);
            endScreenPanel.SetActive(true);
        }

        // Freeze the game so nothing keeps moving
        Time.timeScale = 0f;
        IsGameOver = true;
    }

    public void RestartGame()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }

    public void ChooseMap()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene("MapSelectionScene");
    }

    public void GoToMainMenu()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene("MainMenuScene");
    }
}