import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np
import math
from clover import srv
from std_srvs.srv import Trigger
from std_msgs.msg import String
from server import Server
from threading import Thread
from mavros_msgs.srv import CommandBool

# Инициализация сервера управления
server = Server

# Инициализация ROS-ноды
rospy.init_node('flight')

# Создание топика для публикации информации о зданиях
buildings = rospy.Publisher('/buildings', String, queue_size=1)

# Прокси для вызова сервисов Clover
get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
land = rospy.ServiceProxy('land', Trigger)
arming = rospy.ServiceProxy('mavros/cmd/arming', CommandBool)

# Создание объекта для преобразования изображений из ROS в OpenCV
bridge = CvBridge()

# Функция навигации с ожиданием достижения цели
def navigate_wait(x=0, y=0, z=0, yaw=float('nan'), speed=0.4, frame_id='', auto_arm=False, tolerance=0.2):
    navigate(x=x, y=y, z=z, yaw=yaw, speed=speed, frame_id=frame_id, auto_arm=auto_arm)

    while not rospy.is_shutdown():
        telem = get_telemetry(frame_id='navigate_target')
        if math.sqrt(telem.x ** 2 + telem.y ** 2 + telem.z ** 2) < tolerance:
            break
        rospy.sleep(0.2)


# Обработчик изображения для определения цвета зданий
def image_callback_color():
    img = bridge.imgmsg_to_cv2(rospy.wait_for_message('main_camera/image_raw', Image), 'bgr8') # Получение изображения
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # Преобразование изображения в HSV
    telemet = get_telemetry(frame_id='aruco_map') # Получение телеметрии для координат
    
    # Задание границ цветов для определения зданий
    red_high= (15, 255, 255)   
    red_low= (0, 240, 240)

    blue_high= (122, 255, 255)  
    blue_low= (110, 245, 245)

    green_high= (62, 255, 255)  
    green_low= (55, 247, 250)

    yellow_high= (35, 255, 255)  
    yellow_low= (25, 245, 250)
    
    # Создание масок для каждого цвета
    red_mask = cv2.inRange(img_hsv, red_low, red_high)
    blue_mask = cv2.inRange(img_hsv, blue_low, blue_high)
    green_mask = cv2.inRange(img_hsv, green_low, green_high)
    yellow_mask = cv2.inRange(img_hsv, yellow_low, yellow_high)
    
    # Определение цвета в центре изображения и публикация информации в топик и на веб-сервер
    if red_mask[119][159] == 255:
        server.buildings.append([round(telemet.x), round(telemet.y), 'red'])
        print("administration building; red at x: " + str(round(telemet.x)) + ", y: " + str(round(telemet.y)))    
        buildings.publish(data = ("administration building; red at x: " + str(round(telemet.x)) + ", y: " + str(round(telemet.y))))    

    elif blue_mask[119][159] == 255:
        server.buildings.append([round(telemet.x), round(telemet.y), 'blue'])
        print("coal enrichment building; blue at x: " + str(round(telemet.x)) + ", y: " + str(round(telemet.y)))
        buildings.publish(data = ("coal enrichment building; blue at x: " + str(round(telemet.x)) + ", y: " + str(round(telemet.y))))
    elif green_mask[119][159] == 255:
        server.buildings.append([round(telemet.x), round(telemet.y), 'green'])
        print("laboratory; green at x: " + str(round(telemet.x)) + ", y: " + str(round(telemet.y)))
        buildings.publish(data = ("laboratory; green at x: " + str(round(telemet.x)) + ", y: " + str(round(telemet.y))))
    elif yellow_mask[119][159] == 255:
        server.buildings.append([round(telemet.x), round(telemet.y), 'yellow'])
        print("entrance to the mine; yellow at x: " + str(round(telemet.x)) + ", y: " + str(round(telemet.y)))
        buildings.publish(data = ("entrance to the mine; yellow at x: " + str(round(telemet.x)) + ", y: " + str(round(telemet.y))))

# Проверка на остановку и возобновление полета
def checkStop():
    stoped = False
    if (server.action != 'start'):
        land() # Приземление, если полет остановлен
        stoped = True
        if(server.action == 'kill'): # Завершение программы, если команда "kill switch"
            print('Killed')
            exit()
        rospy.sleep(10)
        print('Disarmed, can start again')
        server.action = 'landed'
    while (server.action != 'start'): # Ожидание возобновления полета
        if(server.action == 'kill'): # Завершение программы, если команда "kill switch"
            print('Killed')
            exit()
        pass
    if (stoped): # Возобновление полета
        print('Started again')
        navigate(x=0, y=0, z=1.7, speed=0.5, frame_id='body', auto_arm=True)
        rospy.sleep(5)

# Основная функция управления дроном
def main():
    while (server.action != 'start'): # Ожидание возобновления полета
        if(server.action == 'kill'): # Завершение программы, если команда "kill switch"
            print('Killed')
            exit()
        pass
    # Начало полёта
    print('Start fly')
    navigate(x=0, y=0, z=1.7, speed=0.5, frame_id='body', auto_arm=True)
    rospy.sleep(7)
    teleme = get_telemetry(frame_id='aruco_map')
    startx = round(teleme.x)
    starty = round(teleme.y)

    # Сканирование территории
    for y1 in range(10): # Поочередное движение по сетке
        if y1 % 2==0:
            for x1 in range(10):
                checkStop()
                navigate_wait(x = x1, y = y1, z = 1.7, frame_id='aruco_map')
                rospy.sleep(1)
                image_callback_color()
                rospy.sleep(2)
        else:
            for x1 in range(9, -1, -1):
                checkStop()
                navigate_wait(x = x1, y = y1, z = 1.7, frame_id='aruco_map')
                rospy.sleep(1)
                image_callback_color()
                rospy.sleep(2)
                
    # Возврат на стартовую позицию
    x1, y1 = 0, 9
    while (x1 > startx or y1 > starty):
        x1 -= x1 > startx
        y1 -= y1 > starty
        checkStop()
        navigate_wait(x = x1, y = y1, z = 1.7, frame_id='aruco_map')
        rospy.sleep(1.5)
    
    land() # Приземление по завершении работы
    print('End program')
    exit()

# Запуск основной функции в отдельном потоке
th = Thread(target=main)
th.start()

# Запуск веб-сервиса
server.start()
