from scipy import signal
from scipy.signal import butter, sosfilt, sosfreqz, lfilter, iirnotch, filtfilt

def remove_dc_offset(data, fs=250, offset=.5, order=3):
    nyq = .5 * fs
    normal_cutoff = offset / nyq
    b, a = butter(N=order, Wn=normal_cutoff, btype='highpass', analog=False)
    fil_data = lfilter(b, a, data)
    return fil_data


def lowpass_filter(data, fs=250, offset=.5, order=3):
    nyq = .5 * fs
    normal_cutoff = offset / nyq
    b, a = butter(N=order, Wn=normal_cutoff, btype='lowpass', analog=False)
    fil_data = lfilter(b, a, data)
    return fil_data


def mains_removal(data, fs=250, notch_freq=60.0, quality_factor=30.0):
    b, a = iirnotch(notch_freq, quality_factor, fs)
    fil_data = filtfilt(b, a, data, padlen=len(data) -1)
    return fil_data


def standardize_data(data, axis=1):
    # print('input to normalization {}'.format(data.shape))
    mu = data.mean(axis=axis)
    std = data.std(axis=axis)
    standarized_data = (data.transpose() - mu) / std

    return standarized_data.transpose()


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], analog=False, btype='bandpass', output='sos')
    return sos


def butter_bandpass_filter(data, lowcut=5, highcut=35, fs=250, order=5):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sosfilt(sos, data)
    return y



def preprocess(data):
    rectifed_data = abs(data)
    scaled_rectified_data = rectifed_data / 128.0  # Mode 3
    notched_data = mains_removal(scaled_rectified_data, fs=200, notch_freq=60.0, quality_factor=30.0)
    filtered = butter_bandpass_filter(notched_data, lowcut=10.0, highcut=99.0, fs=200, order=5)

    return filtered