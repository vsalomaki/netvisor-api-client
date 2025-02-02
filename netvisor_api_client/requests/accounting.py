"""
netvisor.requests.accounting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013-2016 by Fast Monkeys Oy | 2019- by Heltti Oy
:license: MIT, see LICENSE for more details.
"""

from ..responses.accounting import AccountingLedgerResponse, CreateAccountingResponse
from ..schemas.accounting import CreateAccountingVoucherSchema
from .base import Request


class AccountingLedgerRequest(Request):
    method = "GET"
    uri = "AccountingLedger.nv"
    response_cls = AccountingLedgerResponse


class CreateAccountingRequest(Request):
    method = "POST"
    uri = "Accounting.nv"
    response_cls = CreateAccountingResponse
    schema_cls = CreateAccountingVoucherSchema
    tag_name = "Voucher"
