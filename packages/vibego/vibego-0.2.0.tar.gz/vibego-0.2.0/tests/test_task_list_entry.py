import asyncio
from datetime import datetime, UTC
from types import MethodType, SimpleNamespace
import pytest
import bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Chat, InlineKeyboardMarkup, Message, User
from tasks.models import TaskRecord
from tasks.service import TaskService


class DummyCallback:
    def __init__(self, message, user, data):
        self.message = message
        self.from_user = user
        self.data = data
        self.answers = []

    async def answer(self, text=None, show_alert=False):
        self.answers.append(
            {
                "text": text,
                "show_alert": show_alert,
            }
        )

class DummyMessage:
    def __init__(self, text=""):
        self.text = text
        self.calls = []
        self.edits = []
        self.chat = SimpleNamespace(id=1)
        self.from_user = SimpleNamespace(id=1, full_name="Tester")
        self.message_id = 100

    async def answer(self, text, parse_mode=None, reply_markup=None, **kwargs):
        self.calls.append(
            {
                "text": text,
                "parse_mode": parse_mode,
                "reply_markup": reply_markup,
            }
        )
        return SimpleNamespace(message_id=len(self.calls))

    async def edit_text(self, text, parse_mode=None, reply_markup=None, **kwargs):
        self.edits.append(
            {
                "text": text,
                "parse_mode": parse_mode,
                "reply_markup": reply_markup,
            }
        )
        return SimpleNamespace(message_id=len(self.edits))


def make_state(message: DummyMessage) -> tuple[FSMContext, MemoryStorage]:
    storage = MemoryStorage()
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=999, chat_id=message.chat.id, user_id=message.from_user.id),
    )
    return state, storage

def test_task_list_view_contains_create_button(monkeypatch):
    class DummyService:
        async def paginate(self, **kwargs):
            return [], 1

        async def count_tasks(self, **kwargs):
            return 0

    monkeypatch.setattr(bot, "TASK_SERVICE", DummyService())

    text, markup = asyncio.run(bot._build_task_list_view(status=None, page=1, limit=10))

    assert text.startswith("*任务列表*")
    buttons = [button.text for row in markup.inline_keyboard for button in row]
    assert "🔍 搜索任务" in buttons
    assert "➕ 创建任务" in buttons


def test_task_list_view_renders_entries_with_icons(monkeypatch):
    task = TaskRecord(
        id="TASK_9001",
        project_slug="demo",
        title="修复登录问题",
        status="research",
        priority=2,
        task_type="task",
        tags=(),
        due_date=None,
        description="",
        parent_id=None,
        root_id="TASK_9001",
        depth=0,
        lineage="0001",
        created_at="2025-01-01T00:00:00+08:00",
        updated_at="2025-01-01T00:00:00+08:00",
        archived=False,
    )

    class DummyService:
        async def paginate(self, **kwargs):
            return [task], 1

        async def count_tasks(self, **kwargs):
            return 1

    monkeypatch.setattr(bot, "TASK_SERVICE", DummyService())

    text, markup = asyncio.run(bot._build_task_list_view(status=None, page=1, limit=10))

    assert "- 🛠️ 修复登录问题" not in text
    assert "- ⚪ 修复登录问题" not in text
    detail_buttons = [
        button.text
        for row in markup.inline_keyboard
        for button in row
        if button.callback_data and button.callback_data.startswith("task:detail")
    ]
    assert detail_buttons
    status_icon = bot._status_icon(task.status)
    type_icon = bot.TASK_TYPE_EMOJIS.get(task.task_type) or "⚪"
    expected_prefix = f"{status_icon} {type_icon} "
    assert detail_buttons[0].startswith(expected_prefix)
    assert "修复登录问题" in detail_buttons[0]


def test_task_list_create_callback_forwards_command(monkeypatch):
    dummy_bot = SimpleNamespace()
    monkeypatch.setattr(bot, "current_bot", lambda: dummy_bot)

    captured = {}

    async def fake_feed_update(bot_obj, update):
        captured["bot"] = bot_obj
        captured["update"] = update

    monkeypatch.setattr(bot.dp, "feed_update", fake_feed_update)  # type: ignore[attr-defined]

    chat = Chat.model_construct(id=1, type="private")
    bot_user = User.model_construct(id=999, is_bot=True, first_name="Bot")
    human_user = User.model_construct(id=123, is_bot=False, first_name="Tester")
    base_message = Message.model_construct(
        message_id=42,
        date=datetime.now(UTC),
        chat=chat,
        text="*任务列表*",
        from_user=bot_user,
    )
    callback = DummyCallback(base_message, human_user, bot.TASK_LIST_CREATE_CALLBACK)

    asyncio.run(bot.on_task_list_create(callback))  # type: ignore[arg-type]

    assert callback.answers and callback.answers[-1]["text"] is None
    assert captured["bot"] is dummy_bot
    update = captured["update"]
    assert update.message.text == "/task_new"
    assert update.message.from_user.id == human_user.id
    assert any(entity.type == "bot_command" for entity in update.message.entities or [])


def test_worker_create_button_triggers_task_new(monkeypatch):
    captured = {}

    async def fake_dispatch(message, actor):
        captured["message"] = message
        captured["actor"] = actor

    monkeypatch.setattr(bot, "_dispatch_task_new_command", fake_dispatch)

    chat = Chat.model_construct(id=2, type="private")
    human_user = User.model_construct(id=321, is_bot=False, first_name="Tester")
    message = Message.model_construct(
        message_id=77,
        date=datetime.now(UTC),
        chat=chat,
        text=bot.WORKER_CREATE_TASK_BUTTON_TEXT,
        from_user=human_user,
    )

    storage = MemoryStorage()
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=999, chat_id=chat.id, user_id=human_user.id),
    )

    async def _scenario():
        await state.set_state(bot.TaskCreateStates.waiting_title.state)
        await bot.on_task_create_button(message, state)
        assert await state.get_state() is None

    asyncio.run(_scenario())

    assert captured["message"] is message
    assert captured["actor"] is human_user


def test_compose_task_button_label_truncates_but_keeps_status():
    long_title = "这是一个非常长的任务标题，用于验证状态图标仍然保留在按钮末尾，不会被截断或丢失"
    task = TaskRecord(
        id="TASK_LONG",
        project_slug="demo",
        title=long_title,
        status="test",
        priority=3,
        task_type="defect",
        tags=(),
        due_date=None,
        description="",
        parent_id=None,
        root_id="TASK_LONG",
        depth=0,
        lineage="0001",
        created_at="2025-01-01T00:00:00+08:00",
        updated_at="2025-01-01T00:00:00+08:00",
        archived=False,
    )

    label = bot._compose_task_button_label(task, max_length=40)
    status_icon = bot._status_icon(task.status)
    assert status_icon
    type_icon = bot.TASK_TYPE_EMOJIS.get(task.task_type) or "⚪"
    expected_prefix = f"{status_icon} {type_icon} "
    assert label.startswith(expected_prefix)
    assert len(label) <= 40
    assert "…" in label


@pytest.mark.parametrize(
    "case",
    [
        {
            "name": "normal_case",
            "title": "修复登录问题",
            "status": "research",
            "task_type": "task",
            "max_length": 60,
            "expect_prefix": f"{bot._status_icon('research')} {bot.TASK_TYPE_EMOJIS['task']} ",
            "expect_contains": "修复登录问题",
            "expect_ellipsis": False,
        },
        {
            "name": "no_status",
            "title": "不含状态",
            "status": "",
            "task_type": "task",
            "max_length": 30,
            "expect_prefix": f"{bot.TASK_TYPE_EMOJIS['task']} ",
            "expect_contains": "不含状态",
            "expect_ellipsis": False,
        },
        {
            "name": "unknown_status",
            "title": "未知状态",
            "status": "blocked",
            "task_type": "task",
            "max_length": 30,
            "expect_prefix": f"{bot.TASK_TYPE_EMOJIS['task']} ",
            "expect_contains": "未知状态",
            "expect_ellipsis": False,
        },
        {
            "name": "no_type",
            "title": "无类型任务",
            "status": "research",
            "task_type": None,
            "max_length": 40,
            "expect_prefix": f"{bot._status_icon('research')} ⚪ ",
            "expect_contains": "无类型任务",
            "expect_ellipsis": False,
        },
        {
            "name": "long_title_truncated",
            "title": "这个标题超级超级长，需要被截断才能放进按钮里",
            "status": "test",
            "task_type": "defect",
            "max_length": 20,
            "expect_prefix": f"{bot._status_icon('test')} {bot.TASK_TYPE_EMOJIS['defect']} ",
            "expect_contains": "这个标题超级超级长",
            "expect_ellipsis": True,
        },
        {
            "name": "tight_limit",
            "title": "极短限制",
            "status": "test",
            "task_type": "risk",
            "max_length": 8,
            "expect_prefix": f"{bot._status_icon('test')} {bot.TASK_TYPE_EMOJIS['risk']} ",
            "expect_exact": "🧪 ⚠️ 极短…",
            "expect_ellipsis": True,
        },
        {
            "name": "empty_title",
            "title": "",
            "status": "done",
            "task_type": "requirement",
            "max_length": 20,
            "expect_prefix": f"{bot._status_icon('done')} {bot.TASK_TYPE_EMOJIS['requirement']} ",
            "expect_exact": "✅ 📌 -",
            "expect_ellipsis": False,
        },
        {
            "name": "emoji_title",
            "title": "🔥 紧急处理",
            "status": "done",
            "task_type": "risk",
            "max_length": 25,
            "expect_prefix": f"{bot._status_icon('done')} {bot.TASK_TYPE_EMOJIS['risk']} ",
            "expect_contains": "🔥 紧急处理",
            "expect_ellipsis": False,
        },
        {
            "name": "multibyte_length",
            "title": "多字节标题测试",
            "status": "research",
            "task_type": "defect",
            "max_length": 15,
            "expect_prefix": f"{bot._status_icon('research')} {bot.TASK_TYPE_EMOJIS['defect']} ",
            "expect_contains": "多字节标题测试",
            "expect_ellipsis": False,
        },
        {
            "name": "status_alias",
            "title": "Alias 状态",
            "status": "Research",
            "task_type": "task",
            "max_length": 30,
            "expect_prefix": f"{bot._status_icon('Research')} {bot.TASK_TYPE_EMOJIS['task']} ",
            "expect_contains": "Alias 状态",
            "expect_ellipsis": False,
        },
    ],
    ids=lambda case: case["name"],
)
def test_compose_task_button_label_various_cases(case):
    task = TaskRecord(
        id=f"TASK_CASE_{case['name']}",
        project_slug="demo",
        title=case["title"],
        status=case["status"],
        priority=3,
        task_type=case["task_type"],
        tags=(),
        due_date=None,
        description="",
        parent_id=None,
        root_id=f"TASK_CASE_{case['name']}",
        depth=0,
        lineage="0001",
        created_at="2025-01-01T00:00:00+08:00",
        updated_at="2025-01-01T00:00:00+08:00",
        archived=False,
    )

    label = bot._compose_task_button_label(task, max_length=case["max_length"])

    assert len(label) <= case["max_length"]
    expected_prefix = case.get("expect_prefix")
    if expected_prefix is not None:
        assert label.startswith(expected_prefix)
    expected_contains = case.get("expect_contains")
    if expected_contains:
        assert expected_contains.strip() in label
    if "expect_exact" in case:
        assert label == case["expect_exact"]
    if "expect_ellipsis" in case:
        if case["expect_ellipsis"]:
            assert "…" in label
        else:
            assert "…" not in label


def test_task_list_search_flow(monkeypatch):
    message = DummyMessage()
    user = SimpleNamespace(id=123, is_bot=False)
    callback = DummyCallback(message, user, f"{bot.TASK_LIST_SEARCH_CALLBACK}:-:1:10")
    state, _storage = make_state(message)

    task = TaskRecord(
        id="TASK_0001",
        project_slug="demo",
        title="修复登录问题",
        status="research",
        priority=2,
        task_type="task",
        tags=(),
        due_date=None,
        description="登录接口异常",
        parent_id=None,
        root_id="TASK_0001",
        depth=0,
        lineage="0001",
        created_at="2025-01-01T00:00:00+08:00",
        updated_at="2025-01-01T00:00:00+08:00",
        archived=False,
    )

    async def fake_search(self, keyword, *, page, page_size):
        assert keyword == "登录"
        return [task], 1, 1

    monkeypatch.setattr(
        bot.TASK_SERVICE,
        "search_tasks",
        MethodType(fake_search, bot.TASK_SERVICE),
    )

    async def _scenario():
        await bot.on_task_list_search(callback, state)  # type: ignore[arg-type]
        assert await state.get_state() == bot.TaskListSearchStates.waiting_keyword.state
        assert message.calls
        assert "请输入任务搜索关键词" in message.calls[-1]["text"]
        assert callback.answers and callback.answers[-1]["text"] == "请输入搜索关键词"

        user_message = DummyMessage(text="登录")
        await bot.on_task_list_search_keyword(user_message, state)
        assert await state.get_state() is None
        assert message.edits and "*任务搜索结果*" in message.edits[-1]["text"]
        assert "- 🛠️ 修复登录问题" not in message.edits[-1]["text"]
        assert "- ⚪ 修复登录问题" not in message.edits[-1]["text"]
        assert user_message.calls and "搜索完成" in user_message.calls[-1]["text"]
        markup: InlineKeyboardMarkup = message.edits[-1]["reply_markup"]
        detail_buttons = [
            button.text
            for row in markup.inline_keyboard
            for button in row
            if button.callback_data and button.callback_data.startswith("task:detail")
        ]
        assert detail_buttons
        status_icon = bot._status_icon(task.status)
        type_icon = bot.TASK_TYPE_EMOJIS.get(task.task_type) or "⚪"
        expected_prefix = f"{status_icon} {type_icon} "
        assert detail_buttons[0].startswith(expected_prefix)
        assert "修复登录问题" in detail_buttons[0]

    asyncio.run(_scenario())


def test_task_list_search_cancel_restores_list(monkeypatch):
    message = DummyMessage()
    user = SimpleNamespace(id=123, is_bot=False)
    callback = DummyCallback(message, user, f"{bot.TASK_LIST_SEARCH_CALLBACK}:research:2:5")
    state, _storage = make_state(message)

    async def fake_list_view(status, page, limit):
        return "*任务列表*", InlineKeyboardMarkup(inline_keyboard=[])

    monkeypatch.setattr(bot, "_build_task_list_view", fake_list_view)

    async def _scenario():
        await bot.on_task_list_search(callback, state)  # type: ignore[arg-type]
        cancel_message = DummyMessage(text="取消")
        await bot.on_task_list_search_keyword(cancel_message, state)
        assert await state.get_state() is None
        assert message.edits and "*任务列表*" in message.edits[-1]["text"]
        assert cancel_message.calls and "已返回任务列表" in cancel_message.calls[-1]["text"]

    asyncio.run(_scenario())


def test_task_service_search_tasks(tmp_path):
    db_path = tmp_path / "tasks.db"
    service = TaskService(db_path, "demo")

    async def _scenario():
        await service.initialize()
        await service.create_root_task(
            title="修复登录功能",
            status="research",
            priority=2,
            task_type="task",
            tags=(),
            due_date=None,
            description="处理登录接口报错",
            actor="tester",
        )
        await service.create_root_task(
            title="编写部署文档",
            status="test",
            priority=3,
            task_type="task",
            tags=(),
            due_date=None,
            description="wiki 文档更新",
            actor="tester",
        )
        results, pages, total = await service.search_tasks("登录", page=1, page_size=10)
        return results, pages, total

    results, pages, total = asyncio.run(_scenario())
    assert total == 1
    assert pages == 1
    assert results[0].title == "修复登录功能"


def test_task_service_search_tasks_empty_keyword(tmp_path):
    service = TaskService(tmp_path / "tasks.db", "demo")

    async def _scenario():
        await service.initialize()
        return await service.search_tasks("", page=1, page_size=10)

    results, pages, total = asyncio.run(_scenario())
    assert results == []
    assert pages == 0
    assert total == 0
