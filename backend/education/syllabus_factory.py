from enum import Enum

class ResourceClass(Enum):
    OCW = "ocw"
    WHITEPAPER = "whitepaper"
    DOCUMENTATION = "documentation"
    MEDIA = "media"

DEFAULT_EDU_HEURISTICS = {
    ResourceClass.OCW: (
        "Isolate lecture notes and assignments addressing resource constraints, computational complexity, "
        "and architectural patterns. Skip basic syntax or introductory programming lectures. "
        "Extract core theoretical invariants that map directly to enterprise systems."
    ),
    ResourceClass.WHITEPAPER: (
        "Identify the core problem, structural invariants, trade-offs, and horizontal scalability vector. "
        "Translate academic math notation into concrete execution paradigms (e.g., mapping mathematical matrices "
        "to vectorized hardware arrays or parallel threads)."
    ),
    ResourceClass.DOCUMENTATION: (
        "Filter out routine patch details. Focus strictly on breaking changes, memory allocation updates, "
        "threading enhancements, or newly stabilized high-performance primitives (e.g., modern C++ parallelism or Python zero-copy mechanisms)."
    ),
    ResourceClass.MEDIA: (
        "Bypass superficial tech influencer commentary, productivity hype, and listicles. Extract actionable "
        "production engineering insights, systemic infrastructure post-mortems, or deep technical architectural breakdowns."
    )
}

def expand_educational_intent(resource_type: str, user_directive: str = None) -> str:
    """
    Ensures the tracking agent focuses on core engineering rigor rather than surface-level definitions.
    """
    try:
        res_class = ResourceClass(resource_type.lower())
    except ValueError:
        res_class = ResourceClass.DOCUMENTATION

    base_heuristic = DEFAULT_EDU_HEURISTICS[res_class]
    
    if not user_directive or len(user_directive.strip()) < 15:
        return base_heuristic
        
    return f"{user_directive.strip()} Priority Framework: {base_heuristic}"
