using UnityEngine;
using UnityEngine.EventSystems;

/// Attach to any map button. Scales up on hover, back on exit.
public class ButtonHoverScale : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler, IPointerDownHandler, IPointerUpHandler
{
    [SerializeField] float hoverScale   = 1.08f;
    [SerializeField] float pressScale   = 0.95f;
    [SerializeField] float animSpeed    = 12f;

    Vector3 _targetScale;
    Vector3 _originalScale;

    void Awake()
    {
        _originalScale = transform.localScale;
        _targetScale   = _originalScale;
    }

    void Update()
    {
        transform.localScale = Vector3.Lerp(transform.localScale, _targetScale, Time.unscaledDeltaTime * animSpeed);
    }

    public void OnPointerEnter(PointerEventData _) => _targetScale = _originalScale * hoverScale;
    public void OnPointerExit (PointerEventData _) => _targetScale = _originalScale;
    public void OnPointerDown (PointerEventData _) => _targetScale = _originalScale * pressScale;
    public void OnPointerUp   (PointerEventData _) => _targetScale = _originalScale * hoverScale;
}
