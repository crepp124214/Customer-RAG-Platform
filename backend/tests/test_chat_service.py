from __future__ import annotations

from backend.app.exceptions import AppError
from backend.app.models import Message, Session as ChatSession
from backend.app.services.chat_service import ChatService
from backend.app.services.customer_service_qa import QAResult
from backend.app.services.retrieval_service import RetrievedChunk
from backend.infrastructure.database import create_database_engine, create_session_factory, initialize_database
from backend.tests.support import create_workspace_temp_dir


class FakeChatClient:
    def __init__(self, response: str = "自动生成的标题") -> None:
        self.response = response
        self.calls: list[dict] = []

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls.append({"system_prompt": system_prompt, "user_prompt": user_prompt})
        return self.response


class FakeQAService:
    def __init__(self, result: QAResult, *, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.queries: list[str] = []

    def answer(self, db_session, *, query: str, session_id: str, product_id: str | None = None) -> QAResult:
        self.queries.append(query)
        if self.error is not None:
            raise self.error
        return self.result


def create_session_record(session_factory, *, title: str = "新会话") -> str:
    with session_factory() as db_session:
        session = ChatSession(title=title)
        db_session.add(session)
        db_session.commit()
        return session.id


def test_create_session_persists_default_title() -> None:
    temp_dir = create_workspace_temp_dir("chat-service")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    service = ChatService(qa_service=FakeQAService(QAResult(answer="ok", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None)))

    with session_factory() as db_session:
        session = service.create_session(db_session)

    engine.dispose()

    assert session.title == "新会话"


def test_query_persists_messages_and_updates_title_from_first_query() -> None:
    temp_dir = create_workspace_temp_dir("chat-service")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    qa_service = FakeQAService(
        QAResult(
            answer="这是回答",
            intent="fault_diagnosis",
            citations=[
                RetrievedChunk(
                    chunk_id="chunk-1",
                    document_id="doc-1",
                    document_name="demo.txt",
                    chunk_index=0,
                    content="片段",
                    page_number=1,
                    source_type="text",
                    asset_label=None,
                    preview_available=False,
                    score=0.9,
                )
            ],
            diagnosis={"sop_id": "sop-1", "current_step": {"description": "检查电源"}, "current_step_index": 0, "total_steps": 3},
            similar_tickets=None,
        )
    )
    service = ChatService(qa_service=qa_service)
    session_id = create_session_record(session_factory)

    with session_factory() as db_session:
        qa_result, user_message, assistant_message = service.query(
            db_session,
            session_id=session_id,
            query="这是第一条问题，会自动生成会话标题",
        )

        stored_session = db_session.get(ChatSession, session_id)
        stored_messages = db_session.query(Message).filter(Message.session_id == session_id).all()

    engine.dispose()

    assert qa_result.answer == "这是回答"
    assert user_message.role == "user"
    assert assistant_message.role == "assistant"
    assert len(stored_messages) == 2
    assert stored_session is not None
    assert stored_session.title.startswith("这是第一条问题")
    assert stored_messages[0].citations == []
    assert stored_messages[0].tool_calls == []
    assert stored_messages[1].citations[0]["document_id"] == "doc-1"
    assert stored_messages[1].tool_calls[0]["tool_name"] == "fault_diagnosis"


def test_query_keeps_existing_title_after_first_message() -> None:
    temp_dir = create_workspace_temp_dir("chat-service")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    qa_service = FakeQAService(QAResult(answer="这是回答", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None))
    service = ChatService(qa_service=qa_service)
    session_id = create_session_record(session_factory, title="初始标题")

    with session_factory() as db_session:
        service.query(db_session, session_id=session_id, query="第一条问题")
        session_after_first = db_session.get(ChatSession, session_id)
        first_title = session_after_first.title if session_after_first else ""

        service.query(db_session, session_id=session_id, query="第二条问题")
        session_after_second = db_session.get(ChatSession, session_id)
        stored_messages = db_session.query(Message).filter(Message.session_id == session_id).all()

    engine.dispose()

    assert first_title.startswith("第一条问题")
    assert session_after_second is not None
    assert session_after_second.title == first_title
    assert len(stored_messages) == 4


def test_list_sessions_raises_for_missing_session() -> None:
    temp_dir = create_workspace_temp_dir("chat-service")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    service = ChatService(qa_service=FakeQAService(QAResult(answer="ok", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None)))

    with session_factory() as db_session:
        try:
            service.list_messages(db_session, session_id="missing")
        except AppError as exc:
            assert exc.code == "session_not_found"
        else:  # pragma: no cover
            raise AssertionError("expected session_not_found")

    engine.dispose()


def test_query_does_not_persist_partial_messages_when_qa_fails() -> None:
    temp_dir = create_workspace_temp_dir("chat-service")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    service = ChatService(
        qa_service=FakeQAService(
            QAResult(answer="unused", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None),
            error=AppError("问答失败", code="qa_failed", status_code=502),
        )
    )
    session_id = create_session_record(session_factory)

    with session_factory() as db_session:
        try:
            service.query(db_session, session_id=session_id, query="会失败的问题")
        except AppError as exc:
            assert exc.code == "qa_failed"
        else:  # pragma: no cover
            raise AssertionError("expected qa_failed")

        stored_messages = db_session.query(Message).filter(Message.session_id == session_id).all()

    engine.dispose()

    assert stored_messages == []


def test_stream_query_emits_events_and_persists_messages() -> None:
    temp_dir = create_workspace_temp_dir("chat-stream-service")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    qa_service = FakeQAService(
        QAResult(
            answer="流式回答",
            intent="fault_diagnosis",
            citations=[
                RetrievedChunk(
                    chunk_id="chunk-1",
                    document_id="doc-1",
                    document_name="demo.txt",
                    chunk_index=0,
                    content="片段",
                    page_number=1,
                    source_type="image",
                    asset_label="第 1 页图片 1",
                    preview_available=True,
                    score=0.9,
                )
            ],
            diagnosis={"sop_id": "sop-1", "current_step": {"description": "检查电源"}, "current_step_index": 0, "total_steps": 3},
            similar_tickets=None,
        )
    )
    service = ChatService(qa_service=qa_service)
    session_id = create_session_record(session_factory)

    with session_factory() as db_session:
        events = list(service.stream_query(db_session, session_id=session_id, query="请给出结论"))
        stored_messages = db_session.query(Message).filter(Message.session_id == session_id).all()

    engine.dispose()

    assert [event.event for event in events] == ["message_start", "citation", "tool_call", "tool_result", "token", "message_end"]
    assert events[1].data["document_id"] == "doc-1"
    assert events[1].data["source_type"] == "image"
    assert events[2].data["tool_name"] == "fault_diagnosis"
    assert events[3].data["status"] == "completed"
    assert events[4].data["content"] == "流式回答"
    assert len(stored_messages) == 2
    assert stored_messages[0].role == "user"
    assert stored_messages[1].role == "assistant"
    assert stored_messages[1].citations[0]["document_id"] == "doc-1"
    assert stored_messages[1].citations[0]["source_type"] == "image"
    assert stored_messages[1].tool_calls[0]["tool_name"] == "fault_diagnosis"


def test_stream_query_returns_error_event_and_rolls_back() -> None:
    temp_dir = create_workspace_temp_dir("chat-stream-service")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    service = ChatService(
        qa_service=FakeQAService(
            QAResult(answer="unused", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None),
            error=AppError("流式失败", code="stream_failed", status_code=502),
        )
    )
    session_id = create_session_record(session_factory)

    with session_factory() as db_session:
        events = list(service.stream_query(db_session, session_id=session_id, query="失败问题"))
        stored_messages = db_session.query(Message).filter(Message.session_id == session_id).all()

    engine.dispose()

    assert len(events) == 1
    assert events[0].event == "error"
    assert events[0].data["code"] == "stream_failed"
    assert stored_messages == []


def test_stream_query_emits_tool_events_and_summary() -> None:
    temp_dir = create_workspace_temp_dir("chat-stream-tool-service")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    qa_service = FakeQAService(
        QAResult(
            answer="这是带工具的回答",
            intent="ticket_query",
            citations=[],
            diagnosis=None,
            similar_tickets=[
                {
                    "id": "ticket-1",
                    "title": "设备无法启动",
                    "status": "resolved",
                    "priority": "high",
                    "solution": "更换电源模块",
                }
            ],
        )
    )
    service = ChatService(qa_service=qa_service)
    session_id = create_session_record(session_factory)

    with session_factory() as db_session:
        events = list(service.stream_query(db_session, session_id=session_id, query="今天最新消息"))

    engine.dispose()

    assert [event.event for event in events] == ["message_start", "tool_call", "tool_result", "token", "message_end"]
    assert events[1].data["tool_name"] == "ticket_search"
    assert events[2].data["status"] == "completed"
    assert events[-1].data["tool_calls"][0]["tool_name"] == "ticket_search"


def test_update_session_changes_title() -> None:
    temp_dir = create_workspace_temp_dir("chat-service-update")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    service = ChatService(qa_service=FakeQAService(QAResult(answer="ok", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None)))
    session_id = create_session_record(session_factory, title="旧标题")

    with session_factory() as db_session:
        updated_session = service.update_session(db_session, session_id=session_id, title="新标题")

    engine.dispose()

    assert updated_session.title == "新标题"


def test_update_session_raises_for_missing_session() -> None:
    temp_dir = create_workspace_temp_dir("chat-service-update")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    service = ChatService(qa_service=FakeQAService(QAResult(answer="ok", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None)))

    with session_factory() as db_session:
        try:
            service.update_session(db_session, session_id="missing", title="新标题")
        except AppError as exc:
            assert exc.code == "session_not_found"
        else:  # pragma: no cover
            raise AssertionError("expected session_not_found")

    engine.dispose()


def test_search_sessions_filters_by_keyword() -> None:
    temp_dir = create_workspace_temp_dir("chat-service-search")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    service = ChatService(qa_service=FakeQAService(QAResult(answer="ok", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None)))
    create_session_record(session_factory, title="Python 编程问题")
    create_session_record(session_factory, title="JavaScript 开发")
    create_session_record(session_factory, title="Python 数据分析")

    with session_factory() as db_session:
        results = service.search_sessions(db_session, keyword="Python")

    engine.dispose()

    assert len(results) == 2
    assert all("Python" in session.title for session in results)


def test_search_sessions_returns_all_when_keyword_empty() -> None:
    temp_dir = create_workspace_temp_dir("chat-service-search")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    service = ChatService(qa_service=FakeQAService(QAResult(answer="ok", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None)))
    create_session_record(session_factory, title="会话1")
    create_session_record(session_factory, title="会话2")

    with session_factory() as db_session:
        results = service.search_sessions(db_session, keyword="")

    engine.dispose()

    assert len(results) == 2


def test_generate_session_title_uses_llm_when_available() -> None:
    temp_dir = create_workspace_temp_dir("chat-service-title")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    chat_client = FakeChatClient(response="LLM生成的标题")
    service = ChatService(qa_service=FakeQAService(QAResult(answer="ok", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None)), chat_client=chat_client)
    session_id = create_session_record(session_factory)

    with session_factory() as db_session:
        service.query(db_session, session_id=session_id, query="如何学习Python")
        title = service.generate_session_title(db_session, session_id=session_id)

    engine.dispose()

    assert title == "LLM生成的标题"
    assert len(chat_client.calls) == 1


def test_generate_session_title_falls_back_when_llm_fails() -> None:
    temp_dir = create_workspace_temp_dir("chat-service-title")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    class FailingChatClient:
        def generate(self, *, system_prompt: str, user_prompt: str) -> str:
            raise Exception("LLM调用失败")

    service = ChatService(qa_service=FakeQAService(QAResult(answer="ok", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None)), chat_client=FailingChatClient())
    session_id = create_session_record(session_factory)

    with session_factory() as db_session:
        service.query(db_session, session_id=session_id, query="这是一个很长的问题用于测试标题生成")
        title = service.generate_session_title(db_session, session_id=session_id)

    engine.dispose()

    assert title.startswith("这是一个很长的问题")


def test_generate_session_title_raises_for_empty_session() -> None:
    temp_dir = create_workspace_temp_dir("chat-service-title")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    service = ChatService(qa_service=FakeQAService(QAResult(answer="ok", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None)))
    session_id = create_session_record(session_factory)

    with session_factory() as db_session:
        try:
            service.generate_session_title(db_session, session_id=session_id)
        except AppError as exc:
            assert exc.code == "session_empty"
        else:  # pragma: no cover
            raise AssertionError("expected session_empty")

    engine.dispose()


def test_export_session_markdown_includes_messages_and_citations() -> None:
    temp_dir = create_workspace_temp_dir("chat-service-export")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    qa_service = FakeQAService(
        QAResult(
            answer="这是回答",
            intent="knowledge_query",
            citations=[
                RetrievedChunk(
                    chunk_id="chunk-1",
                    document_id="doc-1",
                    document_name="demo.txt",
                    chunk_index=0,
                    content="这是引用内容",
                    page_number=1,
                    source_type="text",
                    asset_label=None,
                    preview_available=False,
                    score=0.9,
                )
            ],
            diagnosis=None,
            similar_tickets=None,
        )
    )
    service = ChatService(qa_service=qa_service)
    session_id = create_session_record(session_factory, title="测试会话")

    with session_factory() as db_session:
        service.query(db_session, session_id=session_id, query="测试问题")
        service.update_session(db_session, session_id=session_id, title="测试会话")
        title, markdown = service.export_session_markdown(db_session, session_id=session_id)

    engine.dispose()

    assert title == "测试会话"
    assert "# 测试会话" in markdown
    assert "## 用户" in markdown
    assert "测试问题" in markdown
    assert "## 助手" in markdown
    assert "这是回答" in markdown
    assert "### 引用" in markdown
    assert "demo.txt" in markdown
    assert "这是引用内容" in markdown


def test_export_session_markdown_raises_for_missing_session() -> None:
    temp_dir = create_workspace_temp_dir("chat-service-export")
    engine = create_database_engine(f"sqlite+pysqlite:///{(temp_dir / 'chat.sqlite3').resolve()}")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    service = ChatService(qa_service=FakeQAService(QAResult(answer="ok", intent="knowledge_query", citations=[], diagnosis=None, similar_tickets=None)))

    with session_factory() as db_session:
        try:
            service.export_session_markdown(db_session, session_id="missing")
        except AppError as exc:
            assert exc.code == "session_not_found"
        else:  # pragma: no cover
            raise AssertionError("expected session_not_found")

    engine.dispose()
