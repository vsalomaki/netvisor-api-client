from datetime import date
from decimal import Decimal

import pytest
import xmltodict

from tests.utils import get_request_content, get_response_content


class TestAccountingService(object):
    def test_ledger(self, netvisor, responses):
        responses.add(
            method="GET",
            url="http://koulutus.netvisor.fi/AccountingLedger.nv",
            body=get_response_content("AccountingList.xml"),
            content_type="text/html; charset=utf-8",
            match_querystring=True,
        )
        accounting = netvisor.accounting.ledger()
        assert accounting == [
            {
                "status": "valid",
                "key": 12,
                "date": date(2000, 1, 1),
                "number": 13,
                "description": "Invoice 14",
                "class": "PI Purchase Invoice",
                "linked_source": {"type": "purchaseinvoice", "key": 15},
                "uri": "https:/netvisor.com/voucher/16",
                "lines": [
                    {
                        "key": 121,
                        "line_sum": Decimal("-17.18"),
                        "description": "Invoice 19",
                        "account_number": 100,
                        "vat_percent": 20,
                        "vat_code": "-",
                        "dimensions": [],
                    },
                    {
                        "key": 122,
                        "line_sum": Decimal("-21.22"),
                        "description": "Invoice 23",
                        "account_number": 200,
                        "vat_percent": 24,
                        "vat_code": "KOMY",
                        "dimensions": [],
                    },
                ],
            },
            {
                "status": "invalidated",
                "key": 25,
                "date": date(2000, 1, 2),
                "number": 26,
                "description": "Invoice 27",
                "class": "SA Sales Invoice",
                "linked_source": {"type": "salesinvoice", "key": 28},
                "uri": "https:/netvisor.com/voucher/29",
                "lines": [
                    {
                        "key": 251,
                        "line_sum": Decimal("-30.31"),
                        "description": "Invoice 32",
                        "account_number": 300,
                        "vat_percent": 33,
                        "vat_code": "-",
                        "dimensions": [
                            {"name": "Sales", "item": "Mike"},
                            {"name": "Purchase", "item": "Matt"},
                        ],
                    }
                ],
            },
            {
                "key": 36,
                "date": date(2000, 1, 3),
                "number": 37,
                "description": "Invoice 38",
                "class": "Placeholder",
                "linked_source": {"type": "salesinvoice", "key": 38},
                "uri": "https:/netvisor.com/voucher/39",
                "lines": [],
            },
            {
                "status": "valid",
                "key": 38,
                "date": date(2000, 1, 2),
                "number": 39,
                "description": "Invoice 39",
                "class": "SA Sales Invoice",
                "linked_source": {"type": "salesinvoice", "key": 39},
                "uri": "https:/netvisor.com/voucher/39",
                "lines": [
                    {
                        "key": 300,
                        "line_sum": Decimal("-30.31"),
                        "description": "Invoice 39",
                        "account_number": 300,
                        "vat_percent": 33,
                        "vat_code": "-",
                        "dimensions": [{"name": "Sales", "item": None}],
                    }
                ],
            },
        ]

    @pytest.mark.parametrize(
        ("parameter", "key"),
        [
            ("start_date", "StartDate"),
            ("end_date", "EndDate"),
            ("last_modified_start", "LastModifiedStart"),
            ("last_modified_end", "LastModifiedEnd"),
            ("changed_since", "ChangedSince"),
        ],
    )
    def test_date_parameters(self, netvisor, responses, parameter, key):
        value = date(2000, 1, 2)
        url = "http://koulutus.netvisor.fi/AccountingLedger.nv?%s=2000-01-02" % key
        responses.add(
            method="GET",
            url=url,
            body=get_response_content("AccountingList.xml"),
            content_type="text/html; charset=utf-8",
            match_querystring=True,
        )
        assert netvisor.accounting.ledger(**{parameter: value}) is not None
        request = responses.calls[0].request
        assert request.url == url

    @pytest.mark.parametrize(
        ("parameter", "key"),
        [
            ("account_number_start", "AccountNumberStart"),
            ("account_number_end", "AccountNumberEnd"),
            ("voucherstatus", "Voucherstatus"),
        ],
    )
    def test_integer_parameters(self, netvisor, responses, parameter, key):
        value = 1
        url = "http://koulutus.netvisor.fi/AccountingLedger.nv?%s=1" % key
        responses.add(
            method="GET",
            url=url,
            body=get_response_content("AccountingList.xml"),
            content_type="text/html; charset=utf-8",
            match_querystring=True,
        )
        assert netvisor.accounting.ledger(**{parameter: value}) is not None
        request = responses.calls[0].request
        assert request.url == url

    def test_netvisor_key_list_parameter(self, netvisor, responses):
        url = (
            "http://koulutus.netvisor.fi/AccountingLedger.nv?"
            "NetvisorKeyList=1%2C2%2C3"
        )
        responses.add(
            method="GET",
            url=url,
            body=get_response_content("AccountingList.xml"),
            content_type="text/html; charset=utf-8",
            match_querystring=True,
        )
        assert netvisor.accounting.ledger(netvisor_key_list=[1, 2, 3]) is not None
        request = responses.calls[0].request
        assert request.url == url

    def test_create_voucher(self, netvisor, responses):
        responses.add(
            method="POST",
            url="http://koulutus.netvisor.fi/Accounting.nv",
            body=get_response_content("AccountingCreateVoucher.xml"),
            content_type="text/html; charset=utf-8",
            match_querystring=True,
        )

        netvisor_id = netvisor.accounting.create(
            {
                "mode": "net",
                "date": date(2018, 6, 11),
                "description": "Test Company Oy, invoice 1",
                "class": "Myyntilasku",
                "voucher_line": [
                    {
                        "line_sum": {"sum": Decimal("-10000.00"), "type": "net"},
                        "description": "Test Company Oy, invoice 1",
                        "account_number": 3000,
                        "vat_percent": dict(percentage=Decimal("24"), code="KOMY"),
                        "account_dimension": {
                            "dimension": "Test account",
                            "type": "name",
                        },
                        "dimension": {"name": "Projects", "item": "Project X"},
                    },
                    {
                        "line_sum": {"sum": Decimal("-5000"), "type": "net"},
                        "description": "Test Company Oy, invoice 1",
                        "account_number": 2939,
                        "vat_percent": dict(percentage=Decimal(0), code="NONE"),
                    },
                    {
                        "line_sum": {"sum": Decimal("20000"), "type": "net"},
                        "description": "Test Company Oy, invoice 1",
                        "account_number": 1701,
                        "vat_percent": dict(percentage=Decimal(0), code="NONE"),
                    },
                ],
                "attachments": [
                    {
                        "mime_type": "application/pdf",
                        "description": "Test attachment",
                        "filename": "attachment.pdf",
                        "data": "JVBERi0xLjQNJeLjz9MNCjYgMCB",
                    }
                ],
            }
        )
        request = responses.calls[0].request

        assert netvisor_id == 8
        assert xmltodict.parse(request.body) == xmltodict.parse(
            get_request_content("Voucher.xml")
        )
