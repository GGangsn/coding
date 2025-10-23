# 두 사람 반응속도 대결 (turtle)
# 한 컴퓨터에서 A(왼쪽) vs L(오른쪽) 키로 동시에 플레이
# 규칙: 화면이 초록색으로 바뀌면 자기 키를 가장 먼저 누르기!
#       선출발(빨간색일 때 누르면) 반칙으로 상대 득점
# 라운드: 기본 5선승제 (WIN_POINTS)
# 기록: 각 플레이어 최고 반응속도(ms) 파일에 저장(reaction_best.txt)

import turtle as t
import random
import time
import os

# ---------------------- 설정 ----------------------
WIN_POINTS = 5
MIN_WAIT_MS = 1200
MAX_WAIT_MS = 3000
BG_READY = "#86c5ee"   # 대기/안내 색
BG_WAIT  = "#e45757"   # 준비(대기) - 빨강 (누르면 반칙)
BG_GO    = "#39b64a"   # 시작 - 초록
FONT_BIG = ("Arial", 36, "bold")
FONT_MD  = ("Arial", 24, "bold")
FONT_SM  = ("Arial", 16, "normal")
SAVE_FILE = "reaction_best.txt"

# ---------------------- 화면 ----------------------
s = t.Screen()
s.title("두 명 반응속도 대결 (A vs L)")
s.setup(900, 500)
s.tracer(0, 0)
s.delay(0)
s.bgcolor(BG_READY)

# 메인 펜 / HUD / 버튼 펜
pen = t.Turtle(visible=False); pen.up(); pen.hideturtle(); pen.speed(0)
hud = t.Turtle(visible=False); hud.up(); hud.hideturtle(); hud.speed(0)
btn = t.Turtle(visible=False); btn.up(); btn.hideturtle(); btn.speed(0)

# 버튼 영역 (중앙 하단)
BTN = {"x": -130, "y": -60, "w": 260, "h": 80}

# ---------------------- 상태 ----------------------
state = {
    "round": 1,
    "p1_score": 0,
    "p2_score": 0,
    "ready": False,   # 초록불 상태
    "lock": True,     # 입력 잠금(라운드 전/후)
    "start_time": 0.0,
    "p1_best": None,  # ms
    "p2_best": None,
}

# 저장/불러오기
if os.path.exists(SAVE_FILE):
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            lines = [x.strip() for x in f if x.strip()]
        for line in lines:
            who, ms = line.split(":")
            ms = float(ms)
            if who == "P1":
                state["p1_best"] = ms
            elif who == "P2":
                state["p2_best"] = ms
    except Exception:
        pass

# ---------------------- 그리기 ----------------------
def draw_center(text, dy=0, font=FONT_MD, color="white"):
    pen.clear()
    pen.goto(0, dy)
    pen.color(color)
    pen.write(text, align="center", font=font)

def draw_hud(extra=""):
    hud.clear()
    hud.goto(0, 190)
    hud.color("white")
    hud.write(f"Round {state['round']} — 먼저 {WIN_POINTS}점!", align="center", font=FONT_SM)

    # 점수판
    hud.goto(0, 150)
    hud.write(f"P1(A) {state['p1_score']} : {state['p2_score']} P2(L)", align="center", font=FONT_BIG)

    # 최고 기록
    hud.goto(0, 110)
    p1b = f"{state['p1_best']:.0f}ms" if state['p1_best'] is not None else "-"
    p2b = f"{state['p2_best']:.0f}ms" if state['p2_best'] is not None else "-"
    hud.write(f"최고기록  P1: {p1b}   P2: {p2b}", align="center", font=FONT_SM)

    if extra:
        hud.goto(0, -180)
        hud.write(extra, align="center", font=FONT_SM)

    s.update()

def draw_button():
    """중앙 하단에 START 버튼을 그림."""
    btn.clear()
    x, y, w, h = BTN["x"], BTN["y"], BTN["w"], BTN["h"]
    btn.goto(x, y)
    btn.pendown()
    btn.pensize(3)
    btn.color("white")
    for _ in range(2):
        btn.forward(w); btn.left(90); btn.forward(h); btn.left(90)
    btn.penup()
    # 텍스트
    btn.goto(x + w/2, y + h/2 - 10)
    btn.write("START", align="center", font=FONT_MD)

def draw_start_screen():
    s.bgcolor(BG_READY)
    pen.clear(); hud.clear(); btn.clear()
    draw_center("두 명 반응속도 대결", dy=60, font=FONT_BIG)
    draw_center("A키=P1, L키=P2 | 초록일 때 먼저 누르기", dy=20, font=FONT_SM)
    draw_center("빨강일 때 누르면 반칙", dy=-5, font=FONT_SM)
    draw_button()
    draw_hud("시작하려면 버튼을 클릭하세요")
    s.update()

# ---------------------- 로직 ----------------------
def save_bests():
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            if state["p1_best"] is not None:
                f.write(f"P1:{state['p1_best']}\n")
            if state["p2_best"] is not None:
                f.write(f"P2:{state['p2_best']}\n")
    except Exception:
        pass

def new_round_banner(msg):
    s.bgcolor(BG_READY)
    draw_center(msg, dy=10, font=FONT_MD)
    draw_hud("A키=P1, L키=P2 | 반칙=빨강일 때 누름 | 시작=초록에서 먼저 누르기")

def schedule_go():
    # 랜덤 지연 후 시작 신호
    wait_ms = random.randint(MIN_WAIT_MS, MAX_WAIT_MS)
    s.ontimer(start_go, wait_ms)

def start_wait():
    state["ready"] = False
    state["lock"] = False
    s.bgcolor(BG_WAIT)
    draw_center("준비... (빨강일 때 누르면 반칙)", dy=10, font=FONT_MD)
    draw_hud()
    schedule_go()

def start_go():
    # 이미 누군가 반칙으로 라운드가 끝났다면 무시
    if state["lock"]:
        return
    state["ready"] = True
    state["start_time"] = time.perf_counter()
    s.bgcolor(BG_GO)
    draw_center("지금! (초록일 때 눌러!)", dy=10, font=FONT_MD)
    draw_hud()

def early_press(who):
    # 반칙 처리: 상대 득점
    if state["lock"]:
        return
    state["lock"] = True
    if who == "P1":
        state["p2_score"] += 1
        msg = "P1 반칙! → P2 득점"
    else:
        state["p1_score"] += 1
        msg = "P2 반칙! → P1 득점"
    end_round(msg)

def valid_press(who):
    if state["lock"] or not state["ready"]:
        return
    state["lock"] = True
    elapsed = (time.perf_counter() - state["start_time"]) * 1000.0
    if who == "P1":
        state["p1_score"] += 1
        if state["p1_best"] is None or elapsed < state["p1_best"]:
            state["p1_best"] = elapsed
    else:
        state["p2_score"] += 1
        if state["p2_best"] is None or elapsed < state["p2_best"]:
            state["p2_best"] = elapsed
    save_bests()
    end_round(f"{who} 승! 반응속도 {elapsed:.0f}ms")

def end_round(msg):
    # 승리 조건 체크
    if state["p1_score"] >= WIN_POINTS or state["p2_score"] >= WIN_POINTS:
        winner = "P1" if state["p1_score"] > state["p2_score"] else "P2"
        s.bgcolor(BG_READY)
        draw_center(f"🏆 {winner} 승리! 다시하려면 스페이스", dy=20, font=FONT_BIG)
        draw_hud(msg)
        state["lock"] = True
        return

    # 다음 라운드로
    state["round"] += 1
    new_round_banner(msg)
    s.ontimer(start_wait, 900)  # 라운드 간 짧은 인터벌

# ---------------------- 입력 ----------------------
def on_press_a():
    # P1
    if state["lock"]:
        return
    if not state["ready"]:
        early_press("P1")
    else:
        valid_press("P1")

def on_press_l():
    # P2
    if state["lock"]:
        return
    if not state["ready"]:
        early_press("P2")
    else:
        valid_press("P2")

def restart_match():
    # 스페이스로 전체 경기 리셋
    state.update({
        "round": 1,
        "p1_score": 0,
        "p2_score": 0,
        "ready": False,
        "lock": True,
        "start_time": 0.0,
    })
    new_round_banner("새 경기 시작!")
    s.ontimer(start_wait, 1000)

def on_click_start(x, y):
    # 버튼 영역 클릭 검출
    if BTN["x"] <= x <= BTN["x"] + BTN["w"] and BTN["y"] <= y <= BTN["y"] + BTN["h"]:
        btn.clear(); pen.clear()
        s.onclick(None)  # 클릭 핸들러 해제
        restart_match()

s.listen()
s.onkeypress(on_press_a, "a")
s.onkeypress(on_press_l, "l")
s.onkeypress(restart_match, "space")

# ---------------------- 시작 ----------------------
draw_start_screen()
s.onclick(on_click_start)

s.mainloop()
