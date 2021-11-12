import config

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# import db_manage
from db_manage import ShoppingList, ToDoList, BlockedUsers

bot = Bot(token=config.token)
dp = Dispatcher(bot)
users = config.users

shoppinglist = ShoppingList()
todo_list = ToDoList()
current_table = shoppinglist

blocked_list = BlockedUsers()

button_new = InlineKeyboardButton(text='НОВАЯ ЗАПИСЬ', callback_data='new_item')


# Фильтрация пользователей
async def filtering_users(message):
    user = message.chat.id
    if user not in users:
        blocked_list.set_blocked_id(user, message.text)
    return user not in users


# Запустить OkmakBot
@dp.message_handler(filtering_users)
@dp.message_handler(commands='start')
@dp.message_handler(Text(startswith='Выход из'))
async def start(message: types.Message):
    if message.chat.id in users:
        button_shop = KeyboardButton(text='Покупки')
        button_todo = KeyboardButton(text='Дела')
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(button_shop)
        markup.add(button_todo)
        txt = ''
        if not message.text.startswith('Выход из'):
            txt = 'Всегда готов! \U0001F44D \n'
        await message.answer(f'{txt}Выбери нужный раздел \U0001F4C2 ', reply_markup=markup)


# Выбрать вид
@dp.message_handler(Text(equals=['Покупки', 'Дела']))
async def start(message: types.Message):
    global current_table
    if message.text == 'Покупки':
        current_table = shoppinglist
        message.text = 'Покупок'
    elif message.text == 'Дела':
        current_table = todo_list
        message.text = 'Дел'
    button_add = KeyboardButton(text='Внести в список')
    button_lst = KeyboardButton(text='Показать список')
    button_all = KeyboardButton(text='Показать всё')
    button_exit = KeyboardButton(f'Выход из {message.text}')
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(button_add, button_lst)
    markup.add(button_all, button_exit)
    await message.answer('Выбери действие \U000027A1', reply_markup=markup)


# Добавить в список
@dp.message_handler(Text(equals='Внести в список'))
async def add_to_list(message: types.Message):
    if current_table.not_in_actual_list:
        markup = InlineKeyboardMarkup()
        markup.add(*display_btns(current_table.not_in_actual_list))
        markup.add(button_new)
        await message.answer('Что нужно добавить? \U0001F914', reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup()
        markup.add(button_new)
        await message.answer('Выбирать не из чего... \U00002639', reply_markup=markup)


# # Фоновая обработка добавления записи в список
# @dp.callback_query_handler(Text(startswith='ATL'))
# async def atl(call: types.CallbackQuery):
#     current_table.add_to_shoplist(call.data[3:])
#     await call.answer(f'Нужно:  {call.data[3:]} \U0001F44C')
#     markup = InlineKeyboardMarkup()
#     markup.add(*display_btns(current_table.not_in_actual_list, 'ATL'))
#     markup.add(button_new)
#     if current_table.not_in_actual_list:
#         await call.message.edit_text('Что нужно добавить? \U0001F914', reply_markup=markup)
#     else:
#         await call.message.edit_text('Выбирать не из чего... \U00002639', reply_markup=markup)
#     await call.answer()


# Показать список
@dp.message_handler(Text(equals='Показать список'))
async def get_current_table(message: types.Message):
    if current_table.actual_list:
        markup = InlineKeyboardMarkup()
        markup.add(*(display_btns(current_table.actual_list)))
        await message.answer(
            f'Вот список! \U0001F609 \nРед. {current_table.datetime}', reply_markup=markup
        )
    else:
        await message.answer('Список пуст! \U0001F389')


# # Фоновая обработка показа списка
# @dp.callback_query_handler(Text(startswith='GSL'))
# async def gsl(call: types.CallbackQuery):
#     current_table.del_from_shoplist(call.data[3:])
#     markup = InlineKeyboardMarkup()
#     markup.add(*(display_btns(current_table.actual_list, 'GSL')))
#     await call.answer(f'Уже не нужно:  {call.data[3:]} \U0001F44C', cache_time=1)
#     if current_table.actual_list:
#         await call.message.edit_text('Вот список! \U0001F609', reply_markup=markup)
#     else:
#         await call.message.edit_text('Список пуст! \U0001F389')
#     await call.answer()


# Показать все записи
@dp.message_handler(Text(equals='Показать всё'))
async def show_all_list(message):
    if current_table.all_items:
        markup = InlineKeyboardMarkup()
        markup.add(*display_btns(current_table.all_items))
        await message.answer(
            'Вот тебе все записи! \U0001F60E \n'
            'Для удаления записи нажми на элемент... \U0001F447', reply_markup=markup
        )
    else:
        await message.answer('А записей нет! \U0001F602')


# # Фоновая обработка удаления записи
# @dp.callback_query_handler(Text(startswith='DIF'))
# async def dif(call: types.CallbackQuery):
#     current_table.delete_item(call.data[3:])
#     markup = InlineKeyboardMarkup()
#     markup.add(*(display_btns(current_table.all_items, 'DIF')))
#     if current_table.all_items:
#         await call.message.edit_text(f'Удалено из записей: {call.data[3:]} \U0001F44C', reply_markup=markup)
#     else:
#         await call.message.edit_text('Удалять нечего! \U0001F923')
#     await call.answer()


# # Фоновая обработка кнопки добавления новой записи
# @dp.callback_query_handler(Text(startswith='new_item'))
# async def add_new(call: types.CallbackQuery):
#     await call.message.edit_text('Просто напиши тут... \U0001F447')
#     await call.answer()

# Фоновая обработка добавления записи в список
@dp.callback_query_handler(Text(equals='1'))
async def get_items(call: types.CallbackQuery):
    item = call.data
    print(item)
    if item in current_table.not_in_actual_list:
        print('add')
        current_table.add_to_shoplist(item)
        await call.answer(f'Нужно {}:  {call.data[3:]} \U0001F44C')
        markup = InlineKeyboardMarkup()
        markup.add(*display_btns(current_table.not_in_actual_list))
        markup.add(button_new)
        if current_table.not_in_actual_list:
            await call.message.edit_text('Что нужно добавить? \U0001F914', reply_markup=markup)
        else:
            await call.message.edit_text('Выбирать не из чего... \U00002639', reply_markup=markup)
        await call.answer()
    elif item in current_table.actual_list:
        print('del')
        current_table.del_from_shoplist(item)
        markup = InlineKeyboardMarkup()
        markup.add(*(display_btns(current_table.actual_list)))
        await call.answer(f'Уже не нужно:  {call.data[3:]} \U0001F44C', cache_time=1)
        if current_table.actual_list:
            await call.message.edit_text('Вот список! \U0001F609', reply_markup=markup)
        else:
            await call.message.edit_text('Список пуст! \U0001F389')
        await call.answer()
    else:
        print('rm')
        current_table.delete_item(item)
        markup = InlineKeyboardMarkup()
        markup.add(*(display_btns(current_table.all_items)))
        if current_table.all_items:
            await call.message.edit_text(f'Удалено из записей: {call.data[3:]} \U0001F44C', reply_markup=markup)
        else:
            await call.message.edit_text('Удалять нечего! \U0001F923')
        await call.answer()


# Фоновая обработка текста новой записи
@dp.message_handler(filtering_users)
@dp.message_handler(Text)
async def add_new_item(message: types.Message):
    print(0)
    if message.text not in current_table.all_items:
        current_table.add_new_item(message.text)
        await message.answer(f'Добавлено: {message.text} \U0001F44C')
    else:
        await message.answer(f'Не повторяйся! \U0000261D')


@dp.message_handler(Text(equals='blocked'))
async def show_blocked_IDs(message: types.Message):
    await message.answer(blocked_list.get_blocked())


# # Очистить чат
# @dp.message_handler(commands='clear_chat')
# async def clear_chat(message: types.Message):
#     # dt = db_manage.get_datetime()
#     # message.chat.message_auto_delete_time = datetime.time
#     # await bot.delete_message(message.)
#     await message.answer('Ощищено! \U0001F61C')
#     # await message.answer('Пока вообще никак! \U0001F61C')


# Доп. функция. Формирует список кнопок из передаваемого множества
def display_btns(set_type):
    btn_list = []
    for i in sorted(set_type):
        button_item = InlineKeyboardButton(text=i, callback_data='1')
        btn_list.append(button_item)
    return btn_list


if __name__ == '__main__':
    executor.start_polling(dp)