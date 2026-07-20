from app.models.enums import GenerationStatus

ALLOWED_TRANSITIONS: dict[GenerationStatus, set[GenerationStatus]] = {
    GenerationStatus.queued: {GenerationStatus.running, GenerationStatus.cancelled},
    GenerationStatus.running: {
        GenerationStatus.succeeded,
        GenerationStatus.failed,
        GenerationStatus.cancelled,
    },
    GenerationStatus.succeeded: set(),
    GenerationStatus.failed: set(),
    GenerationStatus.cancelled: set(),
}


def can_transition(current: GenerationStatus, new: GenerationStatus) -> bool:
    return new in ALLOWED_TRANSITIONS.get(current, set())
