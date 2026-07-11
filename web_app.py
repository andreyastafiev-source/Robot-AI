"""Web control panel for Robot AI."""
import atexit
import threading
import time
import io
import socket
from contextlib import asynccontextmanager

import cv2
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.responses import Response
import qrcode
from pydantic import BaseModel

from core import config
from robot.controller import RobotController
from robot.master_mission import MasterMission
from robot.mission import AnimalMission
from robot.obstacle_mission import ObstacleMission
from storage.photo_manager import PhotoManager
from vision.animals import analyze
from vision.camera import ESP32Camera
from vision.detector import AnimalDetector
from vision.obstacle import ObstacleDetector

COMMANDS = {"forward", "back", "left", "right", "stop"}
shutdown_event = threading.Event()

def find_robot_host():
    for host in ("robot-ai.local", config.DEFAULT_ROBOT_IP):
        try:
            ip = socket.gethostbyname(host)
            with socket.create_connection((ip, 80), timeout=0.4): return ip
        except OSError: pass
    return config.DEFAULT_ROBOT_IP

def local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Выбираем тот же сетевой адаптер, через который доступен робот,
        # а не VPN или служебную сеть.
        sock.connect((config.DEFAULT_ROBOT_IP, 80))
        return sock.getsockname()[0]
    except OSError: return "127.0.0.1"
    finally: sock.close()

ROBOT_HOST = find_robot_host()
MOBILE_URL = f"http://{local_ip()}:{config.WEB_PORT}"

class CommandBody(BaseModel):
    command: str

class ModeBody(BaseModel):
    mode: str

class Runtime:
    def __init__(self):
        self.camera = ESP32Camera(f"http://{ROBOT_HOST}:81/stream", config.CAMERA_FLIP,
                                  config.MAX_STREAM_BUFFER,
                                  config.CAMERA_RECONNECT_DELAY)
        self.robot = RobotController("http://" + ROBOT_HOST,
                                     config.COMMAND_TIMEOUT)
        self.detector = AnimalDetector(config.YOLO_MODEL, config.CONFIDENCE)
        self.photos = PhotoManager(str(config.ROOT / "photos"))
        obstacle = ObstacleDetector()
        animal_mission = AnimalMission(self.robot, self.photos, config)
        obstacle_mission = ObstacleMission(self.robot, obstacle, config)
        self.auto_mission = MasterMission(self.robot, animal_mission,
                                          obstacle_mission, obstacle)
        self.lock = threading.RLock()
        self.mode = "manual"
        self.manual_command = "stop"
        self.last_detection = None
        self.annotated_frame = None
        self.running = False
        self.worker = None
        self.cooldown_until = 0.0
        self.confirm_count = 0
        self.handling_animal = False
        self.last_heartbeat = time.monotonic()
        self.light_enabled = False

    def start(self):
        if self.running: return
        self.running = True; self.robot.stop(); self.camera.connect()
        self.worker = threading.Thread(target=self._process, daemon=True)
        self.worker.start()

    def stop(self):
        self.running = False
        self.robot.stop(); self.robot.light_off(); self.camera.stop()
        if self.worker and self.worker.is_alive(): self.worker.join(timeout=2)

    def set_mode(self, mode):
        if mode not in {"manual", "automatic"}: raise ValueError("bad mode")
        self.robot.stop()
        with self.lock:
            self.mode, self.manual_command = mode, "stop"

    def command(self, command):
        if command not in COMMANDS: raise ValueError("bad command")
        with self.lock:
            if self.mode != "manual": raise RuntimeError("manual mode required")
            # Повторное нажатие активного направления работает как Stop.
            if command != "stop" and command == self.manual_command:
                command = "stop"
            self.manual_command = command
            self.last_heartbeat = time.monotonic()
            busy = self.handling_animal
        if not busy: self.robot.send_command(command, force=command == "stop")

    def _animal_event(self, frame, animal):
        with self.lock: self.handling_animal = True
        try:
            self.robot.stop(); self.robot.light_on()
            time.sleep(config.LIGHT_SETTLE_DELAY)
            self.photos.save(frame, animal.name, animal.confidence)
        finally:
            self.robot.light_off()
            with self.lock:
                command = self.manual_command
                self.cooldown_until = time.monotonic() + config.MANUAL_DETECTION_COOLDOWN
                self.confirm_count = 0; self.handling_animal = False
            self.robot.send_command(command, force=command == "stop")

    def _process(self):
        interval = 1.0 / config.DETECTION_FPS
        last_frame_id, next_detection = -1, 0.0
        while self.running:
            frame_id, frame = self.camera.read_latest()
            now = time.monotonic()
            if frame is None or frame_id == last_frame_id or now < next_detection:
                time.sleep(0.01); continue
            last_frame_id, next_detection = frame_id, now + interval
            with self.lock:
                mode, cooldown = self.mode, self.cooldown_until
                heartbeat_age = now - self.last_heartbeat
                if (mode == "manual" and self.manual_command != "stop"
                        and heartbeat_age > config.WEB_WATCHDOG_TIMEOUT):
                    self.manual_command = "stop"
                    self.robot.stop()
            if mode == "manual" and now < cooldown:
                with self.lock: self.annotated_frame = frame
                continue
            try:
                result = self.detector.detect(frame)
                animal = analyze(result, config.CONFIDENCE)
                annotated = result.plot()
                detection = ({"name": animal.name,
                              "confidence": round(animal.confidence, 3)}
                             if animal.found else None)
                with self.lock:
                    self.last_detection, self.annotated_frame = detection, annotated
                if mode == "automatic":
                    self.auto_mission.update(frame, animal)
                elif animal.found:
                    self.confirm_count += 1
                    if self.confirm_count >= config.MANUAL_CONFIRM_FRAMES:
                        self._animal_event(frame, animal)
                else:
                    self.confirm_count = 0
            except Exception as error:
                print("Ошибка анализа:", error); time.sleep(0.2)

    def jpeg(self):
        # Видео всегда использует самый свежий кадр камеры. Раньше здесь
        # показывался result.plot(), обновлявшийся лишь с частотой YOLO (4 FPS),
        # из-за чего плавный поток выглядел зависшим.
        frame = self.camera.read()
        if frame is None:
            with self.lock:
                frame = (None if self.annotated_frame is None
                         else self.annotated_frame.copy())
        if frame is None: return None
        ok, data = cv2.imencode(".jpg", frame,
                               [cv2.IMWRITE_JPEG_QUALITY, config.JPEG_QUALITY])
        return data.tobytes() if ok else None

    def status(self):
        with self.lock:
            return {"mode": self.mode, "command": self.manual_command,
                    "detection": self.last_detection,
                    "cooldown": max(0, round(self.cooldown_until-time.monotonic(), 1)),
                    "camera_error": self.camera.last_error,
                    "light": self.light_enabled}

    def heartbeat(self):
        with self.lock: self.last_heartbeat = time.monotonic()

    def toggle_light(self):
        with self.lock: enabled = not self.light_enabled
        ok = self.robot.light_on() if enabled else self.robot.light_off()
        if ok:
            with self.lock: self.light_enabled = enabled
        return ok, self.light_enabled

    def request_shutdown(self):
        self.robot.stop()
        self.robot.light_off()
        threading.Timer(0.5, shutdown_event.set).start()

runtime = Runtime()

@asynccontextmanager
async def lifespan(app):
    runtime.start(); yield; runtime.stop()

app = FastAPI(title="Robot AI", lifespan=lifespan)

HTML = """<!doctype html><html lang='ru'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Robot AI</title><style>
body{font-family:system-ui;background:#10141c;color:#eef;margin:0;padding:20px}.grid{display:grid;grid-template-columns:minmax(320px,2fr) minmax(280px,1fr);gap:20px;max-width:1200px;margin:auto}.card{background:#1b2230;border-radius:14px;padding:16px}img{width:100%;border-radius:10px;background:#000}.modes,.controls{display:grid;gap:10px}.modes{grid-template-columns:1fr 1fr}.controls{grid-template-columns:repeat(3,1fr)}button{padding:16px;border:0;border-radius:10px;background:#34415a;color:white;font-size:16px;cursor:pointer}button.active{background:#1687ff}button.stop,button.shutdown{background:#c93838}.shutdown{width:100%;margin-top:18px}.wide{grid-column:1/4}.up{grid-column:2}.left{grid-column:1}.right{grid-column:3}.down{grid-column:2}.status{line-height:1.8}@media(max-width:760px){.grid{grid-template-columns:1fr}}</style></head><body><div class='grid'><div class='card'><img src='/video' alt='Видео'></div><div class='card'><h2>Robot AI</h2><div class='modes'><button id='manual' onclick="mode('manual')">Ручной</button><button id='automatic' onclick="mode('automatic')">Автоматический</button></div><h3>Управление</h3><div class='controls'><button class='up' onclick="cmd('forward')">▲ Вперёд</button><button class='left' onclick="cmd('left')">◀ Влево</button><button class='stop' onclick="cmd('stop')">■ Стоп</button><button class='right' onclick="cmd('right')">Вправо ▶</button><button class='down' onclick="cmd('back')">▼ Назад</button></div><h3>Состояние</h3><div class='status' id='status'></div><button class='shutdown' onclick='shutdownApp()'>⏻ Завершить программу</button></div></div><script>
async function post(url,data){let r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});if(!r.ok)alert(await r.text())}function cmd(c){post('/api/command',{command:c})}function mode(m){post('/api/mode',{mode:m})}async function shutdownApp(){if(confirm('Остановить робота и завершить программу?')){await post('/api/shutdown',{});document.body.innerHTML='<h2>Robot AI завершён. Эту вкладку можно закрыть.</h2>'}}async function refresh(){try{let s=await (await fetch('/api/status')).json();document.getElementById('manual').classList.toggle('active',s.mode==='manual');document.getElementById('automatic').classList.toggle('active',s.mode==='automatic');let d=s.detection?`${s.detection.name} (${Math.round(s.detection.confidence*100)}%)`:'не обнаружено';document.getElementById('status').innerHTML=`Режим: <b>${s.mode}</b><br>Команда: <b>${s.command}</b><br>Животное: <b>${d}</b><br>Пауза распознавания: ${s.cooldown} с<br>Камера: ${s.camera_error||'подключена'}`}catch(e){}}setInterval(refresh,500);setInterval(()=>post('/api/heartbeat',{}).catch(()=>{}),1000);refresh()</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def index():
    mobile = f"<div style='text-align:center'><p>Телефон: <b>{MOBILE_URL}</b></p><img src='/qr' style='width:150px;background:white;padding:8px'></div>"
    css = """<style>
    body{touch-action:manipulation}
    button{min-height:52px}
    @media(max-width:760px) and (orientation:portrait){
      body{padding:6px!important}.grid{display:flex!important;flex-direction:column;gap:6px!important}
      .card{padding:8px!important}button{min-height:56px;font-size:17px!important}
      .card:first-child img{max-height:42vh;object-fit:contain}
    }
    @media(max-width:1000px) and (orientation:landscape){
      body{padding:5px!important;overflow:auto}.grid{display:grid!important;
      grid-template-columns:minmax(0,62vw) minmax(280px,1fr)!important;gap:6px!important;
      max-width:none!important}.card{padding:7px!important}.card:first-child img{height:calc(100vh - 24px);
      object-fit:contain}.card:nth-child(2){max-height:calc(100vh - 24px);overflow:auto}
      h2{margin:2px 0 6px}h3{margin:8px 0 5px}button{min-height:44px;padding:7px!important}
    }
    </style>"""
    light = "<button id='light' style='width:100%;margin-top:10px' onclick='toggleLight()'>💡 Подсветка: выкл.</button>"
    script = "<script>async function toggleLight(){let r=await fetch('/api/light',{method:'POST'});let s=await r.json();if(!r.ok){alert(s.detail||'Ошибка');return}let b=document.getElementById('light');b.textContent='💡 Подсветка: '+(s.light?'вкл.':'выкл.');b.classList.toggle('active',s.light)}</script>"
    return HTML.replace("<button class='shutdown'", light + "<button class='shutdown'").replace("</body>", mobile + css + script + "</body>")

@app.get("/qr")
def qr():
    image = qrcode.make(MOBILE_URL); data = io.BytesIO()
    image.save(data, format="PNG")
    return Response(data.getvalue(), media_type="image/png")

def frames():
    delay = 1.0/config.VIDEO_FPS
    while runtime.running:
        data = runtime.jpeg()
        if data: yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"+data+b"\r\n"
        time.sleep(delay)

@app.get("/video")
def video(): return StreamingResponse(frames(), media_type="multipart/x-mixed-replace; boundary=frame")
@app.get("/api/status")
def status(): return runtime.status()
@app.post("/api/heartbeat")
def heartbeat(): runtime.heartbeat(); return {"ok": True}
@app.post("/api/light")
def light():
    ok, enabled = runtime.toggle_light()
    if not ok: raise HTTPException(503, "Робот не ответил")
    return {"ok": True, "light": enabled}
@app.post("/api/shutdown")
def shutdown(): runtime.request_shutdown(); return {"ok": True}
@app.post("/api/command")
def command(body: CommandBody):
    try: runtime.command(body.command); return {"ok": True}
    except (ValueError, RuntimeError) as error: raise HTTPException(409, str(error))
@app.post("/api/mode")
def mode(body: ModeBody):
    try: runtime.set_mode(body.mode); return {"ok": True}
    except ValueError as error: raise HTTPException(400, str(error))

if __name__ == "__main__":
    server = uvicorn.Server(uvicorn.Config(app, host=config.WEB_HOST,
                                           port=config.WEB_PORT))
    def watch_shutdown():
        shutdown_event.wait()
        server.should_exit = True
    threading.Thread(target=watch_shutdown, daemon=True).start()
    server.run()
