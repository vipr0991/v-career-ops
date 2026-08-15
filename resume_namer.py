"""
Career-Ops Resume Naming & Version Tracking Engine
Maintains sequence-based company versioning for tailored LaTeX and PDF resumes.

Format: [JobSequence].[Version]_[MyName]_[CompanyName]_Resume.[ext]
Examples:
- 1.1_Vinay_Acme_Resume.pdf
- 1.2_Vinay_Acme_Resume.pdf
- 2.1_Vinay_SAP_Resume.pdf
"""
import os
import json
import re
import time
from typing import Dict, Any, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SEQUENCES_FILE = os.path.join(DATA_DIR, "resume_sequences.json")
os.makedirs(DATA_DIR, exist_ok=True)

def sanitize_company_name(company: str) -> str:
    if not company:
        return "Company"
    words = re.findall(r'[a-zA-Z0-9]+', company)
    if not words:
        return "Company"
    clean_parts = []
    for w in words:
        if w.isupper() and len(w) <= 5:
            clean_parts.append(w)
        else:
            clean_parts.append(w.capitalize())
    return "".join(clean_parts)

class ResumeSequenceTracker:
    def __init__(self, storage_path: str = SEQUENCES_FILE):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(self.storage_path):
            self._save_data({
                "companies": {},
                "next_sequence": 1,
                "updated_at": time.time()
            })

    def _load_data(self) -> Dict[str, Any]:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"companies": {}, "next_sequence": 1, "updated_at": time.time()}

    def _save_data(self, data: Dict[str, Any]):
        data["updated_at"] = time.time()
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_or_create_sequence(self, company_name: str, is_update: bool = False) -> Tuple[int, int, str]:
        """
        Returns (sequence_number, version_number, sanitized_company_name).
        If company exists and is_update is True, increments version.
        If company is new, allocates next sequence number and sets version = 1.
        """
        clean_company = sanitize_company_name(company_name)
        comp_key = clean_company.lower()

        data = self._load_data()
        companies = data.get("companies", {})
        next_seq = data.get("next_sequence", 1)

        if comp_key in companies:
            comp_info = companies[comp_key]
            seq = comp_info.get("sequence", 1)
            ver = comp_info.get("current_version", 1)
            if is_update:
                ver += 1
                comp_info["current_version"] = ver
                comp_info["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                companies[comp_key] = comp_info
                data["companies"] = companies
                self._save_data(data)
            return (seq, ver, clean_company)
        else:
            seq = next_seq
            ver = 1
            companies[comp_key] = {
                "sequence": seq,
                "current_version": ver,
                "company_name": clean_company,
                "raw_name": company_name,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            data["companies"] = companies
            data["next_sequence"] = next_seq + 1
            self._save_data(data)
            return (seq, ver, clean_company)

    def generate_filename(
        self,
        company_name: str,
        extension: str = "pdf",
        candidate_name: str = "Vinay",
        is_update: bool = False
    ) -> str:
        """
        Builds standardized filename:
        [JobSequence].[Version]_[MyName]_[CompanyName]_Resume.[ext]
        Example: 1.1_Vinay_Acme_Resume.pdf
        """
        # Ensure candidate name has only valid characters
        cand_clean = candidate_name.split()[0] if candidate_name else "Vinay"
        seq, ver, comp_clean = self.get_or_create_sequence(company_name, is_update=is_update)
        ext = extension.lstrip(".")
        return f"{seq}.{ver}_{cand_clean}_{comp_clean}_Resume.{ext}"

resume_namer = ResumeSequenceTracker()
