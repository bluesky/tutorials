

### Setup to make notebook behave like a single bluesky terminal session


### Setup up current session to be "later in the day"
RE(mv(motor, 0, temperature, 40))

def align_peak():
    uid = yield from scan([noisy_det], motor, -5, 5, 11) 
    if uid is not None:
        #print('doing')
        yield from bps.sleep(3) #need this (or 10s) for hardware
        my_max = bec.peaks["max"]["noisy_det"][0]
        yield from mv(motor, my_max)
    #else:
        #print('passing')
        #pass
        
def one_temperature():
    yield from align_peak()
    yield from count([noisy_det], 5, md={'purpose':'analyze'})
    
def my_experiment(myT_list):
    for myT in myT_list:
        print(f'Changing temperature to {myT}')
        yield from mv(temperature, myT)
        yield from one_temperature()
        print(f'\tFinished scans for temperature {myT}')
        
        

        
        

from ophyd.sim import motor1, motor2, det2       
my_dets = [det, noisy_det, temperature, motor1.readback, det2]

