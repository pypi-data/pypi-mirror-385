# conftest.py
import os
import pytest
import pytesseract

@pytest.fixture(autouse=True)
def tesseract_env(monkeypatch):
    """
    Ensure that in every test:
     - TESSDATA_PREFIX points at conda’s share/tessdata
     - pytesseract.pytesseract.tesseract_cmd points at the conda binary
    """
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if not conda_prefix:
        pytest.skip("CONDA_PREFIX not set; skipping Tesseract-dependent tests")

    tessdata_dir = os.path.join(conda_prefix, "share", "tessdata")
    tesseract_bin = os.path.join(conda_prefix, "bin", "tesseract")

    # 1) env var so tesseract finds its language files
    monkeypatch.setenv("TESSDATA_PREFIX", os.path.dirname(tessdata_dir))
    # 2) point pytesseract at the correct binary
    monkeypatch.setenv("PATH", f"{os.path.join(conda_prefix, 'bin')}:{os.environ.get('PATH', '')}")
    pytesseract.pytesseract.tesseract_cmd = tesseract_bin

    # verify we can actually call it
    try:
        langs = pytesseract.get_languages()
    except pytesseract.TesseractError as e:
        pytest.skip(f"Tesseract not runnable in this env: {e}")

    yield
    # nothing to clean up
