from typing import Dict, List
from websockets.sync.client import connect, ClientConnection
import threading
from urllib.parse import quote
import surveytomato.items as items
import json
import time
import signal
import sys
from typing import Callable


class Params:
    __parameters: Dict[str, List[str]]

    def __init__(self, parameters: Dict[str, List[str]]):
        self.__parameters = parameters

    def get(self, key: str) -> str | None:
        if key in self.__parameters:
            return self.__parameters[key][0]
        else:
            return None

    def get_all(self, key: str) -> List[str] | None:
        if key in self.__parameters:
            return self.__parameters[key]
        else:
            return None


class Form:
    ws: ClientConnection
    header: items.HeaderItem | None
    parameters: Params

    def __init__(self, ws: ClientConnection):
        self.ws = ws
        self.header = None
        self.parameters = Params({})

    def close(self):
        self.ws.send(json.dumps({
            "type": "session_close",
            "data": None
        }))

    def send_canvas(self, canvas: items.FormCanvas) -> Dict[str, any]:
        self.ws.send(json.dumps({
            "type": "session_canvas",
            "data": canvas.get_items()
        }))

        resp = self.ws.recv()
        msg = json.loads(resp)

        if msg["type"] == "session_submit":
            return msg["data"]
        else:
            print("Unexpected message:", msg)
            return {}

    def set_header(self, title: str, icon: str | None = None, description: str | None = None):
        self.header = items.HeaderItem(title, icon, description)

    def input(self, question: str, valueType: str = 'text', placeholder: str | None = None):
        c = items.FormCanvas()
        if self.header is not None:
            c += self.header
        c += items.QuestionItem(question)
        c += items.InputItem("input", placeholder, valueType)
        c += items.SubmitButtonItem()

        return self.send_canvas(c)["input"]

    def ab_buttons(self, question: str, buttons: List[tuple[str, str]] | None = None):
        c = items.FormCanvas()
        if self.header is not None:
            c += self.header
        c += items.QuestionItem(question)
        if buttons is None:
            c += items.ABButtonsItem("ab_buttons")
        else:
            c += items.ABButtonsItem("ab_buttons", buttons)

        return self.send_canvas(c)["ab_buttons"]

    def select(self, question: str, multiple: bool = False, options: List[str] | List[tuple[str, str | int]] | None = None, autoSubmit: bool = False) -> List[str]:
        c = items.FormCanvas()
        if self.header is not None:
            c += self.header
        c += items.QuestionItem(question)
        if options is None:
            c += items.SelectItem("select", multiple=multiple, autoSubmit=autoSubmit)
        else:
            c += items.SelectItem("select", multiple=multiple, options=options, autoSubmit=autoSubmit)
        if autoSubmit != True:
            c += items.SubmitButtonItem()

        return self.send_canvas(c)["select"]

    def detailed_select(self, question: str, multiple: bool | None = None, options: List[items.DetailedSelectOption] | None = None, autoSubmit: bool | None = None) -> List[str]:
        c = items.FormCanvas()
        if self.header is not None:
            c += self.header
        c += items.QuestionItem(question)
        c += items.DetailedSelectItem("select", multiple, options, autoSubmit)
        if autoSubmit != True:
            c += items.SubmitButtonItem()

        return self.send_canvas(c)["select"]


class FormHandler:

    __api_endpoint: str
    __ws_endpoint: str

    def __init__(self, func: Callable, token: str, endpoint: str):
        self.func = func
        self.token = token

        endpoint = endpoint.replace("http", "ws")
        endpoint = endpoint.replace("https", "wss")
        self.__ws_endpoint = endpoint + "/api"

    def serve(self):
        self.__listen_for_sessions()

    def serve_session(self, session_id: str):
        signal.signal(signal.SIGINT, self.__signal_handler)
        self.__run_session(session_id)

    def __signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

    def __listen_for_sessions(self):
        signal.signal(signal.SIGINT, self.__signal_handler)
        with connect(f"{self.__ws_endpoint}/server/wait?token={quote(self.token)}") as websocket:
            print("Waiting for sessions...")
            while True:
                try:
                    msg = json.loads(websocket.recv())
                    if msg["type"] == "new_session":
                        print("New session:", msg["data"])
                        threading.Thread(
                            target=self.__run_session, args=(msg["data"],)).start()
                    elif msg["type"] == "session_token":
                        token = msg["data"]
                        print("Form available at:",
                              f"https://nbforms.com/f/{token}")
                    else:
                        print("Unexpected message:", msg)
                except Exception:
                    print("Connection closed.")
                    break

    def __run_session(self, token: str):
        start = time.process_time_ns()
        with connect(f"{self.__ws_endpoint}/server/session?token={quote(token)}") as websocket:
            print("Connected.")
            form = Form(websocket)
            msg = json.loads(websocket.recv())
            if msg["type"] == "session_parameters":
                form.parameters = Params(msg["data"])
            self.func(form)
            form.close()
        end = time.process_time_ns()
        print("Session done in", end)

def form(*, token: str, endpoint: str = "https://exchange.surveytomato.com") -> Callable[[Callable[[Form], None]], FormHandler]:
    def wrapper(func: Callable[[Form], None]) -> FormHandler:
        return FormHandler(func, token, endpoint)
    return wrapper
