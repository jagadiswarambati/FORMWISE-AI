"""Response-safe retention lifecycle audit recording."""

from datetime import datetime
from typing import Any

from formwise_document_core.privacy_models import PrivacyAuditEvent


class FirestoreRetentionAuditRecorder:
    def __init__(self, client: Any) -> None:
        self._client = client

    def policy_version_for_conversation(self, conversation_id: str) -> str | None:
        conversation = self._client.collection("conversations").document(conversation_id).get()
        if not conversation.exists:
            return None
        data = conversation.to_dict() or {}
        summary = data.get("privacySummary")
        if isinstance(summary, dict) and isinstance(summary.get("policyVersion"), str):
            return summary["policyVersion"]
        document_id = data.get("documentId")
        if not isinstance(document_id, str):
            return None
        document = self._client.collection("documents").document(document_id).get()
        document_data = document.to_dict() or {}
        policy_version = document_data.get("privacyPolicyVersion")
        return policy_version if isinstance(policy_version, str) else None

    def append_once(
        self,
        *,
        event_id: str,
        conversation_id: str,
        event_type: str,
        policy_version: str,
        timestamp: datetime,
        explanation_key: str,
    ) -> None:
        reference = self._client.collection("auditEvents").document(event_id)
        if reference.get().exists:
            return
        event = PrivacyAuditEvent(
            event_id=event_id,
            conversation_id=conversation_id,
            event_type=event_type,
            policy_version=policy_version,
            timestamp=timestamp,
            provider_id=None,
            processing_mode=None,
            actor_type="worker",
            explanation_key=explanation_key,
        )
        reference.create(event.model_dump(by_alias=True, mode="python"))
