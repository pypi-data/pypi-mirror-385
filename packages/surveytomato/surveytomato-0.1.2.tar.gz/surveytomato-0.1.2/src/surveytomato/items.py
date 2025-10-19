import json
from typing import List, NamedTuple


class FormItem:
    item: dict

    def __init__(self):
        self.item = {}


class DataGenItem(FormItem):
    def __init__(self):
        super().__init__()

    def store(self, field_name: str):
        self.item['store'] = field_name
        return self


class FormCanvas:
    items: List[FormItem] = []

    def __init__(self, items: List[FormItem] | None = None):
        if items:
            self.items = items

    def __add__(self, other):
        if isinstance(other, FormItem):
            new_items = self.items.copy()
            new_items.append(other)
            return FormCanvas(new_items)
        else:
            raise TypeError(f"Expected FormItem, got {type(other)}")

    def get_items(self):
        l = []
        for i in self.items:
            l.append(i.item)

        return l

    def __str__(self):
        return json.dumps(self.get_items())


class InputItem(DataGenItem):
    def __init__(self, id: str | None = None, placeholder: str | None = None, valueType: str = 'text'):
        super().__init__()
        self.item['type'] = 'input'
        if id is not None:
            self.item['id'] = id
        if placeholder is not None:
            self.item['placeholder'] = placeholder
        self.item['valueType'] = valueType


class ABButtonsItem(DataGenItem):
    def __init__(self, id: str | None = None, buttons: List[tuple[str, str]] = [("Option A", "a"), ("Option B", "b")]):
        super().__init__()
        self.item['type'] = 'ab_buttons'
        self.item['id'] = id
        self.item['options'] = []

        for button in buttons:
            if len(button) < 1:
                continue

            value = None
            if len(button) > 1:
                value = button[1]

            self.item['options'].append({
                "text": button[0],
                "value": value
            })


class SelectItem(DataGenItem):
    def __init__(self, id: str | None = None, multiple: bool = False, options: List[str] | List[tuple[str, str | int]] = [("Option A", "a"), ("Option B", "b")], autoSubmit: bool = False):
        super().__init__()
        self.item['type'] = 'select'
        if id is not None:
            self.item['id'] = id
        self.item['multiple'] = multiple
        self.item['options'] = []
        self.item['autoSubmit'] = autoSubmit

        for option in options:
            if isinstance(option, str):
                option = (option, option)
            elif not isinstance(option, tuple) or len(option) < 1:
                continue
            
            value = option[0]
            if len(option) > 1:
                value = option[1]

            self.item['options'].append({
                "text": option[0],
                "value": value
            })


class DetailedSelectOption(NamedTuple):
    text: str
    value: str | None = None
    icon: str | None = None
    description: str | None = None


class DetailedSelectItem(DataGenItem):
    def __init__(self, id: str | None = None, multiple: bool | None = None, options: List[DetailedSelectOption] = [], autoSubmit: bool | None = None):
        super().__init__()
        self.item['type'] = 'detailed_select'
        self.item['id'] = id
        self.item['multiple'] = multiple
        self.item['options'] = options
        self.item['autoSubmit'] = autoSubmit


class HeaderItem(FormItem):
    def __init__(self, title: str, icon: str | None = None, description: str | None = None):
        super().__init__()
        self.item['type'] = 'header'
        self.item['title'] = title
        if icon is not None:
            self.item['icon'] = icon
        if description is not None:
            self.item['description'] = description


class QuestionItem(FormItem):
    def __init__(self, question: str):
        super().__init__()
        self.item['type'] = 'question'
        self.item['question'] = question


class SubmitButtonItem(FormItem):
    def __init__(self, text: str | None = None, path: str | None = None):
        super().__init__()
        self.item['type'] = 'submit'
        if text is not None:
            self.item['text'] = text
        if path is not None:
            self.item['path'] = path
