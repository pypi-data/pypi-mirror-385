import numpy as np
import pandas as pd
from pobm.obm.desat import DesaturationsMeasures, desat_embedding
from pobm.obm.complex import ComplexityMeasures
from pobm.obm.burden import HypoxicBurdenMeasures
from pobm.obm.general import OverallGeneralMeasures
from pobm.obm.periodicity import PRSAMeasures, PSDMeasures
from pobm.prep import set_range, median_spo2

def features_all_desat(signal, time_signal, ODI_Threshold=6, hard_threshold=88, relative=True, desat_max_length=14400):
    '''
        Extracts desaturation event features from a given oxygen saturation (SpO2) signal.

        :param signal: The input SpO2 signal (oxygen saturation values).
        :type signal: array-like
        :param time_signal: Time vector corresponding to the SpO2 signal samples.
        :type time_signal: array-like
        :param ODI_Threshold: Minimum relative drop in SpO2 (in %) to classify as a desaturation event.
        :type ODI_Threshold: int, optional (default=6)
        :param hard_threshold: Absolute SpO2 threshold. Values below this are considered desaturations regardless of relative drop.
        :type hard_threshold: int, optional (default=88)
        :param relative: Whether to use a relative drop from baseline to detect desaturations.
        :type relative: bool, optional (default=True)
        :param desat_max_length: Maximum duration of a desaturation event (in sample points).
        :type desat_max_length: int, optional (default=14400)

        :return: A DataFrame containing detected desaturation events and their features.
            Columns include:
                - begin: Start time of the desaturation event.
                - end: End time of the desaturation event.
                - begin_idx: Start index in the signal.
                - end_idx: End index in the signal.
                - depth: Maximum depth of the desaturation.
                - length: Duration of the desaturation event.
                - area: Area under the desaturation curve based on maximum value.
        '''
    
    # Convert signal into a 1D array
    time_signal = np.array(time_signal)

    desat_class = DesaturationsMeasures(ODI_Threshold=ODI_Threshold, hard_threshold=hard_threshold, relative=relative,
                                        desat_max_length=desat_max_length)
    desat_class.compute(signal)

    begin_idx = desat_class.begin
    end_idx = desat_class.end

    desaturations, desaturation_valid, desaturation_length_all, desaturation_int_100_all, \
        desaturation_int_max_all, desaturation_depth_100_all, desaturation_depth_max_all, \
        desaturation_slope_all = desat_embedding(begin_idx, end_idx)
    time_spo2_array = np.array(range(len(signal)))

    starts = []
    for (i, desaturation) in enumerate(desaturations):
        starts.append(desaturation['Start'])
        desaturation_idx = (time_spo2_array >= desaturation['Start']) & (time_spo2_array <= desaturation['End'])

        if np.sum(desaturation_idx) == 0:
            continue
        signal = np.array(signal)

        desaturation_time = time_spo2_array[desaturation_idx]
        desaturation_spo2 = signal[desaturation_idx]
        desaturation_min = np.nanmin(desaturation_spo2)
        desaturation_max = np.nanmax(desaturation_spo2)

        desaturation_valid[i] = True
        desaturation_length_all[i] = desaturation['Duration']
        desaturation_int_100_all[i] = np.nansum(100 - desaturation_spo2)
        desaturation_int_max_all[i] = np.nansum(desaturation_max - desaturation_spo2)
        desaturation_depth_100_all[i] = 100 - desaturation_min
        desaturation_depth_max_all[i] = desaturation_max - desaturation_min

        desaturation_idx_max = np.where(desaturation_spo2 == desaturation_max)[0][0]
        desaturation_idx_min = np.where(desaturation_spo2 == desaturation_min)[0][-1]
        desaturation_idx_max_min = np.arange(desaturation_idx_max, desaturation_idx_min + 1)

        if len(desaturation_idx_max_min) > 0:
            p = np.polyfit(np.int64(desaturation_time[desaturation_idx_max_min]),
                           desaturation_spo2[desaturation_idx_max_min], 1)

            desaturation_slope_all[i] = p[0]

    begin_time = time_signal[begin_idx]
    end_time = time_signal[end_idx]

    desat_patient = pd.DataFrame({
        "begin": begin_time,
        "end": end_time,
        "begin_idx": begin_idx,
        "end_idx": end_idx,
        "depth": desaturation_depth_max_all,
        "length": desaturation_length_all,
        "area": desaturation_int_max_all
    })
    return desat_patient


def extract_biomarkers_per_signal(signal, patient, time_begin, time_end):
    '''
    This function extracts SpO2 biomarkers per signal.
        :param signal: The input SpO2 signal (oxygen saturation values).
        :type signal: array-like
        :param time_begin:
        :param time_end:
        :return: dictionary of SpO2 biomarkers
        '''
    
    # Compute complexity features
    complexity_class = ComplexityMeasures()
    results_complexity = complexity_class.compute(signal)
    
    # Compute desaturation biomarkers
    desat_class = DesaturationsMeasures()
    results_desat = desat_class.compute(signal)
    
    # Compute hypoxic burden features
    hypoxic_class = HypoxicBurdenMeasures(results_desat.begin, results_desat.end)
    results_hypoxic = hypoxic_class.compute(signal)
    
    # Compute overall general features
    statistics_class = OverallGeneralMeasures()
    results_overall = statistics_class.compute(signal)
    
    # Compute PRSA features
    prsa_class = PRSAMeasures()
    results_PRSA = prsa_class.compute(signal)
    
    # Compute PSD features
    psd_class = PSDMeasures()
    results_PSD = psd_class.compute(signal)

    biomarkers = pd.DataFrame({
        "time begin": [time_begin],
        "time end": [time_end],
        "patient": [patient],
        "AV": [results_overall.AV],
        "MED": [results_overall.MED],
        "Min": [results_overall.Min],
        "SD": [results_overall.SD],
        "RG": [results_overall.RG],
        "P": [results_overall.P],
        "M": [results_overall.M],
        "ZC": [results_overall.ZC],
        "DI": [results_overall.DI],

        "ODI": [results_desat.ODI],

        "DL_u": [results_desat.DL_u],
        "DL_sd": [results_desat.DL_sd],
        "DA100_u": [results_desat.DA100_u],
        "DA100_sd": [results_desat.DA100_sd],
        "DAmax_u": [results_desat.DAmax_u],
        "DAmax_sd": [results_desat.DAmax_sd],
        "DD100_u": [results_desat.DD100_u],
        "DD100_sd": [results_desat.DD100_sd],
        "DDmax_u": [results_desat.DDmax_u],
        "DDmax_sd": [results_desat.DDmax_sd],
        "DS_u": [results_desat.DS_u],
        "DS_sd": [results_desat.DS_sd],
        "TD_u": [results_desat.TD_u],
        "TD_sd": [results_desat.TD_sd],

        "CA": [results_hypoxic.CA],
        "CT": [results_hypoxic.CT],
        "POD": [results_hypoxic.POD],
        "AODmax": [results_hypoxic.AODmax],
        "AOD100": [results_hypoxic.AOD100],

        "ApEn": [results_complexity.ApEn],
        "LZ": [results_complexity.LZ],
        "CTM": [results_complexity.CTM],
        "SampEn": [results_complexity.SampEn],
        "DFA": [results_complexity.DFA],

        "PRSAc": [results_PRSA.PRSAc],
        "PRSAad": [results_PRSA.PRSAad],
        "PRSAos": [results_PRSA.PRSAos],
        "PRSAsb": [results_PRSA.PRSAsb],
        "PRSAsa": [results_PRSA.PRSAsa],
        "AC": [results_PRSA.AC],

        "PSD_total": [results_PSD.PSD_total],
        "PSD_band": [results_PSD.PSD_band],
        "PSD_ratio": [results_PSD.PSD_ratio],
        "PSD_peak": [results_PSD.PSD_peak],
    })
    return biomarkers

def get_spo2_biomarkers(signal, fs, patient_name="Unknown"):
    '''
        This function preprocesses the SpO2 signal, then computes the biomarkers.

        :param signal: SpO2 signal
        :type signal: np.ndarray
        :param fs: sampling frequency
        :type fs: float
        :return: dictionary of SpO2 biomarkers
        '''
    
    # Remove values lower than 50 and greater than 100
    spo2_signal = set_range(signal)
    # Apply median filter to the SpO2 signal
    spo2_signal = median_spo2(spo2_signal, FilterLength=301)
    # Calculate the time signal
    time_signal = np.arange(0, len(spo2_signal)) / fs
    
    biomarker = pd.DataFrame()
    
    time_begin = time_signal[0]
    time_end = time_signal[-1]
    
    # Compute biomarkers
    biomarker = extract_biomarkers_per_signal(spo2_signal, patient_name, time_begin, time_end)
    
    return biomarker