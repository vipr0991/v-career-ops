"""
Career-Ops Pipeline Manager & Long-Term Exclusion Memory
Handles persistent job tracking, deduplication, stages, document kit associations, and permanent exclusion memory.
"""
import os
import json
import time
import re
from typing import Dict, List, Optional, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PIPELINE_FILE = os.path.join(DATA_DIR, "pipeline_store.json")
EXCLUSIONS_FILE = os.path.join(DATA_DIR, "excluded_jobs.json")

os.makedirs(DATA_DIR, exist_ok=True)

STAGES = [
    "discovered",
    "evaluating",
    "scored",
    "pipeline_saved",
    "research_ready",
    "assets_generated",
    "outreach_active",
    "interviewing",
    "archived"
]

def normalize_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'[^a-z0-9]', '', str(text).lower())

class ExclusionStore:
    def __init__(self, storage_path: str = EXCLUSIONS_FILE):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(self.storage_path):
            self._save_data({"excluded": [], "updated_at": time.time()})

    def _load_data(self) -> Dict[str, Any]:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"excluded": [], "updated_at": time.time()}

    def _save_data(self, data: Dict[str, Any]):
        data["updated_at"] = time.time()
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_exclusion(self, company: str, title: str, url: str = "", reason: str = "User excluded") -> Dict[str, Any]:
        data = self._load_data()
        excluded = data.get("excluded", [])
        
        norm_company = normalize_text(company)
        norm_title = normalize_text(title)
        
        # Check if already excluded
        for item in excluded:
            if item.get("norm_company") == norm_company and item.get("norm_title") == norm_title:
                return item

        entry = {
            "id": f"excl-{int(time.time())}-{len(excluded)+1}",
            "company": company,
            "title": title,
            "url": url,
            "norm_company": norm_company,
            "norm_title": norm_title,
            "reason": reason,
            "excluded_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        excluded.insert(0, entry)
        self._save_data(data)
        return entry

    def is_excluded(self, company: str, title: str, url: str = "") -> bool:
        data = self._load_data()
        excluded = data.get("excluded", [])
        if not excluded:
            return False

        norm_c = normalize_text(company)
        norm_t = normalize_text(title)

        for item in excluded:
            ex_c = item.get("norm_company", "")
            ex_t = item.get("norm_title", "")
            
            # Exact or high-confidence match on company and title
            if ex_c and ex_t and ex_c == norm_c and ex_t == norm_t:
                return True
            # Match by URL if provided
            if url and item.get("url") and item.get("url") == url:
                return True
            # Company wildcard match if title matches strongly
            if ex_c and norm_c and (ex_c in norm_c or norm_c in ex_c) and ex_t == norm_t:
                return True

        return False

    def get_all(self) -> List[Dict[str, Any]]:
        data = self._load_data()
        return data.get("excluded", [])

    def remove_exclusion(self, item_id: str) -> bool:
        data = self._load_data()
        initial_len = len(data.get("excluded", []))
        data["excluded"] = [x for x in data.get("excluded", []) if x.get("id") != item_id]
        if len(data["excluded"]) < initial_len:
            self._save_data(data)
            return True
        return False

class PipelineManager:
    def __init__(self, storage_path: str = PIPELINE_FILE):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(self.storage_path):
            self._save_data({"items": [], "updated_at": time.time()})

    def _load_data(self) -> Dict[str, Any]:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"items": [], "updated_at": time.time()}

    def _save_data(self, data: Dict[str, Any]):
        data["updated_at"] = time.time()
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def generate_dedup_hash(self, company: str, title: str, location: str) -> str:
        norm_c = normalize_text(company)
        norm_t = normalize_text(title)
        norm_l = normalize_text(location.split(",")[0] if location else "")
        return f"{norm_c}_{norm_t}_{norm_l}"

    def get_all(self, stage: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
        data = self._load_data()
        items = data.get("items", [])
        if stage:
            items = [x for x in items if x.get("stage") == stage]
        if location:
            loc_norm = normalize_text(location)
            items = [x for x in items if loc_norm in normalize_text(x.get("location", ""))]
        return items

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        data = self._load_data()
        for item in data.get("items", []):
            if item.get("id") == item_id:
                return item
        return None

    def upsert_job(self, job_data: Dict[str, Any], auto_pipeline_threshold: float = 85.0) -> Dict[str, Any]:
        """
        Inserts or updates a job.
        Automatically sets stage to 'pipeline_saved' if score >= auto_pipeline_threshold.
        Deduplicates based on company, title, and location.
        """
        data = self._load_data()
        items = data.get("items", [])

        company = job_data.get("company", "Unknown Company")
        title = job_data.get("title") or job_data.get("job_title", "Unknown Role")
        location = job_data.get("location", "Dubai, UAE")
        dedup_key = self.generate_dedup_hash(company, title, location)

        # Check existing item
        existing_idx = None
        for idx, it in enumerate(items):
            if it.get("dedup_key") == dedup_key or it.get("id") == job_data.get("id"):
                existing_idx = idx
                break

        score = job_data.get("score")
        if isinstance(score, dict):
            score_val = score.get("overall_score", 0)
        elif isinstance(score, (int, float)):
            score_val = float(score)
        else:
            score_val = 0.0

        current_time = time.strftime("%Y-%m-%d %H:%M:%S")

        if existing_idx is not None:
            # Update existing
            existing = items[existing_idx]
            existing.update(job_data)
            existing["dedup_key"] = dedup_key
            existing["updated_at"] = current_time
            if score_val >= auto_pipeline_threshold and existing.get("stage") in ["discovered", "evaluating", "scored"]:
                existing["stage"] = "pipeline_saved"
            items[existing_idx] = existing
            self._save_data(data)
            return existing
        else:
            # Create new
            item_id = job_data.get("id") or f"job-{int(time.time())}-{len(items)+1}"
            stage = job_data.get("stage")
            if not stage:
                stage = "pipeline_saved" if score_val >= auto_pipeline_threshold else "discovered"

            new_item = {
                "id": item_id,
                "dedup_key": dedup_key,
                "title": title,
                "company": company,
                "location": location,
                "salary_range": job_data.get("salary_range", "Not Disclosed"),
                "url": job_data.get("url", ""),
                "source": job_data.get("source", "Direct Ingestion"),
                "description": job_data.get("description", ""),
                "score": job_data.get("score"),
                "stage": stage,
                "company_research": job_data.get("company_research"),
                "decision_makers": job_data.get("decision_makers", []),
                "tailored_resume_tex": job_data.get("tailored_resume_tex"),
                "tailored_resume_pdf": job_data.get("tailored_resume_pdf"),
                "presentation_deck": job_data.get("presentation_deck"),
                "linkedin_outreach": job_data.get("linkedin_outreach", {}),
                "created_at": current_time,
                "updated_at": current_time
            }
            items.insert(0, new_item)
            self._save_data(data)
            return new_item

    def update_stage(self, item_id: str, new_stage: str) -> Optional[Dict[str, Any]]:
        if new_stage not in STAGES:
            new_stage = "pipeline_saved"
        data = self._load_data()
        for it in data.get("items", []):
            if it.get("id") == item_id:
                it["stage"] = new_stage
                it["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self._save_data(data)
                return it
        return None

    def delete_item(self, item_id: str) -> bool:
        data = self._load_data()
        initial_len = len(data.get("items", []))
        data["items"] = [x for x in data.get("items", []) if x.get("id") != item_id]
        if len(data["items"]) < initial_len:
            self._save_data(data)
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Return summary metrics and stage counts across all pipeline jobs."""
        data = self._load_data()
        items = data.get("items", [])
        stage_counts = {s: 0 for s in STAGES}
        for it in items:
            st = it.get("stage", "discovered")
            stage_counts[st] = stage_counts.get(st, 0) + 1
        return {
            "total_jobs": len(items),
            "stages": stage_counts,
            "pipeline_saved": stage_counts.get("pipeline_saved", 0),
            "interviewing": stage_counts.get("interviewing", 0),
            "assets_generated": stage_counts.get("assets_generated", 0),
            "outreach_active": stage_counts.get("outreach_active", 0),
            "updated_at": data.get("updated_at")
        }

# Global Singleton Instances
pipeline_store = PipelineManager()
exclusion_store = ExclusionStore()
