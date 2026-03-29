import os
from ultralytics import YOLO
import cv2
import numpy as np
from tensorflow.keras.models import load_model


class ImageProcessor:

    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.model = YOLO(os.path.join(base_dir, "MODELS", "yolov8m.pt"))

        self.unet_model = load_model(
            os.path.join(base_dir, "MODELS", "unet_best_model_250_160_1024.h5"),
            compile=False
        )

        self.boxes = []
        self.labels = []

    def yolo(self, image):

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = self.model(image_rgb)
        result = results[0]

        self.boxes = result.boxes.xyxy.cpu().numpy()

        classes = result.boxes.cls.cpu().numpy().astype(int)

        self.labels = [self.model.names[i] for i in classes]

        for i in range(len(self.labels)):
            if self.labels.count(self.labels[i]) > 1:
                self.labels[i] = f"{i+1}_{self.labels[i]}"

        self.labels.append("Background")

        print(self.labels)

        return self.labels

    def Boxes(self, image, label):

        self.yolo(image)

        for box, lab in zip(self.boxes, self.labels):

            if lab == label:

                x1, y1, x2, y2 = map(int, box[:4])

                return [x1, y1, x2, y2]

        return None

    def unet(self, image, target_label):

        if target_label == "Background":
            return image

        input_data = cv2.resize(image, (160, 160))
        input_data = np.array(input_data, dtype=np.float32) / 255.0
        input_data = np.expand_dims(input_data, axis=0)

        unet_mask = self.unet_model.predict(input_data)

        pred_mask = np.argmax(unet_mask, axis=-1)
        pred_mask = np.squeeze(pred_mask)
        pred_mask = np.where(pred_mask > 0, 1, 0).astype(np.uint8)

        mask = pred_mask * 255

        mask = cv2.resize(mask, (image.shape[1], image.shape[0]))

        for label, box in zip(self.labels, self.boxes):

            if label == target_label:

                x1, y1, x2, y2 = map(int, box)

                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)

                object_mask = np.zeros(mask.shape, dtype=np.uint8)

                object_mask[y1:y2, x1:x2] = mask[y1:y2, x1:x2]

                result = cv2.inpaint(image, object_mask, 20, cv2.INPAINT_TELEA)

                return result

        return image
    
    def background_paint(self,img,color):

        input_data = cv2.resize(img, (160, 160))
        input_data = np.array(input_data, dtype=np.float32) / 255.0
        input_data = np.expand_dims(input_data, axis=0)

        unet_mask = self.unet_model.predict(input_data)

        hex_color = color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        color = (b,g,r)
        image = img
        pred_mask = np.argmax(unet_mask,axis=-1)
        pred_mask = np.squeeze(pred_mask)
        pred_mask = np.where(pred_mask>0,1,0).astype(np.uint8)
        mask = cv2.cvtColor(pred_mask * 255,cv2.COLOR_GRAY2BGR)
        resized_mask = cv2.resize(mask,(image.shape[1],image.shape[0]),interpolation=cv2.INTER_NEAREST)
        gray_mask = cv2.cvtColor(resized_mask, cv2.COLOR_BGR2GRAY)
        blurred_mask = cv2.GaussianBlur(gray_mask, (35, 35), 0)
        alpha = blurred_mask.astype(float) / 255.0
        alpha = np.expand_dims(alpha, axis=2)

        bg = np.ones_like(image) * color

        painted = (alpha * image + (1 - alpha) * bg).astype(np.uint8)
        return painted


obj = ImageProcessor()