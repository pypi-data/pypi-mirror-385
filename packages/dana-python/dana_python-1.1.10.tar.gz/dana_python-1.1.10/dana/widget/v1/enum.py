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
from enum import Enum
class ServiceType(str, Enum):
    PARKING = "PARKING"
    INVESTMENT = "INVESTMENT"

class ServiceScenario(str, Enum):
    SCAN_AND_PAY = "SCAN_AND_PAY"
    EXIT_AND_PAY = "EXIT_AND_PAY"
    EMAS_PURCHASE = "EMAS_PURCHASE"

class PromoType(str, Enum):
    CASH_BACK = "CASH_BACK"
    DISCOUNT = "DISCOUNT"
    VOUCHER = "VOUCHER"
    POINT = "POINT"

class AcquirementStatus(str, Enum):
    INIT = "INIT"
    SUCCESS = "SUCCESS"
    CLOSED = "CLOSED"
    PAYING = "PAYING"
    MERCHANT_ACCEPT = "MERCHANT_ACCEPT"
    CANCELLED = "CANCELLED"

class Mode(str, Enum):
    API = "API"
    DEEPLINK = "DEEPLINK"

class ResourceType(str, Enum):
    BALANCE = "BALANCE"
    TRANSACTION_URL = "TRANSACTION_URL"
    MASK_DANA_ID = "MASK_DANA_ID"
    TOPUP_URL = "TOPUP_URL"
    OTT = "OTT"
    USER_KYC = "USER_KYC"

class ResultStatus(str, Enum):
    S = "S"
    F = "F"
    U = "U"

class SourcePlatform(str, Enum):
    IPG = "IPG"

class TerminalType(str, Enum):
    APP = "APP"
    WEB = "WEB"
    WAP = "WAP"
    SYSTEM = "SYSTEM"

class OrderTerminalType(str, Enum):
    APP = "APP"
    WEB = "WEB"
    WAP = "WAP"
    SYSTEM = "SYSTEM"

class PayMethod(str, Enum):
    BALANCE = "BALANCE"
    COUPON = "COUPON"
    NET_BANKING = "NET_BANKING"
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    VIRTUAL_ACCOUNT = "VIRTUAL_ACCOUNT"
    OTC = "OTC"
    DIRECT_DEBIT_CREDIT_CARD = "DIRECT_DEBIT_CREDIT_CARD"
    DIRECT_DEBIT_DEBIT_CARD = "DIRECT_DEBIT_DEBIT_CARD"
    ONLINE_CREDIT = "ONLINE_CREDIT"
    LOAN_CREDIT = "LOAN_CREDIT"
    NETWORK_PAY = "NETWORK_PAY"
    CARD = "CARD"

class PayOption(str, Enum):
    NETWORK_PAY_PG_SPAY = "NETWORK_PAY_PG_SPAY"
    NETWORK_PAY_PG_OVO = "NETWORK_PAY_PG_OVO"
    NETWORK_PAY_PG_GOPAY = "NETWORK_PAY_PG_GOPAY"
    NETWORK_PAY_PG_LINKAJA = "NETWORK_PAY_PG_LINKAJA"
    NETWORK_PAY_PG_CARD = "NETWORK_PAY_PG_CARD"
    NETWORK_PAY_PC_INDOMARET = "NETWORK_PAY_PC_INDOMARET"
    NETWORK_PAY_PG_QRIS = "NETWORK_PAY_PG_QRIS"
    VIRTUAL_ACCOUNT_BCA = "VIRTUAL_ACCOUNT_BCA"
    VIRTUAL_ACCOUNT_BNI = "VIRTUAL_ACCOUNT_BNI"
    VIRTUAL_ACCOUNT_MANDIRI = "VIRTUAL_ACCOUNT_MANDIRI"
    VIRTUAL_ACCOUNT_BRI = "VIRTUAL_ACCOUNT_BRI"
    VIRTUAL_ACCOUNT_BTPN = "VIRTUAL_ACCOUNT_BTPN"
    VIRTUAL_ACCOUNT_CIMB = "VIRTUAL_ACCOUNT_CIMB"
    VIRTUAL_ACCOUNT_PERMATA = "VIRTUAL_ACCOUNT_PERMATA"
    VIRTUAL_ACCOUNT_PANI = "VIRTUAL_ACCOUNT_PANI"

class Type(str, Enum):
    PAY_RETURN = "PAY_RETURN"
    NOTIFICATION = "NOTIFICATION"

