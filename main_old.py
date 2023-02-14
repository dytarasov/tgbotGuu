import logging
from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar
from aiogram import Bot, Dispatcher, executor, types
from db_commands import register_user, select_user, is_admin
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar


API_TOKEN = '5810734735:AAEHoE-jjC0PiyNy8m48aLREirzewbjbYBo'

logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot,storage = MemoryStorage())


class reg(StatesGroup):
    user_type = State()
    fio = State()
    fio_p = State()
    department = State()
    course = State()
    group = State()


class meet(StatesGroup):
    m_date = State()
    m_time = State()
    m_desc = State()


@dp.message_handler(commands="start", state="*")
async def cmd_start(message: types.Message):
    print({message.from_user: message.text})
    user = select_user(user_id = int(message.from_user.id))
    if user:
        await message.answer(
                             f"Ваш профиль:\n"
                             f"\n"
                             f"ФИО: {user.fio}\n"
                             f"Институт: {user.department}\n"
                             f"Курс: {user.course}\n"
                            )
        but = [[types.KeyboardButton(text="Савостицкий Артём Сергеевич")],[types.KeyboardButton(text="Сычёв Андрей Алексеевич")]]
        keyboard = types.ReplyKeyboardMarkup(keyboard=but)
        await message.answer(text = 'Выберете преподавателя с которым вы хотите встретиться:', reply_markup=keyboard)

    else:
        kb = [
            [types.KeyboardButton(text="Я студент ГУУ")],
            [types.KeyboardButton(text="Я сотрудник ГУУ")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        await message.answer("Выберете ответ", reply_markup=keyboard)

@dp.message_handler(text="Я сотрудник ГУУ", state="*")
async def st_p_step(message: types.Message, state: FSMContext):
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
        await state.update_data(fio_p=message.text.title())
        user_data = await state.get_data()
        await state.finish()
        user = register_user(message=message, fio=user_data['fio_p'],user_type=user_data['user_type'],department='None',course='None',group='None')
        if user:
            await message.answer('Вы успешно зарегистрировались как сотрудник ГУУ!')


@dp.message_handler(text="Я студент ГУУ", state="*")
async def st_s_step(message: types.Message, state: FSMContext):
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
    await state.update_data(fio=message.text.title())
    await message.answer(text='Напишите свой институт, например - ИЭФ')
    await reg.department.set()

@dp.message_handler(state=reg.department)
async def department_step(message: types.Message, state: FSMContext):
    await state.update_data(department=message.text.title())
    await message.answer(text='Напишите свой курс')
    await reg.course.set()

@dp.message_handler(state=reg.course)
async def course_step(message: types.Message, state: FSMContext):
    await state.update_data(course=message.text.title())
    await message.answer(text='Напишите свою группу')
    await reg.group.set()

@dp.message_handler(state=reg.group, content_types=types.ContentTypes.TEXT)
async def res_step(message: types.Message, state: FSMContext):
    await state.update_data(group=message.text.lower())
    user_data = await state.get_data()
    await state.finish()
    user = register_user(message = message,fio = user_data['fio'],department=user_data['department'],group= user_data['group'],course=user_data['course'],user_type = user_data['user_type'])
    if user:
        await message.answer('Вы успешно зарегистрировались как студент ГУУ!')


#@dp.message_handler(commands = 'setWeek')
#async def setWeek(message: types.Message):
#    if is_admin(message.from_user.id) == True:
#        await message.answer('Hoooo you are '+str(message.from_user.id)+'')
#        #тут дергаем функцию вывода возможных окошек
#        pass

@dp.message_handler(text = "Савостицкий Артём Сергеевич")
async def create_notification(message: types.Message,):
    await message.answer("Выберете дату встречи:", reply_markup=await SimpleCalendar().start_calendar())




@dp.message_handler(text="Сычёв Андрей Алексеевич")
async def create_notification(message: types.Message):
    await message.answer("Выберете дату встречи:", reply_markup=await SimpleCalendar().start_calendar())


@dp.callback_query_handler(simple_cal_callback.filter(),state="*")
async def process_dialog_calendar(callback_query: CallbackQuery,callback_data: dict,state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        date = str(date.strftime("%d.%m.%Y"))
        await state.update_data(m_date=date)
        await callback_query.message.answer('Вы выбрали дату: '+date)
        await callback_query.message.answer(text='Напишите время встречи в формате часы минуты, например так - 12 00',reply_markup=types.ReplyKeyboardRemove())
        await meet.m_time.set()



@dp.message_handler(state=meet.m_time, content_types=types.ContentTypes.TEXT)
async def time_m_step(message: types.Message, state: FSMContext):
        await state.update_data(m_time=message.text.title())
        await message.answer(text='Напишите цель встречи')
        await meet.m_desc.set()

@dp.message_handler(state=meet.m_desc, content_types=types.ContentTypes.TEXT)
async def desc_m_step(message: types.Message, state: FSMContext):
        await state.update_data(m_desc=message.text.title())
        meet_data = await state.get_data()
        await state.finish()
        await message.answer(meet_data)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


