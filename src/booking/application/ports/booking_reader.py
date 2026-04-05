from abc import ABC, abstractmethod
from typing import BinaryIO

import pandas as pd


class IBookingReader(ABC):
    @abstractmethod
    async def read(self, file_obj: BinaryIO) -> pd.DataFrame:
        """
        Прочитать файл и вернуть DataFrame.

        Отвечает только за:
        - чтение файла
        - определение разделителя
        - загрузку CSV
        - базовую техническую проверку (например, файл не пуст)

        Не отвечает за:
        - бизнес-валидацию
        - дедупликацию
        - маппинг в доменные сущности
        """
        raise NotImplementedError
