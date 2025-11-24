from todoist_api_python.api import TodoistAPI

class TodoistClient(TodoistAPI):
    # def __init__(self, token, debug=False):
    #     super().__init__(token)
    #     self.debug = debug

    def get_nonscheduled_tasks(self):
        self.get_label("2181651855")