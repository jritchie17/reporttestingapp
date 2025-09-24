import importlib
from pathlib import Path


def test_generate_pdf_report_handles_textual_mismatches(monkeypatch, tmp_path):
    module = importlib.import_module("src.reporting.generate_pdf_report")
    module = importlib.reload(module)

    fixture_path = Path(__file__).parent / "fixtures" / "results_textual_mismatches.csv"
    monkeypatch.setattr(module, "RESULTS_CSV", str(fixture_path))

    output_html = tmp_path / "report.html"
    monkeypatch.setattr(module, "OUTPUT_HTML", str(output_html))

    def fake_chart(match_count, mismatch_count):
        chart_path = tmp_path / "chart.png"
        chart_path.write_bytes(b"")
        return str(chart_path)

    monkeypatch.setattr(module, "create_modern_pie_chart", fake_chart)

    module.main()

    assert output_html.exists(), "Expected PDF HTML output to be generated"
    html_content = output_html.read_text(encoding="utf-8")

    assert "Not Numeric" in html_content
    assert "Alpha" in html_content
    assert "Missing entry" in html_content
    assert "$1,000.00" in html_content
    assert "$500.00" in html_content
