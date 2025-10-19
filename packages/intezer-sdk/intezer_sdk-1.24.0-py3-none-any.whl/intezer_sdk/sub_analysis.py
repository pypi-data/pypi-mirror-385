import datetime
from typing import IO
from typing import List
from typing import Optional
from typing import Union

from intezer_sdk import _operation
from intezer_sdk import errors
from intezer_sdk import operation
from intezer_sdk._api import IntezerApi
from intezer_sdk.api import IntezerApiClient
from intezer_sdk.api import get_global_api


class SubAnalysis:
    """
    SubAnalysis is a class representing a sub-analysis object in an Intezer API.
    """
    def __init__(self,
                 analysis_id: str,
                 composed_analysis_id: str,
                 sha256: str,
                 source: str,
                 extraction_info: Optional[dict],
                 api: IntezerApiClient = None,
                 verdict=None):
        self.composed_analysis_id = composed_analysis_id
        self.analysis_id = analysis_id
        self._sha256 = sha256
        self._source = source
        self._extraction_info = extraction_info
        self._verdict = verdict
        self._api = IntezerApi(api or get_global_api())
        self._code_reuse = None
        self._metadata = None
        self._operations = {}
        self._indicators = None

    @classmethod
    def from_analysis_id(cls,
                         analysis_id: str,
                         composed_analysis_id: str,
                         lazy_load=True,
                         api: IntezerApiClient = None) -> Optional['SubAnalysis']:
        """
        class method that creates a new instance of the class by fetching the details of the sub-analysis from the Intezer API.
        If lazy_load is set to True, the details of the sub-analysis are not fetched immediately.
        If lazy_load is set to False, the details of the sub-analysis are fetched immediately.
        Returns None when analysis doesn't exist.
        :param analysis_id: The ID of the analysis to retrieve.
        :param composed_analysis_id: The ID of the parent analysis to retrieve.
        :param lazy_load: bool indicating if the details of the sub-analysis should be fetched immediately or not
        :param api: The API connection to Intezer.
        :return: A SubAnalysis instance with the given analysis ID.
        """
        sub_analysis = cls(analysis_id, composed_analysis_id, '', '', None, api)
        if not lazy_load:
            try:
                sub_analysis._init_sub_analysis_from_parent()
            except errors.SubAnalysisNotFoundError:
                return None
        return sub_analysis

    @property
    def sha256(self) -> str:
        if not self._sha256:
            self._init_sub_analysis_from_parent()

        return self._sha256

    @property
    def source(self) -> str:
        if not self._source:
            self._init_sub_analysis_from_parent()

        return self._source

    @property
    def extraction_info(self) -> Optional[dict]:
        # Since extraction_info could be none, we check if the sha256 was provided, signaling we already fetch it
        if not self._sha256:
            self._init_sub_analysis_from_parent()

        return self._extraction_info

    @property
    def code_reuse(self):
        if self._code_reuse is None:
            self._code_reuse = self._api.get_sub_analysis_code_reuse_by_id(self.composed_analysis_id, self.analysis_id)
        return self._code_reuse

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = self._api.get_sub_analysis_metadata_by_id(self.composed_analysis_id, self.analysis_id)
        return self._metadata

    @property
    def verdict(self) -> str:
        if self.source != 'endpoint':
            raise TypeError('Verdict is support only for endpoint sub-analyses that')
        return self._verdict

    @property
    def indicators(self) -> List[dict]:
        if self._indicators is None:
            self._indicators = self.metadata.get('indicators', [])

        return self._indicators

    def _init_sub_analysis_from_parent(self):
        sub_analyses = self._api.get_sub_analyses_by_id(self.composed_analysis_id)
        sub_analysis = next((
            sub_analysis for sub_analysis in sub_analyses if sub_analysis['sub_analysis_id'] == self.analysis_id),
            None)
        if not sub_analysis:
            raise errors.SubAnalysisNotFoundError(self.analysis_id)

        self._sha256 = sub_analysis['sha256']
        self._source = sub_analysis['source']
        self._extraction_info = sub_analysis.get('extraction_info')

    def find_related_files(self,
                           family_id: str,
                           wait: Union[bool, int] = False,
                           wait_timeout: Optional[datetime.timedelta] = None) -> operation.Operation:
        result_url = self._api.get_sub_analysis_related_files_by_family_id(self.composed_analysis_id,
                                                                           self.analysis_id,
                                                                           family_id)
        return _operation.handle_operation(self._operations,
                                          self._api,
                                          f'Related files: {family_id}',
                                          result_url,
                                          wait,
                                          wait_timeout)

    def get_account_related_samples(self,
                                    wait: Union[bool, int] = False,
                                    wait_timeout: Optional[datetime.timedelta] = None) -> Optional[operation.Operation]:
        try:
            result_url = self._api.get_sub_analysis_account_related_samples_by_id(self.composed_analysis_id,
                                                                                  self.analysis_id)
        except Exception:
            return None

        return _operation.handle_operation(self._operations,
                                          self._api,
                                          'Account files related samples',
                                          result_url,
                                          wait,
                                          wait_timeout)

    def generate_vaccine(self,
                         wait: Union[bool, int] = False,
                         wait_timeout: Optional[datetime.timedelta] = None) -> operation.Operation:
        result_url = self._api.generate_sub_analysis_vaccine_by_id(self.composed_analysis_id, self.analysis_id)
        return _operation.handle_operation(self._operations, self._api, 'Vaccine', result_url, wait, wait_timeout)

    def get_capabilities(self,
                         wait: Union[bool, int] = False,
                         wait_timeout: Optional[datetime.timedelta] = None) -> operation.Operation:
        result_url = self._api.get_sub_analysis_capabilities_by_id(self.composed_analysis_id, self.analysis_id)
        return _operation.handle_operation(self._operations, self._api, 'Capabilities', result_url, wait, wait_timeout)

    def get_strings(self,
                    wait: Union[bool, int] = False,
                    wait_timeout: Optional[datetime.timedelta] = None) -> operation.Operation:
        result = self._api.get_strings_by_id(self.composed_analysis_id, self.analysis_id)
        return _operation.handle_operation(self._operations,
                                          self._api,
                                          'Strings',
                                          result['result_url'],
                                          wait, wait_timeout)

    def get_string_related_samples(self,
                                   string_value: str,
                                   wait: Union[bool, int] = False,
                                   wait_timeout: Optional[datetime.timedelta] = None) -> operation.Operation:
        result_url = self._api.get_string_related_samples_by_id(self.composed_analysis_id,
                                                                self.analysis_id,
                                                                string_value)
        return _operation.handle_operation(self._operations,
                                          self._api,
                                          f'Strings related samples: {string_value}',
                                          result_url,
                                          wait,
                                          wait_timeout)

    def download_file(self, path: str = None, output_stream: IO = None, password_protection: str = None):
        """
        Downloads the analysis's file.
        `path` or `output_stream` must be provided.
        :param path: A path to where to save the file, it can be either a directory or non-existing file path.
        :param output_stream: A file-like object to write the file's content to.
        :param password_protection: set password protection to download file as zip with password.
        """
        self._api.download_file_by_sha256(self.sha256, path, output_stream, password_protection)
