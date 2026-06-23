# tests/test_tools.py
import pytest
from core.tools import search_company_documents, search_org_chart

def test_document_tool_retrieval():
    # Validates that the vector DB tool fetches data
    result = search_company_documents("Rust coding standards")
    assert "eng_handbook_v2.pdf" in result

def test_org_chart_traversal():
    # Validates graph traversal path
    result = search_org_chart("Rust")
    assert "Sarah" in result