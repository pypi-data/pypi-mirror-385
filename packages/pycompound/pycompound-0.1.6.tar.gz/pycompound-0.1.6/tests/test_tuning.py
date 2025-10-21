
from pycompound.spec_lib_matching import tune_params_on_HRMS_data_grid
from pycompound.spec_lib_matching import tune_params_on_NRMS_data_grid
from pycompound.spec_lib_matching import tune_params_DE
from pathlib import Path
import os


'''
print('\n\ntest #1:')
tune_params_on_HRMS_data_grid(query_data=f'{Path.cwd()}/data/tuning/lcms_query_library.csv',
                              reference_data=f'{Path.cwd()}/data/lcms_reference_library.csv',
                              output_path=f'{Path.cwd()}/tuning_param_output_test1.txt')

print('\n\ntest #2:')
tune_params_on_HRMS_data_grid(query_data=f'{Path.cwd()}/data/tuning/lcms_query_library.csv',
                              reference_data=f'{Path.cwd()}/data/lcms_reference_library.csv',
                              grid={'similarity_measure':['cosine'], 'spectrum_preprocessing_order':['FCNMWL'], 'mz_min':[0], 'mz_max':[9999999], 'int_min':[0], 'int_max':[99999999], 'window_size_centroiding':[0.5], 'window_size_matching':[0.1,0.5], 'noise_threshold':[0.0], 'wf_mz':[0.0], 'wf_int':[1.0], 'LET_threshold':[0.0], 'entropy_dimension':[1.1], 'high_quality_reference_library':[False]},
                              output_path=f'{Path.cwd()}/tuning_param_output_test2.txt')

print('\n\ntest #3:')
tune_params_on_NRMS_data_grid(query_data=f'{Path.cwd()}/data/tuning/gcms_query_library.csv',
                              reference_data=f'{Path.cwd()}/data/gcms_reference_library.csv',
                              output_path=f'{Path.cwd()}/tuning_param_output_test3.txt')

print('\n\ntest #4:')
tune_params_on_NRMS_data_grid(query_data=f'{Path.cwd()}/data/tuning/gcms_query_library.csv',
                              reference_data=f'{Path.cwd()}/data/gcms_reference_library.csv',
                              grid={'similarity_measure':['cosine','shannon'], 'spectrum_preprocessing_order':['FNLW'], 'mz_min':[0], 'mz_max':[9999999], 'int_min':[0], 'int_max':[99999999], 'noise_threshold':[0.0,0.1], 'wf_mz':[0.0], 'wf_int':[1.0], 'LET_threshold':[0.0,3.0], 'entropy_dimension':[1.1], 'high_quality_reference_library':[False]},
                              output_path=f'{Path.cwd()}/tuning_param_output_test4.txt')

print('\n\ntest #5:')
tune_params_on_HRMS_data_grid(query_data=f'{Path.cwd()}/data/tuning/lcms_query_library.csv',
                              reference_data=f'{Path.cwd()}/data/lcms_reference_library.csv',
                              grid={'similarity_measure':['cosine'], 'weight':[{'Cosine':0.2, 'Shannon':0.2, 'Renyi':0.3, 'Tsallis':0.3},{'Cosine':0.25, 'Shannon':0.25, 'Renyi':0.25, 'Tsallis':0.25}], 'spectrum_preprocessing_order':['FCNMWL'], 'mz_min':[0], 'mz_max':[9999999], 'int_min':[0], 'int_max':[99999999], 'window_size_centroiding':[0.5], 'window_size_matching':[0.5], 'noise_threshold':[0.0], 'wf_mz':[0.0], 'wf_int':[1.0], 'LET_threshold':[0.0,3], 'entropy_dimension':[1.1], 'high_quality_reference_library':[False,True]},
                              output_path=f'{Path.cwd()}/tuning_param_output_test5.txt')

print('\n\ntest #6:')
tune_params_DE(query_data=f'{Path.cwd()}/data/tuning/tuning_data/filtered/lcms_query_data.csv',
               reference_data=f'{Path.cwd()}/data/tuning/tuning_data/filtered/lcms_reference_data.csv',
               chromatography_platform='HRMS',
               similarity_measure='shannon',
               optimize_params=["window_size_matching","noise_threshold","wf_mz","wf_int"],
               param_bounds={"window_size_matching":(0.0,0.5),"noise_threshold":(0.0,0.25),"wf_mz":(0.0,5.0),"wf_int":(0.0,5.0)},
               default_params={"window_size_centroiding": 0.5, "window_size_matching":0.5, "noise_threshold":0.10, "wf_mz":0.0, "wf_int":1.0, "LET_threshold":0.0, "entropy_dimension":1.1},
               maxiters=5)
'''

print('\n\ntest #7:')
tune_params_DE(query_data=f'{Path.cwd()}/data/tuning/tuning_data/filtered/gcms_query_data.csv',
               reference_data=f'{Path.cwd()}/data/tuning/tuning_data/filtered/gcms_reference_data.csv',
               chromatography_platform='NRMS',
               similarity_measure='renyi',
               optimize_params=["wf_mz","wf_int","LET_threshold","entropy_dimension"],
               param_bounds={"wf_mz":(0.0,5.0),"wf_int":(0.0,5.0),"LET_threshold":(0,5),"entropy_dimension":(1.01,3)},
               default_params={"noise_threshold":0.10, "wf_mz":0.0, "wf_int":1.0, "LET_threshold":0.0, "entropy_dimension":1.1},
               de_workers=-1,
               return_output=True)

