from urllib import request
from threading import Thread
from sim900 import Sim900, Call, Message, Sim900NoResponse
from json import dumps as json_dumps
from .simple_db import DB
from .simple_log import Log
from time import sleep


class RSim(Sim900):

    def __init__(self,
                 db=DB(),
                 log=Log(),
                 host: str | None = 'http://127.0.0.1:80',
                 devname: str = 'Sim900',
                 *args,
                 **kwargs
                 ) -> None:
        self.db = db
        self.log = log
        self.host = host
        self.devname = devname
        super().__init__(*args, **kwargs)

    def read(self) -> tuple[str]:
        data = super().read()
        self.log(self.buffer.decode('utf-8'))
        return data

    def save_message(self, msg: Message) -> None:
        self.db.save_message(msg)

    def save_all_messages(self) -> None:
        msg = self.get_all_sms_message()
        set(map(self.additional_function_message, msg))

    def save_call(self, call: Call) -> None:
        self.db.save_call(call)

    @staticmethod
    def additional_function(host: str, data: str) -> None:
        try:
            request.urlopen(host, data=bytes(data, 'utf-8'))
        except Exception as e:
            print(f'Error additional_function: {e} ;'
                  f'\r\nHost: {host}\r\nData:  {data}')

    def send_data(self, data) -> None:
        t = Thread(target=self.additional_function, args=(self.host, data))
        t.start()

    def preprocessing_data(self, a: str, b: dict) -> str:
        return json_dumps({**dict(incoming=a, dev=self.devname), **b})

    def additional_function_message(self, msg: Message) -> None:
        self.log(f'additional_function_message: {msg}')
        self.save_message(msg)
        self.send_data(self.preprocessing_data('Message', dict(msg)))

    def additional_function_call(self, call: Call) -> None:
        self.log(f'additional_function_call: {call}')
        self.save_call(call)
        self.send_data(self.preprocessing_data('Call', dict(call)))

    def power_on(self, pwr: str) -> None:
        with open(pwr, 'w') as f:
            f.write('1')
            sleep(2)
            f.write('0')

    def start(self, pwr: str | None = None) -> None:
        try:
            self.connect()
            self.pre_up()
        except Sim900NoResponse:
            if pwr is not None:
                self.power_on(pwr)
            sleep(5)
            self.connect()
            self.pre_up()
        self.save_all_messages()
        self.run()
