import random  # Импортируем модуль random для генерации случайных чисел

# Список доступных цветов для зданий
colors = ['model://dronepoint_yellow',
          'model://dronepoint_red',
          'model://dronepoint_green',
          'model://dronepoint_blue']

# Список возможных позиций (координат) для размещения зданий
poss = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8),
        (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8),
        (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8),
        (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8),
        (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8),
        (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8),
        (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8)]

randPos = []   # Список для хранения случайно выбранных позиций зданий
randColor = [] # Список для хранения случайно выбранных цветов зданий

# Цикл для выбора случайных позиций и цветов для пяти зданий
for i in range(5):
    p = poss[random.randrange(len(poss))] # Выбор случайной позиции из списка
    poss.remove(p)                        # Удаление выбранной позиции из списка возможных
    randColor.append(colors[random.randrange(4)]) # Выбор случайного цвета и сохранения в список
    randPos.append(f"{p[0]} {p[1]}")     # Форматирование позиции в строку и сохрание в список

# Открытие файла для записи настроек мира
world = open('/home/clover/catkin_ws/src/clover/clover_simulation/resources/worlds/clover_aruco.world', 'w')

# Запись содержимого файла
world.write('''<?xml version="1.0" ?>
<sdf version="1.5">
  <world name="NTO">
    <include>
      <uri>model://sun</uri>
    </include>

    <include>
      <uri>model://parquet_plane</uri>
      <pose>0 0 -0.01 0 0 0</pose>
    </include>

    <include>
      <uri>model://aruco_cmit_txt</uri>
    </include>

    <include>
      <name>dronepoint_n1</name>
      <uri>{}</uri>
      <pose>{} 0 0 0 0</pose>
    </include>

    <include>
      <name>dronepoint_n2</name>
      <uri>{}</uri>
      <pose>{} 0 0 0 0</pose>
    </include>

    <include>
      <name>dronepoint_n3</name>
      <uri>{}</uri>
      <pose>{} 0 0 0 0</pose>
    </include>

    <include>
      <name>dronepoint_n4</name>
      <uri>{}</uri>
      <pose>{} 0 0 0 0</pose>
    </include>

    <include>
      <name>dronepoint_n5</name>
      <uri>{}</uri>
      <pose>{} 0 0 0 0</pose>
    </include>

    <scene>
      <ambient>0.8 0.8 0.8 1</ambient>
      <background>0.8 0.9 1 1</background>
      <shadows>false</shadows>
      <grid>false</grid>
      <origin_visual>false</origin_visual>
    </scene>
  
    <physics name='default_physics' default='0' type='ode'>
      <gravity>0 0 -9.8066</gravity>
      <ode>
        <solver>
          <type>quick</type>
          <iters>10</iters>
          <sor>1.3</sor>
          <use_dynamic_moi_rescaling>0</use_dynamic_moi_rescaling>
        </solver>
        <constraints>
          <cfm>0</cfm>
          <erp>0.2</erp>
          <contact_max_correcting_vel>100</contact_max_correcting_vel>
          <contact_surface_layer>0.001</contact_surface_layer>
        </constraints>
      </ode>
      <max_step_size>0.004</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>250</real_time_update_rate>
      <magnetic_field>6.0e-6 2.3e-5 -4.2e-5</magnetic_field>
    </physics>
  </world>
</sdf>

'''.format(
    randColor[0], randPos[0],   # Форматирование данных для первого здания
    randColor[1], randPos[1],   # Форматирование данных для второго здания
    randColor[2], randPos[2],   # Форматирование данных для третьего здания
    randColor[3], randPos[3],   # Форматирование данных для четвертого здания
    randColor[4], randPos[4]    # Форматирование данных для пятого здания
))

world.close() # Закрытие файла после записи
