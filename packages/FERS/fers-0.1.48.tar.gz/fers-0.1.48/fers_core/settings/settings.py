from typing import Optional
from ..settings.anlysis_options import AnalysisOptions
from ..settings.general_info import GeneralInfo


class Settings:
    _settings_counter = 1

    def __init__(
        self,
        analysis_options: Optional[AnalysisOptions] = None,
        general_info: Optional[GeneralInfo] = None,
        id: Optional[int] = None,
    ):
        self.settings_id = id or Settings._settings_counter
        if id is None:
            Settings._settings_counter += 1
        self.analysis_options = analysis_options if analysis_options else AnalysisOptions()
        self.general_info = general_info if general_info else GeneralInfo()

    @classmethod
    def reset_counter(cls):
        cls._settings_counter = 1

    def to_dict(self):
        return {
            "id": self.settings_id,
            "analysis_options": self.analysis_options.to_dict(),
            "general_info": self.general_info.to_dict(),
        }
