using UnityEngine;
using System.Collections;

public class TankHealth : MonoBehaviour
{
    [Header("Health Settings")]
    [SerializeField] int maxHealth = 3;

    [Header("Particles")]
    [SerializeField] GameObject deathExplosionPrefab;

    private int currentHealth;
    private bool isDead = false;
    private bool isShielded = false;
    private Coroutine shieldCoroutine;

    [Header("Shield Visual")]
    [SerializeField] GameObject shieldVisualPrefab;  // Optional: a circle/bubble sprite around the tank
    private GameObject activeShieldVisual;

    [Header("Heal Visual")]
    [SerializeField] GameObject healEffectPrefab;


    void Start()
    {
        currentHealth = maxHealth;
    }

    public void TakeDamage(int damageAmount)
    {
        if (isDead) return;

        // Shield blocks all damage
        if (isShielded)
        {
            Debug.Log(gameObject.name + " damage blocked by shield!");
            return;
        }

        currentHealth -= damageAmount;
        Debug.Log(gameObject.name + " took damage! Health: " + currentHealth);

        // Play hurt sound when taking damage
        if (AudioManager.Instance != null && currentHealth > 0)
        {
            AudioManager.Instance.PlayHurt();
        }

        if (UIManager.Instance != null)
        {
            UIManager.Instance.UpdateHealth(gameObject.tag, currentHealth);
        }

        if (currentHealth <= 0)
        {
            StartCoroutine(DeathRoutine());
        }
    }

    IEnumerator DeathRoutine()
    {
        if (isDead) yield break;
        isDead = true;

        Debug.Log(gameObject.name + " was destroyed!");

        // Play explosion sound once
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayExplode();
        }

        if (deathExplosionPrefab != null)
        {
            Instantiate(deathExplosionPrefab, transform.position, Quaternion.identity);
        }

        // Hide all child sprites
        SpriteRenderer[] sprites = GetComponentsInChildren<SpriteRenderer>();
        foreach (SpriteRenderer sr in sprites)
        {
            sr.enabled = false;
        }

        // Turn off trails
        TrailRenderer[] trails = GetComponentsInChildren<TrailRenderer>();
        foreach (TrailRenderer tr in trails)
        {
            tr.emitting = false;
        }

        // Disable collision and scripts safely
        BoxCollider2D col = GetComponent<BoxCollider2D>();
        if (col != null) col.enabled = false;

        TankMovement movement = GetComponent<TankMovement>();
        if (movement != null) movement.enabled = false;

        TankShooting shooting = GetComponent<TankShooting>();
        if (shooting != null) shooting.enabled = false;

        // Notify GameManager
        if (GameManager.Instance != null)
        {
            GameManager.Instance.OnTankDestroyed(gameObject.tag);
        }

        yield return new WaitForSecondsRealtime(1f);
        Destroy(gameObject);
    }

    /// <summary>
    /// Called by PowerUp to temporarily make the tank invincible.
    /// </summary>
    public void ApplyShield(float duration)
    {
        if (shieldCoroutine != null)
            StopCoroutine(shieldCoroutine);

        shieldCoroutine = StartCoroutine(ShieldRoutine(duration));
    }

    IEnumerator ShieldRoutine(float duration)
    {
        isShielded = true;
        Debug.Log(gameObject.name + " shield active for " + duration + "s");

        // Show shield visual
        if (shieldVisualPrefab != null && activeShieldVisual == null)
        {
            activeShieldVisual = Instantiate(shieldVisualPrefab, transform);
            activeShieldVisual.transform.localPosition = Vector3.zero;
        }

        yield return new WaitForSeconds(duration);

        isShielded = false;
        Debug.Log(gameObject.name + " shield ended");

        // Remove shield visual
        if (activeShieldVisual != null)
        {
            Destroy(activeShieldVisual);
            activeShieldVisual = null;
        }

        shieldCoroutine = null;
    }
    public void Heal(int amount)
    {
        if (isDead) return;

        int previousHealth = currentHealth;
        currentHealth = Mathf.Min(currentHealth + amount, maxHealth);

        if (currentHealth > previousHealth)
        {
            Debug.Log(gameObject.name + " healed! Health: " + currentHealth);

            // Play heal effect
            if (healEffectPrefab != null)
            {
                GameObject effect = Instantiate(healEffectPrefab, transform.position, Quaternion.identity, transform);
                Destroy(effect, 2f);
            }

            // Update HUD
            if (UIManager.Instance != null)
            {
                UIManager.Instance.UpdateHealth(gameObject.tag, currentHealth);
            }
        }
    }
}