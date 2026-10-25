from app.models.schemas import CaseRecord, GemmaExtractionResult, UrgencyLevel


class PriorityService:
    """Keep urgency explainable: corroboration raises priority, never replaces safety."""

    SAFETY_TERMS = ("spark", "exposed wire", "fire", "smoke", "short circuit", "electric shock", "flood", "collapse")

    @classmethod
    def apply(cls, case: CaseRecord) -> None:
        score, level, reasons = cls.calculate(
            case.extraction,
            case.raw_complaint,
            case.corroborating_report_count,
            case.affected_people,
        )
        case.priority_score = score
        case.priority_level = level
        case.priority_reasons = reasons

    @classmethod
    def calculate(
        cls,
        extraction: GemmaExtractionResult,
        raw_text: str,
        corroborating_count: int,
        affected_people: int | None,
    ) -> tuple[int, UrgencyLevel, list[str]]:
        base = extraction.estimated_priority_score
        score = base
        reasons = [f"Base severity from structured triage: {base}/10."]
        text = raw_text.lower()
        is_safety_critical = extraction.detected_urgency == UrgencyLevel.CRITICAL or any(
            term in text for term in cls.SAFETY_TERMS
        )
        if is_safety_critical:
            score = max(score, 10)
            reasons.append("Immediate safety risk keeps this issue at critical priority, regardless of report count.")

        extra_reports = max(0, corroborating_count - 1)
        if extra_reports >= 9:
            score += 3
            reasons.append(f"{corroborating_count} corroborating reports add the maximum evidence boost.")
        elif extra_reports >= 4:
            score += 2
            reasons.append(f"{corroborating_count} corroborating reports increase operational urgency.")
        elif extra_reports >= 1:
            score += 1
            reasons.append(f"{corroborating_count} related reports provide corroborating evidence.")

        if affected_people is not None and affected_people >= 100:
            score += 2
            reasons.append(f"Estimated impact on {affected_people} people increases priority.")
        elif affected_people is not None and affected_people >= 20:
            score += 1
            reasons.append(f"Estimated impact on {affected_people} people increases priority.")

        score = min(10, max(1, score))
        level = (
            UrgencyLevel.CRITICAL if score >= 9 else
            UrgencyLevel.HIGH if score >= 7 else
            UrgencyLevel.MEDIUM if score >= 4 else
            UrgencyLevel.LOW
        )
        return score, level, reasons
