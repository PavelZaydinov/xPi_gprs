from json import dumps


class Log:

    def __init__(self) -> None:
        self.debug = True
        self.log: list = []
        self.max_len: int = 1500

    def __call__(self, log: str) -> None:
        self.write(log)
        if self.debug:
            self.print()

    def print(self) -> None:
        print(self.log[-1])

    def write(self, log: str) -> None:
        self.log.append(log)
        ll = len(self.log)
        if ll > self.max_len:
            self.log = self.log[ll - 500:ll]

    def save(self, file_name: str = 'log.txt') -> None:
        with open(file_name, 'a') as f:
            f.write(dumps(self.log) + '\r\n')
