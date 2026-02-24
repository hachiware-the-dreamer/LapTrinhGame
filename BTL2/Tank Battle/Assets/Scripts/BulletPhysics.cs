using UnityEngine;

public class BulletPhysics : MonoBehaviour
{
    [Header("Bullet Settings")]
    [SerializeField] float speed = 10f;
    [SerializeField] float lifetime = 3f;
    [SerializeField] LayerMask collisionLayers;

    [HideInInspector] public string ownerTag;

    private Vector2 velocity;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        velocity = transform.up * speed;
        Destroy(gameObject, lifetime); // Despawns after lifetime
    }

    // Update is called once per frame
    void Update()
    {
        Vector2 step = velocity * Time.deltaTime;
        RaycastHit2D hit = Physics2D.Raycast(transform.position, velocity.normalized, step.magnitude, collisionLayers);

        if (hit.collider != null)
        {
            // Player hit
            if (hit.collider.CompareTag(ownerTag)) // Check if bullet is from this tank
            {
                transform.position += (Vector3)step;
                return;
            }
            
            TankHealth enemyTank = hit.collider.GetComponent<TankHealth>();
            if (enemyTank != null)
            {
                enemyTank.TakeDamage(1);
                Destroy(gameObject);
                return;
            }

            // Wall hit            
            Vector2 n = hit.normal;
            Vector2 vOld = velocity;
            float dotProduct = Vector2.Dot(vOld, n);
            Vector2 vNew = vOld - (2f * dotProduct * n);

            velocity = vNew; // Set new velocity
            transform.up = velocity.normalized; // Rotate bullet
            // Snap the bullet to the slightly above the point where it hits the wall
            // -> Prevents the bullet from glitching through
            transform.position = hit.point + (hit.normal * 0.05f);
        }
        else
        {
            transform.position += (Vector3)step;
        }
    }
}
