import typing as t
import datetime
import threading

class Logger:
    # just some ID that can be used to uniquely identify critical errors on the 
    # server
    id = round(datetime.datetime.now().timestamp())
    inc_lock = threading.Lock()

    def __init__(self, module : str):
        self.module = module
    
    def warn(self, msg: str):
        self.log('e', msg)

    def error(self, msg: str):
        # inc support ID
        with Logger.inc_lock:
            Logger.id += 1
            next_id = hex(Logger.id)

        # the number converted in hex is 0x... we need to remove the 0x
        # from the support ID
        support_id = next_id[2:]

        # print the complete message with support ID on the console
        self.log(f'e|{support_id}', msg)
        return support_id

    def log(self, type, msg: str):
        msg_no_line = msg.replace('\n', '').replace('\r', '')
        print(f'{type}|{self.module}|{datetime.datetime.now()}|{msg_no_line}')

    