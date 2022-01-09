import typing as t

class FormField(t.NamedTuple):
    name: str
    desc: str
    is_required: bool

FormFieldList = t.List[FormField]
FormFieldValues = t.Dict[str, str]
