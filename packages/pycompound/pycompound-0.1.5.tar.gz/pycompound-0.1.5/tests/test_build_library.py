
from pycompound.build_library import build_library_from_raw_data
from pathlib import Path
import os


print('\nTest #0:')
build_library_from_raw_data(input_path=f'{Path.cwd()}/data/GNPS-SELLECKCHEM-FDA-PART1.mgf', output_path=None, is_reference=False)

print('\nTest #1:')
build_library_from_raw_data(input_path=f'{Path.cwd()}/data/GNPS-SELLECKCHEM-FDA-PART1.mgf', output_path=f'{Path.cwd()}/data/library_from_mgf_not_reference.csv', is_reference=False)

print('\nTest #2:')
build_library_from_raw_data(input_path=f'{Path.cwd()}/data/GNPS-SELLECKCHEM-FDA-PART1.mgf', output_path=f'{Path.cwd()}/data/library_from_mgf_reference.csv', is_reference=True)

print('\nTest #3:')
build_library_from_raw_data(input_path=f'{Path.cwd()}/data/1min.mzML', output_path=f'{Path.cwd()}/data/library_from_mzML.csv', is_reference=False)

print('\nTest #4:')
build_library_from_raw_data(input_path=f'{Path.cwd()}/data/MoNA-export-Human_Plasma_Quant.msp', output_path=None, is_reference=True)

print('\nTest #:5')
build_library_from_raw_data(input_path=None, output_path=None, is_reference=False)

# note that the CDF file is too large to store in a GitHub repo. So, this test won't work unless a CDF file that exists is specified
#print('\nTest #10:')
#build_library_from_raw_data(input_path=f'{Path.cwd()}/data/liver_9-1_MTBSTFA_split10.cdf', output_path=f'{Path.cwd()}/data/library_from_cdf.csv', is_reference=False)

