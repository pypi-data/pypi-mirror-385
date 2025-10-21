from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.definitions_kv_definition import DefinitionsKVDefinition


T = TypeVar("T", bound="DefinitionsKVDefinitions")


@_attrs_define
class DefinitionsKVDefinitions:
    """ """

    additional_properties: dict[str, "DefinitionsKVDefinition"] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.definitions_kv_definition import DefinitionsKVDefinition

        d = dict(src_dict)
        definitions_kv_definitions = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = DefinitionsKVDefinition.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        definitions_kv_definitions.additional_properties = additional_properties
        return definitions_kv_definitions

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "DefinitionsKVDefinition":
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: "DefinitionsKVDefinition") -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
