# -*- coding: utf-8 -*-

import random
import sys

class WorkersList(type):
    workers = []

    def __new__(mcs, name, bases, attrs, **kwargs):
        worker_class = super(WorkersList, mcs).__new__(mcs, name, bases, attrs)
        if '__not_bot__' not in attrs:
            WorkersList.workers.append((name, worker_class))
        return worker_class

    def get_workers(cls, list, tapi):
        workers = []
        # available = cls.workers
        for worker in cls.workers:
            exist = False
            for str in list:
                if str == worker[0]:
                    exist = True
                    break
            if not exist:
                cls.workers.remove(worker)

        for str in list:
            try:
                workers.append(getattr(sys.modules[__name__], str)(tapi))
                print(str)
            except:
                print("There isn't " + str)
        return workers


class BaseWorker(object, metaclass=WorkersList):
    __not_bot__ = True

    HELP = ""
    
    def __init__(self, teleapi):
        self.tAPI = teleapi
        self.MENU_KEYBOARD = []



class Blacklist(BaseWorker):
    # HELP = "There is a blacklist for rude users!\n\n"

    def is_it_for_me(self, tmsg):
        if self.tAPI.DB_IS_ENABLED:
            collection = self.tAPI.db.blacklist
            return ((tmsg.text.startswith("/addbl")) or (tmsg.text.startswith("/delbl")) or
                    (collection.find_one({"pers_id": str(tmsg.pers_id)}) is not None))
        return False

    def run(self, tmsg):
        # TODO adding and deleting from blacklist.
        return 0

    def quit(self, pers_id, chat_id, additional_info = '', msg_id=None):
        pass


class Stop(BaseWorker):
    COMMAND = "/StopPls"

    def is_it_for_me(self, tmsg):
        return (tmsg.text == self.COMMAND) and (str(tmsg.pers_id) == self.tAPI.admin_ids[0])

    def run(self, tmsg):
        print(self.tAPI.send("I'll be back, " + tmsg.name + "!", tmsg.chat_id))
        return 2

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        pass


class Humanity(BaseWorker):
    HELP = "Поддерживается понимание некоторых человеческих фраз, список команд можно посмотреть," \
           "введя слово \"команды\"\n\n"

    def __init__(self, teleapi):
        super(Humanity, self).__init__(teleapi)
        self.waitlist = set()
        import re
        self.re = re

    def is_it_for_me(self, tmsg):
        return not (tmsg.is_inline)

    def run(self, tmsg):
        tmsg.text_change_to(tmsg.text.lower())
        #TODO: Add your own commands
        if self.re.match(r"^(((\/| )*)команды)", tmsg.text):
            self.tAPI.send("Список фраз:\n\"Example\" или \"Пример\" - пример команды."
                           , tmsg.chat_id, tmsg.id)
            return 0
        tmsg.text_replace(r"^(((\/| )*)(example|пример))", Example.COMMAND, self.re.sub)
        return 1

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        pass

#TODO: Rename, channge the command and the hel info.
class Example(BaseWorker):
    COMMAND = "/example"
    HELP = COMMAND + " - пример комнды\n\n"

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith(self.COMMAND) or tmsg.is_inline

    def run(self, tmsg):
        #TODO: Add the logic of message processing
        return 0

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        #TODO: Feel free to change
        if (pers_id, chat_id) in self.waitlist:
            self.waitlist.pop((pers_id, chat_id))
            if additional_info != '':
                self.tAPI.send_inline_keyboard(additional_info, chat_id, self.MENU_KEYBOARD, msg_id)


class Info(BaseWorker):
    COMMAND = "/help"

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith(self.COMMAND) or tmsg.text.startswith("/start")

    def run(self, tmsg):
        HELP = ""
            # "Включен режим презентации, Вы можете получить слова из банка." if self.tAPI.db_shell.TEST_WORDS else ""
            # "Storage is " + ("on" if self.tAPI.DB_IS_ENABLED else "off") + "!\n\n"
        for worker in WorkersList.workers:
            HELP += worker[1].HELP
        HELP = HELP[:-2]
        self.tAPI.send_inline_keyboard(HELP, tmsg.chat_id, self.MENU_KEYBOARD)
        return 0

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        pass
