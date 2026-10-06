from typing import TYPE_CHECKING
from ..config import ACCENT, ERROR, MUTED
from ..core.questions import table_questions
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
    ui.text(f"Привет, {app.profile.name}!", 70, 155, 36)
    ui.text("Выбери таблицу. Короткие раунды — большой прогресс.", 70, 220, 23, MUTED)
    for i, table in enumerate(range(2, 10)):
        x, y = 70 + (i % 4) * 245, 295 + (i // 4) * 125
        ui.button(f"×{table}", (x, y, 225, 100), lambda t=table: app.start_round(t), True)
    ui.button("Мой прогресс", (70, 575, 460, 70), lambda: app.navigate("progress"))
    ui.button("Сменить профиль", (560, 575, 460, 70), lambda: app.navigate("profiles"))
    ui.text("10 вопросов • 3 жизни • повторы сложных примеров", 70, 685, 22, MUTED)


def game(app: "Academy") -> None:
    ui, r = app.ui, app.round
    q, score = r.question, r.score
    ui.text(f"Таблица ×{r.table}   •   Вопрос {r.count}/10", 70, 150, 26)
    ui.text(f"Жизни: {score.lives}    Очки: {score.points}    Серия: {score.streak}", 70, 200, 23, ACCENT)
    ui.panel((70, 260, 950, 150))
    ui.text(f"{q.table} × {q.factor} = ?", 340, 292, 64)
    if r.answered:
        color = ACCENT if app.last_correct else ERROR
        message = "Верно! Отличная работа." if app.last_correct else f"Запомним: {q.table} × {q.factor} = {q.answer}"
        ui.text(message, 100, 460, 32, color)
        ui.button("Результат" if r.finished else "Дальше", (320, 565, 460, 76), app.advance, True)
        ui.text("Нажми Enter или пробел", 360, 665, 20, MUTED)
    else:
        for i, value in enumerate(r.options):
            ui.button(f"{i + 1}.   {value}", (70 + (i % 2) * 490, 455 + (i // 2) * 100, 460, 80), lambda v=value: app.answer(v))
        ui.text("Выбери ответ мышью или клавишами 1–4", 70, 695, 20, MUTED)


def result(app: "Academy") -> None:
    ui, score = app.ui, app.round.score
    ui.text("Раунд завершён!", 70, 155, 42)
    ui.text("Каждая попытка помогает запомнить больше.", 70, 220, 24, MUTED)
    ui.panel((70, 280, 950, 245))
    for i, label in enumerate([f"Верно: {score.correct}", f"Ошибок: {score.errors}", f"Очки: {score.points}", f"Лучшая серия: {score.best_streak}", f"Правильных ответов: {score.percentage}%"]):
        ui.text(label, 100 + (i % 2) * 455, 305 + (i // 2) * 70, 28)
    ui.button("Ещё раунд", (70, 575, 460, 75), lambda: app.start_round(app.round.table), True)
    ui.button("Главное меню", (560, 575, 460, 75), lambda: app.navigate("menu"))


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
