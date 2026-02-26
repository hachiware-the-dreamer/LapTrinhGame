using UnityEngine;
using UnityEngine.SceneManagement;
using TMPro;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance;

    [Header("End Screen UI")]
    [SerializeField] GameObject endScreenPanel;   // Assign a UI panel (disabled by default)
    private TextMeshProUGUI winnerText;           // Auto-found from endScreenPanel children

    void Awake()
    {
        Instance = this;

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

    /// <summary>
    /// Called by TankHealth when a tank is destroyed.
    /// </summary>
    public void OnTankDestroyed(string destroyedTag)
    {
        // The winner is the OTHER player
        string winner = (destroyedTag == "Player1") ? "Player 2 Win!" : "Player 1 Win!";

        if (winnerText != null)
            winnerText.text = winner;

        if (endScreenPanel != null)
            endScreenPanel.SetActive(true);

        // Freeze the game so nothing keeps moving
        Time.timeScale = 0f;
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
