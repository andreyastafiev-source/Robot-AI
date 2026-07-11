/*
  Проект: Автономный робот для поиска животных
  Файл: esp32_robot_car.ino
  Плата: Keyestudio KS5024 (ESP32-CAM AI-Thinker + L298N) — ТОЛЬКО штатный набор.

  Важно: никакой автономности здесь нет специально.
  ESP32 — это просто "руки и глаза" робота: крутит моторы по команде
  и стримит видео. Все решения (когда ехать, когда останавливаться,
  куда повернуть) принимает Python на компьютере (main.py) и присылает
  сюда простые HTTP-команды.

  Пины камеры и моторов — из официальной документации Keyestudio KS5024:
  https://docs.keyestudio.com/projects/KS5024/en/latest/docs/4WD%20Camera%20Robot%20Car.html
*/

#include "esp_camera.h"
#include <WiFi.h>
#include <ESPmDNS.h>
#include "esp_timer.h"
#include "img_converters.h"
#include "Arduino.h"
#include "fb_gfx.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "esp_http_server.h"

// ---------- Wi-Fi ----------
//Set “your_SSID” to your wifi name
const char* ssid = "RT-WiFi-A128";
//Set “your_PASSWORD” to your wifi passwords
const char* password = "UCuQezasxE";

// ---------- Камера (AI-Thinker, официальные пины KS5024) ----------
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

// ---------- Моторы (официальные пины KS5024 / L298N) ----------
#define MOTOR_R_PIN_1 14
#define MOTOR_R_PIN_2 15
#define MOTOR_L_PIN_1 13
#define MOTOR_L_PIN_2 12
#define FLASH_LED_PIN 4

int MOTOR_SPEED = 160; // 0-255, подберите под свою батарею

httpd_handle_t camera_httpd = NULL;
httpd_handle_t stream_httpd = NULL;

#define PART_BOUNDARY "123456789000000000000987654321"
static const char *_STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char *_STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char *_STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

void startCameraServer();

// ---------------------- Управление моторами ----------------------
// Логика уровней сигналов — как в официальной таблице "Motor Drive Logic" KS5024.

void motorForward() {
  analogWrite(MOTOR_R_PIN_1, 0);
  analogWrite(MOTOR_R_PIN_2, MOTOR_SPEED);
  analogWrite(MOTOR_L_PIN_1, MOTOR_SPEED);
  analogWrite(MOTOR_L_PIN_2, 0);
}

void motorBackward() {
  analogWrite(MOTOR_R_PIN_1, MOTOR_SPEED);
  analogWrite(MOTOR_R_PIN_2, 0);
  analogWrite(MOTOR_L_PIN_1, 0);
  analogWrite(MOTOR_L_PIN_2, MOTOR_SPEED);
}

void motorLeft() {
  analogWrite(MOTOR_R_PIN_1, 0);
  analogWrite(MOTOR_R_PIN_2, MOTOR_SPEED);
  analogWrite(MOTOR_L_PIN_1, 0);
  analogWrite(MOTOR_L_PIN_2, MOTOR_SPEED);
}

void motorRight() {
  analogWrite(MOTOR_R_PIN_1, MOTOR_SPEED);
  analogWrite(MOTOR_R_PIN_2, 0);
  analogWrite(MOTOR_L_PIN_1, MOTOR_SPEED);
  analogWrite(MOTOR_L_PIN_2, 0);
}

void motorStop() {
  analogWrite(MOTOR_R_PIN_1, 0);
  analogWrite(MOTOR_R_PIN_2, 0);
  analogWrite(MOTOR_L_PIN_1, 0);
  analogWrite(MOTOR_L_PIN_2, 0);
}

// ---------------------- HTTP: команды движения ----------------------
// Простые отдельные эндпоинты — Python вызывает их напрямую (requests.get),
// без какой-либо HTML-страницы с кнопками (она нам не нужна, управляет Python).

static esp_err_t forward_handler(httpd_req_t *req) {
  motorForward();
  return httpd_resp_send(req, "OK", HTTPD_RESP_USE_STRLEN);
}
static esp_err_t back_handler(httpd_req_t *req) {
  motorBackward();
  return httpd_resp_send(req, "OK", HTTPD_RESP_USE_STRLEN);
}
static esp_err_t left_handler(httpd_req_t *req) {
  motorLeft();
  return httpd_resp_send(req, "OK", HTTPD_RESP_USE_STRLEN);
}
static esp_err_t right_handler(httpd_req_t *req) {
  motorRight();
  return httpd_resp_send(req, "OK", HTTPD_RESP_USE_STRLEN);
}
static esp_err_t stop_handler(httpd_req_t *req) {
  motorStop();
  return httpd_resp_send(req, "OK", HTTPD_RESP_USE_STRLEN);
}
static esp_err_t light_on_handler(httpd_req_t *req) {
  digitalWrite(FLASH_LED_PIN, HIGH);
  return httpd_resp_send(req, "OK", HTTPD_RESP_USE_STRLEN);
}
static esp_err_t light_off_handler(httpd_req_t *req) {
  digitalWrite(FLASH_LED_PIN, LOW);
  return httpd_resp_send(req, "OK", HTTPD_RESP_USE_STRLEN);
}

// ---------------------- HTTP: видеопоток ----------------------

static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t *_jpg_buf = NULL;
  char *part_buf[64];

  res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if (res != ESP_OK) return res;

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      res = ESP_FAIL;
    } else {
      if (fb->format != PIXFORMAT_JPEG) {
        bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if (!jpeg_converted) res = ESP_FAIL;
      } else {
        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;
      }
    }
    if (res == ESP_OK) {
      size_t hlen = snprintf((char *)part_buf, 64, _STREAM_PART, _jpg_buf_len);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if (res == ESP_OK) res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    if (res == ESP_OK) res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));

    if (fb) {
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    } else if (_jpg_buf) {
      free(_jpg_buf);
      _jpg_buf = NULL;
    }
    if (res != ESP_OK) break;
  }
  return res;
}

static const char PROGMEM INDEX_HTML[] = R"rawliteral(
<html><head><title>Robot AI</title></head>
<body><h1>ESP32 Robot Car (командный режим)</h1>
<p>Видео: <a href="/stream">/stream</a></p>
<p>Команды (используются программой Python): /forward /back /left /right /stop</p>
</body></html>
)rawliteral";

static esp_err_t index_handler(httpd_req_t *req) {
  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, (const char *)INDEX_HTML, strlen(INDEX_HTML));
}

void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;
  config.max_uri_handlers = 8;

  httpd_uri_t index_uri   = {.uri="/", .method=HTTP_GET, .handler=index_handler, .user_ctx=NULL};
  httpd_uri_t forward_uri = {.uri="/forward", .method=HTTP_GET, .handler=forward_handler, .user_ctx=NULL};
  httpd_uri_t back_uri    = {.uri="/back", .method=HTTP_GET, .handler=back_handler, .user_ctx=NULL};
  httpd_uri_t left_uri    = {.uri="/left", .method=HTTP_GET, .handler=left_handler, .user_ctx=NULL};
  httpd_uri_t right_uri   = {.uri="/right", .method=HTTP_GET, .handler=right_handler, .user_ctx=NULL};
  httpd_uri_t stop_uri    = {.uri="/stop", .method=HTTP_GET, .handler=stop_handler, .user_ctx=NULL};
  httpd_uri_t light_on_uri  = {.uri="/light/on", .method=HTTP_GET, .handler=light_on_handler, .user_ctx=NULL};
  httpd_uri_t light_off_uri = {.uri="/light/off", .method=HTTP_GET, .handler=light_off_handler, .user_ctx=NULL};

  if (httpd_start(&camera_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(camera_httpd, &index_uri);
    httpd_register_uri_handler(camera_httpd, &forward_uri);
    httpd_register_uri_handler(camera_httpd, &back_uri);
    httpd_register_uri_handler(camera_httpd, &left_uri);
    httpd_register_uri_handler(camera_httpd, &right_uri);
    httpd_register_uri_handler(camera_httpd, &stop_uri);
    httpd_register_uri_handler(camera_httpd, &light_on_uri);
    httpd_register_uri_handler(camera_httpd, &light_off_uri);
  }

  config.server_port += 1;
  config.ctrl_port += 1;
  httpd_uri_t stream_uri = {.uri="/stream", .method=HTTP_GET, .handler=stream_handler, .user_ctx=NULL};
  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
  }
}

// ---------------------- setup / loop ----------------------

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  pinMode(MOTOR_R_PIN_1, OUTPUT);
  pinMode(MOTOR_R_PIN_2, OUTPUT);
  pinMode(MOTOR_L_PIN_1, OUTPUT);
  pinMode(MOTOR_L_PIN_2, OUTPUT);
  pinMode(FLASH_LED_PIN, OUTPUT);
  digitalWrite(FLASH_LED_PIN, LOW);

  Serial.begin(115200);
  Serial.setDebugOutput(false);

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_HVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x\n", err);
    return;
  }

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  if (MDNS.begin("robot-ai")) {
    MDNS.addService("http", "tcp", 80);
    Serial.println("mDNS: http://robot-ai.local");
  }
  Serial.print("Stream: http://");
  Serial.print(WiFi.localIP());
  Serial.println(":81/stream");
  Serial.print("Commands: http://");
  Serial.println(WiFi.localIP());

  startCameraServer();
}

void loop() {
  // Основной цикл пуст — вся логика в HTTP-callback'ах.
  // Никакой автономности на плате нет: все решения принимает Python.
}
