using UnityEngine;
using UnityEngine.InputSystem;
using System.Collections;

public class TankShooting : MonoBehaviour
{
    [Header("Weapon Setup")]
    [SerializeField] GameObject bulletPrefab;
    [SerializeField] Transform firePoint;
    [SerializeField] InputActionReference fireAction;

    [Header("Weapon Stats")]
    [SerializeField] float fireCooldown = 0.5f;
    private float lastFireTime = -10f; // -10 to allow first shot

    [Header("Particles")]
    [SerializeField] GameObject muzzleFlashPrefab;

    // Power-up state
    private bool tripleShot = false;
    private Coroutine tripleShotCoroutine;

    [Header("Triple Shot Visual")]
    [SerializeField] GameObject tripleShotVisualPrefab;  // Glow or aura effect
    private GameObject activeTripleShotVisual;

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
        
        // Play shooting sound
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayFire();
        }
        
        // Fire the main bullet (center)
        FireBullet(firePoint.position, firePoint.rotation * Quaternion.Euler(0, 0, 180f));

        // Triple shot: fire two extra bullets at an angle
        if (tripleShot)
        {
            float spreadAngle = 15f;
            FireBullet(firePoint.position, firePoint.rotation * Quaternion.Euler(0, 0, 180f + spreadAngle));
            FireBullet(firePoint.position, firePoint.rotation * Quaternion.Euler(0, 0, 180f - spreadAngle));
        }

        if (muzzleFlashPrefab != null)
        {
            Instantiate(muzzleFlashPrefab, firePoint.position, firePoint.rotation);
        }
    }

    void FireBullet(Vector3 position, Quaternion rotation)
    {
        GameObject newBullet = Instantiate(bulletPrefab, position, rotation);
        BulletPhysics bulletScript = newBullet.GetComponent<BulletPhysics>();
        if (bulletScript != null)
        {
            bulletScript.ownerTag = gameObject.tag;
        }
    }

    /// <summary>
    /// Called by PowerUp to temporarily enable triple shot.
    /// </summary>
    public void ApplyTripleShot(float duration)
    {
        if (tripleShotCoroutine != null)
            StopCoroutine(tripleShotCoroutine);

        tripleShotCoroutine = StartCoroutine(TripleShotRoutine(duration));
    }

    IEnumerator TripleShotRoutine(float duration)
    {
        tripleShot = true;
        Debug.Log(gameObject.name + " triple shot active for " + duration + "s");

        // Show triple shot visual
        if (tripleShotVisualPrefab != null && activeTripleShotVisual == null)
        {
            activeTripleShotVisual = Instantiate(tripleShotVisualPrefab, transform);
            activeTripleShotVisual.transform.localPosition = Vector3.zero;
        }

        yield return new WaitForSeconds(duration);

        tripleShot = false;
        Debug.Log(gameObject.name + " triple shot ended");

        // Remove triple shot visual
        if (activeTripleShotVisual != null)
        {
            Destroy(activeTripleShotVisual);
            activeTripleShotVisual = null;
        }

        tripleShotCoroutine = null;
    }
}
