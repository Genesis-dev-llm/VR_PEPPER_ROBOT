using UnityEngine;

public class HeadController : MonoBehaviour
{
    [Header("Network Reference")]
    public PepperConnection pepperConnection;
    
    [Header("Head Settings")]
    [Range(0f, 1f)] public float movementSpeed = 0.3f;
    [Range(0f, 1f)] public float smoothingFactor = 0.2f;
    
    [Header("Joint Limits (degrees)")]
    public float headYawMin = -119.5f, headYawMax = 119.5f;
    public float headPitchMin = -38.5f, headPitchMax = 29.5f;

    private float headYawCurrent = 0f, headPitchCurrent = 0f;

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

    public void UpdateHeadTarget(Quaternion headsetRotation)
    {
        Vector3 eulerAngles = headsetRotation.eulerAngles;
        
        float yaw = NormalizeAngle(eulerAngles.y);
        float pitch = NormalizeAngle(eulerAngles.x);
        
        float headYawTarget = Mathf.Clamp(yaw * Mathf.Deg2Rad, headYawMin * Mathf.Deg2Rad, headYawMax * Mathf.Deg2Rad);
        float headPitchTarget = Mathf.Clamp(-pitch * Mathf.Deg2Rad, headPitchMin * Mathf.Deg2Rad, headPitchMax * Mathf.Deg2Rad);
        
        headYawCurrent = Mathf.Lerp(headYawCurrent, headYawTarget, smoothingFactor);
        headPitchCurrent = Mathf.Lerp(headPitchCurrent, headPitchTarget, smoothingFactor);
        
        SendHeadCommand();
    }

    float NormalizeAngle(float angle)
    {
        while (angle > 180f) angle -= 360f;
        while (angle < -180f) angle += 360f;
        return angle;
    }

    void SendHeadCommand()
    {
        if (pepperConnection == null || !pepperConnection.IsConnected()) return;
        
        var command = new HeadCommand { type = "head_move", yaw = headYawCurrent, pitch = headPitchCurrent, speed = movementSpeed };
        pepperConnection.SendCommand(command);
    }
}

[System.Serializable]
public class HeadCommand
{
    public string type;
    public float yaw;
    public float pitch;
    public float speed;
}