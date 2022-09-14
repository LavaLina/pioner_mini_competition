Проект для квадрокоптера [Pioneer Mini](https://www.geoscan.aero/ru/pioneer-mini)

Создание карты полета квадрокоптера и обработка её классификатором
==========================

Авторы проекта
----------------

Выполнила: Петелина Ярослава Андреевна (11 лет) ученица 6 класса ГБОУ г. Москвы 

Описание проекта
----------------

* с помощью программы [Lobe](https://www.lobe.ai/) был обучен классификатор на три вида объектов: пусто, танк, РСЗО;
* полет квадрокоптера запрограммирован для облета прямоугольной территории по координатам;
* в параллельном потоке делает фотографии территории;
* после приземления все фото склеиваются в одну карту с помощью библиотеки [OpenCV](https://opencv.org/);
* получившаяся карта делится на прямоугольники такой величины, чтобы на каждом куске было примерно по одному объекту;
* каждый кусок карты обрабатывается классификатором и подсчитывается количество классифицированных объектов.

![alt text](https://github.com/LavaLina/pioner_mini_competition/blob/main/docs/build/html/_images/correct_training.jpg?raw=true)

![alt text](https://github.com/LavaLina/pioner_mini_competition/blob/main/docs/build/html/_images/flight_and_photo.jpg?raw=true)

![alt text](https://github.com/LavaLina/pioner_mini_competition/blob/main/docs/build/html/_images/stitching.jpg?raw=true)

![alt text](https://github.com/LavaLina/pioner_mini_competition/blob/main/docs/build/html/_images/crop.jpg?raw=true)
