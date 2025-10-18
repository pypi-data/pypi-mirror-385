from labels import create_label_image, ERROR_CORRECTION_MAP
from PIL import Image

# Test data
eln_link = "https://example.com/eln/sample123"
sample_name = "Sample123"
error_level = ERROR_CORRECTION_MAP["M (15%) - Standard"]

# Create label
label_img = create_label_image(eln_link, sample_name, error_level)

if label_img:
    label_img.show()  # Opens the image in default viewer
    label_img.save("test_label_with_logo.png")
    print("Label created and saved as test_label_with_logo.png")
else:
    print("Label generation failed")
