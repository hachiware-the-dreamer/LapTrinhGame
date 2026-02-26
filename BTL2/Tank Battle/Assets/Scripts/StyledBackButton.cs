using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;

/// Attach to the Back Button GameObject.
/// Fully self-contained: generates rounded sprite, positions itself, styles label.
[RequireComponent(typeof(Button))]
public class StyledBackButton : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler, IPointerDownHandler, IPointerUpHandler
{
    static readonly Color NormalColor = new Color(0.85f, 0.28f, 0.28f, 1f); 
    static readonly Color HoverColor  = new Color(0.95f, 0.35f, 0.35f, 1f); 
    static readonly Color PressColor  = new Color(0.70f, 0.15f, 0.15f, 1f); 

    const float AnimSpeed = 15f;

    Image           _bg;
    TextMeshProUGUI _label;
    
    Color   _targetColor;
    Vector3 _targetScale; // Bouncy animation

    void Awake()
    {
        RectTransform rt = GetComponent<RectTransform>();
        rt.anchorMin        = Vector2.zero;
        rt.anchorMax        = Vector2.zero;
        rt.pivot            = Vector2.zero;
        rt.anchoredPosition = new Vector2(40f, 40f);
        rt.sizeDelta        = new Vector2(140f, 50f);

        // ── Image: generated rounded-rect sprite ─────────────────────────────
        _bg = GetComponent<Image>();
        if (_bg == null) _bg = gameObject.AddComponent<Image>();
        
        _bg.sprite = MakeRoundedRect(128, 64, 16); 
        _bg.type   = Image.Type.Sliced;
        _bg.color  = NormalColor;

        Button btn = GetComponent<Button>();
        btn.transition = Selectable.Transition.None;

        _label = GetComponentInChildren<TextMeshProUGUI>(true);
        if (_label != null)
        {
            _label.text      = "◄  BACK";
            _label.fontSize  = 22f;
            _label.fontStyle = FontStyles.Bold;
            _label.color     = Color.white;
            _label.alignment = TextAlignmentOptions.Center;
        }

        _targetColor = NormalColor;
        _targetScale = Vector3.one;
    }

    void Update()
    {
        // Smoothly lerp BOTH color and scale every frame
        _bg.color = Color.Lerp(_bg.color, _targetColor, Time.unscaledDeltaTime * AnimSpeed);
        transform.localScale = Vector3.Lerp(transform.localScale, _targetScale, Time.unscaledDeltaTime * AnimSpeed);
    }

    // ── Input Handling with Bounce Animation ─────────────────────────────────
    public void OnPointerEnter(PointerEventData _) 
    {
        _targetColor = HoverColor;
        _targetScale = new Vector3(1.05f, 1.05f, 1f); // Pop up slightly on hover
    }
    
    public void OnPointerExit(PointerEventData _) 
    {
        _targetColor = NormalColor;
        _targetScale = Vector3.one; // Return to normal
    }
    
    public void OnPointerDown(PointerEventData _) 
    {
        _targetColor = PressColor;
        _targetScale = new Vector3(0.95f, 0.95f, 1f); // Squish down on click
    }
    
    public void OnPointerUp(PointerEventData _) 
    {
        _targetColor = HoverColor;
        _targetScale = new Vector3(1.05f, 1.05f, 1f); // Bounce back up when released
    }

    // ── Procedural rounded-rectangle sprite ──────────────────────────────────
    static Sprite MakeRoundedRect(int w, int h, int radius)
    {
        Texture2D tex = new Texture2D(w, h, TextureFormat.ARGB32, false);
        tex.filterMode = FilterMode.Bilinear;
        Color fill  = Color.white;
        Color empty = Color.clear;

        for (int y = 0; y < h; y++)
        for (int x = 0; x < w; x++)
            tex.SetPixel(x, y, InsideRounded(x, y, w, h, radius) ? fill : empty);

        tex.Apply();

        int b = radius;
        return Sprite.Create(tex, new Rect(0, 0, w, h), new Vector2(0.5f, 0.5f), 100f, 0, SpriteMeshType.FullRect, new Vector4(b, b, b, b));
    }

    static bool InsideRounded(int x, int y, int w, int h, int r)
    {
        int[] cx = { r,     w-r-1, r,     w-r-1 };
        int[] cy = { r,     r,     h-r-1, h-r-1 };
        for (int i = 0; i < 4; i++)
        {
            int dx = x - cx[i], dy = y - cy[i];
            bool inCornerRegion = (x < r || x >= w-r) && (y < r || y >= h-r);
            if (inCornerRegion && dx*dx + dy*dy > r*r) return false;
        }
        return true;
    }
}