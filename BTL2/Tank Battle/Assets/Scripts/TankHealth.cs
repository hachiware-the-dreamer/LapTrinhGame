using UnityEngine;
using System.Collections;

public class TankHealth : MonoBehaviour
{
    [Header("Health Settings")]
    [SerializeField] int maxHealth = 3;

    [Header("Particles")]
    [SerializeField] GameObject deathExplosionPrefab;
    private int currentHealth;

    void Start()
    {
        currentHealth = maxHealth;
    }

    public void TakeDamage(int damageAmount)
    {
        currentHealth -= damageAmount;
        Debug.Log(gameObject.name + " took damage! Health: " + currentHealth);
        UIManager.Instance.UpdateHealth(gameObject.tag, currentHealth); // Update HUD

        if (currentHealth <= 0)
        {
            StartCoroutine(DeathRoutine());
        }
    }

    IEnumerator DeathRoutine()
    {
        Debug.Log(gameObject.name + " was destroyed!");

        if (deathExplosionPrefab != null)
        {
            Instantiate(deathExplosionPrefab, transform.position, Quaternion.identity);
        }

        // Hide all child sprites
        SpriteRenderer[] sprites = GetComponentsInChildren<SpriteRenderer>();
        foreach(SpriteRenderer sr in sprites)
        {
            sr.enabled = false;
        }

        // Turn off the trails
        TrailRenderer[] trails = GetComponentsInChildren<TrailRenderer>();
        foreach(TrailRenderer tr in trails)
        {
            tr.emitting = false; 
        }

        // Disable collision and scripts
        GetComponent<BoxCollider2D>().enabled = false;
        GetComponent<TankMovement>().enabled = false;
        GetComponent<TankShooting>().enabled = false;

        // Tell the GameManager to show the UI
        if (GameManager.Instance != null)
        {
            GameManager.Instance.OnTankDestroyed(gameObject.tag);
        }

        // Wait for explosion
        yield return new WaitForSecondsRealtime(1f);
        Destroy(gameObject);
    }
}