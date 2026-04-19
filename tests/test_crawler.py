from app.services.validation_service import validate_target_url

def test_validate_target_url_rejects_empty():
    ok, _ = validate_target_url("")
    assert ok is False