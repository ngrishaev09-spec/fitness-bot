import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,
    FSInputFile
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

# ============================================================
# НАСТРОЙКИ
# ============================================================
import os
TOKEN = os.environ.get('BOT_TOKEN')

bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

# ============================================================
# КАРТИНКИ (файлы в папке с bot.py)
# ============================================================
IMG = {
    'welcome': 'welcome.jpg',
    'goal': 'goal.jpg',
    'body': 'body.jpg',
    'inventory': 'inventory.jpg',
    'level': 'level.jpg',
    'time': 'time.jpg',
    'frequency': 'frequency.jpg',
    'restrictions': 'restrictions.jpg',
    'result': 'result.jpg',
}

# ============================================================
# СОСТОЯНИЯ
# ============================================================
class Quiz(StatesGroup):
    goal = State()
    body_type = State()
    inventory = State()
    level = State()
    time = State()
    frequency = State()
    restrictions = State()

# ============================================================
# ОПРОС
# ============================================================
QUESTIONS = {
    'goal': {
        'text': '🎯 <b>Какую вершину будем штурмовать?</b>\n\nВыбери свою главную цель:',
        'img': 'goal',
        'options': [
            ('🔥 Рельеф', 'Рельеф'),
            ('💪 Масса', 'Масса'),
            ('⚡ Сила', 'Сила'),
            ('🧘 Здоровье', 'Здоровье'),
        ]
    },
    'body_type': {
        'text': '🧐 <b>Как выглядит твоё тело сейчас?</b>\n\nБудь честен:',
        'img': 'body',
        'options': [
            ('🦴 Худой', 'Худой'),
            ('🏃 Обычный', 'Обычный'),
            ('🏋️ Плотный', 'Плотный'),
            ('⚖️ Лишний вес', 'Лишний вес'),
        ]
    },
    'inventory': {
        'text': '🧳 <b>Что у тебя есть дома?</b>\n\nКоврик есть во всех вариантах:',
        'img': 'inventory',
        'options': [
            ('🧘 Только коврик', 'kovrik'),
            ('🏋️ Только гантели', 'ganteli'),
            ('💪 Брусья/турник', 'turnik'),
            ('🏆 Всё есть', 'vse'),
        ]
    },
    'level': {
        'text': '📊 <b>Как часто ты тренируешься?</b>\n\nБудь честен:',
        'img': 'level',
        'options': [
            ('🍼 Начальный', 'Начальный'),
            ('⚡ Средний', 'Средний'),
            ('🔥 Продвинутый', 'Продвинутый'),
        ]
    },
    'time': {
        'text': '⏱️ <b>Сколько минут в день?</b>\n\nГовори как есть:',
        'img': 'time',
        'options': [
            ('⏱️ 15–20 мин', '15-20'),
            ('⏱️ 30–40 мин', '30-40'),
            ('⏱️ 45–60 мин', '45-60'),
            ('⏱️ 60+ мин', '60+'),
        ]
    },
    'frequency': {
        'text': '🗓️ <b>Сколько раз в неделю?</b>\n\nЛучше честно:',
        'img': 'frequency',
        'options': [
            ('2️⃣ 2 раза', '2'),
            ('3️⃣ 3 раза', '3'),
            ('4️⃣ 4–5 раз', '4-5'),
            ('🔥 Каждый день', '7'),
        ]
    },
    'restrictions': {
        'text': '🩺 <b>Есть травмы или ограничения?</b>\n\nМожно выбрать несколько:',
        'img': 'restrictions',
        'multi': True,
        'options': [
            ('❌ Спина', 'Спина'),
            ('❌ Колени', 'Колени'),
            ('❌ Плечи', 'Плечи'),
            ('❌ Шея', 'Шея'),
            ('✅ Ограничений нет', 'Нет'),
        ]
    }
}

# ============================================================
# УПРАЖНЕНИЯ
# ============================================================
EXERCISES = {
    'kovrik': {
        'Начальный': ['Приседания у стены (I)', '«Лодочка» (II)', 'Отжимания от стены (III)', 'Планка на коленях (кор)', 'Ягодичный мост (I)', 'Скручивания (кор)'],
        'Средний': ['Классические приседания (I)', '«Лодочка» вперёд (II)', 'Отжимания с колен (III)', 'Планка 30 сек (кор)', 'Выпады вперёд (I)', 'Скручивания за головой (кор)'],
        'Продвинутый': ['Приседания на одной ноге (I)', '«Лодочка» за головой (II)', 'Классические отжимания (III)', 'Планка с подъёмом ноги (кор)', 'Болгарские выпады (I)', 'Скручивания с подъёмом ног (кор)']
    },
    'ganteli': {
        'Начальный': ['Приседания с гантелями (I)', 'Румынская тяга (II)', 'Жим гантелей сидя (III)', 'Скручивания с гантелью (кор)', 'Ягодичный мост с гантелью (I)', 'Разведения лёжа (III)'],
        'Средний': ['Приседания с гантелями (I)', 'Румынская тяга (II)', 'Жим гантелей лёжа (III)', 'Скручивания за головой (кор)', 'Выпады с гантелями (I)', 'Тяга гантели в наклоне (III)'],
        'Продвинутый': ['Приседания на одной ноге (I)', 'Становая на одной ноге (II)', 'Жим с паузой (III)', 'Скручивания прямыми руками (кор)', 'Болгарские выпады (I)', 'Тяга с паузой (III)']
    },
    'turnik': {
        'Начальный': ['Приседания у стены (I)', 'Австралийские подтягивания (II)', 'Отжимания от стены (III)', 'Подъёмы ног в висе (кор)', 'Ягодичный мост (I)', 'Вис 20 сек'],
        'Средний': ['Классические приседания (I)', 'Подтягивания с резиной (II)', 'Отжимания с колен (III)', 'Подъёмы ног в висе (кор)', 'Выпады (I)', 'Отжимания на брусьях (III)'],
        'Продвинутый': ['Приседания на одной ноге (I)', 'Подтягивания (II)', 'Отжимания на брусьях (III)', 'Подъёмы ног до перекладины (кор)', 'Болгарские выпады (I)', 'Подтягивания узким хватом (III)']
    },
    'vse': {
        'Начальный': ['Приседания с гантелями (I)', 'Тяга гантели (II)', 'Жим гантелей (III)', 'Планка на коленях (кор)', 'Подтягивания с резиной (III)', 'Ягодичный мост (I)'],
        'Средний': ['Приседания с гантелями (I)', 'Тяга гантели (II)', 'Жим гантелей лёжа (III)', 'Подтягивания (III)', 'Планка (кор)', 'Выпады (I)'],
        'Продвинутый': ['Приседания на одной ноге (I)', 'Становая на одной ноге (II)', 'Подтягивания с весом (III)', 'Отжимания на брусьях с весом (III)', 'Подъёмы ног в висе (кор)', 'Болгарские выпады (I)']
    }
}

LOAD_PARAMS = {
    'Рельеф': {'Начальный': (2, '12–15', '45–60', '2/1/2/1'), 'Средний': (3, '15–20', '30–45', '1/0/1/0'), 'Продвинутый': (3, '15–20', '30', '1/0/1/0')},
    'Масса': {'Начальный': (3, '8–10', '60–90', '2/1/2/1'), 'Средний': (3, '10–12', '60', '2/1/2/1'), 'Продвинутый': (4, '8–12', '60–90', '2/1/2/1')},
    'Сила': {'Начальный': (3, '6–8', '90–120', '2/1/2/1'), 'Средний': (4, '5–6', '120', 'произвольный'), 'Продвинутый': (5, '4–6', '120–180', 'произвольный')},
    'Здоровье': {'Начальный': (2, '10–12', '60', '2/1/2/1'), 'Средний': (3, '10–15', '45–60', '2/1/2/1'), 'Продвинутый': (3, '12–15', '45', '2/1/2/1')},
}

TIME_EX = {'15-20': 3, '30-40': 4, '45-60': 5, '60+': 6}

SCHEDULE = {
    '2': 'ПН / ЧТ', '3': 'ПН / СР / ПТ',
    '4-5': 'ПН / ВТ / ЧТ / ПТ', '7': 'ПН / ВТ / СР / ЧТ / ПТ / СБ'
}

DIET = {
    'Рельеф': 'Дефицит 300–500 ккал. Белок 1,5–1,7 г/кг. Углеводы 3–5 г/кг.',
    'Масса': 'Профицит 300–500 ккал. Белок 1,5–1,7 г/кг. Углеводы 5–6 г/кг.',
    'Сила': 'Белок 1,5–1,7 г/кг. Углеводы 4–5 г/кг. Жиры 20–30%.',
    'Здоровье': 'Сбалансированно: белок 1,2 г/кг, углеводы 3–5 г/кг.'
}

CARDIO = {
    'Худой': 'Кардио 1–2 раза в неделю по 15–20 мин.',
    'Обычный': 'Кардио 2–3 раза в неделю по 20–30 мин.',
    'Плотный': 'Кардио 3–4 раза в неделю по 25–30 мин.',
    'Лишний вес': 'Кардио 4–5 раз в неделю по 30–40 мин.'
}

user_answers = {}

# ============================================================
# КЛАВИАТУРЫ
# ============================================================
def make_keyboard(step):
    q = QUESTIONS[step]
    buttons = [[InlineKeyboardButton(text=label, callback_data=f"{step}:{value}")] for label, value in q['options']]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def make_restrictions_keyboard(selected=None):
    if selected is None:
        selected = []
    buttons = []
    for label, value in QUESTIONS['restrictions']['options']:
        prefix = '✅ ' if value in selected else ''
        buttons.append([InlineKeyboardButton(text=prefix + label, callback_data=f"restrictions:{value}")])
    buttons.append([InlineKeyboardButton(text='➡️ Далее', callback_data='restrictions:done')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ============================================================
# ОТПРАВКА ВОПРОСА С КАРТИНКОЙ
# ============================================================
async def send_question(message, step, chat_id=None):
    q = QUESTIONS[step]
    img_file = IMG.get(q.get('img'))
    keyboard = make_restrictions_keyboard([]) if step == 'restrictions' else make_keyboard(step)

    if img_file:
        try:
            photo = FSInputFile(img_file)
            await bot.send_photo(chat_id=chat_id or message.chat.id, photo=photo, caption=q['text'], reply_markup=keyboard, parse_mode='HTML')
            return
        except Exception as e:
            print(f"Ошибка загрузки картинки {img_file}: {e}")

    await bot.send_message(chat_id=chat_id or message.chat.id, text=q['text'], reply_markup=keyboard, parse_mode='HTML')

# ============================================================
# СТАРТ
# ============================================================
@dp.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    user_answers[message.from_user.id] = {}
    await state.set_state(Quiz.goal)

    welcome_text = (
        '👋 <b>Привет!</b>\n\n'
        'Я подберу тебе персональную программу тренировок <b>по книге Сергея Струкова</b>.\n\n'
        'Ответь на 7 вопросов — и получишь план.\n\n'
        '🚀 <b>Поехали!</b>'
    )

    try:
        photo = FSInputFile(IMG['welcome'])
        await message.answer_photo(photo=photo, caption=welcome_text, parse_mode='HTML')
    except Exception:
        await message.answer(welcome_text, parse_mode='HTML')

    await asyncio.sleep(0.5)
    await send_question(message, 'goal')

# ============================================================
# ОБРАБОТКА ОТВЕТОВ
# ============================================================
@dp.callback_query()
async def process_callback(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    if ':' not in data:
        return
    step, value = data.split(':', 1)
    user_id = callback.from_user.id

    if step == 'restrictions':
        if value == 'done':
            await callback.message.edit_reply_markup(reply_markup=None)
            await callback.message.answer('⏳ Генерирую программу...')
            await generate_program(callback.message, user_id)
            return

        selected = user_answers.get(user_id, {}).get('restrictions', [])
        if value == 'Нет':
            selected = ['Нет']
        else:
            selected = [s for s in selected if s != 'Нет']
            if value in selected:
                selected.remove(value)
            else:
                selected.append(value)
        user_answers[user_id]['restrictions'] = selected
        await callback.message.edit_reply_markup(reply_markup=make_restrictions_keyboard(selected))
        await callback.answer()
        return

    user_answers[user_id][step] = value

    steps_order = ['goal', 'body_type', 'inventory', 'level', 'time', 'frequency', 'restrictions']
    idx = steps_order.index(step)

    if idx + 1 < len(steps_order):
        next_step = steps_order[idx + 1]
        await state.set_state(getattr(Quiz, next_step))
        try:
            await callback.message.delete()
        except Exception:
            pass
        await send_question(callback.message, next_step, chat_id=callback.message.chat.id)
    else:
        await callback.message.answer('⏳ Генерирую программу...')
        await generate_program(callback.message, user_id)

    await callback.answer()

# ============================================================
# ГЕНЕРАЦИЯ ПРОГРАММЫ
# ============================================================
async def generate_program(message, user_id):
    ans = user_answers.get(user_id, {})
    goal = ans.get('goal', 'Рельеф')
    body_type = ans.get('body_type', 'Обычный')
    inventory = ans.get('inventory', 'kovrik')
    level = ans.get('level', 'Начальный')
    time_min = ans.get('time', '30-40')
    frequency = ans.get('frequency', '3')
    restrictions = ans.get('restrictions', ['Нет'])

    sets, reps, rest, tempo = LOAD_PARAMS[goal][level]
    ex_count = TIME_EX[time_min]
    exercises = EXERCISES[inventory][level][:ex_count]
    schedule = SCHEDULE[frequency]
    inv_name = {'kovrik': 'Коврик', 'ganteli': 'Гантели', 'turnik': 'Брусья/турник', 'vse': 'Всё есть'}[inventory]

    restr_note = ''
    if restrictions and 'Нет' not in restrictions:
        restr_note = f"\n⚠️ <b>Учтены ограничения:</b> {', '.join(restrictions)}\n"

    text = f"🎉 <b>Твоя программа готова!</b>\n\n"
    text += f"🎯 Цель: <b>{goal}</b>\n"
    text += f"🧐 Телосложение: <b>{body_type}</b>\n"
    text += f"🧳 Инвентарь: <b>{inv_name}</b>\n"
    text += f"📊 Уровень: <b>{level}</b>\n"
    text += f"⏱️ Время: <b>{time_min} мин</b>\n"
    text += f"📅 Расписание: <b>{schedule}</b>\n"
    text += restr_note

    text += "\n🔥 <b>РАЗМИНКА (5–7 мин):</b>\n"
    text += "• Суставная гимнастика\n• Динамические упражнения\n• Дыхание\n"

    text += "\n🏋️ <b>ОСНОВНАЯ ЧАСТЬ:</b>\n"
    text += "<i>Тренировка всего тела — 3 линии + кор.</i>\n\n"
    for i, ex in enumerate(exercises, 1):
        text += f"{i}. {ex} — {sets}×{reps}, отдых {rest} сек\n"

    text += f"\n📝 Темп: {tempo}\n"

    text += "\n🧘 <b>ЗАМИНКА:</b>\n• Дыхание\n• Коррекция осанки\n• Растяжка\n"

    text += f"\n🍽️ <b>Питание:</b>\n{DIET[goal]}\n"
    text += f"\n💪 <b>Кардио:</b>\n{CARDIO[body_type]}\n"
    text += "\n📈 <b>Прогрессия:</b>\nДобавляй 2,5–5 кг, когда выполнишь все повторения в 2 тренировках подряд.\n"
    text += "\n⚠️ <b>Важно:</b> держи спину прямой, дыши ровно."

    try:
        photo = FSInputFile(IMG['result'])
        await message.answer_photo(photo=photo, caption=text, parse_mode='HTML')
    except Exception:
        await message.answer(text, parse_mode='HTML')

# ============================================================
# ЗАПУСК
# ============================================================
async def main():
    print('Бот запущен. Напиши /start в Telegram.')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())