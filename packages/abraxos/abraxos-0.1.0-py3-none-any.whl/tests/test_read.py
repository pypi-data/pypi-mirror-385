import pandas as pd

import abraxos
from abraxos.extract import ReadCsvResult


def test_read_csv_all() -> None:
    result: ReadCsvResult = abraxos.extract.read_csv_all('tests/bad.csv')
    assert result.bad_lines == [
        ['', '', '', 'd', '', 'f', '', '', '', '', 'f', '', '', '', ''],
        ['', 'f', 'f', '5', '6', '7', '8']
    ]
    assert result.dataframe.equals(
        pd.DataFrame(
            {
                'id': {0: 1, 1: 2, 2: 3, 3: 2, 4: 1},
                'name': {0: 'Odos', 1: 'Kayla', 2: 'Dexter', 3: 'Kayla', 4: 'Odos'},
                'age': {0: '38', 1: '31', 2: 'two', 3: '31', 4: '38'}
            }
        )
    )
