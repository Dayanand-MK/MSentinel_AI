from services import ChatService

class ChatController:
    def __init__(self):
        self.chat = ChatService()

    def ask(self, question):
        return self.chat.ask(question)