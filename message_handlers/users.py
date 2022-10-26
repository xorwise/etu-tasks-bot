from services.users import name_validation, group_validation, is_sender_validation
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from states.states import DeleteProfileState, RegisterState, ProfileState
from asyncio import sleep
from inlines.default_inlines import default_inline
from database.users import add_user, get_user, update_user, delete_user
from database.groups import add_group, get_group, update_group


async def register(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    if user:
        await callback.message.answer('Данный аккаунт телеграм уже зарегистрирован.',
                                      reply_markup=ReplyKeyboardRemove())
        inline_buttons = await default_inline(user)
        await sleep(1)
        await callback.message.answer('Выбери один из предложенных вариантов.', reply_markup=inline_buttons)
        await callback.message.delete()
    else:
        await RegisterState.full_name.set()
        button = InlineKeyboardButton('Отмена', callback_data='/cancel')
        inline_buttons = InlineKeyboardMarkup(row_width=2).add(button)
        await callback.message.answer('Введите ФИО: ', reply_markup=inline_buttons)
    await callback.answer()


async def get_fullname(message: types.Message, state: FSMContext):
    if await name_validation(message.text):
        async with state.proxy() as data:
            data['full_name'] = message.text
        await RegisterState.next()
        button = InlineKeyboardButton('Отмена', callback_data='/cancel')
        inline_buttons = InlineKeyboardMarkup(row_width=2).add(button)
        await message.answer('Введите номер группы: ', reply_markup=inline_buttons)
    else:
        button = InlineKeyboardButton('Отмена', callback_data='/cancel')
        inline_buttons = InlineKeyboardMarkup(row_width=2).add(button)
        await message.answer('Введите ФИО корректно в формате:\nФамилия Имя Отчество (при наличии).',
                             reply_markup=inline_buttons)


async def retrieve_group(message: types.Message, state: FSMContext):
    if await group_validation(message.text):
        async with state.proxy() as data:
            data['group'] = int(message.text)
        await RegisterState.next()
        button1 = InlineKeyboardButton('Да', callback_data='Да')
        button2 = InlineKeyboardButton('Нет', callback_data='Нет')
        button3 = InlineKeyboardButton('Отмена', callback_data='/cancel')
        inline_buttons = InlineKeyboardMarkup(row_width=2).row(button1, button2).add(button3)
        await message.answer('Хочешь ли ты отправлять задания?', reply_markup=inline_buttons)
    else:
        await message.answer('Введите номер группы корректно. (Целое число от 1000 до 9999)')


async def get_is_sender(callback: types.CallbackQuery, state: FSMContext):
    if await is_sender_validation(callback['data']):
        async with state.proxy() as data:
            data['is_sender'] = True if callback['data'] == 'Да' else False

        async with state.proxy() as data:
            data['user_id'] = callback.from_user.id
            data['chat_id'] = callback.message.chat.id
            await add_user(dict(data))
            user = await get_user(data['user_id'])
            group = await get_group(data['group'])
            if group is None:
                print(user['user_id'])
                group_data = {
                    'id': data['group'],
                    'tasks': [],
                    'students': [user['chat_id']],
                }
                if await add_group(group_data) == False:
                    await delete_user(data['chat_id'])
                    await state.finish()
                    button = InlineKeyboardButton('Создать профиль', callback_data='/register')
                    inline_buttons = InlineKeyboardMarkup(row_width=2)
                    inline_buttons.add(button)
                    await callback.message.answer('Введённая вами группа не существует.', reply_markup=inline_buttons)
                    await callback.answer()
                    return
            else:
                group['students'].append(user['chat_id'])
                await update_group(data['group'], group)
        if user:
            await callback.message.answer('Регистрация прошла успешно!', reply_markup=ReplyKeyboardRemove())
            await sleep(1)
            inline_buttons = await default_inline(user)
            await callback.message.answer('Выбери один из предложенных вариантов.', reply_markup=inline_buttons)
            await callback.message.delete()
        else:
            button = InlineKeyboardButton('Создать профиль', callback_data='/register')
            inline_buttons = InlineKeyboardMarkup(row_width=2)
            inline_buttons.add(button)
            await callback.message.answer('Неизвестная ошибка, повторите позже!', reply_markup=inline_buttons)
        await state.finish()

    else:
        await callback.message.answer('Выберите один из двух вариантов.')


async def cancel_registration(callback: types.CallbackQuery, state: FSMContext):
    button = InlineKeyboardButton('Создать профиль', callback_data='/register')
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    inline_buttons.add(button)
    await callback.message.answer('Нажми на кнопку "Создать профиль" и задай нужные параметры.',
                                  reply_markup=inline_buttons)
    await state.finish()
    return await callback.answer()


async def get_user_profile(callback):
    user = await get_user(callback.from_user.id)
    button1 = InlineKeyboardButton('Изменить профиль', callback_data='/update_profile')
    button2 = InlineKeyboardButton('Удалить профиль', callback_data='/delete_profile')
    button3 = InlineKeyboardButton('Главное меню', callback_data='/menu')
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    inline_buttons.row(button1, button2).add(button3)
    if type(callback) == types.Message:
        if user is None:
            return await start_registration_message(callback)
        await callback.answer(
            f'Профиль пользователя {callback.from_user.username}:\nФИО: {user["full_name"]}\nГруппа: {user["group"]}\nДоступ к отправлению заданий: {user["is_sender"]}',
            reply_markup=inline_buttons)
        await callback.delete()
    else:
        if user is None:
            return await start_registration_callback(callback)
        await callback.message.answer(
            f'Профиль пользователя {callback.from_user.username}:\nФИО: {user["full_name"]}\nГруппа: {user["group"]}\nДоступ к отправлению заданий: {user["is_sender"]}',
            reply_markup=inline_buttons)
        await callback.message.delete()
        await callback.answer()


async def start_registration_callback(callback):
    button = InlineKeyboardButton('Создать профиль', callback_data='/register')
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    inline_buttons.add(button)
    await callback.message.answer('Вы не зарегистрированы.', reply_markup=inline_buttons)
    await callback.message.delete()
    await callback.answer()


async def start_registration_message(message):
    button = InlineKeyboardButton('Создать профиль', callback_data='/register')
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    inline_buttons.add(button)
    await message.answer('Вы не зарегистрированы.', reply_markup=inline_buttons)
    await message.delete()
    return


async def update_user_profile(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    if user is None:
        button = InlineKeyboardButton('Создать профиль', callback_data='/register')
        inline_buttons = InlineKeyboardMarkup(row_width=2)
        inline_buttons.add(button)
        await callback.message.answer('Вы не зарегистрированы.', reply_markup=inline_buttons)
        await callback.message.delete()
        await callback.answer()
        return
    await ProfileState.full_name.set()
    button = InlineKeyboardButton('Отмена', callback_data='/cancel')
    inline_buttons = InlineKeyboardMarkup(row_width=2).add(button)
    await callback.message.answer('Введите ФИО: ', reply_markup=inline_buttons)
    await callback.answer()


async def get_updated_fullname(message: types.Message, state: FSMContext):
    if await name_validation(message.text):
        async with state.proxy() as data:
            data['full_name'] = message.text
        await ProfileState.next()
        button = InlineKeyboardButton('Отмена', callback_data='/cancel')
        inline_buttons = InlineKeyboardMarkup(row_width=2).add(button)
        await message.answer('Введите номер группы: ', reply_markup=inline_buttons)
    else:
        await message.answer('Введите ФИО корректно в формате:\nФамилия Имя Отчество (при наличии).')


async def retrieve_updated_group(message: types.Message, state: FSMContext):
    if await group_validation(int(message.text)):
        async with state.proxy() as data:
            data['group'] = int(message.text)
        await ProfileState.next()
        button1 = InlineKeyboardButton('Да', callback_data='Да')
        button2 = InlineKeyboardButton('Нет', callback_data='Нет')
        button3 = InlineKeyboardButton('Отмена', callback_data='/cancel')
        inline_buttons = InlineKeyboardMarkup(row_width=2).row(button1, button2).add(button3)
        await message.answer('Хочешь ли ты отправлять задания?', reply_markup=inline_buttons)
    else:
        await message.answer('Введите номер группы корректно.')


async def get_updated_is_sender(callback: types.CallbackQuery, state: FSMContext):
    if await is_sender_validation(callback['data']):
        async with state.proxy() as data:
            data['is_sender'] = True if callback['data'] == 'Да' else False

        async with state.proxy() as data:
            old_user = await get_user(callback.from_user.id)
            await update_user(callback.from_user.id, dict(data))
            user = await get_user(callback.from_user.id)
            old_group = await get_group(old_user['group'])
            group = await get_group(data['group'])
            if group is None:
                group_data = {
                    'id': data['group'],
                    'tasks': [],
                    'students': [user['chat_id']]
                }
                del old_group['students'][old_group['students'].index(old_user['chat_id'])]
                await update_group(old_user['group'], old_group)
                await add_group(group_data)
            else:
                del old_group['students'][old_group['students'].index(old_user['chat_id'])]
                await update_group(old_user['group'], old_group)
                old_group['students'].append(user['chat_id'])
                await update_group(data['group'], old_group)
        if user:
            await callback.message.answer('Данные успешно изменены!', reply_markup=ReplyKeyboardRemove())
            await sleep(1)
            button = InlineKeyboardButton('Меню', callback_data='/menu')
            inline_buttons = InlineKeyboardMarkup(row_width=2).add(button)
            await callback.message.answer(f'Новый профиль пользователя {callback.from_user.username}:\n \
                ФИО: {user["full_name"]}\n \
                Группа: {user["group"]}\n \
                Доступ к отправлению заданий: {user["is_sender"]}', reply_markup=inline_buttons)
            await callback.message.delete()
        else:
            button = InlineKeyboardButton('Создать профиль', callback_data='/register')
            inline_buttons = InlineKeyboardMarkup(row_width=2)
            inline_buttons.add(button)
            await callback.message.answer('Неизвестная ошибка, повторите позже!', reply_markup=inline_buttons)
        await state.finish()

    else:
        await callback.message.answer('Выберите один из двух вариантов.')
    await callback.answer()


async def cancel_profile_edit(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    button1 = InlineKeyboardButton('Изменить профиль', callback_data='/update_profile')
    button2 = InlineKeyboardButton('Удалить профиль', callback_data='/delete_profile')
    button3 = InlineKeyboardButton('Главное меню', callback_data='/menu')
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    inline_buttons.row(button1, button2).add(button3)

    await callback.message.answer(f'Профиль пользователя {callback.from_user.username}:\n \
        ФИО: {user["full_name"]}\n \
        Группа: {user["group"]}\n \
        Доступ к отправлению заданий: {user["is_sender"]}', reply_markup=inline_buttons)
    await state.finish()
    return await callback.answer()


async def delete_user_profile(callback: types.CallbackQuery):
    await DeleteProfileState.verify.set()
    button1 = InlineKeyboardButton('Да', callback_data='/verify')
    button2 = InlineKeyboardButton('Нет', callback_data='/cancel')
    inline_buttons = InlineKeyboardMarkup(row_width=2).row(button1, button2)
    await callback.message.answer('Вы уверены, что хотите удалить профиль?', reply_markup=inline_buttons)
    await callback.message.delete()
    await callback.answer()


async def get_verification(callback: types.CallbackQuery, state: FSMContext):
    if callback['data'] == '/verify':
        user = await get_user(callback.from_user.id)
        await delete_user(callback.from_user.id)
        group = await get_group(user['group'])
        del group['students'][group['students'].index(user)]
        await update_group(group['id'], group)
        if await get_user(callback.from_user.id) is None:
            button = InlineKeyboardButton('Создать профиль', callback_data='/register')
            inline_buttons = InlineKeyboardMarkup(row_width=2)
            inline_buttons.add(button)
            await callback.message.answer('Профиль был успешно удален.\nЕсли хотите, можете создать профиль заново:',
                                          reply_markup=inline_buttons)
        else:
            inline_buttons = await default_inline(get_user(callback.from_user.id))
            await callback.message.answer('Произошла ошибка, повторите позже', reply_markup=inline_buttons)
        await state.finish()
    else:
        user = await get_user(callback.from_user.id)
        inline_buttons = await default_inline(user)
        await callback.message.answer('Выбери один из предложенных вариантов.', reply_markup=inline_buttons)
        await callback.message.delete()
        await state.finish()
    await callback.answer()


async def command_get_user_profile(message: types.Message):
    await get_user_profile(message)


def users_handlers_register(dp: Dispatcher):
    dp.register_callback_query_handler(register, text='/register', state=None)
    dp.register_message_handler(get_fullname, state=RegisterState.full_name)
    dp.register_message_handler(retrieve_group, state=RegisterState.group)
    dp.register_callback_query_handler(get_is_sender, text=['Да', 'Нет'], state=RegisterState.is_sender)
    dp.register_callback_query_handler(get_user_profile, text='/get_profile')
    dp.register_callback_query_handler(update_user_profile, text='/update_profile', state=None)
    dp.register_message_handler(get_updated_fullname, state=ProfileState.full_name)
    dp.register_message_handler(retrieve_updated_group, state=ProfileState.group)
    dp.register_callback_query_handler(delete_user_profile, text='/delete_profile', state=None)
    dp.register_callback_query_handler(get_verification, text=['/verify', '/cancel'], state=DeleteProfileState.verify)
    dp.register_callback_query_handler(cancel_registration, text='/cancel', state=RegisterState)
    dp.register_callback_query_handler(cancel_profile_edit, text='/cancel', state=ProfileState)
    dp.register_callback_query_handler(get_updated_is_sender, text=['Да', 'Нет'], state=ProfileState.is_sender)
    dp.register_message_handler(command_get_user_profile, commands=['get_user_profile'])
