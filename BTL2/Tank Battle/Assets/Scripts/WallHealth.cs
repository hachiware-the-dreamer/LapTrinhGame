using UnityEngine;

public class WallHealth : MonoBehaviour
{
    [Header("Health Settings")]
    [SerializeField] int maxHealth = 5;
    
    [Header("Visual Feedback")]
    [SerializeField] bool showDamageEffect = true;
    
    private int currentHealth;
    private SpriteRenderer spriteRenderer;
    private Color originalColor;
    private bool isDestroyed = false;

    void Start()
    {
        currentHealth = maxHealth;
        spriteRenderer = GetComponent<SpriteRenderer>();
        if (spriteRenderer != null)
        {
            originalColor = spriteRenderer.color;
        }
    }

    public void TakeDamage(int damage)
    {
        if (isDestroyed) return;

        currentHealth -= damage;

        // Visual feedback - darken the wall as it takes damage
        if (showDamageEffect && spriteRenderer != null)
        {
            float healthPercent = (float)currentHealth / maxHealth;
            spriteRenderer.color = Color.Lerp(Color.gray, originalColor, healthPercent);
        }

        if (currentHealth <= 0)
        {
            DestroyWall();
        }
    }

    void DestroyWall()
    {
        if (isDestroyed) return;
        isDestroyed = true;

        // Play explosion sound
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayExplode();
        }

        Destroy(gameObject);
    }
}
