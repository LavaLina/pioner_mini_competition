import cv2
import numpy as np
from lobe import ImageModel
from PIL import Image

import pioneer_sdk

pioneer = pioneer_sdk.Pioneer()

model = ImageModel.load('./zbee_onnx')

while True:
    raw = pioneer.get_raw_video_frame()
    frame = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    model_frame = Image.fromarray(frame_rgb)

    predictions = model.predict(model_frame)

    key = cv2.waitKey(1)

    if key == 27:  # esc
        print('esc pressed')
        cv2.destroyAllWindows()
        exit(0)

    cv2.putText(frame, f'Predicted class is {predictions.prediction}', (20, 450), cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5, color=(0, 0, 255))
    cv2.imshow("Frame", frame)

cv2.destroyAllWindows()
