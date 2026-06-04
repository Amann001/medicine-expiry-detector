import cv2
from pathlib import Path

image_path = Path(__file__).parent / "test_image.jpeg"

img = cv2.imread(str(image_path))

# rotate
img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

# enlarge 3x
img = cv2.resize(img, None, fx=3, fy=3)

# grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# sharpen
gray = cv2.GaussianBlur(gray, (0, 0), 3)
gray = cv2.addWeighted(gray, 1.5, gray, -0.5, 0)

output = Path(__file__).parent / "processed.jpeg"

cv2.imwrite(str(output), gray)

print("Saved:", output)