import logging
import datetime
from db_commands import register_user, select_user, is_admin, create_meet, update_meet_status, get_time_list, get_meets, \
    get_user_id_from_meet

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from aiogram.utils.callback_data import CallbackData
from config import TOKEN

API_TOKEN = TOKEN

# логи

logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler('bot_app.log')
ch.setLevel(logging.DEBUG)
strfmt = '[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)
ch.setFormatter(formatter)
logger.addHandler(ch)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

vote_cb = CallbackData('call','initcall', 'values')


# стейт для регистрации

class reg(StatesGroup):
    user_type = State()
    fio = State()
    fio_p = State()
    department = State()
    course = State()
    group = State()

# стейт для встреч и их установки

class meet(StatesGroup):
    m_professor = State()
    m_date = State()
    m_time = State()
    m_desc = State()


# хендлер для команды старт
@dp.message_handler(commands="start", state="*")
async def cmd_start(message: types.Message):
    logger.info(message)
    # тут проверяем зареган ли юзер
    user = select_user(user_id=int(message.from_user.id))
    if user:
        await message.answer(
            f"Ваш профиль:\n"
            f"\n"
            f"ФИО: {user.fio}\n"
            f"Институт: {user.department}\n"
            f"Курс: {user.course}\n"
        )
        # тут он у нас зареган, отправляем ему его профиль и кнопки с именами
        but = [[types.KeyboardButton(text="Савостицкий Артём Сергеевич")],
               [types.KeyboardButton(text="Сычёв Андрей Алексеевич")], [types.KeyboardButton(text="/meets")]]
        keyboard = types.ReplyKeyboardMarkup(keyboard=but)
        await message.answer(text='Выберете преподавателя с которым вы хотите встретиться:', reply_markup=keyboard)


    else:
        # тут он у нас не зареган, отправляем ему его профиль и кнопки с именами
        kb = [
            [types.KeyboardButton(text="Я студент ГУУ")],
            [types.KeyboardButton(text="Я сотрудник ГУУ")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        await message.answer("Вы не зарегистрированы, выберете один из вариантов регистрации:", reply_markup=keyboard)


@dp.message_handler(text="Я сотрудник ГУУ", state="*")
async def st_p_step(message: types.Message, state: FSMContext):
    logger.info(message)
    user = select_user(user_id=int(message.from_user.id))
    if user:
        await message.answer('Вы уже зарегистрированы! Введите /start для записи к преподавателю')
        pass
    else:
        await state.update_data(user_type=1)
        await message.answer(text='Напишите ваше ФИО')
        await reg.fio_p.set()


@dp.message_handler(state=reg.fio_p, content_types=types.ContentTypes.TEXT)
async def fio_p_step(message: types.Message, state: FSMContext):
    logger.info(message)
    await state.update_data(fio_p=message.text.title())
    user_data = await state.get_data()
    await state.finish()
    user = register_user(message=message, fio=user_data['fio_p'], user_type=user_data['user_type'], department='None',
                         course='None', group='None')
    if user:
        await message.answer('Вы успешно зарегистрировались как сотрудник ГУУ!')
        but = [[types.KeyboardButton(text="Савостицкий Артём Сергеевич")],
               [types.KeyboardButton(text="Сычёв Андрей Алексеевич")]]
        keyboard = types.ReplyKeyboardMarkup(keyboard=but)
        await message.answer(text='Выберете преподавателя с которым вы хотите встретиться:', reply_markup=keyboard)


@dp.message_handler(text="Я студент ГУУ", state="*")
async def st_s_step(message: types.Message, state: FSMContext):
    logger.info(message)
    user = select_user(user_id=int(message.from_user.id))
    if user:
        await message.answer('Вы уже зарегистрированы! Введите /start для записи к преподавателю')
        pass
    else:
        await state.update_data(user_type=2)
        await message.answer(text='Напиши ФИО')
        await reg.fio.set()


@dp.message_handler(state=reg.fio, content_types=types.ContentTypes.TEXT)
async def fio_s_step(message: types.Message, state: FSMContext):
    logger.info(message)
    await state.update_data(fio=message.text)
    await message.answer(text='Напишите свой институт, например - ИЭФ')
    await reg.department.set()


@dp.message_handler(state=reg.department)
async def department_step(message: types.Message, state: FSMContext):
    logger.info(message)
    await state.update_data(department=message.text)
    await message.answer(text='Напишите свой курс')
    await reg.course.set()


@dp.message_handler(state=reg.course)
async def course_step(message: types.Message, state: FSMContext):
    logger.info(message)
    await state.update_data(course=message.text)
    await message.answer(text='Напишите свою группу')
    await reg.group.set()


@dp.message_handler(state=reg.group, content_types=types.ContentTypes.TEXT)
async def res_step(message: types.Message, state: FSMContext):
    logger.info(message)
    await state.update_data(group=message.text)
    user_data = await state.get_data()
    await state.finish()
    user = register_user(message=message, fio=user_data['fio'], department=user_data['department'],
                         group=user_data['group'], course=user_data['course'], user_type=user_data['user_type'])
    if user:
        await message.answer('Вы успешно зарегистрировались как студент ГУУ!')
        but = [[types.KeyboardButton(text="Савостицкий Артём Сергеевич")],
               [types.KeyboardButton(text="Сычёв Андрей Алексеевич")]]
        keyboard = types.ReplyKeyboardMarkup(keyboard=but)
        await message.answer(text='Выберете преподавателя с которым вы хотите встретиться:', reply_markup=keyboard)



@dp.message_handler(text="Савостицкий Артём Сергеевич", state="*")
async def create_notification(message: types.Message, state: FSMContext):
    logger.info(message)
    await message.answer("Выберете дату встречи:", reply_markup=await SimpleCalendar().start_calendar())
    await state.update_data(m_professor='487310360')


@dp.message_handler(text="Сычёв Андрей Алексеевич", state="*")
async def create_notification(message: types.Message, state: FSMContext):
    logger.info(message)
    await message.answer("Выберете дату встречи:", reply_markup=await SimpleCalendar().start_calendar())
    await state.update_data(m_professor='1252167219')


@dp.callback_query_handler(simple_cal_callback.filter(), state="*")
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    logger.info(callback_query.message)
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        date_o = date
        date = str(date.strftime("%d.%m.%Y"))
        if date_o.date() >= datetime.datetime.now().date():
            await state.update_data(m_date=date)
            await callback_query.message.answer('Вы выбрали дату: ' + date)
            meet_data = await state.get_data()
            time_list = get_time_list(m_date=date, professor_id=meet_data['m_professor'], )
            kb_keys = [[types.KeyboardButton(text=i)] for i in time_list]
            keyboard_t = types.ReplyKeyboardMarkup(keyboard=kb_keys)
            await callback_query.message.answer(text='Выберете время встречи:', reply_markup=keyboard_t)
            await meet.m_time.set()
        else:
            await callback_query.message.answer("Вы выбрали уже прошедшую дату, пожалуйста выберете дату в будущем")
            await callback_query.message.answer("Выберете дату встречи:",
                                                reply_markup=await SimpleCalendar().start_calendar())


@dp.message_handler(state=meet.m_time, content_types=types.ContentTypes.TEXT)
async def time_m_step(message: types.Message, state: FSMContext):
    logger.info(message)
    await state.update_data(m_time=message.text.title())
    await message.answer(text='Напишите цель встречи:', reply_markup=types.ReplyKeyboardRemove())
    await meet.m_desc.set()


@dp.message_handler(state=meet.m_desc, content_types=types.ContentTypes.TEXT)
async def desc_m_step(message: types.Message, state: FSMContext):
    logger.info(message)
    await state.update_data(m_desc=message.text.title())
    meet_data = await state.get_data()
    await state.finish()
    meet_creation = create_meet(message=message, professor_id=meet_data['m_professor'], m_date=meet_data['m_date'],
                                m_time=meet_data['m_time'], m_desc=meet_data['m_desc'])

    keys_cr = InlineKeyboardMarkup(row_width=1)
    confrim_b = InlineKeyboardButton(text='Подтвердить встречу', callback_data=vote_cb.new(initcall = 'accept',values = meet_creation[1]))
    reject_b = InlineKeyboardButton(text='Отклонить встречу', callback_data=vote_cb.new(initcall = 'reject',values = meet_creation[1]))
    keys_cr.add(confrim_b, reject_b)
    await message.answer(text='Заявка на встречу создана, ее ID - '+str(int(meet_creation[1])+666))
    from_user = select_user(user_id=message.from_user.id)
    if from_user.user_type == 2:
        await bot.send_message(meet_data['m_professor'],text=f"У вас новый запрос на встречу:\n"
                                  f"От студента: \n"
                                  f"  ФИО: {from_user.fio}\n"
                                  f"  Институт: {from_user.department}\n"
                                  f"  Курс: {from_user.course}\n"
                                  f"  Группа: {from_user.group}\n"
                                  f"  На дату: {meet_data['m_date'] + ' ' + meet_data['m_time']}\n"
                                  f"  Цель встречи: {meet_data['m_desc']}\n", reply_markup=keys_cr)
    else:
        await bot.send_message(meet_data['m_professor'],text=f"У вас новый запрос на встречу:\n"
                                  f"От сотрудника ГУУ: \n"
                                  f"  ФИО: {from_user.fio}\n"
                                  f"  На дату: {meet_data['m_date'] + ' ' + meet_data['m_time']}\n"
                                  f"  Цель встречи: {meet_data['m_desc']}\n", reply_markup=keys_cr)


@dp.callback_query_handler(vote_cb.filter(initcall='accept'), state='*')
async def confirm(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    logger.info(callback.message)
    meet_data = await state.get_data()
    status = update_meet_status(meet_id=callback_data['values'], new_status=1)
    if status == True:
        await callback.message.answer('Встреча принята')
        await bot.send_message(get_user_id_from_meet(callback_data['values']), 'Преподаватель принял вашу заявку c ID - '+str(int(callback_data['values'])+666))
    elif status == 3:
        await callback.message.answer('Встреча отклонена инциатором')
    else:
        await callback.message.answer('Что-то пошло не так, уже знаем и чиним')
        logger.error(callback.message)


@dp.callback_query_handler(vote_cb.filter(initcall='reject'), state='*')
async def reject(callback: types.CallbackQuery, state: FSMContext,callback_data: dict):
    logger.info(callback.message)
    meet_data = await state.get_data()
    status = update_meet_status(meet_id=callback_data['values'], new_status=2)
    if  status == True:
        await callback.message.answer('Встреча отклонена')
        await bot.send_message(get_user_id_from_meet(callback_data['values']), 'Преподаватель отклонил вашу заявку c ID - '+str(int(callback_data['values'])+666))
    elif status == 3:
        await callback.message.answer('Встреча отклонена инциатором')
    else:
        await callback.message.answer('Что-то пошло не так, уже знаем и чиним')
        logger.error(callback.message)


@dp.message_handler(commands="meets",state='*')
async def get_user_meets(message: types.Message,state: FSMContext):
    logger.info(message)
    await message.answer(text="Ваши текущие заявки на встречи с преподавателями:")
    for i in get_meets(user_id = str(message.from_user.id)):
        if i.status == 0:
            sts = 'На рассмотрении'
        elif i.status == 1:
            sts = 'Принята преподавателем'
        elif i.status == 2:
            sts = 'Отклонена преподавателем'
        elif i.status == 3:
            sts = 'Отклонена вами'
        else:
            sts = 'Напишите пожалуйста в поддержку бота с помощью команды /support'
        text = f"ID встречи: {str(int(i.id) + 666)} \n" f"  Дата: {i.m_date}\n" f"  Время: {i.m_time}\n" f"  Статус: {sts}\n" f"  Цель встречи: {i.m_desc}\n"
        keys_cr = InlineKeyboardMarkup(row_width=1)
        meet_id = str(int(i.id))
        confrim_b = InlineKeyboardButton(text='Отменить встречу',  callback_data=vote_cb.new(initcall = 'rej_i',values = meet_id))
        keys_cr.add(confrim_b)
        await message.answer(text=text,reply_markup = keys_cr)

@dp.callback_query_handler(vote_cb.filter(initcall='rej_i'))
async def confirm(callback: types.CallbackQuery,callback_data: dict):
    logger.info(callback.message)
    meet_id = str(callback_data['values'])
    status = update_meet_status(meet_id = meet_id, new_status=3)
    if status:
        logger.info('Заявка '+meet_id+' отменена инициатором')
        await callback.message.answer(text=('Заявка '+str(int(meet_id)+666)+' отменена инициатором'))
        await bot.send_message('6295079014',text=('Заявка ID - ' + str(int(meet_id) + 666) + ' отменена инициатором'))



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
