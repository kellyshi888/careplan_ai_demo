import structlog
from typing import Dict, Any, Optional
from datetime import datetime
import json


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

audit_logger = structlog.get_logger("careplan_audit")


async def audit_log(
    action: str,
    patient_id: Optional[str] = None,
    careplan_id: Optional[str] = None,
    reviewer_id: Optional[str] = None,
    approver_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
):
    """
    Log audit events for care plan operations
    
    Args:
        action: The action being performed (e.g., 'intake_submitted', 'careplan_generated')
        patient_id: Patient identifier
        careplan_id: Care plan identifier
        reviewer_id: Clinician reviewer identifier
        approver_id: Final approver identifier
        details: Additional context and metadata
        user_id: User performing the action
        session_id: Session identifier for request tracking
    """
    
    audit_entry = {
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
        "patient_id": patient_id,
        "careplan_id": careplan_id,
        "reviewer_id": reviewer_id,
        "approver_id": approver_id,
        "user_id": user_id,
        "session_id": session_id,
        "details": details or {}
    }
    
    # Remove None values to keep logs clean
    audit_entry = {k: v for k, v in audit_entry.items() if v is not None}
    
    audit_logger.info("audit_event", **audit_entry)


class AuditMiddleware:
    """FastAPI middleware for automatic audit logging"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Extract request information
            method = scope["method"]
            path = scope["path"]
            
            # Start timing
            start_time = datetime.utcnow()
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    end_time = datetime.utcnow()
                    duration_ms = (end_time - start_time).total_seconds() * 1000
                    
                    # Log API request
                    await audit_log(
                        action="api_request",
                        details={
                            "method": method,
                            "path": path,
                            "status_code": status_code,
                            "duration_ms": round(duration_ms, 2)
                        }
                    )
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


def get_audit_summary(
    patient_id: Optional[str] = None,
    careplan_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Generate audit summary for compliance reporting
    
    This would typically query a logging database or service
    """
    
    # Placeholder implementation
    # In production, this would query your logging infrastructure
    
    summary = {
        "report_generated": datetime.utcnow().isoformat(),
        "filters": {
            "patient_id": patient_id,
            "careplan_id": careplan_id,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "event_counts": {
            "intake_submitted": 0,
            "careplan_generated": 0,
            "careplan_reviewed": 0,
            "careplan_approved": 0,
            "careplan_sent_to_patient": 0,
            "api_requests": 0
        },
        "compliance_notes": [
            "All patient data access logged",
            "Care plan generation tracked with AI model versions",
            "Clinician review workflow documented",
            "Patient delivery confirmation recorded"
        ]
    }
    
    return summary


# Security event logging
async def security_audit_log(
    event_type: str,
    severity: str,
    description: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None
):
    """Log security-related events"""
    
    security_entry = {
        "event_type": event_type,
        "severity": severity,
        "description": description,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "ip_address": ip_address,
        "context": additional_context or {}
    }
    
    security_logger = structlog.get_logger("security_audit")
    security_logger.warning("security_event", **security_entry)


# Performance monitoring
async def performance_log(
    operation: str,
    duration_ms: float,
    success: bool,
    details: Optional[Dict[str, Any]] = None
):
    """Log performance metrics for monitoring"""
    
    perf_entry = {
        "operation": operation,
        "duration_ms": round(duration_ms, 2),
        "success": success,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {}
    }
    
    perf_logger = structlog.get_logger("performance")
    perf_logger.info("performance_metric", **perf_entry)