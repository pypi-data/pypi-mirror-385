"""
Mixin for IP data types
"""

# pylint: disable=too-few-public-methods

import ipaddress
from typing import TYPE_CHECKING

from nadap.base import ValEnv
from nadap.errors import SchemaDefinitionError
import nadap.mixin.allowed_value
import nadap.mixin.not_allowed_value
from nadap.doc import UnorderedTextList

if TYPE_CHECKING:
    from nadap.doc import TextField


class IpMixin(
    nadap.mixin.not_allowed_value.NotAllowedValueMixin,
    nadap.mixin.allowed_value.AllowedValueMixin,
):
    """
    Add handling of strings representing IPv4 or IPv6 string
    """

    _cls_python_classes = [str]
    _doc_data_type = "str"
    _ip_data_type_name = "IP"

    def __init__(self, **kwargs):
        self._test_loopback = None
        self._test_link_local = None
        self._test_multicast = None
        self._test_private = None
        self._test_public = None
        super().__init__(**kwargs)

    def _get_ip_obj(self, data):
        return ipaddress.ip_address(data)

    def _test_data_type(self, data: any, path: str, env: "ValEnv" = None) -> "any":
        # pylint: disable=raise-missing-from
        data = super()._test_data_type(data=data, path=path, env=env)
        try:
            self._get_ip_obj(data)
        except ValueError:
            msg = f"String does not represent an {self._ip_data_type_name}"
            if env is None:
                raise SchemaDefinitionError(
                    msg=msg,
                    path=path,
                )
            self._create_finding_with_error(msg=msg, path=path, env=env)
        return data

    def _pop_options(self, definition: dict, schema_path: str):
        self._test_loopback = definition.pop("loopback", None)
        self._test_link_local = definition.pop("link_local", None)
        self._test_private = definition.pop("private", None)
        self._test_public = definition.pop("public", None)
        self._test_multicast = definition.pop("multicast", None)
        super()._pop_options(definition=definition, schema_path=schema_path)

    def _validate_options(self, schema_path: str):
        super()._validate_options(schema_path=schema_path)
        if (
            self._test_link_local is not None
            and self._test_loopback is not None
            and self._test_link_local == self._test_loopback
        ):
            raise SchemaDefinitionError(
                "Mismatching test for link_local and loopback", schema_path
            )
        if (
            self._test_link_local is not None
            and self._test_multicast is not None
            and self._test_link_local == self._test_multicast
        ):
            raise SchemaDefinitionError(
                "Mismatching test for link_local and multicast", schema_path
            )
        if (
            self._test_loopback is not None
            and self._test_multicast is not None
            and self._test_loopback == self._test_multicast
        ):
            raise SchemaDefinitionError(
                "Mismatching test for loopback and multicast", schema_path
            )
        if (
            self._test_private is not None
            and self._test_public is not None
            and self._test_private == self._test_public
        ):
            raise SchemaDefinitionError(
                "Mismatching test for private and public", schema_path
            )

    def _validate_data(
        self,
        data: any,
        path: str,
        env: "ValEnv" = None,
    ) -> "any":
        """
        Check if data matches IP options
        """
        data = super()._validate_data(data=data, path=path, env=env)
        ip_obj = self._get_ip_obj(data)
        msg = None
        if (
            self._test_link_local is not None
            and self._test_link_local != ip_obj.is_link_local
        ):
            msg = "Is link-local" if ip_obj.is_link_local else "Is not link-local"
        elif (
            self._test_loopback is not None
            and self._test_loopback != ip_obj.is_loopback
        ):
            msg = "Is loopback" if ip_obj.is_loopback else "Is not loopback"
        elif (
            self._test_multicast is not None
            and self._test_multicast != ip_obj.is_multicast
        ):
            msg = "Is multicast" if ip_obj.is_multicast else "Is not multicast"
        elif self._test_private is not None and self._test_private != ip_obj.is_private:
            msg = "Is private" if ip_obj.is_private else "Is not private"
        elif self._test_public is not None and self._test_public != ip_obj.is_global:
            msg = "Is public" if ip_obj.is_global else "Is not public"
        if msg:
            self._create_finding_with_error(msg=msg, path=path, env=env)

        return data

    @property
    def yaml_data_type(self) -> str:
        """Get YAML data type string"""
        return self._ip_data_type_name

    @property
    def doc_types(self) -> list[str]:
        """Get list of data type strings"""
        return [self._ip_data_type_name]

    @property
    def restrictions(self) -> "TextField":
        """
        Get all restrictions for valid data
        """
        tf = super().restrictions
        opt_list = UnorderedTextList()
        if self._test_link_local is not None:
            opt_list.append(f"link-local: {self._test_link_local}")
        if self._test_loopback is not None:
            opt_list.append(f"loopback: {self._test_loopback}")
        if self._test_multicast is not None:
            opt_list.append(f"multicast: {self._test_multicast}")
        if self._test_private is not None:
            opt_list.append(f"private: {self._test_private}")
        if self._test_public is not None:
            opt_list.append(f"public: {self._test_public}")
        if opt_list:
            tf.append("IP restrictions:")
            tf.append(opt_list)
        return tf

    @classmethod
    def _doc_options_md_upper_part(cls) -> list[str]:
        return super()._doc_options_md_upper_part() + [
            "| **link_local** | <code>bool</code> | | | IP must be link-local |",
            "| **loopback** | <code>bool</code> | | | IP must be loopback |",
            "| **multicast** | <code>bool</code> | | | IP must be multicast |",
            "| **private** | <code>bool</code> | | | IP must be private |",
            "| **public** | <code>bool</code> | | | IP must be public/global |",
        ]

    @classmethod
    def _doc_options_yaml_upper_part(cls) -> list[str]:
        return super()._doc_options_yaml_upper_part() + [
            "",
            "link_local: <true|false",
            "loopback: <true|false",
            "multicast: <true|false",
            "private: <true|false",
            "public: <true|false",
        ]
