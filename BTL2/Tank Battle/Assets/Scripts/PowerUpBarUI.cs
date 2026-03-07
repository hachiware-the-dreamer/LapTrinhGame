using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// A single power-up bar that depletes over time and destroys itself when empty.
/// Premium version: Elastic pop-in, 3D highlight, text outlines, and pulsing / flashing effects.
/// </summary>
public class PowerUpBarUI : MonoBehaviour
{
    private RectTransform fillRect;
    private Image fillImage;
    private RectTransform rootRectTransform;

    private float totalDuration;
    private float remainingTime;
    
    private Color baseColor;
    private float popInTimer;

    public static PowerUpBarUI Create(Transform parent, string powerUpName, float duration, Color barColor)
    {
        // ── Root (Managed by Vertical Layout Group) ──
        GameObject root = new GameObject("PowerUpBar_" + powerUpName);
        root.transform.SetParent(parent, false);

        RectTransform rootRT = root.AddComponent<RectTransform>();
        rootRT.sizeDelta = new Vector2(200, 26);
        rootRT.localScale = Vector3.zero; // Start at scale 0 for pop-in animation

        LayoutElement rootLE = root.AddComponent<LayoutElement>();
        rootLE.preferredWidth = 200;
        rootLE.preferredHeight = 26;

        // ── Outer Border (Deep dark base) ──
        GameObject borderObj = new GameObject("Border");
        borderObj.transform.SetParent(root.transform, false);

        Image borderImg = borderObj.AddComponent<Image>();
        borderImg.color = new Color(0.05f, 0.05f, 0.05f, 0.95f);

        RectTransform borderRT = borderObj.GetComponent<RectTransform>();
        borderRT.anchorMin = Vector2.zero;
        borderRT.anchorMax = Vector2.one;
        borderRT.offsetMin = Vector2.zero;
        borderRT.offsetMax = Vector2.zero;

        // Extra drop shadow on the bounding box for depth
        Shadow borderShadow = borderObj.AddComponent<Shadow>();
        borderShadow.effectColor = new Color(0f, 0f, 0f, 0.6f);
        borderShadow.effectDistance = new Vector2(2f, -2f);

        // ── Bar Background (Inner track) ──
        GameObject barBg = new GameObject("InnerTrack");
        barBg.transform.SetParent(borderObj.transform, false);

        Image bgImg = barBg.AddComponent<Image>();
        bgImg.color = new Color(0.15f, 0.15f, 0.15f, 1f);

        RectTransform bgRT = barBg.GetComponent<RectTransform>();
        bgRT.anchorMin = Vector2.zero;
        bgRT.anchorMax = Vector2.one;
        // 3px border thickness
        bgRT.offsetMin = new Vector2(3f, 3f);
        bgRT.offsetMax = new Vector2(-3f, -3f);

        // ── Fill Bar (stretches from left) ──
        GameObject barFill = new GameObject("Fill");
        barFill.transform.SetParent(barBg.transform, false);

        Image fill = barFill.AddComponent<Image>();
        fill.color = barColor;

        RectTransform fRT = barFill.GetComponent<RectTransform>();
        fRT.anchorMin = new Vector2(0f, 0f);
        fRT.anchorMax = new Vector2(1f, 1f);
        fRT.offsetMin = Vector2.zero;
        fRT.offsetMax = Vector2.zero;

        // ── 3D Highlight Overlay (Top half of the fill is slightly brighter) ──
        GameObject highlight = new GameObject("Highlight");
        highlight.transform.SetParent(barFill.transform, false);
        Image hlImg = highlight.AddComponent<Image>();
        hlImg.color = new Color(1f, 1f, 1f, 0.2f); // 20% white overlay
        
        RectTransform hlRT = highlight.GetComponent<RectTransform>();
        hlRT.anchorMin = new Vector2(0f, 0.5f); // covers only the top half
        hlRT.anchorMax = new Vector2(1f, 1f);
        hlRT.offsetMin = Vector2.zero;
        hlRT.offsetMax = Vector2.zero;

        // ── Label (Crisp bold text on top) ──
        GameObject labelObj = new GameObject("Label");
        labelObj.transform.SetParent(root.transform, false);

        Text label = labelObj.AddComponent<Text>();
        label.text = powerUpName;
        label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        label.fontSize = 14;
        label.fontStyle = FontStyle.Bold;
        label.color = Color.white;
        label.alignment = TextAnchor.MiddleCenter;

        RectTransform labelRT = labelObj.GetComponent<RectTransform>();
        labelRT.anchorMin = Vector2.zero;
        labelRT.anchorMax = Vector2.one;
        labelRT.offsetMin = Vector2.zero;
        labelRT.offsetMax = Vector2.zero;

        // Outline component makes text FAR more readable than Shadow
        Outline textOutline = labelObj.AddComponent<Outline>();
        textOutline.effectColor = new Color(0f, 0f, 0f, 0.85f);
        textOutline.effectDistance = new Vector2(1.5f, -1.5f);

        // ── Attach logic component ──
        PowerUpBarUI bar = root.AddComponent<PowerUpBarUI>();
        bar.rootRectTransform = rootRT;
        bar.fillRect = fRT;
        bar.fillImage = fill;
        bar.totalDuration = duration;
        bar.remainingTime = duration;
        bar.baseColor = barColor;

        return bar;
    }

    public void ResetDuration(float newDuration)
    {
        totalDuration = newDuration;
        remainingTime = newDuration;
        popInTimer = 0f; // Re-trigger the pop-in animation slightly
        if (fillRect != null)
            fillRect.anchorMax = new Vector2(1f, 1f);
    }

    void Update()
    {
        remainingTime -= Time.deltaTime;
        float t = Mathf.Clamp01(remainingTime / totalDuration);

        // 1) Shrink the fill from right to left smoothly
        if (fillRect != null)
            fillRect.anchorMax = new Vector2(t, 1f);

        // 2) Elastic pop-in animation sequence at spawn
        if (popInTimer < 1f && rootRectTransform != null)
        {
            popInTimer += Time.deltaTime * 3.5f; 
            float scaleT = Mathf.Clamp01(popInTimer);
            
            // Custom Elastic Out curve math
            float elasticScale = Mathf.Sin(-13f * (scaleT + 1f) * Mathf.PI * 0.5f) * Mathf.Pow(2f, -10f * scaleT) + 1f;
            rootRectTransform.localScale = new Vector3(elasticScale, elasticScale, 1f);
        }

        // 3) Dynamics / Flash based on remaining time
        if (t < 0.25f && fillImage != null)
        {
            // Rapid danger-flash when expiring soon (flashes to an intense red)
            float pulse = Mathf.PingPong(Time.time * 8f, 1f);
            fillImage.color = Color.Lerp(baseColor, new Color(1f, 0.1f, 0.1f), pulse);
        }
        else if (fillImage != null)
        {
            // Gentle breathing effect while active
            float breath = Mathf.PingPong(Time.time * 2f, 1f) * 0.2f;
            fillImage.color = Color.Lerp(baseColor, Color.white, breath);
        }

        // 4) Pop-out shrink before destroying
        if (remainingTime <= 0.15f && rootRectTransform != null)
        {
            float shrinkProgress = remainingTime / 0.15f;
            rootRectTransform.localScale = new Vector3(shrinkProgress, shrinkProgress, 1f);
        }

        // 5) Remove when completely empty
        if (remainingTime <= 0f)
        {
            Destroy(gameObject);
        }
    }
}
