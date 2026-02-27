using UnityEngine;
using UnityEngine.InputSystem;

public class TankMovement : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] float moveSpeed = 5f;
    [SerializeField] float rotationSpeed = 180f;

    [Header("Input Setup")]
    [SerializeField] InputActionReference moveAction; // for local multiplayer

    [Header("Collision Setup")]
    [SerializeField] BoxCollider2D tankCollider;
    [SerializeField] LayerMask wallLayerMask;

    [Header("Audio")]
    [SerializeField] AudioSource engineAudioSource;

    private Vector2 currentInput;
    private float currentAngle = 0f;
    private bool isMoving = false;

    // Must manually enable the move action when using references
    private void OnEnable() { moveAction.action.Enable(); }
    private void OnDisable() { moveAction.action.Disable(); }

    void Start()
    {
        // Setup engine audio if AudioManager exists
        if (engineAudioSource == null)
        {
            engineAudioSource = gameObject.AddComponent<AudioSource>();
            engineAudioSource.loop = true;
            engineAudioSource.playOnAwake = false;
            if (AudioManager.Instance != null)
            {
                engineAudioSource.clip = AudioManager.Instance.moveSound;
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        currentInput = moveAction.action.ReadValue<Vector2>();

        // Handle engine sound
        bool shouldMove = currentInput.magnitude > 0.1f;
        if (shouldMove && !isMoving)
        {
            isMoving = true;
            if (engineAudioSource != null && engineAudioSource.clip != null && !engineAudioSource.isPlaying)
            {
                engineAudioSource.Play();
            }
        }
        else if (!shouldMove && isMoving)
        {
            isMoving = false;
            if (engineAudioSource != null)
            {
                engineAudioSource.Stop();
            }
        }

        // Rotation
        if (currentInput.x != 0)
        {
            // Subtracting the input so 'Right' rotates clockwise
            currentAngle -= currentInput.x * rotationSpeed * Time.deltaTime;
            transform.rotation = Quaternion.Euler(0, 0, currentAngle);
        }

        // Movement
        if (currentInput.y != 0)
        {
            // Apply a +270 degree offset because the sprite naturally faces down
            float angleInRadians = (currentAngle + 270f) * Mathf.Deg2Rad;
            // Move formulas
            float velocityX = moveSpeed * Mathf.Cos(angleInRadians);
            float velocityY = moveSpeed * Mathf.Sin(angleInRadians);

            Vector3 movement = new Vector3(velocityX, velocityY, 0f) * currentInput.y * Time.deltaTime;
            Vector3 finalPosition = transform.position;
            
            // Try X-axis movement
            Vector3 xOnlyPosition = transform.position + new Vector3(movement.x, 0f, 0f);
            Vector2 xPos2D = new Vector2(xOnlyPosition.x, xOnlyPosition.y);
            Vector2 minCornerX = xPos2D + tankCollider.offset - (tankCollider.size / 2f);
            Vector2 maxCornerX = xPos2D + tankCollider.offset + (tankCollider.size / 2f);
            
            if (Physics2D.OverlapArea(minCornerX, maxCornerX, wallLayerMask) == null)
            {
                finalPosition.x = xOnlyPosition.x; // Allow X movement
            }
            
            // Try Y-axis movement
            Vector3 yOnlyPosition = transform.position + new Vector3(0f, movement.y, 0f);
            Vector2 yPos2D = new Vector2(yOnlyPosition.x, yOnlyPosition.y);
            Vector2 minCornerY = yPos2D + tankCollider.offset - (tankCollider.size / 2f);
            Vector2 maxCornerY = yPos2D + tankCollider.offset + (tankCollider.size / 2f);
            
            if (Physics2D.OverlapArea(minCornerY, maxCornerY, wallLayerMask) == null)
            {
                finalPosition.y = yOnlyPosition.y; // Allow Y movement
            }
            
            transform.position = finalPosition;
        }
    }
}
