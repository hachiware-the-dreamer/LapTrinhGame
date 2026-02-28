using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;

public class UIManager : MonoBehaviour
{
    // Singleton pattern
    public static UIManager Instance;

    [Header("Player 1 UI")]
    public GameObject[] p1Hearts;

    [Header("Player 2 UI")]
    public GameObject[] p2Hearts;

    [Header("Power-Up HUD")]
    [SerializeField] Text p1PowerUpText;    // Assign a Text element near P1's hearts
    [SerializeField] Text p2PowerUpText;    // Assign a Text element near P2's hearts

    // Track multiple active power-ups per player
    private Dictionary<string, float> p1ActivePowerUps = new Dictionary<string, float>();
    private Dictionary<string, float> p2ActivePowerUps = new Dictionary<string, float>();

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
                hearts[i].SetActive(true);
            }
            else
            {
                hearts[i].SetActive(false);
            }
        }
    }

    /// <summary>
    /// Shows a power-up notification on the HUD for the given player.
    /// Supports multiple simultaneous power-ups.
    /// </summary>
    public void ShowPowerUp(string playerTag, string powerUpName, float duration)
    {
        if (playerTag == "Player1")
        {
            p1ActivePowerUps[powerUpName] = duration;
        }
        else if (playerTag == "Player2")
        {
            p2ActivePowerUps[powerUpName] = duration;
        }
    }

    void Update()
    {
        // Tick down all active power-ups and update display
        UpdatePowerUpDisplay(p1ActivePowerUps, p1PowerUpText);
        UpdatePowerUpDisplay(p2ActivePowerUps, p2PowerUpText);
    }

    void UpdatePowerUpDisplay(Dictionary<string, float> activePowerUps, Text text)
    {
        if (text == null) return;

        // Tick down timers
        List<string> expired = new List<string>();
        List<string> keys = new List<string>(activePowerUps.Keys);
        foreach (string key in keys)
        {
            activePowerUps[key] -= Time.deltaTime;
            if (activePowerUps[key] <= 0f)
            {
                expired.Add(key);
            }
        }

        // Remove expired
        foreach (string key in expired)
        {
            activePowerUps.Remove(key);
        }

        // Build display text
        if (activePowerUps.Count == 0)
        {
            text.text = "";
            text.gameObject.SetActive(false);
        }
        else
        {
            text.gameObject.SetActive(true);
            string display = "";
            foreach (var kvp in activePowerUps)
            {
                if (display.Length > 0) display += "\n";
                display += kvp.Key + " (" + Mathf.CeilToInt(kvp.Value) + "s)";
            }
            text.text = display;
        }
    }
}