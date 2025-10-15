using UnityEngine;

public class IKSolver : MonoBehaviour
{
    [Header("IK Chain Definition")]
    public Transform shoulderOrigin;
    public float upperArmLength = 0.2f;
    public float forearmLength = 0.2f;
    private float totalArmLength;

    [Header("Solver Parameters")]
    public int iterations = 10;
    public float tolerance = 0.01f;

    [Header("Joint References (for Debug)")]
    public Transform elbowHint;

    private Vector3[] chain;
    private float[] boneLengths;

    void Awake()
    {
        Initialize();
    }

    void Initialize()
    {
        chain = new Vector3[3]; 
        boneLengths = new float[2];
        boneLengths[0] = upperArmLength;
        boneLengths[1] = forearmLength;
        totalArmLength = upperArmLength + forearmLength;
    }

    public Vector3[] Solve(Vector3 targetPosition)
    {
        if (shoulderOrigin == null) return null;

        Vector3 rootPos = shoulderOrigin.position;
        float distanceToTarget = Vector3.Distance(rootPos, targetPosition);

        if (distanceToTarget > totalArmLength)
        {
            Vector3 direction = (targetPosition - rootPos).normalized;
            chain[0] = rootPos;
            chain[1] = rootPos + direction * upperArmLength;
            chain[2] = chain[1] + direction * forearmLength;
            return chain;
        }

        chain[0] = rootPos;
        chain[1] = (rootPos + (targetPosition - rootPos).normalized * upperArmLength);
        chain[2] = chain[1] + (targetPosition - chain[1]).normalized * forearmLength;

        for (int i = 0; i < iterations; i++)
        {
            if (Vector3.Distance(chain[chain.Length - 1], targetPosition) < tolerance) break;

            chain[chain.Length - 1] = targetPosition;
            for (int j = chain.Length - 2; j >= 0; j--)
            {
                Vector3 direction = (chain[j] - chain[j + 1]).normalized;
                chain[j] = chain[j + 1] + direction * boneLengths[j];
            }

            chain[0] = rootPos;
            for (int j = 1; j < chain.Length; j++)
            {
                Vector3 direction = (chain[j] - chain[j - 1]).normalized;
                chain[j] = chain[j - 1] + direction * boneLengths[j - 1];
            }
        }
        
        if (elbowHint != null)
        {
            Plane plane = new Plane(elbowHint.position, rootPos, targetPosition);
            chain[1] = plane.ClosestPointOnPlane(chain[1]);
        }

        return chain;
    }

    void OnDrawGizmos()
    {
        if (Application.isPlaying && chain != null && chain.Length > 0)
        {
            Gizmos.color = Color.cyan;
            Gizmos.DrawLine(chain[0], chain[1]);
            Gizmos.DrawLine(chain[1], chain[2]);
            Gizmos.color = Color.yellow;
            Gizmos.DrawSphere(chain[0], 0.03f);
            Gizmos.DrawSphere(chain[1], 0.03f);
            Gizmos.DrawSphere(chain[2], 0.03f);
        }
    }
}