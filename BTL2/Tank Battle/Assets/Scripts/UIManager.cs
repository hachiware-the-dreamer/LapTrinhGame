using UnityEngine;
using UnityEngine.UI; // Required for interacting with UI elements

public class UIManager : MonoBehaviour
{
    // Singleton pattern
    public static UIManager Instance;

    [Header("Player 1 UI")]
    public GameObject[] p1Hearts;

    [Header("Player 2 UI")]
    public GameObject[] p2Hearts;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
        }
        else
        {
            Destroy(gameObject);
        }
    }

    public void UpdateHealth(string playerTag, int currentHealth)
    {
        if (playerTag == "Player1")
        {
            UpdateHeartDisplay(p1Hearts, currentHealth);
        }
        else if (playerTag == "Player2")
        {
            UpdateHeartDisplay(p2Hearts, currentHealth);
        }
    }

    private void UpdateHeartDisplay(GameObject[] hearts, int currentHealth)
    {
        for (int i = 0; i < hearts.Length; i++)
        {
            if (i < currentHealth)
            {
                hearts[i].SetActive(true);  // Turn the heart on
            }
            else
            {
                hearts[i].SetActive(false); // Turn the heart off (hide it)
            }
        }
    }
}