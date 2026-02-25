using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance;

    [Header("End Screen UI")]
    [SerializeField] GameObject endScreenPanel;   // Assign a UI panel (disabled by default)
    [SerializeField] Text winnerText;             // Assign a Text to show who won

    void Awake()
    {
        Instance = this;
    }

    /// <summary>
    /// Called by TankHealth when a tank is destroyed.
    /// </summary>
    public void OnTankDestroyed(string destroyedTag)
    {
        // The winner is the OTHER player
        string winner = (destroyedTag == "Player1") ? "Player 2 Wins!" : "Player 1 Wins!";

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

    public void GoToMainMenu()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene("MainMenuScene");
    }
}
