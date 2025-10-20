# magma-converter
Python package to convert CVGHM seismic data structures into SDS format.

## Install
```python
pip install magma-converter
```

## Supported Directory Structure (_Indonesia_)
| Volcano            | directory_structure                              | Group       |
|--------------------|--------------------------------------------------|-------------|
| Anak Krakatau      | `kra`,`krakatau`,`anak krakatau`,`anak-krakatau` | SAC         |
| Awu                | `awu`                                            | Seisan      |
| Bromo              | `bro`,`bromo`                                    | SAC         |
| Dieng**            | `die`,`dieng`                                    | SAC, Seisan |
| Dukono             | `duk`,`dukono`                                   | Seisan      |
| Ibu                | `ibu`                                            | Seisan      |
| Ijen*              | `ije`,`ijen`                                     | Ijen        |
| Kelud              | `kld`,`kelud`                                    | Kelud       |
| Lamongan           | `lam`,`lamongan`                                 | SAC         |
| Lewotobi Laki-laki | `lwk`,`lewotobi laki-laki`                       | Seisan      |
| Lokon              | `lok`,`lokon`                                    | Seisan      |
| Mahawu             | `mah`,`mahawu`                                   | Seisan      |
| Marapi             | `mar`,`marapi`                                   | SAC         |
| Papandayan         | `pap`,`papandayan`                               | SAC         |
| Rinjani            | `rin`,`rinjani`                                  | SAC         |
| Ruang              | `rua`,`ruang`                                    | Seisan      |
| Semeru             | `smr`,`semeru`                                   | SAC         |
| Soputan            | `sop`,`soputan`                                  | Seisan      |
| Tambora            | `tam`,`tambora`                                  | Seisan      |
| Tandikat           | `tan`,`tandikat`                                 | SAC         |

*) Special case

**) Depends on time. For Dieng, SAC was used from 2013-08-12 to 2021-09-15 and 2023-10-16 to 2024-08-15. 
Seisan was used from 2021-03-26 to 2023-10-16. 

## How to
Run this codes:
```python
from magma_converter import Convert

input_dir = 'L:\\Ijen\\Seismik Ijen'
output_dir = 'L:\\converted'
start_date: str = "2019-01-01"
end_date: str = "2019-12-31"

convert = Convert(
    input_dir=input_dir,
    output_directory=output_dir,
    directory_structure='ijen', # check table above
    min_completeness=30, # convert to SDS if completeness of data greater than 30%
).between_dates(start_date, end_date)

convert.run()
```

## Check converting results
```python
convert.success
convert.failed
```
Example output for `convert.success` or `convert.failed`:
```json
[{'trace_id': 'VG.KRA1.00.EHZ',
  'date': '2018-01-01',
  'start_time': '2018-01-01 00:00:00',
  'end_time': '2018-01-01 23:59:59',
  'sampling_rate': 100.0,
  'completeness': 99.7532986111111,
  'file_location': 'L:\\converted\\SDS\\2018\\VG\\KRA1\\EHZ.D\\VG.KRA1.00.EHZ.D.2018.001'},
 {'trace_id': 'VG.KRA2.00.EHZ',
  'date': '2018-01-01',
  'start_time': '2018-01-01 00:00:00',
  'end_time': '2018-01-01 23:59:59',
  'sampling_rate': 100.0,
  'completeness': 99.99770833333334,
  'file_location': 'L:\\converted\\SDS\\2018\\VG\\KRA2\\EHZ.D\\VG.KRA2.00.EHZ.D.2018.001'},
 {'trace_id': 'VG.KRA3.00.EHZ',
  'date': '2018-01-01',
  'start_time': '2018-01-01 00:00:00',
  'end_time': '2018-01-01 23:59:59',
  'sampling_rate': 100.0,
  'completeness': 99.79653935185185,
  'file_location': 'L:\\converted\\SDS\\2018\\VG\\KRA3\\EHZ.D\\VG.KRA3.00.EHZ.D.2018.001'},
 {'trace_id': 'VG.PULO.00.EHZ',
  'date': '2018-01-01',
  'start_time': '2018-01-01 00:00:00',
  'end_time': '2018-01-01 23:59:59',
  'sampling_rate': 100.0,
  'completeness': 98.79126157407407,
  'file_location': 'L:\\converted\\SDS\\2018\\VG\\PULO\\EHZ.D\\VG.PULO.00.EHZ.D.2018.001'},
 {'trace_id': 'VG.SRTG.00.EHZ',
  'date': '2018-01-01',
  'start_time': '2018-01-01 00:00:00',
  'end_time': '2018-01-01 23:59:59',
  'sampling_rate': 100.0,
  'completeness': 99.995625,
  'file_location': 'L:\\converted\\SDS\\2018\\VG\\SRTG\\EHZ.D\\VG.SRTG.00.EHZ.D.2018.001'},
 {'trace_id': 'VG.INFR.00.EHZ',
  'date': '2018-01-01',
  'start_time': '2018-01-01 00:00:00',
  'end_time': '2018-01-01 23:59:59',
  'sampling_rate': 100.0,
  'completeness': 99.99770833333334,
  'file_location': 'L:\\converted\\SDS\\2018\\VG\\INFR\\EHZ.D\\VG.INFR.00.EHZ.D.2018.001'}]
```
