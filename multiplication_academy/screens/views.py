from typing import TYPE_CHECKING
from ..config import ACCENT, ERROR, MUTED
from ..core.questions import table_questions
from ..utils.space import PLANETS, COLORS
import pygame
if TYPE_CHECKING:
    from ..app import Academy


def profiles(app: "Academy") -> None:
    ui = app.ui
    ui.text("Выбери свой профиль", 70, 145, 32)
    start = app.profile_page * 6
    for i, p in enumerate(app.store.profiles[start:start + 6]):
        x, y = 70 + (i % 2) * 490, 205 + (i // 2) * 82
        ui.button(p.name, (x, y, 460, 62), lambda p=p: app.select_profile(p))
    if app.profile_page:
        ui.button("Назад", (70, 455, 180, 48), lambda: app.page(-1))
    if len(app.store.profiles) > start + 6:
        ui.button("Ещё профили", (780, 455, 250, 48), lambda: app.page(1))
    ui.text("Новый профиль — введи имя и нажми Enter", 70, 525, 23, MUTED)
    ui.panel((70, 570, 650, 64))
    ui.text(app.name_input + "|", 90, 584, 28)
    ui.button("Создать", (750, 570, 280, 64), app.create_profile, True)
    ui.text(app.notice, 70, 662, 18, ERROR)


def menu(app: "Academy") -> None:
    ui = app.ui
    ui.text(f"Капитан {app.profile.name}, к полёту!", 70, 150, 32)
    ui.text("Выбери планету. Верные ответы заряжают корабль.", 70, 202, 23, MUTED)
    for i, table in enumerate(range(2, 10)):
        x, y = 70 + (i % 4) * 245, 275 + (i // 4) * 130
        ui.button(f"×{table}   {PLANETS[i]}", (x, y, 225, 92), lambda t=table: app.start_round(t))
        pygame.draw.circle(ui.surface, COLORS[i], (x + 25, y + 20), 7)
        mastered = sum(app.profile.example(q.key).mastered for q in table_questions(table))
        ui.text(f"Изучено: {mastered * 10}%", x + 20, y + 98, 18, MUTED)
    ui.button("Мой прогресс", (70, 575, 460, 70), lambda: app.navigate("progress"))
    ui.button("Сменить капитана", (560, 575, 460, 70), lambda: app.navigate("profiles"))
    ui.text("10 вопросов • 3 щита • 3 верных подряд включают гипердрайв", 70, 685, 21, MUTED)


def game(app: "Academy") -> None:
    ui, r = app.ui, app.round
    q, score = r.question, r.score
    ui.text(f"Миссия ×{r.table}   •   Сектор {r.count}/10", 70, 150, 25)
    ui.text(f"Энергия: {score.points}    Серия: {score.streak}", 70, 195, 23, ACCENT)
    ui.panel((70, 245, 540, 125))
    expression = f"{q.table} × {q.factor} = ?"
    label = ui.font(56).render(expression, True, (239, 244, 255))
    ui.surface.blit(label, label.get_rect(center=(340, 307)))
    ui.text("ЩИТЫ", 70, 390, 20, MUTED)
    for i in range(3):
        pygame.draw.rect(ui.surface, ACCENT if i < score.lives else (61, 66, 91), (155 + i * 42, 390, 30, 24), border_radius=7)
    app.space.mission(ui, r.table, score.lives, score.streak)
    if r.answered:
        color = ACCENT if app.last_correct else ERROR
        points = score.points - app.previous_points
        message = f"+{points} энергии! " + ("Гипердрайв включён!" if score.streak >= 3 else "Курс верный!") if app.last_correct else f"Щит сработал! Запомним: {q.table} × {q.factor} = {q.answer}"
        ui.text(message, 70, 466, 27, color)
        ui.text("Летим дальше!" if app.last_correct else "Этот пример вернётся позже. Ты справишься!", 70, 514, 22, MUTED)
        ui.button("Итоги миссии" if r.finished else "Следующий сектор", (320, 575, 460, 76), app.advance, True)
        ui.text("Нажми Enter или пробел", 360, 680, 20, MUTED)
    else:
        for i, value in enumerate(r.options):
            ui.button(f"{i + 1}.   {value}", (70 + (i % 2) * 490, 455 + (i // 2) * 100, 460, 80), lambda v=value: app.answer(v))
        ui.text("Заряди двигатель: выбери ответ мышью или клавишами 1–4", 70, 695, 20, MUTED)


def result(app: "Academy") -> None:
    ui, score = app.ui, app.round.score
    arrived = score.lives > 0
    title = f"Планета {PLANETS[app.round.table - 2]} достигнута!" if arrived else "Возвращаемся на базу"
    ui.text(title, 70, 145, 36)
    ui.text("Отличный полёт, капитан!" if arrived else "Корабль в безопасности. Подзарядимся и попробуем ещё!", 70, 200, 23, MUTED)
    medals = 3 if score.correct == 10 else 2 if score.correct == 9 else 1 if arrived else 0
    for i in range(3):
        app.space.medal(ui.surface, 450 + i * 100, 270, i < medals)
    ui.panel((70, 325, 950, 215))
    for i, label in enumerate([f"Верно: {score.correct}", f"Ошибок: {score.errors}", f"Энергия: {score.points}", f"Лучшая серия: {score.best_streak}", f"Правильных ответов: {score.percentage}%"]):
        ui.text(label, 100 + (i % 2) * 455, 343 + (i // 2) * 60, 27)
    ui.button("Повторить полёт", (70, 585, 460, 75), lambda: app.start_round(app.round.table), True)
    ui.button("Выбрать планету", (560, 585, 460, 75), lambda: app.navigate("menu"))


def progress(app: "Academy") -> None:
    ui, p = app.ui, app.profile
    total = sum(p.example(q.key).mastered for t in range(2, 10) for q in table_questions(t))
    ui.text(f"Мой прогресс    •    освоено {round(total / 80 * 100)}%", 70, 135, 36)
    for i, table in enumerate(range(2, 10)):
        mastered = sum(p.example(q.key).mastered for q in table_questions(table))
        x, y = 70 + (i % 4) * 245, 205 + (i // 4) * 110
        ui.panel((x, y, 225, 90))
        ui.text(f"×{table}    {mastered * 10}%", x + 20, y + 17, 27, ACCENT)
        ui.text(f"Освоено {mastered} из 10", x + 20, y + 57, 18, MUTED)
    ui.text("Самые трудные примеры", 70, 445, 28)
    difficult = sorted(((k, s) for k, s in p.stats.items() if s.errors), key=lambda item: (item[1].errors / item[1].shown, item[1].errors), reverse=True)[:4]
    if not difficult:
        ui.text("Пока ошибок нет. Начни первый раунд!", 70, 495, 23, MUTED)
    for i, (key, stat) in enumerate(difficult):
        a, b = key.split("x")
        ui.text(f"{a} × {b} = {int(a) * int(b)}   •   ошибок: {stat.errors} из {stat.shown}", 70, 490 + i * 36, 23, MUTED)
    ui.button("Главное меню", (70, 665, 950, 60), lambda: app.navigate("menu"), True)

VIEWS = {"profiles": profiles, "menu": menu, "game": game, "result": result, "progress": progress}
