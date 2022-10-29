from aiogram import types, Dispatcher
from asyncio import sleep
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from inlines.default_inlines import default_inline
from database.users import get_user
from database.groups import get_group
from services.groups import put_message_together, get_students


async def send_welcome(message: types.Message):
    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer('Привет! Я бот, который поможет тебе делать все задания вовремя!')
        await sleep(1)
        button = InlineKeyboardButton('Создать профиль', callback_data='/register')
        inline_buttons = InlineKeyboardMarkup(row_width=2)
        inline_buttons.add(button)
        await message.answer('Нажми на кнопку "Создать профиль" и задай нужные параметры.', reply_markup=inline_buttons)
    else:
        inline_buttons = await default_inline(user)
        await message.answer('Выбери один из предложенных вариантов.', reply_markup=inline_buttons)
        await message.delete()


async def menu(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    if await is_callback_user_none(callback, user): return
    inline_buttons = await default_inline(user)
    await callback.message.answer('Выберите один из предложенных вариантов.', reply_markup=inline_buttons)
    await callback.message.delete()
    await callback.answer()


async def is_callback_user_none(callback: types.CallbackQuery, user):
    if user is None:
        button = InlineKeyboardButton('Создать профиль', callback_data='/register')
        inline_buttons = InlineKeyboardMarkup(row_width=2)
        inline_buttons.add(button)
        await callback.message.answer('Вы не зарегистрированы.', reply_markup=inline_buttons)
        await callback.message.delete()
        await callback.answer()
        return True
    return False


async def command_menu(message: types.Message):
    user = await get_user(message.from_user.id)
    if await is_message_user_none(message, user): return
    inline_buttons = await default_inline(user)
    await message.answer('Выберите один из предложенных вариантов.', reply_markup=inline_buttons)
    await message.delete()


async def is_message_user_none(message: types.Message, user: dict) -> bool:
    if user is None:
        button = InlineKeyboardButton('Создать профиль', callback_data='/register')
        inline_buttons = InlineKeyboardMarkup(row_width=2)
        inline_buttons.add(button)
        await message.answer('Вы не зарегистрированы.', reply_markup=inline_buttons)
        await message.delete()
        return True
    return False


async def support(message: types.Message):
    await message.delete()
    inline_buttons = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('Меню', callback_data='/menu'))
    await message.answer('По техническим вопросам писать @xorwise.', reply_markup=inline_buttons)


async def retrieve_group(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    if await is_callback_user_none(callback, user): return
    group = await get_group(user.get('group'))
    names = await get_students(group)
    inline_buttons = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('Меню', callback_data='/menu'))
    await callback.message.delete()
    await callback.message.answer(await put_message_together(group.get('id'), names), reply_markup=inline_buttons)
    await callback.answer()


async def command_retrieve_group(message: types.Message):
    user = await get_user(message.from_user.id)
    if await is_message_user_none(message, user): return
    group = await get_group(user.get('group'))
    names = await get_students(group)
    inline_buttons = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('Меню', callback_data='/menu'))
    await message.delete()
    await message.answer(await put_message_together(group.get('id'), names), reply_markup=inline_buttons)


def other_handlers_register(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'], state=None)
    dp.register_callback_query_handler(menu, text='/menu')
    dp.register_message_handler(command_menu, commands=['menu'])
    dp.register_message_handler(support, commands=['support', 'help'])
    dp.register_callback_query_handler(retrieve_group, text='/get_group')
    dp.register_message_handler(command_retrieve_group, commands=['get_group'])
