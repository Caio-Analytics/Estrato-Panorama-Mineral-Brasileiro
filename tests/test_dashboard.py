"""Boundary checks for data embedded into the offline HTML artifact."""
import json

import duckdb

from dashboard import build_dashboard as dashboard


def test_embedded_data_cannot_close_script(monkeypatch, tmp_path):
    dangerous = '</ScRiPt><script>alert(1)</script>'
    payload = {'label': dangerous, 'rows': []}
    monkeypatch.setattr(dashboard, 'build_dataset_payload', lambda *args, **kwargs: payload)
    monkeypatch.setattr(dashboard, 'build_cruzamento_payload', lambda con: {})
    database = tmp_path / 'test.duckdb'
    duckdb.connect(str(database)).close()
    result = dashboard.build_dashboard(tmp_path / 'dashboard.html', duckdb_path=database).read_text()
    embedded = result.split('const DATA = ', 1)[1].split(';\n</script>', 1)[0]
    assert '<' not in embedded
    assert json.loads(embedded)['bruta']['label'] == dangerous
    assert '__DATA_JSON__' not in result
    assert '__APP_JS__' not in result
