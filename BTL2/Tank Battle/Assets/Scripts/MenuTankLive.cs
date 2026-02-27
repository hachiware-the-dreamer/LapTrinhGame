using UnityEngine;

public class MenuTankLive : MonoBehaviour
{
    [Header("Breathing")]
    public float breathSpeed = 3f;
    public float breathAmount = 0.08f;
    private Vector3 startScale;

    [Header("Shooting")]
    public GameObject bulletPrefab;
    public Transform firePoint;
    public float shootInterval = 2f;
    public float bulletSpeed = 15f;

    void Start()
    {
        startScale = transform.localScale;
        InvokeRepeating("Shoot", 1f, shootInterval);
    }

    void Update()
    {
        float scaleOffset = Mathf.Sin(Time.time * breathSpeed) * breathAmount;
        transform.localScale = startScale + new Vector3(scaleOffset, scaleOffset, 0f);
    }

    void Shoot()
    {
        if (bulletPrefab != null && firePoint != null)
        {
            GameObject bullet = Instantiate(bulletPrefab, firePoint.position, firePoint.rotation);
            
            Rigidbody2D rb = bullet.GetComponent<Rigidbody2D>();
            if (rb != null)
            {
                rb.linearVelocity = -firePoint.right * bulletSpeed; 
            }

            Destroy(bullet, 3f);
        }
    }
}