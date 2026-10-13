"""
FastAPI REST API Server for MIA-Defense: Model Shadow Training & Membership Inference Risk Agent.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import MIADefenseCoordinator

coordinator = MIADefenseCoordinator()


def create_app():
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel, Field
        from agents.base import PHIGuard, SecurityException
        import json

        app = FastAPI(
            title="MIA-Defense: Model Shadow Training & Membership Inference Risk Agent",
            description="Trains shadow models to calculate precision-recall of Membership Inference Attacks (MIA) against healthcare diagnostic classifiers.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = Field(default=28.5, allow_inf_nan=False)
            secondary_metric: float = Field(default=14.2, allow_inf_nan=False)
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = {}

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "membership-inference-defense-agent", "domain": "Privacy-Preserving Federated Healthcare & FHE", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            try:
                for value in (req.task_id, req.target_identifier, req.status_descriptor):
                    PHIGuard.assert_no_phi(value)
                PHIGuard.assert_no_phi(json.dumps(req.attributes, ensure_ascii=False))
            except SecurityException:
                raise HTTPException(status_code=422, detail="Input contains a potentially sensitive identifier") from None
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            return coordinator.process(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
