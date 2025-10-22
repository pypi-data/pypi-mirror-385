from __future__ import annotations

from app.code.ui.bootstrap import build_bootstrap_config


def test_bootstrap_contains_expected_panels() -> None:
    config = build_bootstrap_config()
    assert config["version"] == 1

    panel_ids = {panel["id"] for panel in config["panels"]}
    assert {"data-panel", "imaging-panel", "evidence-panel"} <= panel_ids

    data_panel = next(panel for panel in config["panels"] if panel["id"] == "data-panel")
    assert data_panel["tables"], "data panel should expose table previews"

    table_preview = data_panel["tables"][0]
    assert table_preview["rows"], "table preview rows should not be empty"
    assert table_preview["schema"], "table preview schema should be present"

    imaging_panel = next(panel for panel in config["panels"] if panel["id"] == "imaging-panel")
    assert imaging_panel["scenes"], "imaging panel should include demo scenes"
    assert any(
        action["label"] == "Send selection to Notebook" for action in imaging_panel["actions"]
    ), "imaging panel should expose notebook action"

    evidence_panel = next(panel for panel in config["panels"] if panel["id"] == "evidence-panel")
    assert evidence_panel["graph"] == {
        "nodes": [],
        "edges": [],
        "glyphs": [],
    }, "default evidence panel should expose an empty graph shell"
