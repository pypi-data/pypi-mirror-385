import cv2
from ultralytics import YOLO
from PIL import Image
import numpy as np

def process_detections(image, model, confidence_threshold=0.8):
    # Initialize YOLO model
    # PIL.PngImagePlugin.PngImageFile
    # imageTestdata = cv2.imread("dataset/endScreenData/20241112_093434_image.png")
    # print (type(imageTestdata))
    
    if not isinstance(image, np.ndarray):
        # Check if image is a string (file path)
        # image = np.array(image)
        opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    else :
        opencvImage = cv2.imread(image)

    # Run YOLO detection
    results = model.predict(
        source=image,
        conf=confidence_threshold,
        verbose=False
        )
    detected = len(results[0].boxes) > 0    
    # Initialize flags and storage
    first_type_found = None
    second_type_boxes = []
    if detected:
        print(f"Detected {len(results[0].boxes)} objects in the image")
        # Process detections
        for r in results[0].boxes:
            class_id = int(r.cls[0])
            confidence = float(r.conf[0])
            box = r.xyxy[0].cpu().numpy()  # Get box coordinates
            
            # Check for first object type (assuming class_id 0)
            if class_id == 0:
                first_type_found = box
                print("First object type detected!")
            
            # Collect all instances of second object type (assuming class_id 1)
            elif class_id == 1:
                second_type_boxes.append(box)
        
        if second_type_boxes:
            print(f"Found {len(second_type_boxes)} instances of second object type")
        else:
            print("No instances of second object type found")
        
    return first_type_found, second_type_boxes

# Example usage
if __name__ == "__main__":
    image_path = "dataset/20241112_093434_image.png"
    model_path = "models/detectTable/weights/best.pt"
    model = YOLO(model_path)
    first_found, second_boxes = process_detections(image_path, model)
    
    if not first_found:
        print("First object type not found in image")
    if not second_boxes:
        print("No instances of second object type found")