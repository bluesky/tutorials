import threading

import numpy
import numpy as np
from ophyd import Component, Device, Signal, DeviceStatus
from bluesky.plan_stubs import mv

from generate_data import make_random_peaks, generate_flat_field, generate_image

LIMIT = 9999.0

big_image_mode = False #use only if running on something that isn't binder machine (otherwise slow)

_time = {"state": 0.0}

_history = {"sample": [], "light": [], "image": []}

_history['decay_a'] = 1000
_history['panel_amp'] = 50
_history['panel_oset'] = 10
_history['panel_wid'] = 32
_history['noise'] = 50
_history["panel_wl"] = 80000
_history["panel_wl_hard"] = 100
_history['action_time'] = 0.5
_history['perfect_data'] = False
_history['integration_bins'] = 101
SHAPE = (128,128)


if big_image_mode:
    SHAPE = (512, 512)
    _history['panel_wid'] = 128 
    _history['integration_bins'] = 301
    _history['panel_wl_hard'] = 400
    
def sim_sleep(t):
    print (f"sleeping for {t}")
    time_travel(current_time()+t)

def time_travel(t):
    if t > LIMIT:
        raise ValueError(f"Cannot time travel past {LIMIT}")
    _time["state"] = t


def current_time():
    t = _time["state"]
    #print("current time is", t)
    return t

class Shutter(Signal):
    def put(self, value):
        current_value = self.get()
        if value == "open":
            _history["light"].append((current_time(),))
            
        if value == "closed":
            (opened_time,) = _history["light"].pop()
            _history["light"].append((opened_time, current_time()))
        super().put(value)

        
class SampleSelector(Signal):
    def put(self, value):
        current_value = self.get()
        if current_value != value: #check if need to change anything
            if current_value:
                (loaded_time,) = _history["sample"].pop()
                _history["sample"].append((loaded_time, current_time()))
            if value:
                _history["sample"].append((current_time(),))
                _history["image"].append(patterns[value])
        #else:
        #    print ('already have sample number '+str(value)+' selected')
            
        super().put(value)

        
shutter = Shutter(name="shutter", value="closed")
sample_selector = SampleSelector(name="sample_selector", value=0)


patterns = {}
x = numpy.linspace(0, 30, num=_history['integration_bins'])
intensities = {}


for i in range(1, 5):
    if big_image_mode:
        intensity = make_random_peaks(x, peak_chance=0.1) * 1000.0
    else:
        intensity = make_random_peaks(x, peak_chance=0.2) * 1000.0
    
    image = generate_image(x, intensity, SHAPE)
    intensities[i] = intensity
    patterns[i] = image
    
    
def det_panels(shape, oset=1, wid=32, amp=2000):
    det_im = np.zeros(shape)
    #print ('amp '+str(amp))
    for x in range(shape[1]):
        det_im[:int(shape[0]/2),x] = amp*np.mod(x,wid)**.5+oset
        det_im[int(shape[0]/2):,x] = amp*np.mod(shape[1]-x,wid)**.5+oset
    return det_im    

def noisy_im(shape,noise=10):
    return np.random.random(shape)*noise

class TimerStatus(DeviceStatus):
    """Simulate the time it takes for a detector to acquire an image."""

    def __init__(self, device, delay):
        super().__init__(device)
        self.delay = delay  # for introspection purposes
        threading.Timer(delay, self.set_finished).start()


class DiffractionDetector(Device):
    # exposure_time = Component(Signal, value=1)
    image = Component(Signal, value=numpy.zeros(SHAPE))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def trigger(self):
        # Start with a flat field.
        # arr = generate_flat_field(SHAPE)          
        
        f = make_illumination_combinations(
            _history["sample"], _history["image"], _history["light"], _history["decay_a"]
        )
        
        arr = f(current_time())
        #arr = patterns[sample_selector.read()['sample_selector']['value']]
        #self.image.set(arr)
        
        #add panel effect to image
        varying_pan_amp = np.sin(current_time()*(2.0*np.pi/_history["panel_wl"]))+1.0
        
        arr += det_panels(SHAPE,
                          oset=_history["panel_oset"],
                          wid=_history["panel_wid"],
                          amp=varying_pan_amp* _history["panel_amp"])
        
        #add noisy effect to image
        arr += noisy_im(SHAPE,noise=_history["noise"])
        
        if _history["perfect_data"]:
            #wipe out all other effects, just make a perfect iamge from patterns
            arr = patterns[sample_selector.read()['sample_selector']['value']]
        
        self.image.set(arr)
        READOUT_TIME = 0.17
        
        #move time forward
        time_travel(current_time()+_history['action_time'])
        
        return TimerStatus(self, READOUT_TIME)

    def collect_asset_docs(self):
        yield from []


detector = DiffractionDetector(name="detector")

def make_simple_decay_func(I0, a=10, t1=2, t2=10,s=10):
    def decay_func(x):
        #rise = np.exp((x-t1)*s)/(1+np.exp((x-t1)*s)) * (x>=t1) * (x<=t2)    
        rise = 1.0*(x>=t1) * (x<=t2)
        fall = np.exp(-a*(x-t2)/I0) * (x > t2)
        return I0 * (rise + fall)
    return decay_func

def make_decay_func(I0, a=10, t1=2, t2=10):
    def decay_func(x):
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            pre = np.nan_to_num(I0 ** 2 / a * np.exp(-(a * x / I0)))

            f1 = np.heaviside(t1 - t2, 1) * np.heaviside(x - t2, 1)
            f1a = np.exp(a * t2 / I0) - np.exp(a * x / I0)
            f1b = (np.exp(x * a / I0) - np.exp(a * t1 / I0)) * np.heaviside(-t1 + x, 1)
            f1 *= f1a + f1b

            f2 = np.heaviside(t2 - t1, 1) * np.heaviside(x - t1, 1)
            f2a = np.exp(t1 * a / I0) - np.exp(x * a / I0)
            f2b = (np.exp(x * a / I0) - np.exp(t2 * a / I0)) * np.heaviside(x - t2, 1)
            f2 *= f2a + f2b

        return np.nan_to_num(pre * (f1 - f2))

    return decay_func


def make_illumination_combinations(
    sample_history, im_history, light_history, a, tmax=LIMIT):
    sample_history = sample_history.copy()
    im_history = im_history.copy()
    light_history = light_history.copy()
    decay_func_list = []
    tmax = _time["state"]
    
    #check for empty lists
    if len(sample_history) > 0 and len(light_history) > 0:
        if len(sample_history[-1]) == 1:
            sample_history[-1] = (sample_history[-1][0], tmax)
            # print ('setting max time to sample_history '+str(sample_history[-1]))

        if len(light_history[-1]) == 1:
            light_history[-1] = (light_history[-1][0], tmax)

        for i in range(len(sample_history)):
            this_im = im_history[i]
            # make a series of tuples
            im_tstart = sample_history[i][0]
            im_tend = sample_history[i][1]

            my_list = []
            # see if a time exists in a light_loop
            for j in range(len(light_history)):
                light_tstart = light_history[j][0]  # light on
                light_tend = light_history[j][1]  # light off

                # first, check if image ends before light starts
                if light_tstart > im_tend or light_tend < im_tstart:
                    # print ('this light does not overlap sample')
                    pass
                else:  # have some overlap
                    # determine start
                    use_start = im_tstart
                    if im_tstart < light_tstart:
                        use_start = light_tstart
                    use_end = im_tend
                    if im_tend > light_tend:
                        use_end = light_tend
                    my_list.append((use_start, use_end))

            for k in range(len(my_list)):
                #print ('making a decay func for times '+str(my_list[k][0])+' '+str(my_list[k][1]))
                # make a decay func for these
                decay_func_list.append(
                    #make_decay_func(this_im, a=a, t1=my_list[k][0], t2=my_list[k][1])
                    make_simple_decay_func(this_im, a=a, t1=my_list[k][0], t2=my_list[k][1], s = 10)
                )
        #print ("total length of combination list is "+str(len(my_list)))
    
    else:
        #print ('something empty')
        pass 
    
    def f(t):
        return sum(f(t) for f in decay_func_list)

    return f


def load_sample(i):
    yield from mv(sample_selector, i)
    time_travel(current_time()+_history['action_time'])

def unload_sample():
    yield from mv(sample_selector, 0)
    time_travel(current_time()+_history['action_time'])

def light(state):
    "state: True or False"
    if shutter.get() == "open" and not state:
        yield from mv(shutter, {True: "open", False: "closed"}[bool(state)])
        time_travel(current_time()+_history['action_time'])
    
    elif shutter.get() == "closed" and state:
        yield from mv(shutter, {True: "open", False: "closed"}[bool(state)])
        time_travel(current_time()+_history['action_time'])
    
    else:
        #print ('shutter already in requested state')
        pass
    
def history_reset():
    sample_selector.put(0)
    if shutter.get() == 'open': #check if open
        shutter.put('closed') #command to close shutter directly
    
    _history["sample"] = []
    _history["light"] = []
    _history["image"] = []
    time_travel(0)

