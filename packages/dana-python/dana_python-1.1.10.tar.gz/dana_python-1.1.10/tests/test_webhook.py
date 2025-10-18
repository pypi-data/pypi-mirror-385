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

import json
import os
from dana.webhook.finish_notify_request import FinishNotifyRequest
from dana.webhook import WebhookParser
from dana.utils.snap_header import SnapHeader
# Import fixtures directly from their modules to avoid circular imports
from tests.fixtures.api_client import api_instance_payment_gateway
from tests.fixtures.payment_gateway import webhook_key_pair

class TestWebhookParser:
    def test_webhook_signature_and_parsing_success(self):
        # Load keys from environment variables
        public_key = os.getenv("WEBHOOK_PUBLIC_KEY")
        
        webhook_http_method = "POST"
        webhook_relative_url = "/api/v2/test-notif/dana"
        
        webhook_body_str = '{"amount":{"currency":"IDR","value":"100000.00"},"originalReferenceNo":"20250916111230999500166191900293793","merchantId":"216620080007039826152","latestTransactionStatus":"00","additionalInfo":{"paidTime":"1757998714761","paymentInfo":{"payOptionInfos":[{"transAmount":{"currency":"IDR","value":"100000.00"},"payAmount":{"currency":"IDR","value":"100000.00"},"payMethod":"NETWORK_PAY","payOption":"NETWORK_PAY_PG_LINKAJA"}],"extendInfo":"{\"externalPromoInfos\":[]}"}},"originalPartnerReferenceNo":"LINKIT25091757998646","createdTime":"1757998647000","finishedTime":"1757998714761","transactionStatusDesc":"SUCCESS"}'
        
        x_timestamp = "2025-09-16T12:11:30+07:00"
        signature = "d/7mle7A+FCl4zvBZ2dMr3s7TVbbaK+toMtZwoev4OmLhn6Ctz/ynMaL3m3vHjAmV3UL3Fq5xp9thZFsO8BY74Vehqr1N9LQblV6i3TfMwT6lMvvhzWr0Fjbasyj23c5nFu1MOxpBiZFMMDNh8GQNLBAehHbjOmNldXSL6OQYRrK/TN9tdDyYFK6ltnKf4BN6bZa2ViAlI/np/U3QBW2LnDL82+8ZK7tYVF5bZyLLUSLXeWXBGQFTSDWqN+JdUHSnxGdQr3hZ7Y9Vqm/7G6rj6NrCxLPiEJYq1DQO3DjokMsORA2lOxzuo53bwqmhmD1mFhJKWF1JmyJuFdo2HB9JA=="
        
        headers = {
            "Channel-Id": "DANA",
            "Charset": "UTF-8",
            "Content-Type": "application/json",
            "User-Agent": "Jakarta Commons-HttpClient/3.1",
            "X-External-Id": "cFQ0PK5yS9wkMTMOVem4fIoUuyuA28jg",
            "X-Partner-Id": "2025090110410957288340",
            "X-Signature": signature,
            "X-Timestamp": x_timestamp
        }
        
        # Create the parser with the public key
        parser = WebhookParser(public_key=public_key)
        
        # Verify and parse
        result = parser.parse_webhook(
            http_method=webhook_http_method,
            relative_path_url=webhook_relative_url,
            headers=headers,
            body=webhook_body_str
        )
        
        # Verify specific fields like in the Go test
        assert result is not None
        assert result.original_partner_reference_no == "LINKIT25091757998646"
        assert result.original_reference_no == "20250916111230999500166191900293793"
        assert result.merchant_id == "216620080007039826152"
        assert result.amount.value == "100000.00"
        assert result.amount.currency == "IDR"
        assert result.latest_transaction_status == "00"

    def test_webhook_with_double_escaped_quotes(self):
        """Test webhook parsing with double-escaped quotes in JSON (like PHP test)"""
        # Load keys from environment variables
        public_key = os.getenv("WEBHOOK_PUBLIC_KEY")
        
        webhook_http_method = "POST"
        webhook_relative_url = "/d34021fa-7599-413b-8743-ddab605fea49"
        
        # This webhook body contains double-escaped quotes in extendInfo field
        webhook_body_str = '{"amount":{"currency":"IDR","value":"50000.00"},"originalReferenceNo":"20251010111230999500166931000229476","merchantId":"216620090016041032029","latestTransactionStatus":"00","additionalInfo":{"paidTime":"2025-10-10T16:16:33+07:00","paymentInfo":{"payOptionInfos":[{"transAmount":{"currency":"IDR","value":"50000.00"},"payAmount":{"currency":"IDR","value":"50000.00"},"payMethod":"VIRTUAL_ACCOUNT","payOption":"VIRTUAL_ACCOUNT_BRI"}],"extendInfo":"{\\"externalPromoInfos\\":[]}"}},"originalPartnerReferenceNo":"ORDER-1760087736146","createdTime":"2025-10-10T16:15:37+07:00","finishedTime":"2025-10-10T16:16:33+07:00","transactionStatusDesc":"SUCCESS"}'
        
        x_timestamp = "2025-10-13T13:43:30+07:00"
        signature = "fqrQPxlzEN4ZGW9vYt3PokmIrbG2HQtlbdj6krjf9HFW1qS3ilZjSR+9Z4XZNYxQIxyHHqXmjEiBU4ui/JrknSXlCpPQe7DztB/Ye+yLxIHYBnwdeCXn2zGGAV51nQki+eD2aL8Z6d6MyWz9hoytwE+jtWKUC0KtU7wQfoB0XjdEXzU3/4Ao/rWQbt97UONaaf7i5l3+M/ICP187PYw9iRHLUFh7WRPs8JKpZyO0kcJqEJbeOUjHMmIsLQImOlYVbQTM/1v89Ou1WcVAo0cXNE5yrvosB4pQROeI8KY2X1FNTuB1pdFtQTIyUcd/t1wuIxqHqqFKjrFdcQxlZOIyRg=="
        
        headers = {
            "Channel-Id": "DANA",
            "Charset": "UTF-8",
            "Content-Type": "application/json",
            "User-Agent": "Jakarta Commons-HttpClient/3.1",
            "X-External-Id": "nXPTWcwt7lgCOy01wWGKDerEMlKwV5wc",
            "X-Partner-Id": "2025091611385324660336",
            "X-Signature": signature,
            "X-Timestamp": x_timestamp
        }
        
        # Create the parser with the public key
        parser = WebhookParser(public_key=public_key)
        
        # Verify and parse - this should work with the JSON normalization
        result = parser.parse_webhook(
            http_method=webhook_http_method,
            relative_path_url=webhook_relative_url,
            headers=headers,
            body=webhook_body_str
        )
        
        # Verify specific fields like in the PHP test
        assert result is not None
        assert result.original_partner_reference_no == "ORDER-1760087736146"
        assert result.original_reference_no == "20251010111230999500166931000229476"
        assert result.merchant_id == "216620090016041032029"
        assert result.amount.value == "50000.00"
        assert result.amount.currency == "IDR"
        assert result.latest_transaction_status == "00"
