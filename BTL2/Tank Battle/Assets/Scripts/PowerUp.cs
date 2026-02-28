using UnityEngine;
using System.Collections;

public enum PowerUpType
{
    SpeedBoost,
    TripleShot,
    Shield
}

public class PowerUp : MonoBehaviour
{
    [Header("Power-Up Settings")]
    public PowerUpType type;
    [SerializeField] float duration = 5f;
    [SerializeField] float speedMultiplier = 1.5f;  // Used for SpeedBoost
    [SerializeField] float bobSpeed = 2f;
    [SerializeField] float bobHeight = 0.15f;

    private Vector3 startPos;

    void Start()
    {
        startPos = transform.position;
    }

    void Update()
    {
        // Floating bob animation
        float newY = startPos.y + Mathf.Sin(Time.time * bobSpeed) * bobHeight;
        transform.position = new Vector3(startPos.x, newY, startPos.z);
    }

    void OnTriggerEnter2D(Collider2D other)
    {
        // Only pick up by players
        if (!other.CompareTag("Player1") && !other.CompareTag("Player2"))
            return;

        ApplyEffect(other.gameObject);

        // Show power-up notification on HUD
        if (UIManager.Instance != null)
        {
            string powerUpName = GetPowerUpDisplayName();
            UIManager.Instance.ShowPowerUp(other.gameObject.tag, powerUpName, duration);
        }

        // Play pickup sound
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayPickup();
        }

        Destroy(gameObject);
    }

    string GetPowerUpDisplayName()
    {
        switch (type)
        {
            case PowerUpType.SpeedBoost: return "SPEED UP";
            case PowerUpType.TripleShot: return "TRIPLE SHOT";
            case PowerUpType.Shield:     return "SHIELD";
            default: return "POWER UP";
        }
    }

    void ApplyEffect(GameObject tank)
    {
        switch (type)
        {
            case PowerUpType.SpeedBoost:
                TankMovement movement = tank.GetComponent<TankMovement>();
                if (movement != null)
                {
                    movement.ApplySpeedBoost(speedMultiplier, duration);
                }
                break;

            case PowerUpType.TripleShot:
                TankShooting shooting = tank.GetComponent<TankShooting>();
                if (shooting != null)
                {
                    shooting.ApplyTripleShot(duration);
                }
                break;

            case PowerUpType.Shield:
                TankHealth health = tank.GetComponent<TankHealth>();
                if (health != null)
                {
                    health.ApplyShield(duration);
                }
                break;
        }
    }
}
