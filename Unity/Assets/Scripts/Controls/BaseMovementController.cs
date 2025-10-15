using UnityEngine;

public class BaseMovementController : MonoBehaviour
{
    [Header("Network Reference")]
    public PepperConnection pepperConnection;
    
    [Header("Movement Settings")]
    [Range(0f, 1f)] public float maxLinearSpeed = 0.5f;
    [Range(0f, 2f)] public float maxAngularSpeed = 1.0f;
    [Range(0f, 1f)] public float accelerationSmoothing = 0.2f;
    
    private Vector3 currentLinearVelocity = Vector3.zero;
    private float currentAngularVelocity = 0f;
    
    void Start()
    {
        if (pepperConnection == null)
        {
            pepperConnection = PepperConnection.Instance;
            if (pepperConnection == null)
            {
                Debug.LogError("PepperConnection instance not found!");
                this.enabled = false;
            }
        }
    }

    public void UpdateMovement(Vector2 leftJoystick, float rightJoystickX)
    {
        Vector3 targetLinearVelocity = new Vector3(leftJoystick.y * maxLinearSpeed, leftJoystick.x * maxLinearSpeed, 0);
        float targetAngularVelocity = -rightJoystickX * maxAngularSpeed;
        
        currentLinearVelocity = Vector3.Lerp(currentLinearVelocity, targetLinearVelocity, accelerationSmoothing);
        currentAngularVelocity = Mathf.Lerp(currentAngularVelocity, targetAngularVelocity, accelerationSmoothing);
        
        SendMovementCommand();
    }

    void SendMovementCommand()
    {
        if (pepperConnection == null || !pepperConnection.IsConnected()) return;
        
        var command = new BaseMovementCommand
        {
            type = "base_move",
            linear = new float[] { currentLinearVelocity.x, currentLinearVelocity.y, currentLinearVelocity.z },
            angular = currentAngularVelocity
        };
        pepperConnection.SendCommand(command);
    }
}

[System.Serializable]
public class BaseMovementCommand
{
    public string type;
    public float[] linear;
    public float angular;
}