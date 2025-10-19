from pydesk.todo import add_task, list_tasks, mark_done, load_tasks, save_tasks

def test_add_task():
    save_tasks([])  # reset
    add_task("Test task")
    tasks = load_tasks()
    assert tasks[0]["task"] == "Test task"
    assert tasks[0]["done"] == False
