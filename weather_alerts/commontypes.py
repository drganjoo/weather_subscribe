import typing as t

"""Just some common fields that are used in the API """
class FormField(t.NamedTuple):
    name: str
    desc: str
    is_required: bool

FormFieldList = t.List[FormField]
FormFieldValues = t.Dict[str, str]
