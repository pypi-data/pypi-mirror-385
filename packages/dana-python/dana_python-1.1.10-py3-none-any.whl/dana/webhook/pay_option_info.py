# Copyright 2025 PT Espay Debit Indonesia Koe
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# coding: utf-8

from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from dana.base.model import BaseSdkModel

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from dana.payment_gateway.v1.models.money import Money
from typing import Optional, Set
from typing_extensions import Self
from pydantic import AliasGenerator
from pydantic.alias_generators import to_camel

class PayOptionInfo(BaseModel, BaseSdkModel):
    """
    PayOptionInfo
    """ # noqa: E501
    pay_method: Annotated[str, Field(strict=True, max_length=64)] = Field(description="Payment method name. The enums:<br>   * BALANCE - Payment method with balance<br>   * COUPON - Payment method with coupon<br>   * NET_BANKING - Payment method with internet banking<br>   * CREDIT_CARD - Payment method with credit card<br>   * DEBIT_CARD - Payment method with debit card<br>   * VIRTUAL_ACCOUNT - Payment method with virtual account<br>   * OTC - Payment method with OTC<br>   * DIRECT_DEBIT_CREDIT_CARD - Payment method with direct debit of credit card<br>   * DIRECT_DEBIT_DEBIT_CARD - Payment method with direct debit of debit card<br>   * ONLINE_CREDIT - Payment method with online Credit<br>   * LOAN_CREDIT - Payment method with DANA Cicil<br>   * NETWORK_PAY - Payment method with e-wallet ")
    pay_option: Optional[Annotated[str, Field(strict=True, max_length=64)]] = Field(default=None, description="Payment option which shows the provider of this payment. The enums:<br>   * NETWORK_PAY_PG_SPAY - Payment method with ShopeePay e-wallet<br>   * NETWORK_PAY_PG_OVO - Payment method with OVO e-wallet<br>   * NETWORK_PAY_PG_GOPAY - Payment method with GoPay e-wallet<br>   * NETWORK_PAY_PG_LINKAJA - Payment method with LinkAja e-wallet<br>   * NETWORK_PAY_PG_CARD - Payment method with Card<br>   * VIRTUAL_ACCOUNT_BCA - Payment method with BCA virtual account<br>   * VIRTUAL_ACCOUNT_BNI - Payment method with BNI virtual account<br>   * VIRTUAL_ACCOUNT_MANDIRI - Payment method with Mandiri virtual account<br>   * VIRTUAL_ACCOUNT_BRI - Payment method with BRI virtual account<br>   * VIRTUAL_ACCOUNT_BTPN - Payment method with BTPN virtual account<br>   * VIRTUAL_ACCOUNT_CIMB - Payment method with CIMB virtual account<br>   * VIRTUAL_ACCOUNT_PERMATA - Payment method with Permata virtual account<br> ")
    pay_amount: Optional[Money] = Field(default=None, description="Pay amount. Contains two sub-fields:<br> 1. Value: Transaction amount, including the cents<br> 2. Currency: Currency code based on ISO<br> ")
    trans_amount: Optional[Money] = Field(default=None, description="Trans amount. Contains two sub-fields:<br> 1. Value: Transaction amount, including the cents<br> 2. Currency: Currency code based on ISO<br> ")
    charge_amount: Optional[Money] = Field(default=None, description="Charge amount. Contains two sub-fields:<br> 1. Value: Transaction amount, including the cents<br> 2. Currency: Currency code based on ISO<br> ")
    pay_option_bill_extend_info: Optional[Annotated[str, Field(strict=True, max_length=4096)]] = Field(default=None, description="Extend information of pay option bill")
    extend_info: Optional[Annotated[str, Field(strict=True, max_length=4096)]] = Field(default=None, description="Extend information")
    payment_code: Optional[Annotated[str, Field(strict=True)]] = Field(default=None, description="Payment code")
    __properties: ClassVar[List[str]] = ["payMethod", "payOption", "payAmount", "transAmount", "chargeAmount", "payOptionBillExtendInfo", "extendInfo", "paymentCode"]

    @field_validator('pay_method')
    def pay_method_validate_enum(cls, value):
        """Validates the enum"""
        if value == "":
            return value
        if value not in set(['BALANCE', 'COUPON', 'NET_BANKING', 'CREDIT_CARD', 'DEBIT_CARD', 'VIRTUAL_ACCOUNT', 'OTC', 'DIRECT_DEBIT_CREDIT_CARD', 'DIRECT_DEBIT_DEBIT_CARD', 'ONLINE_CREDIT', 'LOAN_CREDIT', 'NETWORK_PAY']):
            raise ValueError("must be one of enum values ('BALANCE', 'COUPON', 'NET_BANKING', 'CREDIT_CARD', 'DEBIT_CARD', 'VIRTUAL_ACCOUNT', 'OTC', 'DIRECT_DEBIT_CREDIT_CARD', 'DIRECT_DEBIT_DEBIT_CARD', 'ONLINE_CREDIT', 'LOAN_CREDIT', 'NETWORK_PAY')")
        return value

    @field_validator('pay_option')
    def pay_option_validate_enum(cls, value):
        """Validates the enum"""
        if not value:
            return value

        if value not in set(['NETWORK_PAY_PG_SPAY', 'NETWORK_PAY_PG_OVO', 'NETWORK_PAY_PG_GOPAY', 'NETWORK_PAY_PG_LINKAJA', 'NETWORK_PAY_PG_CARD', 'VIRTUAL_ACCOUNT_BCA', 'VIRTUAL_ACCOUNT_BNI', 'VIRTUAL_ACCOUNT_MANDIRI', 'VIRTUAL_ACCOUNT_BRI', 'VIRTUAL_ACCOUNT_BTPN', 'VIRTUAL_ACCOUNT_CIMB', 'VIRTUAL_ACCOUNT_PERMATA']):
            raise ValueError("must be one of enum values ('NETWORK_PAY_PG_SPAY', 'NETWORK_PAY_PG_OVO', 'NETWORK_PAY_PG_GOPAY', 'NETWORK_PAY_PG_LINKAJA', 'NETWORK_PAY_PG_CARD', 'VIRTUAL_ACCOUNT_BCA', 'VIRTUAL_ACCOUNT_BNI', 'VIRTUAL_ACCOUNT_MANDIRI', 'VIRTUAL_ACCOUNT_BRI', 'VIRTUAL_ACCOUNT_BTPN', 'VIRTUAL_ACCOUNT_CIMB', 'VIRTUAL_ACCOUNT_PERMATA')")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
        alias_generator=AliasGenerator(serialization_alias=to_camel, validation_alias=to_camel),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict(), separators=(',', ':'))

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of PayOptionInfo from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of pay_amount
        if self.pay_amount:
            _dict['payAmount'] = self.pay_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of trans_amount
        if self.trans_amount:
            _dict['transAmount'] = self.trans_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of charge_amount
        if self.charge_amount:
            _dict['chargeAmount'] = self.charge_amount.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PayOptionInfo from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "payMethod": obj.get("payMethod"),
            "payOption": obj.get("payOption"),
            "payAmount": Money.from_dict(obj["payAmount"]) if obj.get("payAmount") is not None else None,
            "transAmount": Money.from_dict(obj["transAmount"]) if obj.get("transAmount") is not None else None,
            "chargeAmount": Money.from_dict(obj["chargeAmount"]) if obj.get("chargeAmount") is not None else None,
            "payOptionBillExtendInfo": obj.get("payOptionBillExtendInfo"),
            "extendInfo": obj.get("extendInfo"),
            "paymentCode": obj.get("paymentCode")
        })
        return _obj


