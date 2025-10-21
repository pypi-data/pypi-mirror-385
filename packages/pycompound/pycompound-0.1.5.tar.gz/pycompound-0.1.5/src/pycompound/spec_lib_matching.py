
from pycompound.build_library import build_library_from_raw_data
from .processing import *
from .similarity_measures import *
import pandas as pd
from pathlib import Path
import json
from itertools import product
from joblib import Parallel, delayed
import csv
import sys, csv
from scipy.optimize import differential_evolution


def _vector_to_full_params(X, default_params, optimize_params):
    params = default_params.copy()
    for name, val in zip(optimize_params, X):
        params[name] = float(val)
    return params


def objective_function_HRMS(X, ctx):
    p = _vector_to_full_params(X, ctx["default_params"], ctx["optimize_params"])
    if 'window_size_centroiding' in ctx.keys():
        acc = get_acc_HRMS(
            ctx["df_query"], ctx["df_reference"],
            ctx["unique_query_ids"], ctx["unique_reference_ids"],
            ctx["similarity_measure"], ctx["weights"], ctx["spectrum_preprocessing_order"],
            ctx["mz_min"], ctx["mz_max"], ctx["int_min"], ctx["int_max"],
            p["window_size_centroiding"], p["window_size_matching"], p["noise_threshold"],
            p["wf_mz"], p["wf_int"], p["LET_threshold"],
            p["entropy_dimension"],
            ctx["high_quality_reference_library"],
            verbose=False
        )
    else:
        acc = get_acc_NRMS(
            ctx["df_query"], ctx["df_reference"],
            ctx["unique_query_ids"], ctx["unique_reference_ids"],
            ctx["similarity_measure"], ctx["weights"], ctx["spectrum_preprocessing_order"],
            ctx["mz_min"], ctx["mz_max"], ctx["int_min"], ctx["int_max"],
            p["noise_threshold"],
            p["wf_mz"], p["wf_int"], p["LET_threshold"],
            p["entropy_dimension"],
            ctx["high_quality_reference_library"],
            verbose=False
        )
    print(f"\nparams({ctx['optimize_params']}) = {np.array(X)}\naccuracy: {acc*100}%")
    return 1.0 - acc




def tune_params_DE(query_data=None, reference_data=None, similarity_measure='cosine', weights=None, spectrum_preprocessing_order='CNMWL', mz_min=0, mz_max=999999999, int_min=0, int_max=999999999, high_quality_reference_library=False, optimize_params=["window_size_centroiding","window_size_matching","noise_threshold","wf_mz","wf_int","LET_threshold","entropy_dimension"], param_bounds={"window_size_centroiding":(0.0,0.5),"window_size_matching":(0.0,0.5),"noise_threshold":(0.0,0.25),"wf_mz":(0.0,5.0),"wf_int":(0.0,5.0),"LET_threshold":(0.0,5.0),"entropy_dimension":(1.0,3.0)}, default_params={"window_size_centroiding": 0.5, "window_size_matching":0.5, "noise_threshold":0.10, "wf_mz":0.0, "wf_int":1.0, "LET_threshold":0.0, "entropy_dimension":1.1}):

    '''
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    print(param_bounds)
    print(default_params)
    print(type(param_bounds['noise_threshold'][0]))
    print(type(param_bounds['noise_threshold'][1]))
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    '''

    if query_data is None:
        print('\nError: No argument passed to the mandatory query_data. Please pass the path to the TXT file of the query data.')
        sys.exit()
    else:
        extension = query_data.rsplit('.',1)
        extension = extension[(len(extension)-1)]
        if extension == 'mgf' or extension == 'MGF' or extension == 'mzML' or extension == 'mzml' or extension == 'MZML' or extension == 'cdf' or extension == 'CDF':
            output_path_tmp = query_data[:-3] + 'csv'
            build_library_from_raw_data(input_path=query_data, output_path=output_path_tmp, is_reference=False)
            df_query = pd.read_csv(output_path_tmp)
        if extension == 'csv' or extension == 'CSV':
            df_query = pd.read_csv(query_data)
        unique_query_ids = df_query.iloc[:,0].unique()

    if reference_data is None:
        print('\nError: No argument passed to the mandatory reference_data. Please pass the path to the CSV file of the reference data.')
        sys.exit()
    else:
        if isinstance(reference_data,str):
            df_reference = get_reference_df(reference_data=reference_data)
            unique_reference_ids = df_reference.iloc[:,0].unique()
        else:
            dfs = []
            unique_reference_ids = []
            for f in reference_data:
                tmp = get_reference_df(reference_data=f)
                dfs.append(tmp)
                unique_reference_ids.extend(tmp.iloc[:,0].unique())
            df_reference = pd.concat(dfs, axis=0, ignore_index=True)

    unique_query_ids = df_query['id'].unique().tolist()
    unique_reference_ids = df_reference['id'].unique().tolist()

    ctx = dict(
        df_query=df_query,
        df_reference=df_reference,
        unique_query_ids=unique_query_ids,
        unique_reference_ids=unique_reference_ids,
        similarity_measure=similarity_measure,
        weights=weights,
        spectrum_preprocessing_order=spectrum_preprocessing_order,
        mz_min=mz_min, mz_max=mz_max, int_min=int_min, int_max=int_max,
        high_quality_reference_library=high_quality_reference_library,
        default_params=default_params,
        optimize_params=optimize_params,
    )

    bounds = [param_bounds[p] for p in optimize_params]

    #print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    #print(df_query.head())
    #print(df_reference.head())
    #print(bounds)
    #print(ctx)
    #print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

    result = differential_evolution(
        objective_function_HRMS,
        bounds=bounds,
        args=(ctx,),
        maxiter=3,
        tol=0.0,
        workers=-1,
        seed=1,
    )

    best_full_params = _vector_to_full_params(result.x, default_params, optimize_params)
    best_acc = 100.0 - (result.fun * 100.0)

    print("\n=== Differential Evolution Result ===")
    print(f"Optimized over: {optimize_params}")
    print("Best values (selected params):")
    for name in optimize_params:
        print(f"  {name}: {best_full_params[name]}")
    print("\nFull parameter set used in final evaluation:")
    for k, v in best_full_params.items():
        print(f"  {k}: {v}")
    print(f"\nBest accuracy: {best_acc:.3f}%")




default_HRMS_grid = {'similarity_measure':['cosine'], 'weight':[{'Cosine':0.25,'Shannon':0.25,'Renyi':0.25,'Tsallis':0.25}], 'spectrum_preprocessing_order':['FCNMWL'], 'mz_min':[0], 'mz_max':[9999999], 'int_min':[0], 'int_max':[99999999], 'window_size_centroiding':[0.5], 'window_size_matching':[0.5], 'noise_threshold':[0.0], 'wf_mz':[0.0], 'wf_int':[1.0], 'LET_threshold':[0.0], 'entropy_dimension':[1.1], 'high_quality_reference_library':[False]}
default_NRMS_grid = {'similarity_measure':['cosine'], 'weight':[{'Cosine':0.25,'Shannon':0.25,'Renyi':0.25,'Tsallis':0.25}], 'spectrum_preprocessing_order':['FCNMWL'], 'mz_min':[0], 'mz_max':[9999999], 'int_min':[0], 'int_max':[99999999], 'noise_threshold':[0.0], 'wf_mz':[0.0], 'wf_int':[1.0], 'LET_threshold':[0.0], 'entropy_dimension':[1.1], 'high_quality_reference_library':[False]}


def _eval_one_HRMS(df_query, df_reference, unique_query_ids, unique_reference_ids,
              similarity_measure_tmp, weight,
              spectrum_preprocessing_order_tmp, mz_min_tmp, mz_max_tmp,
              int_min_tmp, int_max_tmp, noise_threshold_tmp,
              window_size_centroiding_tmp, window_size_matching_tmp,
              wf_mz_tmp, wf_int_tmp, LET_threshold_tmp,
              entropy_dimension_tmp, high_quality_reference_library_tmp):

    acc = get_acc_HRMS(
        df_query=df_query, df_reference=df_reference,
        unique_query_ids=unique_query_ids, unique_reference_ids=unique_reference_ids,
        similarity_measure=similarity_measure_tmp, weights=weight,
        spectrum_preprocessing_order=spectrum_preprocessing_order_tmp,
        mz_min=mz_min_tmp, mz_max=mz_max_tmp,
        int_min=int_min_tmp, int_max=int_max_tmp,
        window_size_centroiding=window_size_centroiding_tmp,
        window_size_matching=window_size_matching_tmp,
        noise_threshold=noise_threshold_tmp,
        wf_mz=wf_mz_tmp, wf_int=wf_int_tmp,
        LET_threshold=LET_threshold_tmp,
        entropy_dimension=entropy_dimension_tmp,
        high_quality_reference_library=high_quality_reference_library_tmp,
        verbose=True
    )

    return (
        acc, similarity_measure_tmp, json.dumps(weight), spectrum_preprocessing_order_tmp,
        mz_min_tmp, mz_max_tmp, int_min_tmp, int_max_tmp,
        noise_threshold_tmp, window_size_centroiding_tmp, window_size_matching_tmp,
        wf_mz_tmp, wf_int_tmp, LET_threshold_tmp, entropy_dimension_tmp,
        high_quality_reference_library_tmp
    )


def _eval_one_NRMS(df_query, df_reference, unique_query_ids, unique_reference_ids,
              similarity_measure_tmp, weight,
              spectrum_preprocessing_order_tmp, mz_min_tmp, mz_max_tmp,
              int_min_tmp, int_max_tmp, noise_threshold_tmp,
              wf_mz_tmp, wf_int_tmp, LET_threshold_tmp,
              entropy_dimension_tmp, high_quality_reference_library_tmp):

    acc = get_acc_NRMS(
        df_query=df_query, df_reference=df_reference,
        unique_query_ids=unique_query_ids, unique_reference_ids=unique_reference_ids,
        similarity_measure=similarity_measure_tmp, weights=weight,
        spectrum_preprocessing_order=spectrum_preprocessing_order_tmp,
        mz_min=mz_min_tmp, mz_max=mz_max_tmp,
        int_min=int_min_tmp, int_max=int_max_tmp,
        noise_threshold=noise_threshold_tmp,
        wf_mz=wf_mz_tmp, wf_int=wf_int_tmp,
        LET_threshold=LET_threshold_tmp,
        entropy_dimension=entropy_dimension_tmp,
        high_quality_reference_library=high_quality_reference_library_tmp,
    )

    return (
        acc, similarity_measure_tmp, json.dumps(weight), spectrum_preprocessing_order_tmp,
        mz_min_tmp, mz_max_tmp, int_min_tmp, int_max_tmp, noise_threshold_tmp, 
        wf_mz_tmp, wf_int_tmp, LET_threshold_tmp, entropy_dimension_tmp, high_quality_reference_library_tmp
    )



def tune_params_on_HRMS_data_grid(query_data=None, reference_data=None, grid=None, output_path=None, return_output=False):
    """
    runs spectral library matching on high-resolution mass spectrometry (HRMS) data with all possible combinations of parameters in the grid dict, saves results from each choice of parameters to a TXT file, and prints top-performing parameters

    --query_data: mgf, mzML, or csv file of query mass spectrum/spectra to be identified. If csv file, each row should correspond to a mass spectrum, the left-most column should contain an identifier, and each of the other columns should correspond to a single mass/charge ratio. Mandatory argument.
    --reference_data: mgf, mzML, or csv file of the reference mass spectra. If csv file, each row should correspond to a mass spectrum, the left-most column should contain in identifier (i.e. the CAS registry number or the compound name), and the remaining column should correspond to a single mass/charge ratio. Mandatory argument.
    --grid: dict with all possible parameter values to try.
    --output_path: accuracy from each choice of parameter set is saved to a TXT file here.
    """

    grid = {**default_HRMS_grid, **(grid or {})}
    for key, value in grid.items():
        globals()[key] = value

    if query_data is None:
        print('\nError: No argument passed to the mandatory query_data. Please pass the path to the TXT file of the query data.')
        sys.exit()
    else:
        extension = query_data.rsplit('.',1)
        extension = extension[(len(extension)-1)]
        if extension == 'mgf' or extension == 'MGF' or extension == 'mzML' or extension == 'mzml' or extension == 'MZML' or extension == 'cdf' or extension == 'CDF':
            output_path_tmp = query_data[:-3] + 'csv'
            build_library_from_raw_data(input_path=query_data, output_path=output_path_tmp, is_reference=False)
            df_query = pd.read_csv(output_path_tmp)
        if extension == 'csv' or extension == 'CSV':
            df_query = pd.read_csv(query_data)
        unique_query_ids = df_query.iloc[:,0].unique()

    if reference_data is None:
        print('\nError: No argument passed to the mandatory reference_data. Please pass the path to the CSV file of the reference data.')
        sys.exit()
    else:
        if isinstance(reference_data,str):
            df_reference = get_reference_df(reference_data=reference_data)
            unique_reference_ids = df_reference.iloc[:,0].unique()
        else:
            dfs = []
            unique_reference_ids = []
            for f in reference_data:
                tmp = get_reference_df(reference_data=f)
                dfs.append(tmp)
                unique_reference_ids.extend(tmp.iloc[:,0].unique())
            df_reference = pd.concat(dfs, axis=0, ignore_index=True)

    print(f'\nNote that there are {len(unique_query_ids)} unique query spectra, {len(unique_reference_ids)} unique reference spectra, and {len(set(unique_query_ids) & set(unique_reference_ids))} of the query and reference spectra IDs are in common.\n')

    if output_path is None:
        output_path = f'{Path.cwd()}/tuning_param_output.txt'
        print(f'Warning: since output_path=None, the output will be written to the current working directory: {output_path}')

    param_grid = product(similarity_measure, weight, spectrum_preprocessing_order, mz_min, mz_max, int_min, int_max, noise_threshold,
                         window_size_centroiding, window_size_matching, wf_mz, wf_int, LET_threshold, entropy_dimension, high_quality_reference_library)
    results = Parallel(n_jobs=-1, verbose=10)(delayed(_eval_one_HRMS)(df_query, df_reference, unique_query_ids, unique_reference_ids, *params) for params in param_grid)

    df_out = pd.DataFrame(results, columns=[
        'ACC','SIMILARITY.MEASURE','WEIGHT','SPECTRUM.PROCESSING.ORDER', 'MZ.MIN','MZ.MAX','INT.MIN','INT.MAX','NOISE.THRESHOLD',
        'WINDOW.SIZE.CENTROIDING','WINDOW.SIZE.MATCHING', 'WF.MZ','WF.INT','LET.THRESHOLD','ENTROPY.DIMENSION', 'HIGH.QUALITY.REFERENCE.LIBRARY'
    ])
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("\"","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("{","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("}","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace(":","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("Cosine","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("Shannon","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("Renyi","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("Tsallis","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace(" ","",regex=False)
    df_out.to_csv(output_path, index=False, sep='\t', quoting=csv.QUOTE_NONE)

    if return_output is False:
        df_out.to_csv(output_path, index=False, sep='\t', quoting=csv.QUOTE_NONE)
    else:
        return df_out



def tune_params_on_HRMS_data_grid_shiny(query_data=None, reference_data=None, grid=None, output_path=None, return_output=False):
    """
    runs spectral library matching on high-resolution mass spectrometry (HRMS) data with all possible 
    combinations of parameters in the grid dict, saves results from each choice of parameters to a TXT file, 
    and prints top-performing parameters

    --query_data: mgf, mzML, or csv file of query mass spectrum/spectra to be identified. If csv file, each row
       should correspond to a mass spectrum, the left-most column should contain an identifier, and each of the 
       other columns should correspond to a single mass/charge ratio. Mandatory argument.
    --reference_data: mgf, mzML, or csv file of the reference mass spectra. If csv file, each row should correspond
       to a mass spectrum, the left-most column should contain in identifier (i.e. the CAS registry number or the 
       compound name), and the remaining column should correspond to a single mass/charge ratio. Mandatory argument.
    --grid: dict with all possible parameter values to try.
    --output_path: accuracy from each choice of parameter set is saved to a TXT file here.
    """

    local_grid = {**default_HRMS_grid, **(grid or {})}
    for key, value in local_grid.items():
        globals()[key] = value

    if query_data is None:
        print('\nError: No argument passed to the mandatory query_data. Please pass the path to the data file.')
        sys.exit()
    else:
        extension = query_data.rsplit('.', 1)[-1]
        if extension in ('mgf','MGF','mzML','mzml','MZML','cdf','CDF'):
            output_path_tmp = query_data[:-3] + 'csv'
            build_library_from_raw_data(input_path=query_data, output_path=output_path_tmp, is_reference=False)
            df_query = pd.read_csv(output_path_tmp)
        elif extension in ('csv','CSV'):
            df_query = pd.read_csv(query_data)
        else:
            print(f'\nError: Unsupported query_data extension: {extension}')
            sys.exit()
        unique_query_ids = df_query.iloc[:, 0].unique()

    if reference_data is None:
        print('\nError: No argument passed to the mandatory reference_data. Please pass the path to the data file(s).')
        sys.exit()
    else:
        if isinstance(reference_data, str):
            df_reference = get_reference_df(reference_data=reference_data)
            unique_reference_ids = df_reference.iloc[:, 0].unique()
        else:
            dfs = []
            unique_reference_ids = []
            for f in reference_data:
                tmp = get_reference_df(reference_data=f)
                dfs.append(tmp)
                unique_reference_ids.extend(tmp.iloc[:, 0].unique())
            df_reference = pd.concat(dfs, axis=0, ignore_index=True)

    print(f'\nNote that there are {len(unique_query_ids)} unique query spectra, '
          f'{len(unique_reference_ids)} unique reference spectra, and '
          f'{len(set(unique_query_ids) & set(unique_reference_ids))} of the query and reference spectra IDs are in common.\n')

    if output_path is None:
        output_path = f'{Path.cwd()}/tuning_param_output.txt'
        print(f'Warning: since output_path=None, the output will be written to the current working directory: {output_path}')

    param_grid = product(
        similarity_measure, weight, spectrum_preprocessing_order, mz_min, mz_max, int_min, int_max,
        noise_threshold, window_size_centroiding, window_size_matching, wf_mz, wf_int, LET_threshold,
        entropy_dimension, high_quality_reference_library
    )

    results = []
    total = (
        len(similarity_measure) * len(weight) * len(spectrum_preprocessing_order) * len(mz_min) * len(mz_max) *
        len(int_min) * len(int_max) * len(noise_threshold) * len(window_size_centroiding) *
        len(window_size_matching) * len(wf_mz) * len(wf_int) * len(LET_threshold) *
        len(entropy_dimension) * len(high_quality_reference_library)
    )
    done = 0

    for params in param_grid:
        res = _eval_one_HRMS(df_query, df_reference, unique_query_ids, unique_reference_ids, *params)
        results.append(res)
        done += 1
        print(f'Completed {done}/{total} grid combinations.\n', flush=True)

    df_out = pd.DataFrame(results, columns=[
        'ACC','SIMILARITY.MEASURE','WEIGHT','SPECTRUM.PROCESSING.ORDER','MZ.MIN','MZ.MAX',
        'INT.MIN','INT.MAX','NOISE.THRESHOLD','WINDOW.SIZE.CENTROIDING','WINDOW.SIZE.MATCHING',
        'WF.MZ','WF.INT','LET.THRESHOLD','ENTROPY.DIMENSION','HIGH.QUALITY.REFERENCE.LIBRARY'
    ])

    if 'WEIGHT' in df_out.columns:
        df_out['WEIGHT'] = (
            df_out['WEIGHT'].astype(str)
                .str.replace("\"","",regex=False)
                .str.replace("{","",regex=False)
                .str.replace("}","",regex=False)
                .str.replace(":","",regex=False)
                .str.replace("Cosine","",regex=False)
                .str.replace("Shannon","",regex=False)
                .str.replace("Renyi","",regex=False)
                .str.replace("Tsallis","",regex=False)
                .str.replace(" ","",regex=False)
        )

    if return_output:
        return df_out
    else:
        df_out.to_csv(output_path, index=False, sep='\t', quoting=csv.QUOTE_NONE)
        print(f'Wrote results to {output_path}')


def tune_params_on_NRMS_data_grid(query_data=None, reference_data=None, grid=None, output_path=None, return_output=False):
    """
    runs spectral library matching on nominal-resolution mass spectrometry (NRMS) data with all possible combinations of parameters in the grid dict, saves results from each choice of parameters to a TXT file, and prints top-performing parameters

    --query_data: mgf, mzML, or csv file of query mass spectrum/spectra to be identified. If csv file, each row should correspond to a mass spectrum, the left-most column should contain an identifier, and each of the other columns should correspond to a single mass/charge ratio. Mandatory argument.
    --reference_data: mgf, mzML, or csv file of the reference mass spectra. If csv file, each row should correspond to a mass spectrum, the left-most column should contain in identifier (i.e. the CAS registry number or the compound name), and the remaining column should correspond to a single mass/charge ratio. Mandatory argument.
    --grid: dict with all possible parameter values to try
    --output_path: accuracy from each choice of parameter set is saved to a TXT file here
    """

    grid = {**default_NRMS_grid, **(grid or {})}
    for key, value in grid.items():
        globals()[key] = value

    if query_data is None:
        print('\nError: No argument passed to the mandatory query_data. Please pass the path to the CSV file of the query data.')
        sys.exit()
    else:
        extension = query_data.rsplit('.',1)
        extension = extension[(len(extension)-1)]
        if extension == 'mgf' or extension == 'MGF' or extension == 'mzML' or extension == 'mzml' or extension == 'MZML' or extension == 'cdf' or extension == 'CDF':
            output_path_tmp = query_data[:-3] + 'csv'
            build_library_from_raw_data(input_path=query_data, output_path=output_path_tmp, is_reference=False)
            df_query = pd.read_csv(output_path_tmp)
        if extension == 'csv' or extension == 'CSV':
            df_query = pd.read_csv(query_data)
        unique_query_ids = df_query.iloc[:,0].unique()

    if reference_data is None:
        print('\nError: No argument passed to the mandatory reference_data. Please pass the path to the CSV file of the reference data.')
        sys.exit()
    else:
        if isinstance(reference_data,str):
            df_reference = get_reference_df(reference_data=reference_data)
            unique_reference_ids = df_reference.iloc[:,0].unique()
        else:
            dfs = []
            unique_reference_ids = []
            for f in reference_data:
                tmp = get_reference_df(reference_data=f)
                dfs.append(tmp)
                unique_reference_ids.extend(tmp.iloc[:,0].unique())
            df_reference = pd.concat(dfs, axis=0, ignore_index=True)

    print(f'\nNote that there are {len(unique_query_ids)} unique query spectra, {len(unique_reference_ids)} unique reference spectra, and {len(set(unique_query_ids) & set(unique_reference_ids))} of the query and reference spectra IDs are in common.\n')

    if output_path is None:
        output_path = f'{Path.cwd()}/tuning_param_output.txt'
        print(f'Warning: since output_path=None, the output will be written to the current working directory: {output_path}')

    param_grid = product(similarity_measure, weight, spectrum_preprocessing_order, mz_min, mz_max, int_min, int_max,
                         noise_threshold, wf_mz, wf_int, LET_threshold, entropy_dimension, high_quality_reference_library)
    results = Parallel(n_jobs=-1, verbose=10)(delayed(_eval_one_NRMS)(df_query, df_reference, unique_query_ids, unique_reference_ids, *params) for params in param_grid)

    df_out = pd.DataFrame(results, columns=[
        'ACC','SIMILARITY.MEASURE','WEIGHT','SPECTRUM.PROCESSING.ORDER', 'MZ.MIN','MZ.MAX','INT.MIN','INT.MAX',
        'NOISE.THRESHOLD','WF.MZ','WF.INT','LET.THRESHOLD','ENTROPY.DIMENSION', 'HIGH.QUALITY.REFERENCE.LIBRARY'
    ])
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("\"","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("{","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("}","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace(":","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("Cosine","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("Shannon","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("Renyi","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace("Tsallis","",regex=False)
    df_out['WEIGHT'] = df_out['WEIGHT'].str.replace(" ","",regex=False)
    if return_output is False:
        df_out.to_csv(output_path, index=False, sep='\t', quoting=csv.QUOTE_NONE)
    else:
        return df_out



def tune_params_on_NRMS_data_grid_shiny(query_data=None, reference_data=None, grid=None, output_path=None, return_output=False):
    """
    runs spectral library matching on nominal-resolution mass spectrometry (NRMS) data with all possible 
    combinations of parameters in the grid dict, saves results from each choice of parameters to a TXT file, 
    and prints top-performing parameters

    --query_data: mgf, mzML, or csv file of query mass spectrum/spectra to be identified. If csv file, each row
       should correspond to a mass spectrum, the left-most column should contain an identifier, and each of the 
       other columns should correspond to a single mass/charge ratio. Mandatory argument.
    --reference_data: mgf, mzML, or csv file of the reference mass spectra. If csv file, each row should correspond
       to a mass spectrum, the left-most column should contain in identifier (i.e. the CAS registry number or the 
       compound name), and the remaining column should correspond to a single mass/charge ratio. Mandatory argument.
    --grid: dict with all possible parameter values to try.
    --output_path: accuracy from each choice of parameter set is saved to a TXT file here.
    """

    local_grid = {**default_NRMS_grid, **(grid or {})}
    for key, value in local_grid.items():
        globals()[key] = value

    if query_data is None:
        print('\nError: No argument passed to the mandatory query_data. Please pass the path to the data file.')
        sys.exit()
    else:
        extension = query_data.rsplit('.', 1)[-1]
        if extension in ('mgf','MGF','mzML','mzml','MZML','cdf','CDF'):
            output_path_tmp = query_data[:-3] + 'csv'
            build_library_from_raw_data(input_path=query_data, output_path=output_path_tmp, is_reference=False)
            df_query = pd.read_csv(output_path_tmp)
        elif extension in ('csv','CSV'):
            df_query = pd.read_csv(query_data)
        else:
            print(f'\nError: Unsupported query_data extension: {extension}')
            sys.exit()
        unique_query_ids = df_query.iloc[:, 0].unique()

    if reference_data is None:
        print('\nError: No argument passed to the mandatory reference_data. Please pass the path to the data file(s).')
        sys.exit()
    else:
        if isinstance(reference_data, str):
            df_reference = get_reference_df(reference_data=reference_data)
            unique_reference_ids = df_reference.iloc[:, 0].unique()
        else:
            dfs = []
            unique_reference_ids = []
            for f in reference_data:
                tmp = get_reference_df(reference_data=f)
                dfs.append(tmp)
                unique_reference_ids.extend(tmp.iloc[:, 0].unique())
            df_reference = pd.concat(dfs, axis=0, ignore_index=True)

    print(f'\nNote that there are {len(unique_query_ids)} unique query spectra, '
          f'{len(unique_reference_ids)} unique reference spectra, and '
          f'{len(set(unique_query_ids) & set(unique_reference_ids))} of the query and reference spectra IDs are in common.\n')

    if output_path is None:
        output_path = f'{Path.cwd()}/tuning_param_output.txt'
        print(f'Warning: since output_path=None, the output will be written to the current working directory: {output_path}')

    param_grid = product(
        similarity_measure, weight, spectrum_preprocessing_order, mz_min, mz_max, int_min, int_max,
        noise_threshold, wf_mz, wf_int, LET_threshold,
        entropy_dimension, high_quality_reference_library
    )

    results = []
    total = (
        len(similarity_measure) * len(weight) * len(spectrum_preprocessing_order) * len(mz_min) * len(mz_max) * len(int_min) *
        len(int_max) * len(noise_threshold) * len(wf_mz) * len(wf_int) * len(LET_threshold) * len(entropy_dimension) * len(high_quality_reference_library)
    )
    done = 0
    for params in param_grid:
        res = _eval_one_NRMS(df_query, df_reference, unique_query_ids, unique_reference_ids, *params)
        results.append(res)
        done += 1
        print(f'Completed {done}/{total} grid combinations.\n', flush=True)

    df_out = pd.DataFrame(results, columns=[
        'ACC','SIMILARITY.MEASURE','WEIGHT','SPECTRUM.PROCESSING.ORDER','MZ.MIN','MZ.MAX',
        'INT.MIN','INT.MAX','NOISE.THRESHOLD','WF.MZ','WF.INT','LET.THRESHOLD','ENTROPY.DIMENSION','HIGH.QUALITY.REFERENCE.LIBRARY'
    ])

    if 'WEIGHT' in df_out.columns:
        df_out['WEIGHT'] = (
            df_out['WEIGHT'].astype(str)
                .str.replace("\"","",regex=False)
                .str.replace("{","",regex=False)
                .str.replace("}","",regex=False)
                .str.replace(":","",regex=False)
                .str.replace("Cosine","",regex=False)
                .str.replace("Shannon","",regex=False)
                .str.replace("Renyi","",regex=False)
                .str.replace("Tsallis","",regex=False)
                .str.replace(" ","",regex=False)
        )

    if return_output:
        return df_out
    else:
        df_out.to_csv(output_path, index=False, sep='\t', quoting=csv.QUOTE_NONE)
        print(f'Wrote results to {output_path}')




def get_acc_HRMS(df_query, df_reference, unique_query_ids, unique_reference_ids, similarity_measure, weights, spectrum_preprocessing_order, mz_min, mz_max, int_min, int_max, window_size_centroiding, window_size_matching, noise_threshold, wf_mz, wf_int, LET_threshold, entropy_dimension, high_quality_reference_library, verbose=True):

    #print('\n\n\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n\n\n')
    n_top_matches_to_save = 1

    all_similarity_scores =  []
    for query_idx in range(0,len(unique_query_ids)):
        if verbose is True:
            print(f'query spectrum #{query_idx} is being identified')
        q_idxs_tmp = np.where(df_query.iloc[:,0] == unique_query_ids[query_idx])[0]
        q_spec_tmp = np.asarray(pd.concat([df_query.iloc[q_idxs_tmp,1], df_query.iloc[q_idxs_tmp,2]], axis=1).reset_index(drop=True))
        #q_spec_tmp = q_spec_tmp.astype(float)

        similarity_scores = []
        for ref_idx in range(0,len(unique_reference_ids)):
            q_spec = q_spec_tmp
            r_idxs_tmp = np.where(df_reference.iloc[:,0] == unique_reference_ids[ref_idx])[0]
            r_spec = np.asarray(pd.concat([df_reference.iloc[r_idxs_tmp,1], df_reference.iloc[r_idxs_tmp,2]], axis=1).reset_index(drop=True))
            #print(r_spec)
            #r_spec = r_spec.astype(float)

            is_matched = False
            for transformation in spectrum_preprocessing_order:
                if np.isinf(q_spec[:,1]).sum() > 0:
                    q_spec[:,1] = np.zeros(q_spec.shape[0])
                if np.isinf(r_spec[:,1]).sum() > 0:
                    r_spec[:,1] = np.zeros(r_spec.shape[0])
                if transformation == 'C' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    q_spec = centroid_spectrum(q_spec, window_size=window_size_centroiding) 
                    r_spec = centroid_spectrum(r_spec, window_size=window_size_centroiding) 
                if transformation == 'M' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    m_spec = match_peaks_in_spectra(spec_a=q_spec, spec_b=r_spec, window_size=window_size_matching)
                    q_spec = m_spec[:,0:2]
                    r_spec = m_spec[:,[0,2]]
                    is_matched = True
                if transformation == 'W' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    q_spec[:,1] = wf_transform(q_spec[:,0], q_spec[:,1], wf_mz, wf_int)
                    r_spec[:,1] = wf_transform(r_spec[:,0], r_spec[:,1], wf_mz, wf_int)
                if transformation == 'L' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    q_spec[:,1] = LE_transform(q_spec[:,1], LET_threshold, normalization_method='standard')
                    r_spec[:,1] = LE_transform(r_spec[:,1], LET_threshold, normalization_method='standard')
                if transformation == 'N' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    q_spec = remove_noise(q_spec, nr = noise_threshold)
                    if high_quality_reference_library == False:
                        r_spec = remove_noise(r_spec, nr = noise_threshold)
                if transformation == 'F' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    q_spec = filter_spec_lcms(q_spec, mz_min = mz_min, mz_max = mz_max, int_min = int_min, int_max = int_max, is_matched = is_matched)
                    if high_quality_reference_library == False:
                        r_spec = filter_spec_lcms(r_spec, mz_min = mz_min, mz_max = mz_max, int_min = int_min, int_max = int_max, is_matched = is_matched)

            q_ints = q_spec[:,1]
            r_ints = r_spec[:,1]
            if np.sum(q_ints) != 0 and np.sum(r_ints) != 0 and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                similarity_score = get_similarity(similarity_measure, q_ints, r_ints, weights, entropy_dimension)
            else:
                similarity_score = 0

            similarity_scores.append(similarity_score)
        all_similarity_scores.append(similarity_scores)

    df_scores = pd.DataFrame(all_similarity_scores, columns = unique_reference_ids)
    df_scores.index = unique_query_ids
    df_scores.index.names = ['Query Spectrum ID']

    preds = []
    scores = []
    for i in range(0, df_scores.shape[0]):
        df_scores_tmp = df_scores
        preds_tmp = []
        scores_tmp = []
        for j in range(0, n_top_matches_to_save):
            top_ref_specs_tmp = df_scores_tmp.iloc[i,np.where(df_scores_tmp.iloc[i,:] == np.max(df_scores_tmp.iloc[i,:]))[0]]
            cols_to_keep = np.where(df_scores_tmp.iloc[i,:] != np.max(df_scores_tmp.iloc[i,:]))[0]
            df_scores_tmp = df_scores_tmp.iloc[:,cols_to_keep]

            preds_tmp.append(';'.join(map(str,top_ref_specs_tmp.index.to_list())))
            if len(top_ref_specs_tmp.values) == 0:
                scores_tmp.append(0)
            else:
                scores_tmp.append(top_ref_specs_tmp.values[0])
        preds.append(preds_tmp)
        scores.append(scores_tmp)

    preds = np.array(preds)
    scores = np.array(scores)
    out = np.c_[unique_query_ids,preds,scores]
    df_tmp = pd.DataFrame(out, columns=['TRUE.ID','PREDICTED.ID','SCORE'])
    acc = (df_tmp['TRUE.ID']==df_tmp['PREDICTED.ID']).mean()
    return acc




def get_acc_NRMS(df_query, df_reference, unique_query_ids, unique_reference_ids, similarity_measure, weights, spectrum_preprocessing_order, mz_min, mz_max, int_min, int_max, noise_threshold, wf_mz, wf_int, LET_threshold, entropy_dimension, high_quality_reference_library, verbose=True):

    n_top_matches_to_save = 1

    min_mz = int(np.min([np.min(df_query.iloc[:,1]), np.min(df_reference.iloc[:,1])]))
    max_mz = int(np.max([np.max(df_query.iloc[:,1]), np.max(df_reference.iloc[:,1])]))
    mzs = np.linspace(min_mz,max_mz,(max_mz-min_mz+1))

    all_similarity_scores =  []
    for query_idx in range(0,len(unique_query_ids)):
        q_idxs_tmp = np.where(df_query.iloc[:,0] == unique_query_ids[query_idx])[0]
        q_spec_tmp = np.asarray(pd.concat([df_query.iloc[q_idxs_tmp,1], df_query.iloc[q_idxs_tmp,2]], axis=1).reset_index(drop=True))
        q_spec_tmp = convert_spec(q_spec_tmp,mzs)

        similarity_scores = []
        for ref_idx in range(0,len(unique_reference_ids)):
            q_spec = q_spec_tmp
            if verbose is True and ref_idx % 1000 == 0:
                print(f'Query spectrum #{query_idx} has had its similarity with {ref_idx} reference library spectra computed')
            r_idxs_tmp = np.where(df_reference.iloc[:,0] == unique_reference_ids[ref_idx])[0]
            r_spec_tmp = np.asarray(pd.concat([df_reference.iloc[r_idxs_tmp,1], df_reference.iloc[r_idxs_tmp,2]], axis=1).reset_index(drop=True))
            r_spec = convert_spec(r_spec_tmp,mzs)

            for transformation in spectrum_preprocessing_order:
                if np.isinf(q_spec[:,1]).sum() > 0:
                    q_spec[:,1] = np.zeros(q_spec.shape[0])
                if np.isinf(r_spec[:,1]).sum() > 0:
                    r_spec[:,1] = np.zeros(r_spec.shape[0])
                if transformation == 'W':
                    q_spec[:,1] = wf_transform(q_spec[:,0], q_spec[:,1], wf_mz, wf_int)
                    r_spec[:,1] = wf_transform(r_spec[:,0], r_spec[:,1], wf_mz, wf_int)
                if transformation == 'L':
                    q_spec[:,1] = LE_transform(q_spec[:,1], LET_threshold, normalization_method='standard')
                    r_spec[:,1] = LE_transform(r_spec[:,1], LET_threshold, normalization_method='standard')
                if transformation == 'N':
                    q_spec = remove_noise(q_spec, nr = noise_threshold)
                    if high_quality_reference_library == False:
                        r_spec = remove_noise(r_spec, nr = noise_threshold)
                if transformation == 'F':
                    q_spec = filter_spec_gcms(q_spec, mz_min = mz_min, mz_max = mz_max, int_min = int_min, int_max = int_max)
                    if high_quality_reference_library == False:
                        r_spec = filter_spec_gcms(r_spec, mz_min = mz_min, mz_max = mz_max, int_min = int_min, int_max = int_max)

            q_ints = q_spec[:,1]
            r_ints = r_spec[:,1]

            if np.sum(q_ints) != 0 and np.sum(r_ints) != 0:
                similarity_score = get_similarity(similarity_measure, q_spec[:,1], r_spec[:,1], weights, entropy_dimension)
            else:
                similarity_score = 0

            similarity_scores.append(similarity_score)
        all_similarity_scores.append(similarity_scores)

    df_scores = pd.DataFrame(all_similarity_scores, columns = unique_reference_ids)
    df_scores.index = unique_query_ids
    df_scores.index.names = ['Query Spectrum ID']

    preds = []
    scores = []
    for i in range(0, df_scores.shape[0]):
        df_scores_tmp = df_scores
        preds_tmp = []
        scores_tmp = []
        for j in range(0, n_top_matches_to_save):
            top_ref_specs_tmp = df_scores_tmp.iloc[i,np.where(df_scores_tmp.iloc[i,:] == np.max(df_scores_tmp.iloc[i,:]))[0]]
            cols_to_keep = np.where(df_scores_tmp.iloc[i,:] != np.max(df_scores_tmp.iloc[i,:]))[0]
            df_scores_tmp = df_scores_tmp.iloc[:,cols_to_keep]

            preds_tmp.append(';'.join(map(str,top_ref_specs_tmp.index.to_list())))
            if len(top_ref_specs_tmp.values) == 0:
                scores_tmp.append(0)
            else:
                scores_tmp.append(top_ref_specs_tmp.values[0])
        preds.append(preds_tmp)
        scores.append(scores_tmp)

    preds = np.array(preds)
    scores = np.array(scores)
    out = np.c_[unique_query_ids,preds,scores]
    df_tmp = pd.DataFrame(out, columns=['TRUE.ID','PREDICTED.ID','SCORE'])
    acc = (df_tmp['TRUE.ID']==df_tmp['PREDICTED.ID']).mean()
    return acc



def run_spec_lib_matching_on_HRMS_data(query_data=None, reference_data=None, likely_reference_ids=None, similarity_measure='cosine', weights={'Cosine':0.25,'Shannon':0.25,'Renyi':0.25,'Tsallis':0.25}, spectrum_preprocessing_order='FCNMWL', high_quality_reference_library=False, mz_min=0, mz_max=9999999, int_min=0, int_max=9999999, window_size_centroiding=0.5, window_size_matching=0.5, noise_threshold=0.0, wf_mz=0.0, wf_intensity=1.0, LET_threshold=0.0, entropy_dimension=1.1, n_top_matches_to_save=1, print_id_results=False, output_identification=None, output_similarity_scores=None, return_ID_output=False, verbose=True):
    '''
    runs spectral library matching on high-resolution mass spectrometry (HRMS) data

    --query_data: mgf, mzML, or csv file of query mass spectrum/spectra to be identified. If csv file, each row should correspond to a mass spectrum, the left-most column should contain an identifier, and each of the other columns should correspond to a single mass/charge ratio. Mandatory argument.
    --reference_data: either string or list of strings with pass to mgf, mzML, sdf, and/or csv file(s) of the reference mass spectra. If csv file, each row should correspond to a mass spectrum, the left-most column should contain in identifier (i.e. the CAS registry number or the compound name), and the remaining column should correspond to a single mass/charge ratio. Mandatory argument.
    --likely_reference_ids: CSV file with one column containing the IDs of a subset of all compounds in the reference_data to be used in spectral library matching. Each ID in this file must be an ID in the reference library. Default: None (i.e. default is to use entire reference library)
    --similarity_measure: cosine, shannon, renyi, tsallis, mixture, jaccard, dice, 3w_jaccard, sokal_sneath, binary_cosine, mountford, mcconnaughey, driver_kroeber, simpson, braun_banquet, fager_mcgowan, kulczynski, intersection, hamming, hellinger. Default: cosine.
    --weights: dict of weights to give to each non-binary similarity measure (i.e. cosine, shannon, renyi, and tsallis) when the mixture similarity measure is specified. Default: 0.25 for each of the four non-binary similarity measures.
    --spectrum_preprocessing_order: The spectrum preprocessing transformations and the order in which they are to be applied. Note that these transformations are applied prior to computing similarity scores. Format must be a string with 2-6 characters chosen from C, F, M, N, L, W representing centroiding, filtering based on mass/charge and intensity values, matching, noise removal, low-entropy trannsformation, and weight-factor-transformation, respectively. For example, if \'WCM\' is passed, then each spectrum will undergo a weight factor transformation, then centroiding, and then matching. Note that if an argument is passed, then \'M\' must be contained in the argument, since matching is a required preprocessing step in spectral library matching of HRMS data. Furthermore, \'C\' must be performed before matching since centroiding can change the number of ion fragments in a given spectrum. Default: FCNMWL')
    --high_quality_reference_library: True/False flag indicating whether the reference library is considered to be of high quality. If True, then the spectrum preprocessing transformations of filtering and noise removal are performed only on the query spectrum/spectra. If False, all spectrum preprocessing transformations specified will be applied to both the query and reference spectra. Default: False')
    --mz_min: Remove all peaks with mass/charge value less than mz_min in each spectrum. Default: 0
    --mz_max: Remove all peaks with mass/charge value greater than mz_max in each spectrum. Default: 9999999
    --int_min: Remove all peaks with intensity value less than int_min in each spectrum. Default: 0
    --int_max: Remove all peaks with intensity value greater than int_max in each spectrum. Default: 9999999
    --window_size_centroiding: Window size parameter used in centroiding a given spectrum. Default: 0.5
    --window_size_matching: Window size parameter used in matching a query spectrum and a reference library spectrum. Default: 0.5
    --noise_threshold: Ion fragments (i.e. points in a given mass spectrum) with intensity less than max(intensities)*noise_threshold are removed. Default: 0.0
    --wf_mz: Mass/charge weight factor parameter. Default: 0.0
    --wf_intensity: Intensity weight factor parameter. Default: 0.0
    --LET_threshold: Low-entropy transformation threshold parameter. Spectra with Shannon entropy less than LET_threshold are transformed according to intensitiesNew=intensitiesOriginal^{(1+S)/(1+LET_threshold)}. Default: 0.0
    --entropy_dimension: Entropy dimension parameter. Must have positive value other than 1. When the entropy dimension is 1, then Renyi and Tsallis entropy are equivalent to Shannon entropy. Therefore, this parameter only applies to the renyi and tsallis similarity measures. This parameter will be ignored if similarity measure cosine or shannon is chosen. Default: 1.1
    --n_top_matches_to_save: The number of top matches to report. For example, if n_top_matches_to_save=5, then for each query spectrum, the five reference spectra with the largest similarity with the given query spectrum will be reported. Default: 1
    --print_id_results: Flag that prints identification results if True. Default: False
    --output_identification: Output TXT file containing the most-similar reference spectra for each query spectrum along with the corresponding similarity scores. Default is to save identification output in current working directory with filename \'output_identification.txt\'.
    --output_similarity_scores: Output TXT file containing similarity scores between all query spectrum/spectra and all reference spectra. Each row corresponds to a query spectrum, the left-most column contains the query spectrum/spectra identifier, and the remaining column contain the similarity scores with respect to all reference library spectra. If no argument passed, then this TXT file is written to the current working directory with filename \'output_all_similarity_scores\'.txt.')
    '''

    if query_data is None:
        print('\nError: No argument passed to the mandatory query_data. Please pass the path to the CSV file of the query data.')
        sys.exit()
    else:
        extension = query_data.rsplit('.',1)
        extension = extension[(len(extension)-1)]
        if extension == 'mgf' or extension == 'MGF' or extension == 'mzML' or extension == 'mzml' or extension == 'MZML' or extension == 'cdf' or extension == 'CDF':
            output_path_tmp = query_data[:-3] + 'csv'
            build_library_from_raw_data(input_path=query_data, output_path=output_path_tmp, is_reference=False)
            df_query = pd.read_csv(output_path_tmp)
        if extension == 'csv' or extension == 'CSV':
            df_query = pd.read_csv(query_data)
        unique_query_ids = df_query.iloc[:,0].unique()

    if reference_data is None:
        print('\nError: No argument passed to the mandatory reference_data. Please pass the path to the CSV file of the reference data.')
        sys.exit()
    else:
        if isinstance(reference_data,str):
            df_reference = get_reference_df(reference_data,likely_reference_ids)
            unique_reference_ids = df_reference.iloc[:,0].unique()
        else:
            dfs = []
            unique_reference_ids = []
            for f in reference_data:
                tmp = get_reference_df(f,likely_reference_ids)
                dfs.append(tmp)
                unique_reference_ids.extend(tmp.iloc[:,0].unique())
            df_reference = pd.concat(dfs, axis=0, ignore_index=True)


    if spectrum_preprocessing_order is not None:
        spectrum_preprocessing_order = list(spectrum_preprocessing_order)
    else:
        spectrum_preprocessing_order = ['F', 'C', 'N', 'M', 'W', 'L']
    if 'M' not in spectrum_preprocessing_order:
        print(f'Error: \'M\' must be a character in spectrum_preprocessing_order.')
        sys.exit()
    if 'C' in spectrum_preprocessing_order:
        if spectrum_preprocessing_order.index('C') > spectrum_preprocessing_order.index('M'):
            print(f'Error: \'C\' must come before \'M\' in spectrum_preprocessing_order.')
            sys.exit()
    if set(spectrum_preprocessing_order) - {'F','C','N','M','W','L'}:
        print(f'Error: spectrum_preprocessing_order must contain only \'C\', \'F\', \'M\', \'N\', \'L\', \'W\'.')
        sys.exit()


    if similarity_measure not in ['cosine','shannon','renyi','tsallis','mixture','jaccard','dice','3w_jaccard','sokal_sneath','binary_cosine','mountford','mcconnaughey','driver_kroeber','simpson','braun_banquet','fager_mcgowan','kuldzynski','intersection','hamming','hellinger']:
        print('\nError: similarity_measure must be either cosine, shannon, renyi, tsallis, mixture, jaccard, dice, 3w_jaccard, sokal_sneath, binary_cosine, mountford, mcconnaughey, driver_kroeber, simpson, braun_banquet, fager_mcgowan, kulczynski, intersection, hamming, or hellinger')
        sys.exit()

    if isinstance(int_min,int) is True:
        int_min = float(int_min)
    if isinstance(int_max,int) is True:
        int_max = float(int_max)
    if isinstance(mz_min,int) is False or isinstance(mz_max,int) is False or isinstance(int_min,float) is False or isinstance(int_max,float) is False:
        print('Error: mz_min must be a non-negative integer, mz_max must be a positive integer, int_min must be a non-negative float, and int_max must be a positive float')
        sys.exit()
    if mz_min < 0:
        print('\nError: mz_min should be a non-negative integer')
        sys.exit()
    if mz_max <= 0:
        print('\nError: mz_max should be a positive integer')
        sys.exit()
    if int_min < 0:
        print('\nError: int_min should be a non-negative float')
        sys.exit()
    if int_max <= 0:
        print('\nError: int_max should be a positive float')
        sys.exit()

    if isinstance(window_size_centroiding,float) is False or window_size_centroiding <= 0.0:
        print('Error: window_size_centroiding must be a positive float.')
        sys.exit()
    if isinstance(window_size_matching,float) is False or window_size_matching<= 0.0:
        print('Error: window_size_matching must be a positive float.')
        sys.exit()

    if isinstance(noise_threshold,int) is True:
        noise_threshold = float(noise_threshold)
    if isinstance(noise_threshold,float) is False or noise_threshold < 0:
        print('Error: noise_threshold must be a positive float.')
        sys.exit()

    if isinstance(wf_intensity,int) is True:
        wf_intensity = float(wf_intensity)
    if isinstance(wf_mz,int) is True:
        wf_mz = float(wf_mz)
    if isinstance(wf_intensity,float) is False or isinstance(wf_mz,float) is False:
        print('Error: wf_mz and wf_intensity must be integers or floats')
        sys.exit()

    if entropy_dimension <= 0:
        print('\nError: entropy_dimension should be a positive float')
        sys.exit()
    else:
        q = entropy_dimension

    normalization_method = 'standard'

    if n_top_matches_to_save <= 0 or isinstance(n_top_matches_to_save,int)==False:
        print('\nError: n_top_matches_to_save should be a positive integer')
        sys.exit()

    if isinstance(print_id_results,bool)==False:
        print('\nError: print_id_results must be either True or False')
        sys.exit()
    
    if output_identification is None:
        output_identification = f'{Path.cwd()}/output_identification.txt'
        print(f'Warning: writing identification output to {output_identification}')

    if output_similarity_scores is None:
        output_similarity_scores = f'{Path.cwd()}/output_all_similarity_scores.txt'
        print(f'Warning: writing similarity scores to {output_similarity_scores}')


    all_similarity_scores =  []
    for query_idx in range(0,len(unique_query_ids)):
        if verbose is True:
            print(f'query spectrum #{query_idx} is being identified')
        q_idxs_tmp = np.where(df_query.iloc[:,0] == unique_query_ids[query_idx])[0]
        q_spec_tmp = np.asarray(pd.concat([df_query.iloc[q_idxs_tmp,1], df_query.iloc[q_idxs_tmp,2]], axis=1).reset_index(drop=True))

        similarity_scores = []
        for ref_idx in range(0,len(unique_reference_ids)):
            q_spec = q_spec_tmp
            r_idxs_tmp = np.where(df_reference.iloc[:,0] == unique_reference_ids[ref_idx])[0]
            r_spec = np.asarray(pd.concat([df_reference.iloc[r_idxs_tmp,1], df_reference.iloc[r_idxs_tmp,2]], axis=1).reset_index(drop=True))

            is_matched = False
            for transformation in spectrum_preprocessing_order:
                if np.isinf(q_spec[:,1]).sum() > 0:
                    q_spec[:,1] = np.zeros(q_spec.shape[0])
                if np.isinf(r_spec[:,1]).sum() > 0:
                    r_spec[:,1] = np.zeros(r_spec.shape[0])
                if transformation == 'C' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    q_spec = centroid_spectrum(q_spec, window_size=window_size_centroiding) 
                    r_spec = centroid_spectrum(r_spec, window_size=window_size_centroiding) 
                if transformation == 'M' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    m_spec = match_peaks_in_spectra(spec_a=q_spec, spec_b=r_spec, window_size=window_size_matching)
                    q_spec = m_spec[:,0:2]
                    r_spec = m_spec[:,[0,2]]
                    is_matched = True
                if transformation == 'W' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    q_spec[:,1] = wf_transform(q_spec[:,0], q_spec[:,1], wf_mz, wf_intensity)
                    r_spec[:,1] = wf_transform(r_spec[:,0], r_spec[:,1], wf_mz, wf_intensity)
                if transformation == 'L' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    q_spec[:,1] = LE_transform(q_spec[:,1], LET_threshold, normalization_method=normalization_method)
                    r_spec[:,1] = LE_transform(r_spec[:,1], LET_threshold, normalization_method=normalization_method)
                if transformation == 'N' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    q_spec = remove_noise(q_spec, nr = noise_threshold)
                    if high_quality_reference_library == False:
                        r_spec = remove_noise(r_spec, nr = noise_threshold)
                if transformation == 'F' and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                    q_spec = filter_spec_lcms(q_spec, mz_min = mz_min, mz_max = mz_max, int_min = int_min, int_max = int_max, is_matched = is_matched)
                    if high_quality_reference_library == False:
                        r_spec = filter_spec_lcms(r_spec, mz_min = mz_min, mz_max = mz_max, int_min = int_min, int_max = int_max, is_matched = is_matched)

            q_ints = q_spec[:,1]
            r_ints = r_spec[:,1]

            if np.sum(q_ints) != 0 and np.sum(r_ints) != 0 and q_spec.shape[0] > 1 and r_spec.shape[1] > 1:
                similarity_score = get_similarity(similarity_measure, q_ints, r_ints, weights, entropy_dimension)
            else:
                similarity_score = 0

            similarity_scores.append(similarity_score)
        all_similarity_scores.append(similarity_scores)

    df_scores = pd.DataFrame(all_similarity_scores, columns = unique_reference_ids)
    df_scores.index = unique_query_ids
    df_scores.index.names = ['Query Spectrum ID']

    preds = []
    scores = []
    for i in range(0, df_scores.shape[0]):
        df_scores_tmp = df_scores
        preds_tmp = []
        scores_tmp = []
        for j in range(0, n_top_matches_to_save):
            top_ref_specs_tmp = df_scores_tmp.iloc[i,np.where(df_scores_tmp.iloc[i,:] == np.max(df_scores_tmp.iloc[i,:]))[0]]
            cols_to_keep = np.where(df_scores_tmp.iloc[i,:] != np.max(df_scores_tmp.iloc[i,:]))[0]
            df_scores_tmp = df_scores_tmp.iloc[:,cols_to_keep]

            preds_tmp.append(';'.join(map(str,top_ref_specs_tmp.index.to_list())))
            if len(top_ref_specs_tmp.values) == 0:
                scores_tmp.append(0)
            else:
                scores_tmp.append(top_ref_specs_tmp.values[0])
        preds.append(preds_tmp)
        scores.append(scores_tmp)

    preds = np.array(preds)
    scores = np.array(scores)
    out = np.c_[preds,scores]

    cnames_preds = []
    cnames_scores = []
    for i in range(0,n_top_matches_to_save):
        cnames_preds.append(f'RANK.{i+1}.PRED')
        cnames_scores.append(f'RANK.{i+1}.SIMILARITY.SCORE')

    df_top_ref_specs = pd.DataFrame(out, columns = [*cnames_preds, *cnames_scores])
    df_top_ref_specs.index = unique_query_ids
    df_top_ref_specs.index.names = ['Query Spectrum ID']

    df_scores.columns = ['Reference Spectrum ID: ' + col for col in  list(map(str,df_scores.columns.tolist()))]

    if print_id_results == True:
        print(df_top_ref_specs.to_string())

    if return_ID_output is False:
        df_top_ref_specs.to_csv(output_identification, sep='\t')
        df_scores.to_csv(output_similarity_scores, sep='\t')
    else:
        return df_top_ref_specs





def run_spec_lib_matching_on_NRMS_data(query_data=None, reference_data=None, likely_reference_ids=None, spectrum_preprocessing_order='FNLW', similarity_measure='cosine', weights={'Cosine':0.25,'Shannon':0.25,'Renyi':0.25,'Tsallis':0.25}, high_quality_reference_library=False, mz_min=0, mz_max=9999999, int_min=0, int_max=9999999, noise_threshold=0.0, wf_mz=0.0, wf_intensity=1.0, LET_threshold=0.0, entropy_dimension=1.1, n_top_matches_to_save=1, print_id_results=False, output_identification=None, output_similarity_scores=None, return_ID_output=False):
    '''
    runs spectral library matching on nominal-resolution mass spectrometry (NRMS) data

    --query_data: cdf or csv file of query mass spectrum/spectra to be identified. If csv file, each row should correspond to a mass spectrum, the left-most column should contain an identifier, and each of the other columns should correspond to a single mass/charge ratio. Mandatory argument.
    --reference_data: cdf of csv file of the reference mass spectra. If csv file, each row should correspond to a mass spectrum, the left-most column should contain in identifier (i.e. the CAS registry number or the compound name), and the remaining column should correspond to a single mass/charge ratio. Mandatory argument.
    --likely_reference_ids: CSV file with one column containing the IDs of a subset of all compounds in the reference_data to be used in spectral library matching. Each ID in this file must be an ID in the reference library. Default: None (i.e. default is to use entire reference library)
    --similarity_measure: cosine, shannon, renyi, tsallis, mixture, jaccard, dice, 3w_jaccard, sokal_sneath, binary_cosine, mountford, mcconnaughey, driver_kroeber, simpson, braun_banquet, fager_mcgowan, kulczynski, intersection, hamming, hellinger. Default: cosine.
    --weights: dict of weights to give to each non-binary similarity measure (i.e. cosine, shannon, renyi, and tsallis) when the mixture similarity measure is specified. Default: 0.25 for each of the four non-binary similarity measures.
    --spectrum_preprocessing_order: The spectrum preprocessing transformations and the order in which they are to be applied. Note that these transformations are applied prior to computing similarity scores. Format must be a string with 2-4 characters chosen from F, N, L, W representing filtering based on mass/charge and intensity values, noise removal, low-entropy trannsformation, and weight-factor-transformation, respectively. For example, if \'WN\' is passed, then each spectrum will undergo a weight factor transformation and then noise removal. Default: FNLW')
    --high_quality_reference_library: True/False flag indicating whether the reference library is considered to be of high quality. If True, then the spectrum preprocessing transformations of filtering and noise removal are performed only on the query spectrum/spectra. If False, all spectrum preprocessing transformations specified will be applied to both the query and reference spectra. Default: False')
    --mz_min: Remove all peaks with mass/charge value less than mz_min in each spectrum. Default: 0
    --mz_max: Remove all peaks with mass/charge value greater than mz_max in each spectrum. Default: 9999999
    --int_min: Remove all peaks with intensity value less than int_min in each spectrum. Default: 0
    --int_max: Remove all peaks with intensity value greater than int_max in each spectrum. Default: 9999999
    --noise_threshold: Ion fragments (i.e. points in a given mass spectrum) with intensity less than max(intensities)*noise_threshold are removed. Default: 0.0
    --wf_mz: Mass/charge weight factor parameter. Default: 0.0
    --wf_intensity: Intensity weight factor parameter. Default: 0.0
    --LET_threshold: Low-entropy transformation threshold parameter. Spectra with Shannon entropy less than LET_threshold are transformed according to intensitiesNew=intensitiesOriginal^{(1+S)/(1+LET_threshold)}. Default: 0.0
    --entropy_dimension: Entropy dimension parameter. Must have positive value other than 1. When the entropy dimension is 1, then Renyi and Tsallis entropy are equivalent to Shannon entropy. Therefore, this parameter only applies to the renyi and tsallis similarity measures. This parameter will be ignored if similarity measure cosine or shannon is chosen. Default: 1.1
    --normalization_method: Method used to normalize the intensities of each spectrum so that the intensities sum to 1. Since the objects entropy quantifies the uncertainy of must be probability distributions, the intensities of a given spectrum must sum to 1 prior to computing the entropy of the given spectrum intensities. Options: \'standard\' and \'softmax\'. Default: standard.
    --n_top_matches_to_save: The number of top matches to report. For example, if n_top_matches_to_save=5, then for each query spectrum, the five reference spectra with the largest similarity with the given query spectrum will be reported. Default: 1
    --print_id_results: Flag that prints identification results if True. Default: False
    --output_identification: Output TXT file containing the most-similar reference spectra for each query spectrum along with the corresponding similarity scores. Default is to save identification output in current working directory with filename \'output_identification.txt\'.
    --output_similarity_scores: Output TXT file containing similarity scores between all query spectrum/spectra and all reference spectra. Each row corresponds to a query spectrum, the left-most column contains the query spectrum/spectra identifier, and the remaining column contain the similarity scores with respect to all reference library spectra. If no argument passed, then this TXT file is written to the current working directory with filename \'output_all_similarity_scores\'.txt.')
    '''

    if query_data is None:
        print('\nError: No argument passed to the mandatory query_data. Please pass the path to the CSV file of the query data.')
        sys.exit()
    else:
        extension = query_data.rsplit('.',1)
        extension = extension[(len(extension)-1)]
        if extension == 'mgf' or extension == 'MGF' or extension == 'mzML' or extension == 'mzml' or extension == 'MZML' or extension == 'cdf' or extension == 'CDF':
            output_path_tmp = query_data[:-3] + 'csv'
            build_library_from_raw_data(input_path=query_data, output_path=output_path_tmp, is_reference=False)
            df_query = pd.read_csv(output_path_tmp)
        if extension == 'csv' or extension == 'CSV':
            df_query = pd.read_csv(query_data)
        unique_query_ids = df_query.iloc[:,0].unique()

    if reference_data is None:
        print('\nError: No argument passed to the mandatory reference_data. Please pass the path to the CSV file of the reference data.')
        sys.exit()
    else:
        if isinstance(reference_data,str):
            df_reference = get_reference_df(reference_data,likely_reference_ids)
            unique_reference_ids = df_reference.iloc[:,0].unique()
        else:
            dfs = []
            unique_reference_ids = []
            for f in reference_data:
                tmp = get_reference_df(f,likely_reference_ids)
                dfs.append(tmp)
                unique_reference_ids.extend(tmp.iloc[:,0].unique())
            df_reference = pd.concat(dfs, axis=0, ignore_index=True)


    if spectrum_preprocessing_order is not None:
        spectrum_preprocessing_order = list(spectrum_preprocessing_order)
    else:
        spectrum_preprocessing_order = ['F','N','W','L']
    if set(spectrum_preprocessing_order) - {'F','N','W','L'}:
        print(f'Error: spectrum_preprocessing_order must contain only \'F\', \'N\', \'W\', \'L\'.')
        sys.exit()

    if similarity_measure not in ['cosine','shannon','renyi','tsallis','mixture','jaccard','dice','3w_jaccard','sokal_sneath','binary_cosine','mountford','mcconnaughey','driver_kroeber','simpson','braun_banquet','fager_mcgowan','kuldzynski','intersection','hamming','hellinger']:
        print('\nError: similarity_measure must be either cosine, shannon, renyi, tsallis, mixture, jaccard, dice, 3w_jaccard, sokal_sneath, binary_cosine, mountford, mcconnaughey, driver_kroeber, simpson, braun_banquet, fager_mcgowan, kulczynski, intersection, hamming, or hellinger')
        sys.exit()

    if isinstance(int_min,int) is True:
        int_min = float(int_min)
    if isinstance(int_max,int) is True:
        int_max = float(int_max)
    if isinstance(mz_min,int) is False or isinstance(mz_max,int) is False or isinstance(int_min,float) is False or isinstance(int_max,float) is False:
        print('Error: mz_min must be a non-negative integer, mz_max must be a positive integer, int_min must be a non-negative float, and int_max must be a positive float')
        sys.exit()
    if mz_min < 0:
        print('\nError: mz_min should be a non-negative integer')
        sys.exit()
    if mz_max <= 0:
        print('\nError: mz_max should be a positive integer')
        sys.exit()
    if int_min < 0:
        print('\nError: int_min should be a non-negative float')
        sys.exit()
    if int_max <= 0:
        print('\nError: int_max should be a positive float')
        sys.exit()

    if isinstance(noise_threshold,int) is True:
        noise_threshold = float(noise_threshold)
    if isinstance(noise_threshold,float) is False or noise_threshold < 0:
        print('Error: noise_threshold must be a positive float.')
        sys.exit()

    if isinstance(wf_intensity,int) is True:
        wf_intensity = float(wf_intensity)
    if isinstance(wf_mz,int) is True:
        wf_mz = float(wf_mz)
    if isinstance(wf_intensity,float) is False or isinstance(wf_mz,float) is False:
        print('Error: wf_mz and wf_intensity must be integers or floats')
        sys.exit()

    if entropy_dimension <= 0:
        print('\nError: entropy_dimension should be a positive float')
        sys.exit()
    else:
        q = entropy_dimension

    normalization_method = 'standard' 

    if n_top_matches_to_save <= 0 or isinstance(n_top_matches_to_save,int)==False:
        print('\nError: n_top_matches_to_save should be a positive integer')
        sys.exit()

    if isinstance(print_id_results,bool)==False:
        print('\nError: print_id_results must be either True or False')
        sys.exit()
    
    if output_identification is None:
        output_identification = f'{Path.cwd()}/output_identification.txt'
        print(f'Warning: writing identification output to {output_identification}')

    if output_similarity_scores is None:
        output_similarity_scores = f'{Path.cwd()}/output_all_similarity_scores.txt'
        print(f'Warning: writing similarity scores to {output_similarity_scores}')



    min_mz = int(np.min([np.min(df_query.iloc[:,1]), np.min(df_reference.iloc[:,1])]))
    max_mz = int(np.max([np.max(df_query.iloc[:,1]), np.max(df_reference.iloc[:,1])]))
    mzs = np.linspace(min_mz,max_mz,(max_mz-min_mz+1))

    all_similarity_scores =  []
    for query_idx in range(0,len(unique_query_ids)):
        q_idxs_tmp = np.where(df_query.iloc[:,0] == unique_query_ids[query_idx])[0]
        q_spec_tmp = np.asarray(pd.concat([df_query.iloc[q_idxs_tmp,1], df_query.iloc[q_idxs_tmp,2]], axis=1).reset_index(drop=True))
        q_spec_tmp = convert_spec(q_spec_tmp,mzs)

        similarity_scores = []
        for ref_idx in range(0,len(unique_reference_ids)):
            if verbose is True and ref_idx % 1000 == 0:
                print(f'Query spectrum #{query_idx} has had its similarity with {ref_idx} reference library spectra computed')
            q_spec = q_spec_tmp
            r_idxs_tmp = np.where(df_reference.iloc[:,0] == unique_reference_ids[ref_idx])[0]
            r_spec_tmp = np.asarray(pd.concat([df_reference.iloc[r_idxs_tmp,1], df_reference.iloc[r_idxs_tmp,2]], axis=1).reset_index(drop=True))
            r_spec = convert_spec(r_spec_tmp,mzs)

            for transformation in spectrum_preprocessing_order:
                if np.isinf(q_spec[:,1]).sum() > 0:
                    q_spec[:,1] = np.zeros(q_spec.shape[0])
                if np.isinf(r_spec[:,1]).sum() > 0:
                    r_spec[:,1] = np.zeros(r_spec.shape[0])
                if transformation == 'W': 
                    q_spec[:,1] = wf_transform(q_spec[:,0], q_spec[:,1], wf_mz, wf_intensity)
                    r_spec[:,1] = wf_transform(r_spec[:,0], r_spec[:,1], wf_mz, wf_intensity)
                if transformation == 'L': 
                    q_spec[:,1] = LE_transform(q_spec[:,1], LET_threshold, normalization_method=normalization_method)
                    r_spec[:,1] = LE_transform(r_spec[:,1], LET_threshold, normalization_method=normalization_method)
                if transformation == 'N': 
                    q_spec = remove_noise(q_spec, nr = noise_threshold)
                    if high_quality_reference_library == False:
                        r_spec = remove_noise(r_spec, nr = noise_threshold)
                if transformation == 'F':
                    q_spec = filter_spec_gcms(q_spec, mz_min = mz_min, mz_max = mz_max, int_min = int_min, int_max = int_max)
                    if high_quality_reference_library == False:
                        r_spec = filter_spec_gcms(r_spec, mz_min = mz_min, mz_max = mz_max, int_min = int_min, int_max = int_max)

            q_ints = q_spec[:,1]
            r_ints = r_spec[:,1]

            if np.sum(q_ints) != 0 and np.sum(r_ints) != 0:
                similarity_score = get_similarity(similarity_measure, q_spec[:,1], r_spec[:,1], weights, entropy_dimension)
            else:
                similarity_score = 0

            similarity_scores.append(similarity_score)
        all_similarity_scores.append(similarity_scores)

    df_scores = pd.DataFrame(all_similarity_scores, columns = unique_reference_ids)
    df_scores.index = unique_query_ids
    df_scores.index.names = ['Query Spectrum ID']

    preds = []
    scores = []
    for i in range(0, df_scores.shape[0]):
        df_scores_tmp = df_scores
        preds_tmp = []
        scores_tmp = []
        for j in range(0, n_top_matches_to_save):
            top_ref_specs_tmp = df_scores_tmp.iloc[i,np.where(df_scores_tmp.iloc[i,:] == np.max(df_scores_tmp.iloc[i,:]))[0]]
            cols_to_keep = np.where(df_scores_tmp.iloc[i,:] != np.max(df_scores_tmp.iloc[i,:]))[0]
            df_scores_tmp = df_scores_tmp.iloc[:,cols_to_keep]

            preds_tmp.append(';'.join(map(str,top_ref_specs_tmp.index.to_list())))
            if len(top_ref_specs_tmp.values) == 0:
                scores_tmp.append(0)
            else:
                scores_tmp.append(top_ref_specs_tmp.values[0])
        preds.append(preds_tmp)
        scores.append(scores_tmp)

    preds = np.array(preds)
    scores = np.array(scores)
    out = np.c_[preds,scores]

    cnames_preds = []
    cnames_scores = []
    for i in range(0,n_top_matches_to_save):
        cnames_preds.append(f'RANK.{i+1}.PRED')
        cnames_scores.append(f'RANK.{i+1}.SIMILARITY.SCORE')

    df_top_ref_specs = pd.DataFrame(out, columns = [*cnames_preds, *cnames_scores])
    df_top_ref_specs.index = unique_query_ids
    df_top_ref_specs.index.names = ['Query Spectrum ID']

    if print_id_results == True:
        print(df_top_ref_specs.to_string())

    df_scores.columns = ['Reference Spectrum ID: ' + col for col in  list(map(str,df_scores.columns.tolist()))]

    if return_ID_output is False:
        df_top_ref_specs.to_csv(output_identification, sep='\t')
        df_scores.columns = ['Reference Spectrum ID: ' + col for col in  list(map(str,df_scores.columns.tolist()))]
        df_scores.to_csv(output_similarity_scores, sep='\t')
    else:
        return df_top_ref_specs

