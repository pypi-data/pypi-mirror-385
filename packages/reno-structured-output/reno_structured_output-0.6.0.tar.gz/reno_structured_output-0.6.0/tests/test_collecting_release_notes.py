from reno_structured_output import collect_notes


def test_collect_notes_as_python_structure():
    notes = collect_notes()
    assert isinstance(notes, dict)
    assert "v0.0.2" in list(notes.keys())
