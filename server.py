from flask import Flask, request, jsonify

# Инициализация приложения Flask
app = Flask(__name__)

# Создание класса Server, для хранения функций и переменных веб-сервиса
class Server:
  action = 'landed' # Текущее состояние, по умолчанию "landed"
  buildings = [] # Список зданий на "карте"
  
  # Эндпоинт для обновления текущего состояния сервера
  @app.route('/action', methods=['POST'])
  def actPage():
    Server.action = request.json['action'] # Установка нового состояния из запроса
    return '' # Пустой ответ
  
  # Эндпоинт для получения текущего состояния и списка зданий
  @app.route('/buildings')
  def positionsPage():
    return [Server.action, Server.buildings] # Возвращает состояние и список зданий
  
  # Главная страница, генерирует HTML-код с интерфейсом
  @app.route('/')
  def actionPage():
    return '''
  <div style="text-align:center">
    <!-- Основной блок с отображением карты и кнопок управления -->
    <div style="display:flex; flex-direction:column;">
      
      <div id="map" style="position:relative; margin: auto">
        <!-- Карта, состоящая из ячеек -->
        <span style="position:absolute; left: -15px; bottom: -5px; font-size: 20px"> 0</span>
        
        <div id="building0" style="display:none; position:absolute; width:50px; height:50px; text-align:center;">
        </div>
        <div id="building1" style="display:none; position:absolute; width:50px; height:50px; text-align:center;">
        </div>
        <div id="building2" style="display:none; position:absolute; width:50px; height:50px; text-align:center;">
        </div>
        <div id="building3" style="display:none; position:absolute; width:50px; height:50px; text-align:center;">
        </div>
        <div id="building4" style="display:none; position:absolute; width:50px; height:50px; text-align:center;">
        </div>
        
      </div>
      
      
        
    </div>
    <div style="margin-top: 20px">
        <!-- Кнопки управления -->
        <button id="start-button" type="button" style="dislay:block; color:green">Start</button>
        <button id="stop-button" type="button" style="dislay:block; color:red">Stop</button>
        <button id="kill-button" type="button" style="dislay:block; color:red">Kill switch</button>
    </div>
    <span id="message"></span>
    <span id="buildings"></span>
  </div>

  <script>
    // Код JavaScript, управляющий отображением карты и обработкой кнопок
    
    // При загрузке страницы создаётся карта и запускается обновление зданий
    document.body.onload = () => {createMap(); setInterval(updateBuildings, 100);};
    
    // Обработчики для кнопок
    document.getElementById("start-button").addEventListener("click", startClick);
    document.getElementById("stop-button").addEventListener("click", stopClick);
    document.getElementById("kill-button").addEventListener("click", killClick);
    
    let startStatus = "''' + Server.action + '''"; // Хранит текущее состояние
    
    // Обновляет информацию о зданиях на карте
    function updateBuildings(){
      fetch("/buildings", {
        method: "GET",
        headers: {"Content-type": "application/json"}
      })
      .then(response => response.json())
      .then(json => {
        let bs = document.getElementById("buildings");
        bs.innerHTML = "";
        if(json[0] == "landed" && startStatus == "landing"){ // Обработка посадки
          startStatus = json[0];
          document.getElementById("start-button").style.color = "green";
          document.getElementById("stop-button").style.color = "red";
          document.getElementById("kill-button").style.color = "green";
          document.getElementById("message").innerHTML = "Landed";
        }
        for(let i = 0; i < json[1].length; i++){
          let b = document.getElementById("building" + i.toString());
          b.style.display = "block"
          b.style.left = json[1][i][0] * 50 + 2 * json[1][i][0] - 24
          b.style.bottom = json[1][i][1] * 50 + 2 * json[1][i][1] - 24
          b.style.background = (json[1][i][2] == "yellow"?"#e6db00":json[1][i][2])
          b.innerHTML = "<span style=\\"color:white\\">x: " + json[1][i][0] + "</span><br/><span style=\\"color:white\\">y: " + json[1][i][1] + "</span>";
          bs.innerHTML = bs.innerHTML + "<br/>" + (json[1][i][2]=="red"?"Администрация":(json[1][i][2]=="green"?"Лаборатория":(json[1][i][2]=="yellow"?"Шахта":"Здание для обогащения угля"))) + "; color: " + json[1][i][2] + "; x: " + json[1][i][0] + "; y: " + json[1][i][1];
        }
      });
    }
    
    // Создаёт карту (9x9 ячеек)
    function createMap() {
      let map = document.getElementById('map');
      document.getElementById("start-button").style.color = "'''+('green' if Server.action == 'landed' else 'red') + '''";
      document.getElementById("stop-button").style.color = "'''+('green' if Server.action == 'start' else 'red') + '''";
      document.getElementById("kill-button").style.color = "'''+('green' if Server.action != 'kill' else 'red') + '''";
      document.getElementById("message").innerHTML = "''' + ('Landed' if Server.action == 'landed' else ('Landing' if Server.action == 'landing' else ('Started' if Server.action == 'start' else 'Killed'))) + '''";

      for (let i = 0; i < 9; i++) {
        let row = document.createElement('div');
        row.style = 'display: flex; justify-content:center';
        for (let i = 0; i < 9; i++) {
          let col = document.createElement('div');
          col.style = 'width:50px; height:50px; border:solid 1px gray';
          row.appendChild(col);
        }
        map.appendChild(row);
      }
    }
    
    // Логика обработки кнопки "Start"
    function startClick() {
      if(startStatus == "start" || startStatus == "kill"|| startStatus == "landing"){
        return
      }
      fetch("/action", {
        method: "POST",
        body:JSON.stringify({action:"start"}),
        headers: {"Content-type": "application/json"}
      })
      document.getElementById("start-button").style.color = "red";
      document.getElementById("stop-button").style.color = "green";
      document.getElementById("kill-button").style.color = "green";
      document.getElementById("message").innerHTML = "Started";
      startStatus = "start";
    }
    
    // Логика обработки кнопки "Stop"
    function stopClick() {
      if(startStatus == "landed" || startStatus == "kill" || startStatus == "landing"){
        return
      }
      fetch("/action", {
        method: "POST",
        body:JSON.stringify({action:"landing"}),
        headers: {"Content-type": "application/json"}
      })
      document.getElementById("start-button").style.color = "red";
      document.getElementById("stop-button").style.color = "red";
      document.getElementById("kill-button").style.color = "red";
      document.getElementById("message").innerHTML = "Landing";
      startStatus = "landing";
    }
    
    // Логика обработки кнопки "Kill"
    function killClick() {
      if(startStatus == "kill" || startStatus == "landing"){
        return
      }
      fetch("/action", {
        method: "POST",
        body:JSON.stringify({action:"kill"}),
        headers: {"Content-type": "application/json"}
      })
      document.getElementById("start-button").style.color = "red";
      document.getElementById("stop-button").style.color = "red";
      document.getElementById("kill-button").style.color = "red";
      document.getElementById("message").innerHTML = "Killed";
      startStatus = "kill";
    }
    
  </script>
  '''
  
  # Метод для запуска сервера
  def start():
    app.run(host='0.0.0.0', port='4000') # Сервер доступен на порту 4000
