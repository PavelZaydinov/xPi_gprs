from sim900 import Message, Call
import json


class DB:

    def __init__(self, message: str = 'message.txt', calls: str = 'phone.txt'):
        self.message = message
        self.calls = calls

    def save_message(self, msg: Message) -> bool:
        try:
            with open(self.message, 'a') as f:
                f.write(json.dumps(msg, default=dict) + '\r\n')
            return True
        except Exception as e:
            print(f'Error saving the message: {e}')
            return False

    def get_all_message(self) -> list[Message]:
        with open(self.message, 'r') as f:
            return [Message(**json.loads(m)) for m in f.readlines()]

    def save_call(self, call: Call) -> bool:
        try:
            with open(self.calls, 'a') as f:
                f.write(json.dumps(call, default=dict) + '\r\n')
            return True
        except Exception as e:
            print(f'Error saving the call: {e}')
            return False
