from aiogram import types
from services.tasks import get_tasks_with_offset, put_together_message, check_deadline, get_solution_message_together, \
    get_solution_message
from states.states import TaskState, UpdateTaskState, GetTaskState, SolutionState, UpdateSolutionState, \
    DeleteSolutionState
from inlines.default_inlines import default_inline, subject_inline, change_options, get_tasks_inline, \
    choose_subject_inline, show_filter, choose_deadline_inline, task_options, get_solution_inline, solution_options, \
    solutions_options, update_solution_options
from database.users import get_user
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import datetime
from database.tasks import add_task, get_task, patch_task, delete_task, get_tasks_by_subject, get_available_deadlines, \
    get_tasks_by_deadline, get_all_current_tasks_inline, get_tasks_by_user, get_all_finished_tasks
from aiogram.dispatcher.filters import Text
from asyncio import sleep
from .other import menu


async def create_task(callback, state: FSMContext):
    await TaskState.subject.set()
    user = await get_user(callback.from_user.id)
    group = user['group']
    inline_buttons = await subject_inline(group)
    button = InlineKeyboardButton('Отмена', callback_data='/menu')
    inline_buttons.add(button)
    if type(callback) == types.Message:
        await callback.answer('Выберите нужный предмет:', reply_markup=inline_buttons)
    else:
        await callback.message.answer('Выберите нужный предмет:', reply_markup=inline_buttons)
        await callback.message.delete()
        await callback.answer()


async def get_subject(callback: types.CallbackQuery, state: FSMContext):
    if callback['data'] == '/menu':
        await cancel_creation(callback, state)
        return
    async with state.proxy() as data:
        data['subject'] = callback['data']
    await TaskState.next()
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    button = InlineKeyboardButton('Отмена', callback_data='/cancel')
    inline_buttons.add(button)
    await callback.message.answer('Введите описание задания:', reply_markup=inline_buttons)
    await callback.answer()


async def get_description(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
        data['photos'] = []
    await TaskState.next()
    button = InlineKeyboardButton('Пропустить', callback_data='/skip')
    inline_buttons = InlineKeyboardMarkup(row_width=2).add(button)
    button = InlineKeyboardButton('Отмена', callback_data='/cancel')
    inline_buttons.add(button)
    await message.answer(
        'Отправьте фото и нажмите на кнопку: Пропустить\n Или нажмите на кнопку сразу, если отправлять фото нет '
        'необходимости.',
        reply_markup=inline_buttons)


async def get_photos(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photos'].append(message.photo[-1].file_id)


async def skip(callback: types.CallbackQuery, state: FSMContext):
    await TaskState.next()
    button1 = InlineKeyboardButton('Да', callback_data='Да')
    button2 = InlineKeyboardButton('Нет', callback_data='Нет')
    inline_buttons = InlineKeyboardMarkup(row_width=2).row(button1, button2)
    button = InlineKeyboardButton('Отмена', callback_data='/cancel')
    inline_buttons.add(button)
    await callback.message.answer('Возможно ли прикрепить к этому заданию решение?', reply_markup=inline_buttons)
    await callback.answer()


async def get_is_solvable(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['is_solvable'] = True if callback['data'] == 'Да' else False
    await TaskState.next()
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    button = InlineKeyboardButton('Отмена', callback_data='/cancel')
    inline_buttons.add(button)
    await callback.message.answer('Введите день Дедлайна (крайнего срока) задания в формате: DD.MM.YYYY или DD.MM:',
                                  reply_markup=inline_buttons)
    await callback.answer()


async def get_deadline(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        response = await check_deadline(data, message)
        if not response:
            return
        data['deadline'] = response
        user = await get_user(message.from_user.id)
        data['sender'] = message.from_user.id
        data['group'] = user['group']
        data['solution'] = list()
        _id = await add_task(dict(data))
    await state.finish()
    button3 = InlineKeyboardButton('Посмотреть задание', callback_data=f'/get_task?id={_id}')
    button1 = InlineKeyboardButton('Изменить задание', callback_data=f'/update_task?id={_id}')
    button2 = InlineKeyboardButton('Удалить задание', callback_data=f'/remove_task?id={_id}')
    button4 = InlineKeyboardButton('Добавить решение', callback_data=f'/add_solution?id={_id}')
    button5 = InlineKeyboardButton('Главное меню', callback_data='/menu')
    inline_buttons = InlineKeyboardMarkup(row_width=2).row(button1, button2).row(button3, button4).add(button5)

    await message.answer('Задание успешно создано.', reply_markup=inline_buttons)


async def cancel_creation(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await menu(callback)


async def retrieve_task(callback: types.CallbackQuery, state: FSMContext = None):
    if state:
        await state.finish()
    id = callback['data'].split('id=')[-1]
    task = await get_task(id)
    media_group = types.MediaGroup()
    user = await get_user(task['sender'])
    inline_buttons = await task_options(id, task, callback.from_user.id)
    if len(task['photos']) != 0:
        for i in range(len(task['photos'])):
            if i == 0:
                media_group.attach_photo(task['photos'][i],
                                         f'Задание на {".".join(task["deadline"].split("-")[::-1])} по предмету {task["subject"]}:\n\nОписание: {task["description"]}\n\nОтправитель: {" ".join(user["full_name"].split()[:2])}')
            else:
                media_group.attach_photo(task['photos'][i])

        await callback.message.answer_media_group(media_group)
    else:
        await callback.message.answer(
            f'Задание на {".".join(task["deadline"].split("-")[::-1])} по предмету {task["subject"]}:\n\nОписание: {task["description"]}\n\nОтправитель: {" ".join(user["full_name"].split()[:2])}')

    await callback.message.answer('Выберите один из предложенных вариантов: ', reply_markup=inline_buttons)
    await callback.answer()


async def update_task(callback: types.CallbackQuery):
    id = callback['data'].split('id=')[-1]
    inline_buttons = await change_options(id)
    await callback.message.delete()
    await callback.message.answer('Выберите параметры, которые хотите изменить.', reply_markup=inline_buttons)
    await callback.answer()


async def update_description(callback: types.CallbackQuery, state: FSMContext):
    await UpdateTaskState.description.set()
    await callback.message.delete()
    await callback.message.answer('Введите новое описание: ')
    async with state.proxy() as data:
        data['id'] = callback['data'].split('id=')[-1]
    await callback.answer()


async def post_new_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
        id = data['task_id']
        del data['id']
        await patch_task(id, dict(data))
    await state.finish()
    await message.answer('Описание успешно изменено!')
    await sleep(1)
    inline_buttons = await change_options(id)
    await message.answer('Выберите параметры, которые хотите изменить.', reply_markup=inline_buttons)


async def update_deadline(callback: types.CallbackQuery, state: FSMContext):
    await UpdateTaskState.deadline.set()
    await callback.message.delete()
    await callback.message.answer('Введите новый дедлайн в формате DD.MM.YYYY или DD.MM: ')
    async with state.proxy() as data:
        data['id'] = callback['data'].split('id=')[-1]
    await callback.answer()


async def post_new_deadline(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        response = await check_deadline(data, message)
        if not response:
            return
        data['deadline'] = response
        id = data['id']
        del data['id']
        await patch_task(id, dict(data))
    await state.finish()
    await message.answer('Дедлайн успешно изменен!')
    await sleep(1)
    inline_buttons = await change_options(id)
    await message.answer('Выберите параметры, которые хотите изменить.', reply_markup=inline_buttons)


async def update_photos(callback: types.CallbackQuery, state: FSMContext):
    await UpdateTaskState.photos.set()
    async with state.proxy() as data:
        data['id'] = callback['data'].split('id=')[-1]
    button1 = InlineKeyboardButton('Да', callback_data='Да')
    button2 = InlineKeyboardButton('Нет', callback_data='Нет')
    inline_buttons = InlineKeyboardMarkup(row_width=2).row(button1, button2)
    await callback.message.delete()
    await callback.message.answer('Вы хотите оставить старые изображения?', reply_markup=inline_buttons)
    await callback.answer()


async def get_verification(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback['data'] == 'Да':
            task = await get_task(data['id'])
            data['photos'] = task['photos']
        else:
            data['photos'] = []
        await callback.message.delete()
        button = InlineKeyboardButton('Пропустить', callback_data='/skip')
        inline_buttons = InlineKeyboardMarkup(row_width=2).add(button)
        await callback.message.answer(
            'Отправьте фото и нажмите на кнопку: Пропустить\n Или нажмите на кнопку сразу, если отправлять фото нет необходимости.',
            reply_markup=inline_buttons)
    await callback.answer()


async def get_updated_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photos'].append(message.photo[-1].file_id)


async def update_skip(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        id = data['id']
        del data['id']
        await patch_task(id, dict(data))

    await state.finish()
    await callback.message.answer('Изображения успешно изменены!')
    await sleep(1)
    inline_buttons = await change_options(id)
    await callback.message.answer('Выберите параметры, которые хотите изменить.', reply_markup=inline_buttons)
    await callback.answer()


async def finish(callback: types.CallbackQuery):
    await retrieve_task(callback)


async def remove_task(callback: types.CallbackQuery):
    id = callback['data'].split('id=')[-1]
    button1 = InlineKeyboardButton('Да', callback_data=f'/verify_removal?id={id}')
    button2 = InlineKeyboardButton('Нет', callback_data=f'/unverify_removal?id={id}')
    inline_buttons = InlineKeyboardMarkup(row_width=2).row(button1, button2)
    await callback.message.delete()
    await callback.message.answer('Вы уверены, что хотите удалить задание?', reply_markup=inline_buttons)
    await callback.answer()


async def verify_removal(callback: types.CallbackQuery):
    if callback['data'].split('?id=')[0] == '/verify_removal':
        id = callback['data'].split('?id=')[-1]
        await delete_task(id)
        user = await get_user(callback.from_user.id)
        inline_buttons = await default_inline(user)
        await callback.message.delete()
        await callback.message.answer('Задание было успешно удалено.')
        await sleep(1)
        await callback.message.answer('Выберите один из предложенных вариантов.', reply_markup=inline_buttons)
        await callback.answer()
    else:
        await retrieve_task(callback)


async def show_tasks(callback):
    user = await get_user(callback.from_user.id)
    inline_buttons = await show_filter(user)
    if type(callback) == types.Message:
        await callback.answer('По какому параметру показать задания:', reply_markup=inline_buttons)
    else:
        await callback.message.delete()
        await callback.message.answer('По какому параметру показать задания:', reply_markup=inline_buttons)
        await callback.answer()


async def choose_subject(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    inline_buttons = await choose_subject_inline(user['group'])
    await GetTaskState.subject.set()
    await callback.message.delete()
    await callback.message.answer('Выберите нужный предмет:', reply_markup=inline_buttons)
    await callback.answer()


async def show_by_parameter(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    parameter, group = callback['data'].split('?offset=')[0], user['group']
    offset = int(callback['data'].split('?offset=')[-1])
    try:
        deadline = datetime.datetime.strptime(parameter, '%Y-%m-%d')
        tasks = await get_tasks_by_deadline(deadline, group)
        async with state.proxy() as data:
            data['deadline'] = deadline
    except ValueError:
        subject = parameter
        tasks = await get_tasks_by_subject(subject, group)
        async with state.proxy() as data:
            data['subject'] = subject
    await send_tasks(callback, offset, parameter, tasks)


async def send_tasks(callback, offset, parameter, tasks):
    if len(tasks) > 6:
        tasks_with_offset = await get_tasks_with_offset(tasks, offset)
    else:
        tasks_with_offset = await get_tasks_with_offset(tasks)
    inline_buttons = await get_tasks_inline(len(tasks), tasks_with_offset, offset, parameter)
    await callback.message.delete()
    await callback.message.answer(f'{await put_together_message(tasks_with_offset)}', reply_markup=inline_buttons)
    await callback.answer()


async def choose_deadline(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    available_deadlines = await get_available_deadlines(user['group'])
    inline_buttons = await choose_deadline_inline(available_deadlines)
    inline_buttons.add(InlineKeyboardButton('Меню', callback_data='/menu'))
    await GetTaskState.deadline.set()
    await callback.message.delete()
    await callback.message.answer('Выбери дату завершения задания:', reply_markup=inline_buttons)
    await callback.answer()


async def show_tasks_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.answer()
    await menu(callback)


async def show_all_current_tasks(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    offset = int(callback['data'].split('?offset=')[-1])
    parameter = '/show_by_group'
    tasks = await get_all_current_tasks_inline(user['group'])
    await GetTaskState.task.set()
    await send_tasks(callback, offset, parameter, tasks)


async def show_tasks_by_user(callback: types.CallbackQuery):
    offset = int(callback['data'].split('?offset=')[-1])
    parameter = '/show_by_user'
    tasks = await get_tasks_by_user(callback.from_user.id)
    await GetTaskState.task.set()
    await send_tasks(callback, offset, parameter, tasks)


async def show_all_finished_tasks(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    offset = int(callback['data'].split('?offset=')[-1])
    parameter = '/show_by_timeout'
    tasks = await get_all_finished_tasks(user['group'])
    await GetTaskState.task.set()
    await send_tasks(callback, offset, parameter, tasks)


async def add_solution(callback: types.CallbackQuery, state: FSMContext):
    task_id = callback['data'].split('?id=')[-1]
    async with state.proxy() as data:
        data['task_id'] = task_id
    await SolutionState.description.set()
    await callback.message.delete()
    inline_buttons = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('Отмена', callback_data=f'/get_task?id={task_id}'))
    await callback.message.answer('Введите описание решения: ', reply_markup=inline_buttons)
    await callback.answer()


async def add_description_solution(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
        data['photos'] = list()
    await SolutionState.next()
    button = InlineKeyboardButton('Пропустить', callback_data='/skip')
    inline_buttons = InlineKeyboardMarkup(row_width=2).add(button).add(InlineKeyboardButton('Отмена', callback_data=f'/get_task?id={data["task_id"]}'))
    await message.answer(
        'Отправьте фото и нажмите на кнопку: Пропустить\nИли нажмите на кнопку сразу, если отправлять фото нет '
        'необходимости.',
        reply_markup=inline_buttons)


async def skip_solution(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        task = await get_task(data['task_id'])
        solution = {
            'description': data['description'],
            'photos': data['photos'],
            'sender': callback.from_user.id
        }
        task['solution'].append(solution)
        inline_buttons = await get_solution_inline(data['task_id'])
        id = data['task_id']
        del data['task_id']
        await patch_task(str(id), task)
    await state.finish()
    await callback.message.answer('Решение успешно добавлено!', reply_markup=inline_buttons)
    await callback.answer()


async def retrieve_solutions(callback: types.CallbackQuery):
    task_id = callback['data'].split('?id=')[-1]
    task = await get_task(task_id)
    user = await get_user(callback.from_user.id)
    inline_buttons = await solutions_options(task, user)
    message = await get_solution_message_together(task)
    await callback.message.delete()
    await callback.message.answer(message, reply_markup=inline_buttons)
    await callback.answer()


async def retrieve_solution(callback: types.CallbackQuery, state: FSMContext = None):
    if state:
        await state.finish()
    task_id = callback['data'].split('?')[1].replace('id=', '')
    solution_number = int(callback['data'].split('?')[2].replace('number=', ''))
    task = await get_task(task_id)
    user = await get_user(callback.from_user.id)
    inline_buttons = await solution_options(task, user, solution_number)
    message = await get_solution_message(task, solution_number)
    await callback.message.delete()
    if len(task['solution'][solution_number]['photos']) == 0:
        await callback.message.answer(message)
    else:
        media_group = types.MediaGroup()
        for i in range(len(task['solution'][solution_number]['photos'])):
            if i == 0:
                media_group.attach_photo(task['solution'][solution_number]['photos'][i], message)
            else:
                media_group.attach_photo(task['solution'][solution_number]['photos'][i])
        await callback.message.answer_media_group(media_group)
    await callback.message.answer('Выберите один из предложенных вариантов:', reply_markup=inline_buttons)
    await callback.answer()


async def update_solution(callback: types.CallbackQuery):
    task_id = callback['data'].split('?')[1].replace('id=', '')
    solution_number = int(callback['data'].split('?')[2].replace('number=', ''))
    await callback.message.delete()
    inline_buttons = await update_solution_options(task_id, solution_number)
    await callback.message.answer('Выберите параметры, которые хотите изменить:', reply_markup=inline_buttons)


async def update_solution_description(callback: types.CallbackQuery, state: FSMContext):
    task_id = callback['data'].split('?')[1].replace('id=', '')
    solution_number = int(callback['data'].split('?')[2].replace('number=', ''))
    async with state.proxy() as data:
        data['task_id'] = task_id
        data['number'] = solution_number
    await UpdateSolutionState.description.set()
    await callback.message.delete()
    inline_buttons = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('Отмена', callback_data=f'/cancel_sol_update?id={task_id}?number={solution_number}'))
    await callback.message.answer('Введите новое описание:', reply_markup=inline_buttons)
    await callback.answer()


async def post_updated_solution_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        task = await get_task(data['task_id'])
        task['solution'][data['number']]['description'] = message.text
        del task['_id']
        await patch_task(data['task_id'], task)
        inline_buttons = await update_solution_options(data['task_id'], data['number'])
    await state.finish()
    await message.answer('Описание успешно изменено!')
    await sleep(1)
    await message.answer('Выберите параметры, которые хотите изменить.', reply_markup=inline_buttons)


async def update_solution_photos(callback: types.CallbackQuery, state: FSMContext):
    await UpdateSolutionState.photos.set()
    task_id = callback['data'].split('?')[1].replace('id=', '')
    solution_number = int(callback['data'].split('?')[2].replace('number=', ''))
    async with state.proxy() as data:
        data['task_id'] = task_id
        data['number'] = solution_number
    button1 = InlineKeyboardButton('Да', callback_data='Да')
    button2 = InlineKeyboardButton('Нет', callback_data='Нет')
    inline_buttons = InlineKeyboardMarkup(row_width=2).row(button1, button2)
    await callback.message.delete()
    await callback.message.answer('Вы хотите оставить старые изображения?', reply_markup=inline_buttons)
    await callback.answer()


async def get_solution_verification(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback['data'] == 'Да':
            task = await get_task(data['task_id'])
            data['photos'] = task['solution'][data['number']]['photos']
        else:
            data['photos'] = []
        await callback.message.delete()
        button = InlineKeyboardButton('Пропустить', callback_data='/skip')
        inline_buttons = InlineKeyboardMarkup(row_width=2).add(button)
        await callback.message.answer(
            'Отправьте фото и нажмите на кнопку: Пропустить\n Или нажмите на кнопку сразу, если отправлять фото нет необходимости.',
            reply_markup=inline_buttons)
    await callback.answer()


async def update_solution_skip(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        task = await get_task(data['task_id'])
        del task['_id']
        task['solution'][data['number']]['photos'] = data['photos']
        await patch_task(data['task_id'], task)
        inline_buttons = await update_solution_options(data['task_id'], data['number'])
    await state.finish()
    await callback.message.answer('Изображения успешно изменены!')
    await sleep(1)
    await callback.message.answer('Выберите параметры, которые хотите изменить.', reply_markup=inline_buttons)
    await callback.answer()


async def cancel_solution_update(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.answer()
    await retrieve_solution(callback, None)


async def delete_solution(callback: types.CallbackQuery, state: FSMContext):
    task_id = callback['data'].split('?')[1].replace('id=', '')
    solution_number = int(callback['data'].split('?')[2].replace('number=', ''))
    async with state.proxy() as data:
        data['task_id'] = task_id
        data['number'] = solution_number
    await DeleteSolutionState.verify.set()
    button1 = InlineKeyboardButton('Да', callback_data='/verify')
    button2 = InlineKeyboardButton('Нет', callback_data='/cancel')
    inline_buttons = InlineKeyboardMarkup(row_width=2).row(button1, button2)
    await callback.message.answer('Вы уверены, что хотите удалить решение?', reply_markup=inline_buttons)
    await callback.message.delete()
    await callback.answer()


async def get_delete_verification(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        task = await get_task(data['task_id'])
        user = await get_user(callback.from_user.id)
        inline_buttons = await task_options(data['task_id'], task, user['user_id'])
        if callback['data'] == '/verify':
            del task['solution'][data['number']]
            del task['_id']
            await patch_task(data['task_id'], task)
    await callback.message.answer('Выбери один из предложенных вариантов.', reply_markup=inline_buttons)
    await callback.message.delete()
    await state.finish()
    await callback.answer()


async def command_create_task(message: types.Message):
    await message.delete()
    await create_task(message, None)


async def command_show_tasks(message: types.Message):
    await message.delete()
    await show_tasks(message)


def tasks_handlers_register(dp: Dispatcher):
    dp.register_callback_query_handler(create_task, text='/create_task', state=None)
    dp.register_callback_query_handler(cancel_creation, text='/cancel', state=[TaskState, None])
    dp.register_callback_query_handler(get_subject, state=TaskState.subject)
    dp.register_message_handler(get_description, state=TaskState.description)
    dp.register_message_handler(get_photos, content_types=['photo'], state=[TaskState.photos, SolutionState.photos, UpdateTaskState, UpdateSolutionState])
    dp.register_callback_query_handler(skip, text='/skip', state=TaskState.photos)
    dp.register_callback_query_handler(get_is_solvable, text=['Да', 'Нет'], state=TaskState.is_solvable)
    dp.register_message_handler(get_deadline, state=TaskState.deadline)
    dp.register_callback_query_handler(retrieve_task, Text(startswith='/get_task?id='), state=[None, GetTaskState, SolutionState])
    dp.register_callback_query_handler(update_task, Text(startswith='/update_task?id='), state=None)
    dp.register_callback_query_handler(update_description, Text(startswith='/update_description?id='))
    dp.register_message_handler(post_new_description, state=UpdateTaskState.description)
    dp.register_callback_query_handler(update_deadline, Text(startswith='/update_deadline?id='), state=None)
    dp.register_message_handler(post_new_deadline, state=UpdateTaskState.deadline)
    dp.register_callback_query_handler(update_photos, Text(startswith='/update_photos?id='), state=None)
    dp.register_callback_query_handler(get_verification, text=['Да', 'Нет'], state=UpdateTaskState.photos)
    dp.register_callback_query_handler(update_skip, text='/skip', state=UpdateTaskState.photos)
    dp.register_callback_query_handler(finish, Text(startswith='/finish?id='))
    dp.register_callback_query_handler(remove_task, Text(startswith='/remove_task?id='))
    dp.register_callback_query_handler(verify_removal, Text(contains='verify_removal'))
    dp.register_callback_query_handler(show_tasks, text='/show_tasks')
    dp.register_callback_query_handler(choose_subject, text='/show_by_subject', state=None)
    dp.register_callback_query_handler(show_all_current_tasks, Text(contains='/show_by_group?offset='), state=[None, GetTaskState])
    dp.register_callback_query_handler(show_tasks_by_user, Text(contains='/show_by_user?offset='), state=[None, GetTaskState, SolutionState])
    dp.register_callback_query_handler(show_all_finished_tasks, Text(contains='/show_by_timeout?offset='), state=[None, GetTaskState])
    dp.register_callback_query_handler(show_by_parameter, Text(contains='?offset='), state=GetTaskState)
    dp.register_callback_query_handler(show_tasks_cancel, text='/menu', state=GetTaskState)
    dp.register_callback_query_handler(choose_deadline, text='/show_by_deadline', state=None)
    dp.register_callback_query_handler(add_solution, Text(startswith='/add_solution?id='), state=None)
    dp.register_message_handler(add_description_solution, state=SolutionState.description)
    dp.register_callback_query_handler(skip_solution, text='/skip', state=SolutionState.photos)
    dp.register_callback_query_handler(retrieve_solutions, Text(startswith='/get_solutions?id='))
    dp.register_callback_query_handler(retrieve_solution, Text(contains=['/get_solution', '?number=']), state=[None, SolutionState, UpdateSolutionState])
    dp.register_callback_query_handler(update_solution, Text(startswith='/update_solution?id='), state=None)
    dp.register_callback_query_handler(update_solution_description, Text(startswith='/update_sol_description?id='), state=None)
    dp.register_message_handler(post_updated_solution_description, state=UpdateSolutionState.description)
    dp.register_callback_query_handler(update_solution_photos, Text(startswith='/update_sol_photos?id='), state=None)
    dp.register_callback_query_handler(get_solution_verification, text=['Да', 'Нет'], state=UpdateSolutionState.photos)
    dp.register_callback_query_handler(update_solution_skip, text='/skip', state=UpdateSolutionState.photos)
    dp.register_callback_query_handler(cancel_solution_update, Text(startswith='/cancel_sol_update?id='), state=[None, UpdateSolutionState])
    dp.register_callback_query_handler(delete_solution, Text(startswith='/remove_solution?id='), state=None)
    dp.register_callback_query_handler(get_delete_verification, text=['/verify', '/cancel'], state=DeleteSolutionState)
    dp.register_message_handler(command_create_task, commands=['create_task'])
    dp.register_message_handler(command_show_tasks, commands=['show_tasks'])