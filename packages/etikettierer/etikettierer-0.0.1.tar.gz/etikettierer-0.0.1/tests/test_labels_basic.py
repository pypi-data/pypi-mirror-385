import io
from etikettierer import create_label_image, ERROR_CORRECTION_MAP

def test_create_label_image_minimal():
    img = create_label_image("https://example.com/test", "Sample-1", ERROR_CORRECTION_MAP["M (15%) - Standard"])
    assert img is not None
    # basic size check
    assert img.size[0] == 762
    assert img.size[1] == 1000
