# 🐦 터틀로 만든 플래피 버드 게임 (복원 버전)
# 조작: 스페이스=점프, P=일시정지, R=재시작, ESC=종료

import turtle as t
import random
import time

# ---------------------------
# ⚙️ 게임 기본 설정 (원래 비율로 복원)
# ---------------------------
WIDTH, HEIGHT = 420, 700
GROUND_H = 90
PIPE_W = 70
PIPE_GAP = 180
PIPE_SPEED = 3.6
SPAWN_MS = 1600
INITIAL_SPAWN_MS = 1300   # 두 번째 파이프 간격을 더 넓힘   # 두 번째 파이프 간격 여유롭게 조정
MAX_GAP_DELTA = 140
GRAVITY = -0.65  # 더 빠르게 하강하도록 중력 증가
FLAP_V = 8.5
MAX_FALL = -14   # 최대 낙하 속도도 소폭 증가
FPS = 50
FRAME_MS = int(1000 / FPS)
BIRD_R = 16

# ---------------------------
# 🧠 상태 변수
# ---------------------------
screen = t.Screen()
screen.title("Flappy Bird (turtle ver)")
screen.setup(WIDTH, HEIGHT)
screen.bgcolor("#86c5ee")
screen.tracer(0, 0)
screen.delay(0)

pen = t.Turtle(visible=False)
pen.hideturtle(); pen.up(); pen.speed(0)

hud = t.Turtle(visible=False)
hud.hideturtle(); hud.up(); hud.speed(0)

running = True
paused = False
alive = True
score = 0
best = 0
last_gap_y = None
time_last_spawn = 0

bird = {"x": -WIDTH * 0.25, "y": 80, "vy": 0.0}
pipes = []

# ---------------------------
# 🕹️ 제어 함수
# ---------------------------

def now_ms():
    return int(time.time() * 1000)

def reset_game():
    global pipes, bird, score, alive, paused, time_last_spawn, last_gap_y
    pipes = []
    bird = {"x": -WIDTH * 0.25, "y": 80, "vy": 0.0}
    score = 0
    alive = True
    paused = False
    time_last_spawn = now_ms()
    last_gap_y = None

    # 🔥 게임 시작 시 첫 파이프 바로 생성
    spawn_pipe()
    time_last_spawn = now_ms() - (SPAWN_MS - INITIAL_SPAWN_MS)

def flap():
    global bird
    if not alive:
        return
    bird["vy"] = FLAP_V

def toggle_pause():
    global paused
    if alive:
        paused = not paused

def restart():
    global best
    if not alive:
        best = max(best, score)
    reset_game()

def quit_game():
    global running
    running = False

# ---------------------------
# 🌿 파이프 함수
# ---------------------------

def spawn_pipe():
    global last_gap_y
    min_center = -HEIGHT//2 + 80 + PIPE_GAP//2
    max_center = HEIGHT//2 - GROUND_H - 60 - PIPE_GAP//2
    rnd = random.randint(min_center, max_center)
    if last_gap_y is None:
        gap_y = rnd
    else:
        lower = max(min_center, last_gap_y - MAX_GAP_DELTA)
        upper = min(max_center, last_gap_y + MAX_GAP_DELTA)
        if lower > upper:
            lower, upper = upper, lower
        gap_y = max(lower, min(upper, rnd))
    pipes.append({"x": WIDTH//2 + 40, "gap_y": gap_y, "passed": False})
    last_gap_y = gap_y

def update_pipes():
    for p in pipes:
        p["x"] -= PIPE_SPEED
    while pipes and pipes[0]["x"] < -WIDTH//2 - PIPE_W:
        pipes.pop(0)

# ---------------------------
# 🎯 물리 및 충돌
# ---------------------------

def update_bird():
    global alive
    bird["vy"] = max(bird["vy"] + GRAVITY, MAX_FALL)
    bird["y"] += bird["vy"]

    ceiling = HEIGHT//2 - 10
    ground_y = -HEIGHT//2 + GROUND_H

    if bird["y"] + BIRD_R > ceiling:
        bird["y"] = ceiling - BIRD_R
        bird["vy"] = 0
    if bird["y"] - BIRD_R < ground_y:
        bird["y"] = ground_y + BIRD_R
        alive = False

def check_collisions_and_score():
    global alive, score
    bx, by = bird["x"], bird["y"]

    for p in pipes:
        left = p["x"] - PIPE_W/2
        right = p["x"] + PIPE_W/2
        gap_top = p["gap_y"] + PIPE_GAP/2
        gap_bottom = p["gap_y"] - PIPE_GAP/2

        if not p["passed"] and bx > right:
            p["passed"] = True
            score += 1

        in_x = (bx + BIRD_R > left) and (bx - BIRD_R < right)
        hit_top = in_x and (by + BIRD_R > gap_top)
        hit_bottom = in_x and (by - BIRD_R < gap_bottom)
        if hit_top or hit_bottom:
            alive = False
            return

# ---------------------------
# 🎨 그리기 함수
# ---------------------------

def draw_rect(x, y, w, h, color):
    pen.up(); pen.goto(x - w/2, y - h/2)
    pen.down(); pen.color(color)
    pen.begin_fill()
    for _ in range(2):
        pen.forward(w); pen.left(90); pen.forward(h); pen.left(90)
    pen.end_fill(); pen.up()

def draw_circle(x, y, r, color):
    pen.up(); pen.goto(x, y - r)
    pen.setheading(0); pen.color(color)
    pen.down(); pen.begin_fill(); pen.circle(r); pen.end_fill(); pen.up()

def update_hud():
    banner = None
    if not alive:
        banner = (
            "GAME OVER\n"
            "R 키로 재시작\n"
            f"점수 {score}   최고기록 {max(best, score)}"
        )
    elif paused and alive:
        banner = "일시정지"

    hud.clear()
    hud.goto(0, HEIGHT/2 - 60)
    hud.color("white")
    hud.write(str(score), align="center", font=("Arial", 36, "bold"))
    if banner:
        hud.goto(0, 40)
        for line in banner.split("\n"):
            style = ("Arial", 20 if line == "일시정지" else 16, "bold" if "GAME OVER" in line else "normal")
            hud.write(line, align="center", font=style)
            hud.sety(hud.ycor() - 28)

def draw_scene():
    pen.clear()
    draw_rect(0, -HEIGHT/2 + GROUND_H/2, WIDTH, GROUND_H, "#e6d6a3")

    for p in pipes:
        top_h = HEIGHT/2 - (p["gap_y"] + PIPE_GAP/2)
        draw_rect(p["x"], (HEIGHT/2 - top_h/2), PIPE_W, top_h, "#39b64a")
        bot_h = (p["gap_y"] - PIPE_GAP/2) - (-HEIGHT/2 + GROUND_H)
        draw_rect(p["x"], (-HEIGHT/2 + GROUND_H) + bot_h/2, PIPE_W, bot_h, "#39b64a")

    draw_circle(bird["x"], bird["y"], BIRD_R, "#ffa64d")
    pen.color("#ffde3c"); pen.up(); pen.goto(bird["x"] + BIRD_R, bird["y"])
    pen.down(); pen.begin_fill()
    pen.goto(bird["x"] + BIRD_R + 12, bird["y"] + 5)
    pen.goto(bird["x"] + BIRD_R + 12, bird["y"] - 5)
    pen.goto(bird["x"], bird["y"])
    pen.end_fill(); pen.up()

    draw_circle(bird["x"] + 6, bird["y"] + 6, 4, "white")
    draw_circle(bird["x"] + 8, bird["y"] + 6, 2, "black")

    update_hud()
    screen.update()

# ---------------------------
# 🔁 메인 루프
# ---------------------------

def loop():
    global time_last_spawn, running
    if not running:
        t.bye(); return

    if not paused:
        if alive and now_ms() - time_last_spawn > SPAWN_MS:
            spawn_pipe(); time_last_spawn = now_ms()
        if alive:
            update_pipes()
        update_bird()
        check_collisions_and_score()

    draw_scene()
    screen.ontimer(loop, FRAME_MS)

# ---------------------------
# 🧭 키보드 입력
# ---------------------------

screen.listen()
screen.onkeypress(flap, "space")
screen.onkeypress(toggle_pause, "p")
screen.onkeypress(restart, "r")
screen.onkeypress(quit_game, "Escape")

# ---------------------------
# 🚀 시작
# ---------------------------
reset_game()
loop()
screen.mainloop()
