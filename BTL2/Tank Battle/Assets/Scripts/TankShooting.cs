using UnityEngine;
using UnityEngine.InputSystem;

public class TankShooting : MonoBehaviour
{
    [Header("Weapon Setup")]
    [SerializeField] GameObject bulletPrefab;
    [SerializeField] Transform firePoint;
    [SerializeField] InputActionReference fireAction;

    [Header("Weapon Stats")]
    [SerializeField] float fireCooldown = 0.5f;
    private float lastFireTime = -10f; // -10 to allow first shot

    private void OnEnable() { fireAction.action.Enable(); }
    private void OnDisable() { fireAction.action.Disable(); }

    // Update is called once per frame
    void Update()
    {
        // WasPressedThisFrame -> holding the button doesn't act like a machine gun
        if (fireAction.action.WasPressedThisFrame())
        {
            if (Time.time >= lastFireTime + fireCooldown)
            {
                Shoot();
            }
        }
    }

    void Shoot()
    {
        lastFireTime = Time.time; // Reset the cooldown timer
        Quaternion bulletRotation = firePoint.rotation * Quaternion.Euler(0, 0, 180f);
        
        GameObject newBullet = Instantiate(bulletPrefab, firePoint.position, bulletRotation);

        BulletPhysics bulletScript = newBullet.GetComponent<BulletPhysics>();
        if (bulletScript != null)
        {
            bulletScript.ownerTag = gameObject.tag; // Passes "Player1" or "Player2"
        }
    }
}
