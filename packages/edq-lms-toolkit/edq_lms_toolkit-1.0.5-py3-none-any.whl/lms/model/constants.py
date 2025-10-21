import typing

import lms.util.net

BACKEND_TYPE_CANVAS: str = 'canvas'
BACKEND_TYPE_MOODLE: str = 'moodle'

BACKEND_TYPES: typing.List[str] = [
    BACKEND_TYPE_CANVAS,
    BACKEND_TYPE_MOODLE,
]

OUTPUT_FORMAT_JSON: str = 'json'
OUTPUT_FORMAT_TABLE: str = 'table'
OUTPUT_FORMAT_TEXT: str = 'text'

OUTPUT_FORMATS: typing.List[str] = [
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_TABLE,
    OUTPUT_FORMAT_TEXT,
]

BACKEND_REQUEST_CLEANING_FUNCS: typing.Dict[str, typing.Callable] = {
    BACKEND_TYPE_CANVAS: lms.util.net.clean_canvas_response,
    BACKEND_TYPE_MOODLE: lms.util.net.clean_moodle_response,
}
