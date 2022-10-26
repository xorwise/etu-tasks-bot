from aiogram.dispatcher.filters.state import State, StatesGroup


class RegisterState(StatesGroup):
    full_name = State()
    group = State()
    is_sender = State()


class ProfileState(StatesGroup):
    full_name = State()
    group = State()
    is_sender = State()


class DeleteProfileState(StatesGroup):
    verify = State()


class TaskState(StatesGroup):
    subject = State()
    description = State()
    photos = State()
    is_solvable = State()
    deadline = State()


class UpdateTaskState(StatesGroup):
    description = State()
    photos = State()
    deadline = State()


class GetTaskState(StatesGroup):
    subject = State()
    deadline = State()
    task = State()


class SolutionState(StatesGroup):
    description = State()
    photos = State()


class UpdateSolutionState(StatesGroup):
    description = State()
    photos = State()
    verification = State()


class DeleteSolutionState(StatesGroup):
    verify = State()