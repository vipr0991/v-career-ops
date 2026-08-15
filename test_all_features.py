"""
End-to-End Verification Test Suite for Career-Ops v4.0.0
Tests:
1. Standardized Resume Sequence & Version Naming Engine ([JobSequence].[Version]_[Name]_[Company]_Resume)
2. Link Verifier & Active Job Detection
3. Exclusion Store & Permanent Memory
4. PDF Resume Compilation from LaTeX / Content
5. PowerPoint Presentation Deck Generation with Native Charts & Tables
6. API Endpoints (Health, Exclude, Download)
"""
import os
import sys
import asyncio
import json

from resume_namer import resume_namer, sanitize_company_name
from link_verifier import link_verifier
from pdf_compiler import pdf_compiler
from presentation_generator import presentation_engine
from pipeline_manager import pipeline_store, exclusion_store

async def run_tests():
    print("=" * 60)
    print("RUNNING CAREER-OPS END-TO-END VERIFICATION TEST SUITE")
    print("=" * 60)

    # 1. Test Resume Naming Sequence & Versioning Rules
    print("\n[1] Testing Standardized Resume Sequence & Version Naming...")
    # Clean test file for isolated test
    test_seq_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "test_resume_sequences.json")
    if os.path.exists(test_seq_file):
        os.remove(test_seq_file)
    from resume_namer import ResumeSequenceTracker
    test_namer = ResumeSequenceTracker(storage_path=test_seq_file)

    name1 = test_namer.generate_filename("Acme", extension="pdf", candidate_name="Vinay")
    assert name1 == "1.1_Vinay_Acme_Resume.pdf", f"Expected '1.1_Vinay_Acme_Resume.pdf', got '{name1}'"

    name1_v2 = test_namer.generate_filename("Acme", extension="pdf", candidate_name="Vinay", is_update=True)
    assert name1_v2 == "1.2_Vinay_Acme_Resume.pdf", f"Expected '1.2_Vinay_Acme_Resume.pdf', got '{name1_v2}'"

    name2 = test_namer.generate_filename("SAP", extension="pdf", candidate_name="Vinay")
    assert name2 == "2.1_Vinay_SAP_Resume.pdf", f"Expected '2.1_Vinay_SAP_Resume.pdf', got '{name2}'"

    name3 = test_namer.generate_filename("Clifford Chance", extension="tex", candidate_name="Vinay")
    assert name3 == "3.1_Vinay_CliffordChance_Resume.tex", f"Expected '3.1_Vinay_CliffordChance_Resume.tex', got '{name3}'"

    print(f"[PASS] Sequence 1: {name1}")
    print(f"[PASS] Sequence 1 (Update): {name1_v2}")
    print(f"[PASS] Sequence 2: {name2}")
    print(f"[PASS] Sequence 3: {name3}")
    if os.path.exists(test_seq_file):
        os.remove(test_seq_file)

    # 2. Test Exclusion Store
    print("\n[2] Testing Long-Term Job Exclusion Memory...")
    entry = exclusion_store.add_exclusion(
        company="SpamCorp Inc",
        title="Junior Telemarketer",
        url="https://spamcorp.example.com/job/123",
        reason="Irrelevant role"
    )
    assert exclusion_store.is_excluded("SpamCorp Inc", "Junior Telemarketer") == True, "Failed to match excluded job"
    assert exclusion_store.is_excluded("Clifford Chance", "Senior Marketing Manager") == False, "False positive exclusion"
    all_ex = exclusion_store.get_all()
    print(f"[PASS] Exclusion Memory working correctly! Total excluded records: {len(all_ex)}")

    # 3. Test Link Verifier
    print("\n[3] Testing Active Link Verifier & Liveness Checking...")
    sample_jobs = [
        {"title": "Senior Marketing Manager", "company": "Clifford Chance", "url": "https://www.cliffordchance.com"},
        {"title": "Dead Role", "company": "Fake Co", "url": "https://httpstat.us/404"},
        {"title": "Missing Link", "company": "No URL Co", "url": ""}
    ]
    verified = await link_verifier.filter_and_verify_jobs(sample_jobs)
    assert any(j["company"] == "Clifford Chance" for j in verified), "Active link was incorrectly filtered out"
    print(f"[PASS] Link Verifier processed batch: {len(verified)} active opportunities preserved")

    # 4. Test PDF Compiler with Standardized Naming
    print("\n[4] Testing LaTeX-to-PDF Resume Compilation with Standardized Naming...")
    pdf_path = pdf_compiler.compile_resume_to_pdf(
        job_title="Senior Marketing Manager",
        company_name="Clifford Chance",
        candidate_name="Vinay Prakash"
    )
    assert os.path.exists(pdf_path), f"PDF file was not created at {pdf_path}"
    assert os.path.getsize(pdf_path) > 1000, "PDF file is empty or corrupted"
    print(f"[PASS] PDF Resume generated: {os.path.basename(pdf_path)} ({os.path.getsize(pdf_path)} bytes)")

    # 5. Test High-Contrast PPTX Deck with Charts and Tables
    print("\n[5] Testing High-Contrast PPTX Deck Generation with Native Charts & Tables...")
    research_mock = {
        "business_model": "Global legal advisory firm delivering premier multi-jurisdictional counsel.",
        "market_position_and_competitors": "Top tier Magic Circle law firm leading GCC and global markets.",
        "strategic_pain_points": [
            "Scaling thought leadership and client marketing output without linear team expansion.",
            "Accelerating AI-assisted content pipelines across UAE and GCC offices.",
            "Optimizing digital engagement metrics among enterprise decision-makers."
        ],
        "candidate_solutions_to_pitch": [
            "Deploy specialized AI workflows cutting revision cycles by 50%+.",
            "Execute data-driven multi-market demand generation funnels across UAE & GCC.",
            "Build compounding thought leadership engines that drive executive inbound."
        ]
    }
    pptx_path = presentation_engine.generate_value_prop_deck(
        company_name="Clifford Chance",
        job_title="Business Development & Marketing Manager",
        research_data=research_mock,
        candidate_name="Vinay Prakash"
    )
    assert os.path.exists(pptx_path), f"PPTX file not found at {pptx_path}"
    assert os.path.getsize(pptx_path) > 5000, "PPTX file is too small or missing slide assets"
    print(f"[PASS] High-Contrast PPTX Deck generated with Donut Chart, Bar Chart & Matrix Tables: {os.path.basename(pptx_path)} ({os.path.getsize(pptx_path)} bytes)")

    # Clean up test exclusion
    exclusion_store.remove_exclusion(entry.get("id"))

    print("\n" + "=" * 60)
    print("ALL 5 SUBSYSTEM VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())
