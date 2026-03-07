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

    [Header("Power-Up Bar Containers")]
    [Tooltip("Assign an empty RectTransform near P1's hearts. Bars will stack here vertically.")]
    [SerializeField] RectTransform p1PowerUpContainer;
    [Tooltip("Assign an empty RectTransform near P2's hearts. Bars will stack here vertically.")]
    [SerializeField] RectTransform p2PowerUpContainer;

    // Track active bars so we can refresh if the same powerup is picked up again
    private Dictionary<string, PowerUpBarUI> p1ActiveBars = new Dictionary<string, PowerUpBarUI>();
    private Dictionary<string, PowerUpBarUI> p2ActiveBars = new Dictionary<string, PowerUpBarUI>();

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

    // Cache reference to HUD Canvas
    private Canvas hudCanvas;

    void Start()
    {
        // Find the HUD Canvas (UIManager is attached to it)
        hudCanvas = GetComponent<Canvas>();
        if (hudCanvas == null) hudCanvas = GetComponentInParent<Canvas>();

        // Auto-create containers if not assigned
        if (p1PowerUpContainer == null)
            p1PowerUpContainer = CreateP1BarContainer();
        if (p2PowerUpContainer == null)
            p2PowerUpContainer = CreateP2BarContainer();

        EnsureVerticalLayout(p1PowerUpContainer, TextAnchor.UpperLeft);
        EnsureVerticalLayout(p2PowerUpContainer, TextAnchor.UpperRight);
    }

    RectTransform CreateP1BarContainer()
    {
        if (hudCanvas == null) return null;

        GameObject go = new GameObject("P1_PowerUpBars");
        go.transform.SetParent(hudCanvas.transform, false);

        RectTransform rect = go.AddComponent<RectTransform>();
        // P1_Name is at anchor(0,1) pos(100,-25) size(200,50) pivot(0.5,0.5)
        //   left edge = 100 - 200*0.5 = 0, right edge = 200
        // P1_Hearts is at anchor(0,1) pos(50,-75) size(100,100) scale 0.5
        //   visual bottom = -75 - 100*0.5*0.5 = -100
        // Place bar just below hearts, left-aligned to match name left edge
        rect.anchorMin = new Vector2(0, 1);
        rect.anchorMax = new Vector2(0, 1);
        rect.pivot = new Vector2(0, 1);
        rect.anchoredPosition = new Vector2(0, -105);
        rect.sizeDelta = new Vector2(200, 0);

        return rect;
    }

    RectTransform CreateP2BarContainer()
    {
        if (hudCanvas == null) return null;

        GameObject go = new GameObject("P2_PowerUpBars");
        go.transform.SetParent(hudCanvas.transform, false);

        RectTransform rect = go.AddComponent<RectTransform>();
        // P2_Name is at anchor(1,1) pos(-100,-25) size(200,50) pivot(0.5,0.5)
        //   right edge = -100 + 200*0.5 = 0
        rect.anchorMin = new Vector2(1, 1);
        rect.anchorMax = new Vector2(1, 1);
        rect.pivot = new Vector2(1, 1);
        rect.anchoredPosition = new Vector2(0, -105);
        rect.sizeDelta = new Vector2(200, 0);

        return rect;
    }

    void EnsureVerticalLayout(RectTransform container, TextAnchor alignment)
    {
        if (container == null) return;
        VerticalLayoutGroup vlg = container.GetComponent<VerticalLayoutGroup>();
        if (vlg == null)
        {
            vlg = container.gameObject.AddComponent<VerticalLayoutGroup>();
        }
        vlg.spacing = 6;
        vlg.childAlignment = alignment;
        vlg.childForceExpandWidth = false;
        vlg.childForceExpandHeight = false;
        vlg.childControlWidth = false;
        vlg.childControlHeight = false;

        ContentSizeFitter csf = container.GetComponent<ContentSizeFitter>();
        if (csf == null)
        {
            csf = container.gameObject.AddComponent<ContentSizeFitter>();
        }
        csf.verticalFit = ContentSizeFitter.FitMode.PreferredSize;
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
    /// Spawns (or refreshes) a power-up bar on the HUD for the given player.
    /// The bar depletes over time and disappears when empty.
    /// </summary>
    public void ShowPowerUp(string playerTag, string powerUpName, float duration)
    {
        Dictionary<string, PowerUpBarUI> bars;
        RectTransform container;

        if (playerTag == "Player1")
        {
            bars = p1ActiveBars;
            container = p1PowerUpContainer;
        }
        else if (playerTag == "Player2")
        {
            bars = p2ActiveBars;
            container = p2PowerUpContainer;
        }
        else return;

        if (container == null) return;

        Color barColor = GetPowerUpColor(powerUpName);

        // If the same powerup is already active, reset its bar
        if (bars.TryGetValue(powerUpName, out PowerUpBarUI existing) && existing != null)
        {
            existing.ResetDuration(duration);
        }
        else
        {
            PowerUpBarUI bar = PowerUpBarUI.Create(container, powerUpName, duration, barColor);
            bars[powerUpName] = bar;
        }
    }

    void Update()
    {
        // Clean up destroyed bar references
        CleanUpBars(p1ActiveBars);
        CleanUpBars(p2ActiveBars);
    }

    void CleanUpBars(Dictionary<string, PowerUpBarUI> bars)
    {
        List<string> toRemove = new List<string>();
        foreach (var kvp in bars)
        {
            if (kvp.Value == null) // destroyed by PowerUpBarUI itself
                toRemove.Add(kvp.Key);
        }
        foreach (string key in toRemove)
        {
            bars.Remove(key);
        }
    }

    Color GetPowerUpColor(string powerUpName)
    {
        switch (powerUpName)
        {
            case "SPEED UP":     return new Color(1f, 0.75f, 0f);      // Orange
            case "TRIPLE SHOT":  return new Color(0.2f, 0.6f, 1f);     // Blue
            case "SHIELD":       return new Color(0.2f, 1f, 0.4f);     // Green
            default:             return new Color(0.9f, 0.9f, 0.9f);   // White
        }
    }
}