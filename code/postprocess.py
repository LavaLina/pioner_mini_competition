import cv2 as cv
import sys
from lobe import ImageModel
from PIL import Image

def stitching():
    print("Склейка началась...")
    imgs = []
    img_names = []

    name = 'frame'

    # i = 0     1    2    3    4   5
    x = [0.0, 0.4, 0.4, 0.0, 0.0, 0]
    y = [0.5, 0.5, 0.7, 0.7, 0.5, 0]

    for i in range(0, len(x)-2):
        file_name = name + str(i) + "_" + str(x[i]) + "_" + str(y[i]) + ".jpg"
        print(file_name)
        img_names.append(file_name)

    for img_name in img_names:
        print(img_name)
        img = cv.imread(cv.samples.findFile(img_name))
        if img is None:
            print("Невозможно прочесть изображение " + img_name)
            sys.exit(-1)
        imgs.append(img)

    stitcher = cv.Stitcher.create(cv.Stitcher_PANORAMA)
    status, full_map = stitcher.stitch(imgs)

    if status != cv.Stitcher_OK:
        print("Невозможно склеить изображения, код ошибки = %d" % status)
        sys.exit(-1)

    cv.imwrite('map.jpg', full_map)
    print("Склейка прошла успешно. Карта сохранена в %s!" % 'map.jpg')

    cv.imshow('Enemy map', full_map)
    cv.waitKey(-1)

def cropping_and_predict():
    tank_width = 60
    tank_height = 60

    cell_width = 3*tank_width
    cell_height = 3*tank_height

    image = cv.imread(cv.samples.findFile('map.jpg'))
    height, width = image.shape[:2]

    x = 0
    y = 0

    x_count = int(width / cell_width)
    cell_width = width // x_count

    y_count = int(height / cell_height)
    cell_height = height // y_count

    print(cell_width, ", ", cell_height)

    crop_imgs = []
    for i in range(1, width//cell_width + 1):
        print("X:", x, ":", (x + cell_width))
        y = 0
        for j in range(1, height//cell_height + 1):
            print("Y: ", y,":",(y + cell_height))
            crop_img = image[y:y+cell_height, x:x+cell_width]

            cv.imwrite("part" + str(i) + "_" + str(j) + ".jpg", crop_img)
            crop_imgs.append(crop_img)
            y = y + cell_height
        x = x + cell_width

    model = ImageModel.load('./zbee_onnx')

    i = 0
    tank_count = 0
    rszo_count = 0
    for crop_img in crop_imgs:
        frame_rgb = cv.cvtColor(crop_img, cv.COLOR_BGR2RGB)
        model_frame = Image.fromarray(frame_rgb)

        predictions = model.predict(model_frame)

        if predictions.prediction == 'Class_tank':
            tank_count = tank_count + 1
        if predictions.prediction == 'Class_rszo':
            rszo_count = rszo_count + 1

        cv.putText(crop_img, f'{predictions.prediction}', (0, 40), cv.FONT_HERSHEY_SIMPLEX,
                    fontScale=1, color=(0, 0, 255))
        cv.imshow(f'{predictions.prediction}.jpg', crop_img)

        cv.imwrite("Frame"+str(i)+".jpg", crop_img)
        i=i+1

        cv.waitKey(-1)

    print("Результат работы")
    print("Количество танков: ", tank_count)
    print("Количество ракетных установок: ", rszo_count)

if __name__ == '__main__':
    stitching()
    cropping_and_predict()