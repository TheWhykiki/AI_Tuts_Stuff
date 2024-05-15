from PIL import Image
import matplotlib.pyplot as plt

def show_image(image_path):
    img = Image.open(image_path)
    plt.imshow(img)
    plt.axis('off')
    plt.show()
    print(f"Image size: {img.size}, Image mode: {img.mode}")

# Pfade zu den hochgeladenen Bildern
image_path_1 = '../source-images-tests/orig/sample-1.png'
image_path_2 = '../source-images-tests/orig/sample-3.png'

# Zeige Bild 1
print("Details for sample-1.png")
show_image(image_path_1)

# Zeige Bild 2
print("Details for sample-3.png")
show_image(image_path_2)
