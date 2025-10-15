using UnityEngine;

/// <summary>
/// IK Solver for Pepper Robot Arms using FABRIK (Forward And Backward Reaching Inverse Kinematics)
/// Updated with real Pepper arm dimensions from official specifications
/// </summary>
public class IKSolver : MonoBehaviour
{
    [Header("IK Chain Definition - PEPPER ROBOT SPECIFICATIONS")]
    public Transform shoulderOrigin;
    
    // CRITICAL: These are Pepper's actual arm segment lengths in meters
    // Source: Aldebaran Pepper technical specifications
    [Tooltip("Pepper upper arm: Shoulder to Elbow (181mm total reach)")]
    public float upperArmLength = 0.105f;  // 105mm - ShoulderPitch to ElbowRoll
    
    [Tooltip("Pepper forearm: Elbow to Wrist")]
    public float forearmLength = 0.05595f;  // 55.95mm - ElbowRoll to WristYaw
    
    [Tooltip("Hand extension from wrist (approx)")]
    public float handLength = 0.02f;  // ~20mm - WristYaw to hand center
    
    private float totalArmLength;
    private float workspaceRadius;  // Maximum safe reach

    [Header("Solver Parameters")]
    [Tooltip("FABRIK iterations for convergence")]
    public int iterations = 10;
    
    [Tooltip("Position error tolerance in meters")]
    public float tolerance = 0.001f;  // 1mm tolerance
    
    [Tooltip("Scale factor for workspace limit (0.9 = 90% of max reach)")]
    [Range(0.5f, 1.0f)]
    public float workspaceSafety = 0.85f;  // Use 85% of max reach for safety

    [Header("Joint References (for Debug)")]
    public Transform elbowHint;
    
    [Header("Debug Visualization")]
    public bool showGizmos = true;
    public Color reachableColor = Color.green;
    public Color unreachableColor = Color.red;

    private Vector3[] chain;
    private float[] boneLengths;
    private bool lastTargetWasReachable = true;

    void Awake()
    {
        Initialize();
    }

    void Initialize()
    {
        // 3-joint chain: shoulder → elbow → wrist
        chain = new Vector3[3]; 
        boneLengths = new float[2];
        boneLengths[0] = upperArmLength;
        boneLengths[1] = forearmLength;
        
        totalArmLength = upperArmLength + forearmLength;
        workspaceRadius = totalArmLength * workspaceSafety;
        
        Debug.Log($"IK Solver initialized for Pepper arm:");
        Debug.Log($"  Upper arm: {upperArmLength * 1000f:F1}mm");
        Debug.Log($"  Forearm: {forearmLength * 1000f:F1}mm");
        Debug.Log($"  Total reach: {totalArmLength * 1000f:F1}mm");
        Debug.Log($"  Safe workspace: {workspaceRadius * 1000f:F1}mm");
    }

    public Vector3[] Solve(Vector3 targetPosition)
    {
        if (shoulderOrigin == null)
        {
            Debug.LogError("IK Solver: shoulderOrigin not assigned!");
            return null;
        }

        Vector3 rootPos = shoulderOrigin.position;
        float distanceToTarget = Vector3.Distance(rootPos, targetPosition);
        
        // Check if target is within safe workspace
        lastTargetWasReachable = distanceToTarget <= workspaceRadius;

        // If target is beyond reach, clamp to workspace boundary
        if (distanceToTarget > workspaceRadius)
        {
            Vector3 direction = (targetPosition - rootPos).normalized;
            targetPosition = rootPos + direction * workspaceRadius;
            distanceToTarget = workspaceRadius;
        }
        
        // If target is too close (collision zone), push to minimum distance
        float minDistance = upperArmLength * 0.3f;  // 30% of upper arm
        if (distanceToTarget < minDistance)
        {
            Vector3 direction = (targetPosition - rootPos).normalized;
            targetPosition = rootPos + direction * minDistance;
            distanceToTarget = minDistance;
        }

        // Handle straight-line case (arm fully extended)
        if (distanceToTarget >= totalArmLength * 0.99f)
        {
            Vector3 direction = (targetPosition - rootPos).normalized;
            chain[0] = rootPos;
            chain[1] = rootPos + direction * upperArmLength;
            chain[2] = chain[1] + direction * forearmLength;
            return chain;
        }

        // Initialize chain with reasonable starting pose
        chain[0] = rootPos;
        Vector3 dirToTarget = (targetPosition - rootPos).normalized;
        chain[1] = rootPos + dirToTarget * upperArmLength;
        chain[2] = chain[1] + dirToTarget * forearmLength;

        // FABRIK Algorithm: Forward and Backward reaching
        for (int iter = 0; iter < iterations; iter++)
        {
            // Check convergence
            if (Vector3.Distance(chain[chain.Length - 1], targetPosition) < tolerance)
                break;

            // FORWARD: Pull from end effector toward target
            chain[chain.Length - 1] = targetPosition;
            for (int i = chain.Length - 2; i >= 0; i--)
            {
                Vector3 direction = (chain[i] - chain[i + 1]).normalized;
                chain[i] = chain[i + 1] + direction * boneLengths[i];
            }

            // BACKWARD: Push from root toward target
            chain[0] = rootPos;
            for (int i = 1; i < chain.Length; i++)
            {
                Vector3 direction = (chain[i] - chain[i - 1]).normalized;
                chain[i] = chain[i - 1] + direction * boneLengths[i - 1];
            }
        }
        
        // Apply elbow hint if provided (constrains elbow to a plane)
        if (elbowHint != null)
        {
            ApplyElbowHint(rootPos, targetPosition);
        }

        return chain;
    }

    private void ApplyElbowHint(Vector3 rootPos, Vector3 targetPos)
    {
        // Create plane through root, target, and hint point
        Vector3 hintPos = elbowHint.position;
        Plane hintPlane = new Plane(hintPos, rootPos, targetPos);
        
        // Project elbow onto this plane
        Vector3 elbowProjected = hintPlane.ClosestPointOnPlane(chain[1]);
        
        // Maintain proper distance from shoulder
        Vector3 shoulderToElbow = (elbowProjected - rootPos).normalized * upperArmLength;
        chain[1] = rootPos + shoulderToElbow;
        
        // Adjust wrist to maintain forearm length
        Vector3 elbowToWrist = (chain[2] - chain[1]).normalized * forearmLength;
        chain[2] = chain[1] + elbowToWrist;
    }

    public bool IsTargetReachable(Vector3 targetPosition)
    {
        if (shoulderOrigin == null) return false;
        float distance = Vector3.Distance(shoulderOrigin.position, targetPosition);
        return distance <= workspaceRadius;
    }

    public float GetWorkspaceRadius()
    {
        return workspaceRadius;
    }

    void OnDrawGizmos()
    {
        if (!showGizmos || !Application.isPlaying) return;
        
        if (shoulderOrigin == null) return;

        // Draw workspace sphere
        Gizmos.color = new Color(0, 1, 1, 0.1f);
        Gizmos.DrawWireSphere(shoulderOrigin.position, workspaceRadius);
        
        // Draw max reach sphere
        Gizmos.color = new Color(1, 0, 0, 0.1f);
        Gizmos.DrawWireSphere(shoulderOrigin.position, totalArmLength);

        // Draw IK chain
        if (chain != null && chain.Length > 0)
        {
            Gizmos.color = lastTargetWasReachable ? reachableColor : unreachableColor;
            
            // Draw bones
            for (int i = 0; i < chain.Length - 1; i++)
            {
                Gizmos.DrawLine(chain[i], chain[i + 1]);
                Gizmos.DrawSphere(chain[i], 0.015f);
            }
            Gizmos.DrawSphere(chain[chain.Length - 1], 0.02f);  // End effector larger
            
            // Draw segment labels in Scene view
            #if UNITY_EDITOR
            UnityEditor.Handles.Label(chain[0], "Shoulder");
            UnityEditor.Handles.Label(chain[1], "Elbow");
            UnityEditor.Handles.Label(chain[2], "Wrist");
            #endif
        }
        
        // Draw elbow hint
        if (elbowHint != null)
        {
            Gizmos.color = Color.yellow;
            Gizmos.DrawSphere(elbowHint.position, 0.02f);
            
            if (chain != null && chain.Length > 1)
            {
                Gizmos.DrawLine(chain[1], elbowHint.position);
            }
        }
    }

    void OnValidate()
    {
        // Ensure arm lengths stay reasonable
        if (upperArmLength < 0.05f) upperArmLength = 0.05f;
        if (forearmLength < 0.03f) forearmLength = 0.03f;
        
        // Recalculate when values change in editor
        if (Application.isPlaying)
        {
            totalArmLength = upperArmLength + forearmLength;
            workspaceRadius = totalArmLength * workspaceSafety;
        }
    }
}