using UnityEngine;
using System.Collections;

public enum PowerUpType
{
    SpeedBoost,
    DamageBoost
}

public class PowerUp : MonoBehaviour
{
    [Header("Power-Up Settings")]
    public PowerUpType type;
    [SerializeField] float duration = 5f;
    [SerializeField] float speedMultiplier = 1.5f;  // Used for SpeedBoost
    [SerializeField] int damageBonus = 1;            // Used for DamageBoost
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
            string powerUpName = (type == PowerUpType.SpeedBoost) ? "SPEED UP" : "DAMAGE UP";
            UIManager.Instance.ShowPowerUp(other.gameObject.tag, powerUpName, duration);
        }

        // Play pickup sound
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayPickup();
        }

        Destroy(gameObject);
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

            case PowerUpType.DamageBoost:
                TankShooting shooting = tank.GetComponent<TankShooting>();
                if (shooting != null)
                {
                    shooting.ApplyDamageBoost(damageBonus, duration);
                }
                break;
        }
    }
}
