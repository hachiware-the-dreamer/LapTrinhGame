using UnityEngine;

public class TankHealth : MonoBehaviour
{
    [Header("Health Settings")]
    [SerializeField] int maxHealth = 3;
    private int currentHealth;

    void Start()
    {
        currentHealth = maxHealth;
    }

    public void TakeDamage(int damageAmount)
    {
        currentHealth -= damageAmount;
        Debug.Log(gameObject.name + " took damage! Health: " + currentHealth);

        if (currentHealth <= 0)
        {
            Die();
        }
    }

    void Die()
    {
        Debug.Log(gameObject.name + " was destroyed!");

        // Notify the GameManager so it can show the end screen
        if (GameManager.Instance != null)
        {
            GameManager.Instance.OnTankDestroyed(gameObject.tag);
        }

        Destroy(gameObject);
    }
}