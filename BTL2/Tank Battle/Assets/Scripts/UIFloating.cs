using UnityEngine;

public class UIFloating : MonoBehaviour
{
    [Header("Animation Settings")]
    public float speed = 2f;      
    public float amount = 10f;    

    private RectTransform rectTransform;
    private Vector2 startPosition;

    void Start()
    {
        rectTransform = GetComponent<RectTransform>();
        startPosition = rectTransform.anchoredPosition;
    }

    void Update()
    {
        float newY = startPosition.y + Mathf.Sin(Time.time * speed) * amount;
        rectTransform.anchoredPosition = new Vector2(startPosition.x, newY);
    }
}