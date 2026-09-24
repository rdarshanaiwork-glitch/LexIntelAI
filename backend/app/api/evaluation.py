import os
import json
import logging
from fastapi import APIRouter, HTTPException
from app.evaluation.evaluator import LexIntelEvaluator

logger = logging.getLogger("lexintel.api.evaluation")
router = APIRouter(prefix="/evaluation", tags=["Evaluation"])
RESULTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "evaluation", "eval_results.json")


def _load() -> dict:
    if not os.path.exists(RESULTS_FILE):
        return LexIntelEvaluator().evaluate_all()
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/results")
async def get_evaluation_results():
    try:
        return _load()
    except Exception as e:
        logger.error("Error reading evaluation results: %s", e)
        raise HTTPException(status_code=500, detail="Failed to read evaluation results")


@router.get("/summary")
async def get_evaluation_summary():
    data = _load()
    return {k: v for k, v in data.items() if k not in {"scenario_breakdown", "agent_reliability"}}


@router.get("/cases")
async def get_evaluation_cases():
    return _load().get("scenario_breakdown", [])


@router.get("/agents")
async def get_evaluation_agents():
    return _load().get("agent_reliability", {})


@router.get("/requirements")
async def get_evaluation_requirements():
    return [{
        "id": row["id"],
        "title": row["title"],
        "independent": row["routing"]["requirements_met_independent"],
        "dependency_aware": row["routing"]["requirements_met_dependency_aware"],
        "expected_path": row["routing"]["expected_path"],
        "observed_path": row["routing"]["observed_path"],
    } for row in _load().get("scenario_breakdown", [])]


@router.get("/retrieval")
async def get_evaluation_retrieval():
    return [{"id": row["id"], **row["retrieval"]} for row in _load().get("scenario_breakdown", [])]


@router.get("/evidence")
async def get_evaluation_evidence():
    return [{"id": row["id"], **row["evidence"]} for row in _load().get("scenario_breakdown", [])]


@router.get("/trajectory")
async def get_evaluation_trajectory():
    return [{"id": row["id"], **row["trajectory"], "verdict": row.get("verdict")} for row in _load().get("scenario_breakdown", [])]


@router.post("/run")
async def run_evaluation():
    try:
        return LexIntelEvaluator().evaluate_all()
    except Exception as e:
        logger.exception("Error running evaluation suite")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")
