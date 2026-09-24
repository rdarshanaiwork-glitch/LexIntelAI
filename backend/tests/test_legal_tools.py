import pytest
from app.tools.legal_tools import LegalToolRegistry

def test_validate_citation_valid():
    res = LegalToolRegistry.validate_citation('18 U.S.C. § 1514A', 'Sarbanes-Oxley Act')
    assert res['is_valid'] is True
    assert res['confidence'] > 0.8
    assert res['status'] == 'SUPPORTED BY SOURCE'

def test_validate_citation_invalid():
    res = LegalToolRegistry.validate_citation('Fake Reporter 999', 'Imaginary Supreme Court Case')
    assert res['is_valid'] is False
    assert res['status'] == 'INSUFFICIENT EVIDENCE'

def test_compare_precedents():
    res = LegalToolRegistry.compare_precedents('Lawson v. FMR LLC', 'Contractor Whistleblower Dispute')
    assert 'comparison_points' in res
    assert 'analogous_ratio' in res

def test_extract_statutory_elements():
    text = 'Whoever intentionally accesses a protected computer without authorization shall be punished.'
    res = LegalToolRegistry.extract_statutory_elements('18 U.S.C. § 1030', text)
    assert 'elements' in res
    assert len(res['elements']) > 0

def test_assess_evidence_sufficiency():
    res = LegalToolRegistry.assess_evidence_sufficiency(['Delivery timestamps', 'Contract PDF'], ['Proof of special circumstances notice'])
    assert 'sufficiency_rating' in res
    assert 'critical_deficiencies' in res

def test_search_legal_knowledge():
    res = LegalToolRegistry.search_legal_knowledge('whistleblower retaliation contractor', top_k=2)
    assert isinstance(res, list)

def test_red_team_argument():
    res = LegalToolRegistry.red_team_argument('The liquidated damages clause is an unenforceable penalty.')
    assert 'counter_theories' in res
    assert len(res['counter_theories']) > 0
