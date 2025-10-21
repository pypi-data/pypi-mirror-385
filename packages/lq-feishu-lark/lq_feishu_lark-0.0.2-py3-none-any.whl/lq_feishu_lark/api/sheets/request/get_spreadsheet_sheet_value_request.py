from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class GetSpreadsheetSheetValueRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.spreadsheet_token: Optional[str] = None
        self.sheet_id: Optional[str] = None

    @staticmethod
    def builder() -> "GetSpreadsheetSheetValueRequestBuilder":
        return GetSpreadsheetSheetValueRequestBuilder()


class GetSpreadsheetSheetValueRequestBuilder(object):

    def __init__(self) -> None:
        get_spreadsheet_sheet_request = GetSpreadsheetSheetValueRequest()
        get_spreadsheet_sheet_request.http_method = HttpMethod.GET
        get_spreadsheet_sheet_request.uri = "/open-apis/sheets/v3/spreadsheets/:spreadsheet_token/sheets/:sheet_id"
        get_spreadsheet_sheet_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._get_spreadsheet_sheet_request: GetSpreadsheetSheetValueRequest = get_spreadsheet_sheet_request

    def spreadsheet_token(self, spreadsheet_token: str) -> "GetSpreadsheetSheetValueRequestBuilder":
        self._get_spreadsheet_sheet_request.spreadsheet_token = spreadsheet_token
        self._get_spreadsheet_sheet_request.paths["spreadsheet_token"] = str(spreadsheet_token)
        return self

    def sheet_id(self, sheet_id: str) -> "GetSpreadsheetSheetValueRequestBuilder":
        self._get_spreadsheet_sheet_request.sheet_id = sheet_id
        self._get_spreadsheet_sheet_request.paths["sheet_id"] = str(sheet_id)
        return self

    def build(self) -> GetSpreadsheetSheetValueRequest:
        return self._get_spreadsheet_sheet_request
