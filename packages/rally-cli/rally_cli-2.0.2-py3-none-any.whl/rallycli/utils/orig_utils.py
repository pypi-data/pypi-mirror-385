import logging
import re
from typing import List, Dict, cast, Any, Optional

from rallycli.errors import RallyError
from rallycli.models import RallyTypeGeneric, RallyPydanticBase

logger = logging.getLogger(__name__)


def rally_lst(model_lst: List[Any]) -> List["RallyTypeGeneric"]:
    if not model_lst:
        return list()
    if not isinstance(model_lst[0], RallyPydanticBase):
        raise RallyError(
            f"Model Class {model_lst[0].__class__} is not a valid RallyPydanticBase subclass"
        )
    return cast(List[RallyTypeGeneric], model_lst)


def dict_lst(model_lst: List[Any]) -> List[Dict[str, Any]]:
    if not isinstance(model_lst[0], RallyPydanticBase):
        raise RallyError(
            f"Model Class {model_lst[0].__class__} is not a valid RallyPydanticBase subclass"
        )
    return [model.dict() for model in model_lst]


def query_yes_no(question, default="yes") -> bool:
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        print(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def get_relative_ref(ref: str) -> str:
    if not str:
        return ""
    path = ref
    if match := re.match(r".*/v2.0(.+)$", str(ref)):
        path = match.group(1)
    return path


def get_oid_from_ref(ref: str) -> Optional[str]:
    if match := re.match(r".*/(\d+)$", ref):
        return match.group(1)
    return None
