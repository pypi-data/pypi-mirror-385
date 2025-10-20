import warnings
warnings.filterwarnings('ignore', category=UserWarning)
import logging
logger = logging.getLogger('open-rppg')
handler = logging.StreamHandler()
formatter = logging.Formatter('OPEN-RPPG:%(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

from .models import * 

import av
import mediapipe as mp
import heartpy as hp
import cv2
import threading
import time
from scipy.interpolate import CubicSpline
from scipy.signal import welch, butter, lfilter, filtfilt, find_peaks, resample
from scipy.sparse import spdiags, diags, eye
from scipy.sparse.linalg import spsolve
import pkg_resources

def validate_param(**kw):
    def decorator(func):
        def wrapper(*args, **kwargs):
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            all_args = bound_args.arguments
            for param_name, value in all_args.items():
                if param_name in kw:
                    allowed = kw[param_name]
                    if value not in allowed:
                        raise ValueError(
                            f"Invalid value for '{param_name}': {value}. "
                            f"Allowed values: {allowed}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def SQI(signal, sr=30, min_freq=0.5, max_freq=3.0):
    n = len(signal)
    if n < 2:
        return 0.0
    signal = signal - np.mean(signal)
    signal = signal / (np.std(signal) + 1e-8)
    autocorr = np.correlate(signal, signal, mode='full')
    autocorr = autocorr[n-1:]
    autocorr = autocorr / autocorr[0]
    min_lag = max(1, int(sr / max_freq))
    max_lag = min(len(autocorr)-1, int(sr / min_freq))
    if min_lag >= max_lag or max_lag <= min_lag:
        return 0.0
    target_autocorr = autocorr[min_lag:max_lag+1]
    peak_value = np.max(target_autocorr)
    return max(0.0, min(1.0, peak_value))

def get_hr(y, sr=30, min=30, max=180):
    p, q = welch(y, sr, nfft=2e4, nperseg=np.min((len(y)-1, 256/30*sr)))
    return p[(p>min/60)&(p<max/60)][np.argmax(q[(p>min/60)&(p<max/60)])]*60

def get_prv(y, ts=None, sr=30):
    '''
    if ts is not None and len(ts)>2:
        y, ts = np.array([(y[i], ts[i]) for i in range(len(y)-1) if ts[i]!=ts[i+1]]+[(y[-1], ts[-1])]).T
        y = CubicSpline(ts, y)(np.linspace(ts[0], ts[-1], round((ts[-1]-ts[0])*120)))
        sr = 120
    '''
    m, n = hp.process(y, sr, high_precision=True, clean_rr=True)
    rr_intervals = m['RR_list'][np.where(1-np.array(m['RR_masklist']))]/1000
    t = np.cumsum(rr_intervals)
    resampled_rate = 4 
    #signal = resample(rr_intervals, int(t[-1]*resampled_rate)) 
    signal = CubicSpline(t, rr_intervals)(np.arange(0, t[-1], 1/resampled_rate))
    f, Pxx = welch(signal, fs=resampled_rate, nperseg=min(len(signal), 256), nfft=4096)
    VLF = Pxx[(f >= 0.0033) & (f < 0.04)].sum()
    LF  = Pxx[(f >= 0.04)   & (f < 0.15)].sum()
    HF  = Pxx[(f >= 0.15)   & (f < 0.4)].sum()
    TP  = VLF + LF + HF
    return {**n, **{'VLF':VLF, 'TP':TP, 'HF':HF, 'LF':LF, 'LF/HF':LF/HF}}

def norm_bvp(bvp, sr=30):
    bvp_ = []
    _ = np.nan
    for i in bvp:
        if np.isnan(i):
            bvp_.append(_)
        else:
            bvp_.append(i)
            _ = i
    if np.isnan(bvp_[0]):
        for i in bvp_:
            if not np.isnan(i):
                _ = i
                break
        n = 0
        while 1:
            if n>=len(bvp_) or not np.isnan(bvp_[0]):
                break
            bvp_[n] = _
            n += 1
    bvp_ = np.array(bvp_)
    bvp_ = detrend(bvp_, sr=sr)
    mean, std = np.mean(bvp_), np.std(bvp_)
    bvp_ = (bvp_-mean)/std
    prominence = (1.5, None)
    peaks = np.sort(np.concatenate([find_peaks(bvp_, prominence=prominence, distance=0.25*sr)[0], find_peaks(-bvp_, prominence=prominence, distance=0.25*sr)[0]]))
    l = [((x-(np.max(x)+np.min(x))/2)/(np.max(x)-np.min(x))) for x in (bvp_[a:b] for a, b in zip(peaks, peaks[1:]+1))]
    bvp = np.concatenate([i[:-1] for i in l[:-1]]+l[-1:])
    bvp = (bvp-np.mean(bvp))/np.std(bvp)
    bvp_[peaks[0]:peaks[-1]+1] = bvp
    return np.clip(bvp_, -2, np.max(bvp))

def detrend(signal, min_freq=0.5, sr=30):
    Lambda = 50*(sr/30)**2*(0.5/min_freq)**2
    signal_length = signal.shape[0]
    diags_data = [
        np.ones(signal_length - 2),
        -2 * np.ones(signal_length - 2),
        np.ones(signal_length - 2)
    ]
    offsets = [0, 1, 2]
    D = diags(diags_data, offsets, shape=(signal_length-2, signal_length), format='csc')
    H = eye(signal_length, format='csc')
    DTD = D.T @ D
    A = H + (Lambda ** 2) * DTD
    x = spsolve(A, signal)
    filtered_signal = signal - x
    return filtered_signal

def bandpass_filter(data, lowcut=0.5, highcut=3, fs=30, order=3):
    b, a = butter(order, [lowcut, highcut], fs=fs, btype='band')
    return filtfilt(b, a, data)

class KalmanFilter1D:
    def __init__(self, process_noise, measurement_noise, initial_state, initial_estimate_error, reference_interval=1/30):
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.estimate = initial_state
        self.estimate_error = initial_estimate_error
        self.reference_interval = reference_interval
    
    def update(self, measurement, dt=None):
        if dt is None:
            dt = self.reference_interval
        time_scale = dt / self.reference_interval
        adjusted_process_noise = self.process_noise * (time_scale ** 2)
        prediction = self.estimate
        prediction_error = self.estimate_error + adjusted_process_noise
        kalman_gain = prediction_error / (prediction_error + self.measurement_noise)
        self.estimate = prediction + kalman_gain * (measurement - prediction)
        self.estimate_error = (1 - kalman_gain) * prediction_error
        return self.estimate


supported_models = ['ME-chunk.rlap', 'ME-flow.rlap', 'ME-chunk.pure', 'ME-flow.pure',
                           'PhysMamba.pure', 'PhysMamba.rlap', 'RhythmMamba.rlap', 'RhythmMamba.pure',
                           'PhysFormer.pure', 'PhysFormer.rlap', 'TSCAN.rlap', 'TSCAN.pure',
                           'PhysNet.rlap', 'PhysNet.pure', 'EfficientPhys.pure', 'EfficientPhys.rlap']

class Model:
    
    @validate_param(model=supported_models)
    def __init__(self, model='ME-chunk.rlap'):
        if model == 'ME-chunk.rlap':
            f, state, meta = load_ME_chunk_rlap()
        if model == 'ME-chunk.pure':
            f, state, meta = load_ME_chunk_pure()
        if model == 'ME-flow.rlap':
            f, state, meta = load_ME_rlap()
        if model == 'ME-flow.pure':
            f, state, meta = load_ME_pure()
        if model == 'PhysMamba.pure':
            f, state, meta = load_PhysMamba_pure()
        if model == 'PhysMamba.rlap':
            f, state, meta = load_PhysMamba_rlap()
        if model == 'RhythmMamba.rlap':
            f, state, meta = load_RhythmMamba_rlap()
        if model == 'RhythmMamba.pure':
            f, state, meta = load_RhythmMamba_pure()
        if model == 'PhysFormer.rlap':
            f, state, meta = load_PhysFormer_rlap()
        if model == 'PhysFormer.pure':
            f, state, meta = load_PhysFormer_pure()
        if model == 'TSCAN.rlap':
            f, state, meta = load_TSCAN_rlap()
        if model == 'TSCAN.pure':
            f, state, meta = load_TSCAN_pure()
        if model == 'PhysNet.rlap':
            f, state, meta = load_PhysNet_rlap()
        if model == 'PhysNet.pure':
            f, state, meta = load_PhysNet_pure()
        if model == 'EfficientPhys.rlap':
            f, state, meta = load_EfficientPhys_rlap()
        if model == 'EfficientPhys.pure':
            f, state, meta = load_EfficientPhys_pure()
        self.__load(f, state, meta)
        with self:
            pass
    
    def __load(self, func, state, meta, face_detect_per_n=1):
        self.state = state 
        self.meta = meta 
        self.fps = meta['fps'] 
        self.input = meta['input'] 
        self.detect_per_n = face_detect_per_n
        self.call = func 
        self.run = None
        self.frame = None
        self.alive = False
        self.preview_lock = threading.Lock()
        self.preview_lock.acquire()
    
    def __enter__(self):
        if self.alive:
            raise RuntimeError('A task is currently running!')
        BaseOptions = mp.tasks.BaseOptions
        FaceDetector = mp.tasks.vision.FaceDetector
        FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        model_asset_path = pkg_resources.resource_filename('rppg','weights/blaze_face_short_range.tflite')
        options = FaceDetectorOptions(
            base_options=BaseOptions(model_asset_path=model_asset_path),
            running_mode=VisionRunningMode.VIDEO, min_detection_confidence=0.5)
        self.boxkf = None
        self.ts = []
        self.n_frame = 0 
        self.n_signal = 0
        self.box = None 
        self.rbox = None 
        self.hasface = 0
        self.face_buff = []
        self.signal_buff = {}
        self.statistic = {'frames':0, 'key':0, 'skipped':0, 'filled':0, 'dependent':0, 'null':0}
        self.sp = threading.Semaphore(0)
        self.frame_lock = threading.Lock()
        self.detector = FaceDetector.create_from_options(options) 
        self.alive = True
        def inference():
            try:
                while self.alive or (len(self.face_buff)>=self.meta['input'][0]):
                    self.sp.acquire()
                    if len(self.face_buff)<self.meta['input'][0]:
                        continue 
                    face_imgs = self.face_buff[:self.meta['input'][0]]
                    ipt = np.array([i[0] for i in face_imgs])
                    msk = np.array([i[1] for i in face_imgs], bool)
                    r, self.state = self.call(ipt, self.state)
                    r = {k:v*msk for k,v in r.items() if v.shape[-1]==len(msk)}
                    with self.frame_lock:
                        for i in range(self.meta['input'][0]):
                            self.face_buff.pop(0)
                    self.n_signal += self.meta['input'][0]
                    if not self.signal_buff:
                        self.signal_buff = {k:list(v) for k,v in r.items()}
                    else:
                        for k, v in self.signal_buff.items():
                            v.extend(r[k])
                if len(self.face_buff):
                    face_imgs = self.face_buff + [self.face_buff[-1]]*(self.meta['input'][0]-len(self.face_buff))
                    ipt = np.array([i[0] for i in face_imgs])
                    msk = np.array([i[1] for i in face_imgs], bool)
                    r, _ = self.call(ipt, self.state)
                    r = {k:v*msk for k,v in r.items() if v.shape[-1]==len(msk)}
                    self.n_signal += len(self.face_buff)
                    #self.signal_buff.append({k:v[:len(self.face_buff)] for k,v in r.items()})
                    for k, v in self.signal_buff.items():
                        v.extend(r[k][:len(self.face_buff)])
                    self.face_buff.clear()
            except Exception as e:
                import sys
                sys.excepthook(*sys.exc_info())
        self.ift = threading.Thread(target=inference,daemon=True)
        self.ift.start()
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type:
                raise exc_value
        finally:
            self.alive = False
            self.sp.release()
            self.ift.join()
            self.detector.close()
                
    def collect_signals(self, start=None, end=None):
        if not start:
            start = 0 
        if not end:
            end = self.now
        if start<0:
            start += self.now
        if end<0:
            end += self.now
        if not self.signal_buff:
            return {}, None
        if not start<=end:
            raise ValueError('Start must be less than end')
        #signals = {k:np.concatenate([i[k] for i in self.signal_buff]) for k in self.signal_buff[0]}
        signals = self.signal_buff
        start_n, end_n = 0, None
        for n, i in enumerate(np.array(self.ts)-self.ts[0]):
            if start and i<start:
                start_n = n 
            if end and i<=end:
                end_n = n+1
        signals = {k:v[start_n:end_n] for k,v in signals.items()}
        ts = np.array(self.ts[start_n:end_n])
        return signals, ts - self.ts[0]
    
    @property
    def now(self):
        return self.ts[self.n_signal-1]-self.ts[0] if self.ts else 0
    
    @property
    def latency(self):
        return self.ts[-1]-self.ts[self.n_signal-1] if self.ts else 0
    
    @property
    def has_signal(self):
        return bool(self.n_signal)
    
    def process_bvp(self, bvp):
        try:
            bvp = bandpass_filter(bvp, fs=self.fps)
            bvp = norm_bvp(bvp, sr=self.fps)
            return bvp
        except:
            logger.warning("Filtering failure.")
            return bvp 
    
    @property
    def video_statistic(self):
        data = self.statistic
        return f"Total Frames: {data['frames']}\nKey Frames: {data['key']}\nNon-Key Frames: {data['dependent']}\nSkipped Frames: {data['skipped']}\nForward Filled Frames: {data['filled']}\nNo Face Detected Frames: {data['null']}"
        
    def bvp(self, start=0, end=None, raw=False):
        signals, ts = self.collect_signals(start, end)
        if 'bvp' not in signals or ts[-1]-ts[0]<2:
            return [], []
        bvp = signals['bvp']
        if len(bvp)<self.fps*2:
            return [], []
        if self.meta.get('cumsum_output'):
            bvp = np.cumsum(bvp)
            bvp = detrend(bvp, sr=self.fps)
        if not raw:
            bvp = self.process_bvp(bvp)
        return bvp, ts
        
    def hr(self, start=0, end=None):
        if self.has_signal:
            bvp, ts = self.bvp(start, end)
            try:
                hrv = get_prv(bvp, ts, self.fps)
                hr  = get_hr(bvp, self.fps)
                sqi = SQI(bvp)
            except:
                hr, sqi, hrv = None, None, {}
            return {'hr':hr, 'SQI':sqi, 'hrv':hrv, 'latency':self.latency}
        return None
    
    def update_face(self, face_img, ts=None, hasface=True):
        if face_img is None:
            if not hasface:
                face_img = np.zeros(self.input[1:], dtype='uint8')
                self.statistic['null'] += 1
            else:
                return
        if ts is None:
            ts = time.time()
        resolution = self.input[1:3]
        face_img = cv2.resize(face_img, resolution, interpolation=cv2.INTER_AREA)
        n = 0
        while (self.n_frame-0.3)/self.fps<=ts-(self.ts+[ts])[0]:
            with self.frame_lock:
                self.ts.append(ts)
                self.statistic['frames'] += 1
                if n>0 :
                    self.statistic['filled'] += 1
                self.face_buff.append((face_img, hasface))
            self.n_frame += 1
            self.sp.release()
            n += 1
        if n==0:
            self.statistic['skipped'] += 1
        
    def update_frame(self, frame, ts=None):
        if ts is None:
            ts = time.time()
        self.frame = frame
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(frame))
        box = None
        if self.n_frame%self.detect_per_n==0:
            r = self.detector.detect_for_video(img, round(ts*1e6))
            if len(r.detections):
                box = r.detections[0].bounding_box
                box = np.array([(box.origin_y-round(box.height*0.2), box.origin_y+round(box.height*0.9)),(box.origin_x, box.width+box.origin_x)])
                box[box<0] = 0
                self.hasface = ts + 1
            elif self.box is None or ts+1-self.hasface>1 or (self.rbox[:,0]<=np.array(0.05)*frame.shape[:2]).any() or (self.rbox[:,1]>=np.array(0.95)*frame.shape[:2]).any():
                self.hasface = 0
        if box is not None:
            if self.boxkf is None:
                kbox, self.boxkf = box, [KalmanFilter1D(0.01,0.5,i,1) for i in box.reshape(-1)]
            else:
                dt = ts-self.ts[-1] if self.ts else None
                kbox = np.array([round(k.update(i, dt)) for k, i in zip(self.boxkf, box.reshape(-1))]).reshape((2,2))
            self.rbox = box
            if self.box is None or max(np.abs((np.mean(kbox, axis=1)-np.mean(self.box, axis=1)))/np.mean(self.box, axis=0))>0.02:
                self.box = kbox
        if self.box is not None:
            img = np.ascontiguousarray(frame[slice(*self.box[0]), slice(*self.box[1])])
        else:
            img = None 
        if self.preview_lock.locked():
            self.preview_lock.release()
        self.update_face(img, ts, self.hasface)
    
    def video_capture(self, vid_path=0):
        if self.run is not None:
            raise RuntimeError('A task is currently running!')
        import sys 
        api = 0
        if sys.platform.startswith('win32'):
            api = 700
        self.run = threading.Thread(target=lambda:self.__process_video_capture(vid_path, api))
        self.run.start()
        stop = self.stop
        class _:
            def __enter__(self):
                return self 
            def __exit__(self, *k):
                stop()
        self.preview_lock.acquire()
        return _()
    
    def wait_completion(self):
        if self.run is None:
            return
        self.run.join()
    
    @property
    def preview(self):
        def f():
            while 1:
                if self.preview_lock is None:
                    return
                self.preview_lock.acquire()
                yield self.frame, self.box 
        return f()
        
    def stop(self):
        self.alive = False
        self.wait_completion()
        self.run = None
    
    def process_video(self, vid_path):
        container = av.open(vid_path, options={"hwaccel": "cuda"})
        stream = container.streams.video[0]
        stream.thread_type = 'AUTO'
        tsarr = []
        with self:
            for frame in container.decode(stream):
                if frame.key_frame:
                    self.statistic['key'] += 1
                else:
                    self.statistic['dependent'] += 1
                rotation = -frame.rotation%360
                ts = frame.time
                tsarr.append(ts)
                img = frame.to_ndarray(format='rgb24')
                if rotation == 90:
                    img = img.swapaxes(0, 1)[:, ::-1, :]
                elif rotation == 180:
                    img = img[::-1, ::-1, :]
                elif rotation == 270:
                    img = img.swapaxes(0, 1)[::-1, :, :]
                self.update_frame(img, ts)
        container.close()
        if len(tsarr)>2:
            goodvid = True
            fps = 1/np.diff(tsarr)
            fps_std = np.std(fps)
            fps = np.mean(fps)
            if not (self.fps*0.95<fps<self.fps*1.05):
                logger.warning('Frame rate mismatch, performing nearest neighbor sampling.')
                goodvid = False
            if fps_std>0.05*fps:
                logger.warning('Frame rate is unstable, performing nearest neighbor sampling.')
                goodvid = False
            if self.statistic['dependent']>0:
                logger.warning('Detected non-key frames, this will damage the rPPG signal. For information on key frames, see https://en.wikipedia.org/wiki/I-frame. \nPlease use https://github.com/KegangWangCCNU/PhysRecorder to record videos that only contain key frames.')
                goodvid = False
            if not goodvid:
                logger.info('\n'+self.video_statistic)
        return self.hr()
            
    
    def __process_video_capture(self, vid_path, api=None):
        cap = cv2.VideoCapture(vid_path, api)
        orientation = cap.get(cv2.CAP_PROP_ORIENTATION_META)
        with self:
            while self.alive:
                _, img = cap.read()
                if isinstance(vid_path, str):
                    ts = round(cap.get(cv2.CAP_PROP_POS_MSEC))%1000000000/1000
                else:
                    ts = time.time()
                if not _:
                    break
                if orientation>0:
                    if orientation == 90:
                        rotate_code = cv2.ROTATE_90_CLOCKWISE
                    elif orientation == 180:
                        rotate_code = cv2.ROTATE_180
                    elif orientation == 270:
                        rotate_code = cv2.ROTATE_90_COUNTERCLOCKWISE
                    img = cv2.rotate(img, rotate_code)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                self.update_frame(img, ts)
        cap.release()
        return self