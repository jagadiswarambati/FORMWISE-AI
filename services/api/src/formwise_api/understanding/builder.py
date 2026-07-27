from datetime import datetime, timezone

from formwise_api.understanding.models import ConfidenceSummary, StructuredDocument, StructuredField, StructuredSection, StructuredTable, StructuredCheckbox, MissingField


class StructuredDocumentBuilder:
    def build(self, document_id: str, document_type: str, classification_confidence: float, sections: list[StructuredSection], fields: list[StructuredField], tables: list[StructuredTable], checkboxes: list[StructuredCheckbox], signature_status: str, missing_fields: list[MissingField], provider_version: str) -> StructuredDocument:
        by_section = {section.id: section for section in sections}
        for field in fields:
            if field.section_id in by_section:
                by_section[field.section_id].field_ids.append(field.id)
        field_confidence = sum(field.confidence for field in fields) / len(fields) if fields else classification_confidence
        table_confidence = sum(table.confidence for table in tables) / len(tables) if tables else 1.0
        checkbox_confidence = sum(item.confidence for item in checkboxes) / len(checkboxes) if checkboxes else 1.0
        overall = round((classification_confidence + field_confidence + table_confidence + checkbox_confidence) / 4, 3)
        return StructuredDocument(document_id=document_id, document_type=document_type, sections=sections, fields=fields, tables=tables, checkboxes=checkboxes, signature_status=signature_status, missing_fields=missing_fields, confidence_summary=ConfidenceSummary(overall=overall, fields=round(field_confidence, 3), tables=round(table_confidence, 3), checkboxes=round(checkbox_confidence, 3)), processing_status="completed", provider_version=provider_version, created_at=datetime.now(timezone.utc))
