import pioneer_sdk
import cv2
import numpy as np
import os

pioneer = pioneer_sdk.Pioneer()

classes = ('tank', 'rszo', 'noenemy')
indexes = []
cur_class = 0

for cls in classes:
    if f'Class_{cls}' not in os.listdir():
        os.mkdir(f'Class_{cls}')
    indexes.append(len(os.listdir(path=f'./Class_{cls}')))

while True:
    raw = pioneer.get_raw_video_frame()
    frame = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)

    k = cv2.waitKey(1)

    # quit
    if k == ord('q'):
        break

    # next
    if k == ord('n') and cur_class < len(classes)-1:
        cur_class += 1
    # prev
    if k == ord('p') and cur_class > 0:
        cur_class -= 1
    # add
    if k == ord('a'):
        indexes[cur_class] += 1
        cv2.imwrite(f'./Class_{classes[cur_class]}/{classes[cur_class]}_{indexes[cur_class]}.png', frame)
        print(f'Image added to class {classes[cur_class]}!!!')

    cv2.putText(frame, f'Current class is {classes[cur_class]}', (20, 450), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
                color=(0, 0, 255))
    cv2.putText(frame, f'Images in class: {indexes[cur_class]}', (20, 470), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
                color=(0, 0, 255))
    cv2.imshow("Frame", frame)

cv2.destroyAllWindows()