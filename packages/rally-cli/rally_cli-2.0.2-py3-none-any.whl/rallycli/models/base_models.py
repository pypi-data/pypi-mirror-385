from __future__ import annotations

import json
from logging import getLogger
from typing import List, Set, Any, Dict

from pydantic import ConfigDict, BaseModel

from rallycli.models.memento import RallyPydanticMemento, Memento

logger = getLogger(__name__)

UPDATE_EXCLUDE_FIELD_SET = {
    "refObjectName",
}
CREATE_EXCLUDE_FIELD_SET = {
    "ref",
    "type",
    "refObjectName",
}


class RallyPydanticBase(BaseModel):
    __slots__ = ("caretaker",)

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "caretaker", CareTaker(self))
        # ? Initial snapshot & performance issues for masive instantiation?
        # self.caretaker.take_snapshot()

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        # arbitrary_types_allowed=True,
        # * populate expects alias when exist with populate_by_name the real name of the field
        # * is allowed also (not sure if needed)
        # populate_by_name=True,
        str_strip_whitespace=True,
        # * Allow is needed due that models don't define all existent fields in rally schema
        # * (custom fields for example)
        extra="allow",
        validate_assignment=True,
        populate_by_name=True,
    )

    def dict(
        self,
        *,
        include: Set = None,
        exclude: Set = None,
        by_alias: bool = False,
        exclude_unset: bool = True,
        exclude_defaults: bool = False,
        exclude_none: bool = True,
    ) -> Dict[str, Any]:
        return super().model_dump(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def dump_for_create(self) -> Dict[str, Any]:
        # * exclude fields begin with _
        exclude = CREATE_EXCLUDE_FIELD_SET
        data = self.model_dump(exclude=exclude, round_trip=True, by_alias=True, exclude_none=True)
        return data

    def dump_for_update(self, body_keys: set = None) -> Dict[str, Any]:
        exclude = UPDATE_EXCLUDE_FIELD_SET
        include = None
        if body_keys:
            # * Always include ref and type fields for update
            body_keys.update({"ref", "type"})
            include = body_keys

        data = self.model_dump(exclude=exclude, include=include, round_trip=True, by_alias=True)
        return data

    def save(self) -> RallyPydanticMemento:
        return RallyPydanticMemento(self.dict(by_alias=True))


class CareTaker:
    def __init__(self, model: RallyPydanticBase):
        self._model = model
        self._mementos: List[Memento] = []

    @staticmethod
    def __serialize_dict(d: dict) -> dict:
        s_dict = {}
        for k, v in d.items():
            if isinstance(v, str):
                sv = v
            else:
                sv = json.dumps(v, sort_keys=True, default=str)
            s_dict[k] = sv
        return s_dict

    def take_snapshot(self) -> "CareTaker":
        self._mementos.append(self._model.save())
        return self

    def get_diff_keys(self) -> List[str]:
        """Diff last snapshot and actual state"""
        s_last_snapshot_state: dict = self.__serialize_dict(self._mementos[-1].get_state())
        s_actual: dict = self.__serialize_dict(self._model.save().get_state())
        s1 = set(s_last_snapshot_state.items())
        s2 = set(s_actual.items())
        diff_keys: List[str] = [k for k, _ in s2 - s1]
        return diff_keys
