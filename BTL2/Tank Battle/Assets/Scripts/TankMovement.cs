using UnityEngine;
using UnityEngine.InputSystem;

public class TankMovement : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] float moveSpeed = 5f;
    [SerializeField] float rotationSpeed = 180f;

    [Header("Input Setup")]
    [SerializeField] InputActionReference moveAction; // for local multiplayer

    private Vector2 currentInput;
    private float currentAngle = 0f;

    // Must manually enable the action when using references
    private void OnEnable()
    {
        moveAction.action.Enable();
    }

    private void OnDisable()
    {
        moveAction.action.Disable();
    }

    // Update is called once per frame
    void Update()
    {
        currentInput = moveAction.action.ReadValue<Vector2>();

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
            
            transform.position += movement;
        }
    }
}
