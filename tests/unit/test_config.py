from tripmate.config import GEMINI_API_KEY, GEMINI_MODEL


def test_gemini_configuration():
    assert GEMINI_API_KEY is not None
    assert GEMINI_MODEL is not None