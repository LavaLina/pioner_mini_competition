.. pioner_mini_map_classification documentation master file, created by
   sphinx-quickstart on Wed Sep 14 09:40:54 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Создание карты полета квадрокоптера и обработка её классификатором
==================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Проект для квадрокоптера `Pioner Mini`_

.. _Pioner Mini: https://www.geoscan.aero/ru/pioneer-mini

Авторы проекта
----------------

**Выполнила**: Петелина Ярослава Андреевна (11 лет) ученица 6 класса ГБОУ г. Москвы

**Наставник**: Петелина Дарья Сергеевна, d.s.petelina@gmail.com

Описание проекта
----------------

* с помощью программы `Lobe`_ был обучен классификатор на три вида объектов: пусто, танк, РСЗО;
* полет квадрокоптера запрограммирован для облета прямоугольной территории по координатам;
* в параллельном потоке делает фотографии территории;
* после приземления все фото склеиваются в одну карту с помощью библиотеки `OpenCV`_ ;
* получившаяся карта делится на прямоугольники такой величины, чтобы на каждом куске было примерно по одному объекту;
* каждый кусок карты обрабатывается классификатором и подсчитывается количество классифицированных объектов.

Проект доступен на `GitHub`_

.. _GitHub: https://github.com/LavaLina/pioner_mini_competition

.. _Lobe:  https://www.lobe.ai/

.. _OpenCV: https://opencv.org/

Обучение и тестирование классификатора
--------------------------------------

Основной инструкцией для обучения послужил проект `Поиск вертолётных площадок`_

1. Создание датасета производилось, как описано в `проекте`_, но для трёх классов:

   * ничего не обнаружено (**noenemy**)
   * танк (**tank**)
   * РСЗО (**rszo**)

   .. image:: ../build/html/_static/media/noenemy.png
      :width: 200
   .. image:: ../build/html/_static/media/tank.png
      :width: 200
   .. image:: ../build/html/_static/media/rszo.png
      :width: 200
   
   .. image:: ../build/html/_static/media/creating_dataset.jpg
      :width: 610

.. _Поиск вертолётных площадок: https://docs.geoscan.aero/ru/master/learning-cases/parking-finder/parking_finder.html

.. _проекте: https://docs.geoscan.aero/ru/master/learning-cases/parking-finder/parking_finder.html#id9

2. Обучение классификатора на этом датасете в программе `Lobe`_:
   
   .. image:: ../build/html/_static/media/training_noenemy.png
      :width: 300
   .. image:: ../build/html/_static/media/training_tank.png
      :width: 300
   .. image:: ../build/html/_static/media/training_rszo.png
      :width: 300

   Пришлось немного дообучать вручную, чтобы добиться 100% верно предсказанных результатов:
   
     .. image:: ../build/html/_static/media/correct_training.jpg
        :width: 600
                
3. Полученная модель классификатора была добавлена в проект, а для её тестирования была написана небольшая программа:
   "Квадрокоптер в бесполетном режиме выдает видео поток, а все полученные из него изображения в реальном времени обрабатываются классификатором.
   Информация о классе обнаруженного на фото объекта, выводится красным текстом прямо на фрейме видео потока":

   .. image:: ../build/html/_static/media/model_in_project.jpg
      :width: 600
   

   .. code-block:: python

      import cv2
      import numpy as np
      from PIL import Image
      from lobe import ImageModel

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


   Результат работы программы:

      .. image:: ../build/html/_static/media/classification_test.jpg
         :width: 600

      .. image:: ../build/html/_static/media/rszo_classification.jpg
         :width: 600
      .. image:: ../build/html/_static/media/tank_classification.jpg
         :width: 600
      .. image:: ../build/html/_static/media/noenemy_classification.jpg
         :width: 600


Основная программа
------------------

* Программа выполняется в 2 потока: один поток отвечает за полёт по координатам,
  а другой – за фотографирование и сохранение изображений.

* Координация между потоками происходит с помощью обмена сообщениями:
  поток, отвечающий за полёт, прибыв в точку, посылает свои координаты второму
  потоку. Второй поток сохраняет изображение, полученное с камеры дрона в этот
  момент, указывая в имени файла координаты.

  .. image:: ../build/html/_static/media/program.jpg
     :width: 600

  .. code-block:: python

     if __name__ == '__main__':
         BaseManager.register('Pioneer', Pioneer)
         manager = BaseManager()
         manager.start()
         pioneer_mini = manager.Pioneer()
         pioneer_mini.arm()
         pioneer_mini.takeoff()
         
         buffer = mp.Queue(maxsize=1)
         
         photo_taker = mp.Process(target=take_photo, args=(buffer, pioneer_mini))
         flight_navigator = mp.Process(target=drone_control, args=(buffer, pioneer_mini))
         
         photo_taker.start()
         flight_navigator.start()
         
         photo_taker.join()
         flight_navigator.join()
         
         pioneer_mini.land()

  .. image:: ../build/html/_static/media/flight_and_photo.jpg
     :width: 600
         
Полёт по координатам
--------------------
  
  .. image:: ../build/html/_static/media/flight.jpg
     :width: 600


  .. code-block:: python

     #i = 0     1    2    3    4   5
     x = [0.0, 0.4, 0.4, 0.0, 0.0, 0]
     y = [0.5, 0.5, 0.7, 0.7, 0.5, 0]

     def drone_control(buff, drone):
         new_point = True

         i = 0

         command_x = x[i]
         command_y = y[i]
         command_z = float(1)
         command_yaw = math.radians(float(0))

         if buff.full():
             buff.get()

         buff.put([i])

         while True:
             if new_point:
                 print("Летим в точку ", command_x, ", ", command_y, ", ", command_z)
                 drone.go_to_local_point(x=command_x, y=command_y, z=command_z, yaw=command_yaw)
                 new_point = False

             key = cv.waitKey(1)
             if key == 27:
                 print('esc pressed')
                 pioneer_mini.land()

                 if buff.full():
                     buff.get()
                 buff.put(['end'])
                 break

             time.sleep(5)

             print("Достигнута точка ", command_x, ", ", command_y, ", ", command_z)

             if buff.full():
                 buff.get()
             buff.put([i])

             i = i + 1

             if i < len(x):
                 command_x = x[i]
                 command_y = y[i]
                 time.sleep(2)
                 new_point = True
             else:
                 drone.land()
                 if buff.full():
                     buff.get()
                 buff.put(['end'])
                 break

Фотографирование по координатам
-------------------------------

Точка B:

  .. image:: ../build/html/_static/media/frame0_0.0_0.5.jpg
     :width: 200
  .. image:: ../build/html/_static/media/B.jpg
     :width: 200             

Точка C:

  .. image:: ../build/html/_static/media/frame1_0.4_0.5.jpg
     :width: 200
  .. image:: ../build/html/_static/media/C.jpg
     :width: 200             

Точка D:

  .. image:: ../build/html/_static/media/frame2_0.4_0.7.jpg
     :width: 200
  .. image:: ../build/html/_static/media/D.jpg
     :width: 200             

Точка E:
             
  .. image:: ../build/html/_static/media/frame3_0.0_0.7.jpg
     :width: 200
  .. image:: ../build/html/_static/media/E.jpg
     :width: 200             

   
  .. code-block:: python
                  
     def take_photo(buff, drone):
         new_message = False
         while True:
             try:
                 frame = cv.imdecode(np.frombuffer(drone.get_raw_video_frame(), dtype=np.uint8),
                                        cv.IMREAD_COLOR)

                 if not buff.empty():
                     message = buff.get()
                     if len(message) == 1 and message[0] == 'end':
                         break
                     i = message[0]
                     new_message = True

                 if new_message:
                     name = "frame" + str(i) + "_" + str(x[i]) + "_" + str(y[i]) + ".jpg"
                     cv.imwrite(name, frame)

                     new_message = False

             except cv.error:
                 continue

             cv.imshow('pioneer_camera_stream', frame)

             key = cv.waitKey(1)
             if key == 27:
                 print('esc pressed')
                 drone.land()
                 break

Постобработка фотографий
------------------------

После полёта получается четыре изображения, которые склеиваются с помощью библиотеки `OpenCV`_ `cv.Stitcher`_:

   .. image:: ../build/html/_static/media/stitching.jpg
     :width: 800 


.. _cv.Stitcher: https://docs.opencv.org/4.x/d2/d8d/classcv_1_1Stitcher.html#a308a47865a1f381e4429c8ec5e99549f
    
  .. code-block:: python

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

Обработка карты по секторам с помощью классификатора
----------------------------------------------------

Склеенную карту разрезаем с помощью той же `OpenCV`_ на сектора и вызываем для каждого вырезанного фото классификатор.

   .. image:: ../build/html/_static/media/crop.jpg
     :width: 800 


.. code-block:: python

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


TODO: планируются улучшения проекта
-----------------------------------

1. Заменить разрезание карты на сектора на детектор объектов `YOLOv3`_ (уже частично реализовано).
2. Увеличить точность подсчета объектов на карте.
3. Усовершенствовать передвижение квадрокоптера по координатам, сейчас столкнулись с непониманием работы функции point_reached(blocking=False). При её использовании некоторые координатные точки пропускались, поэтому она была заменена на неэффективный time.sleep().

.. _YOLOv3: https://arxiv.org/pdf/1804.02767.pdf
