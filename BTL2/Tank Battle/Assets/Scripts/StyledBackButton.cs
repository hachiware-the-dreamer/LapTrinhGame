using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;

/// Attach to the Back Button GameObject.
/// Fully self-contained: generates rounded sprite, positions itself, styles label.
[RequireComponent(typeof(Button))]
public class StyledBackButton : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler, IPointerDownHandler, IPointerUpHandler
{
    static readonly Color NormalColor = new Color(0.80f, 0.08f, 0.08f, 1f); // red
    static readonly Color HoverColor  = new Color(1.00f, 0.22f, 0.22f, 1f); // bright red
    static readonly Color PressColor  = new Color(0.50f, 0.04f, 0.04f, 1f); // dark red

    const float AnimSpeed = 16f;

    Image           _bg;
    TextMeshProUGUI _label;
    Color           _target;

    void Awake()
    {
        // ── RectTransform: small, bottom-left ────────────────────────────────
        RectTransform rt = GetComponent<RectTransform>();
        rt.anchorMin        = Vector2.zero;
        rt.anchorMax        = Vector2.zero;
        rt.pivot            = Vector2.zero;
        rt.anchoredPosition = new Vector2(24f, 24f);
        rt.sizeDelta        = new Vector2(56f, 22f);

        // ── Image: generated rounded-rect sprite ─────────────────────────────
        _bg = GetComponent<Image>();
        if (_bg == null) _bg = gameObject.AddComponent<Image>();
        _bg.sprite = MakeRoundedRect(128, 42, 12);
        _bg.type   = Image.Type.Sliced;
        _bg.color  = NormalColor;

        // Remove default Button transition so our colour tween is the only one
        Button btn = GetComponent<Button>();
        btn.transition = Selectable.Transition.None;

        // ── Label ─────────────────────────────────────────────────────────────
        _label = GetComponentInChildren<TextMeshProUGUI>(true);
        if (_label != null)
        {
            _label.text      = "◄  BACK";
            _label.fontSize  = 11f;
            _label.fontStyle = FontStyles.Bold;
            _label.color     = Color.white;
            _label.alignment = TextAlignmentOptions.Center;
        }

        _target = NormalColor;
    }

    void Update()
    {
        _bg.color = Color.Lerp(_bg.color, _target, Time.unscaledDeltaTime * AnimSpeed);
    }

    public void OnPointerEnter(PointerEventData _) => _target = HoverColor;
    public void OnPointerExit (PointerEventData _) => _target = NormalColor;
    public void OnPointerDown (PointerEventData _) => _target = PressColor;
    public void OnPointerUp   (PointerEventData _) => _target = HoverColor;

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
        return Sprite.Create(tex,
            new Rect(0, 0, w, h),
            new Vector2(0.5f, 0.5f),
            100f,
            0,
            SpriteMeshType.FullRect,
            new Vector4(b, b, b, b));
    }

    static bool InsideRounded(int x, int y, int w, int h, int r)
    {
        // corners
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
