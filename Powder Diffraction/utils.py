from scipy import ndimage
import numpy as np
from simulated_hardware import current_time

def simple_integration(image, num_bins=3001):
    sx, sy = image.shape
    x_, y_ = np.mgrid[-sx // 2 : sx // 2, -sy // 2 : sy // 2]
    r = np.hypot(x_, y_)
    rbin = (num_bins * r / r.max()).astype(np.int)
    radial_mean = ndimage.mean(image, labels=rbin, index=np.arange(1, rbin.max() + 1))
    return radial_mean

def look_at_watch():
    print ('the current time is '+str(current_time()))
    
def normalized_residual(data, ideal):
    return sum(abs(data-ideal))/len(data)

######################


def process_data(pair, num_lights = 1, return_light = False, return_dark = False):
    #assuming pair is tuple
    my_dark = catalog[pair[0]].primary.read().detector_image[0]
    
    if return_dark:
        return simple_integration(my_dark, num_bins=301)
    
    dark_subbed_list = []
    
    for i in range(1,num_lights+1):
        this_light = catalog[pair[i]].primary.read().detector_image[0]
        
        if return_light:
            dark_subbed_list.append(this_light)
        else:
            dark_subbed_list.append(this_light - my_dark)
    
    if num_lights == 1:
        return simple_integration(dark_subbed_list[0],num_bins=301)
    
    else: # more than one
        int_list = []
        for j in range(len(dark_subbed_list)):
            int_list.append(simple_integration(dark_subbed_list[j],num_bins=301))
    
        return np.array(int_list).T

def make_ideal_data(sample_num):
    _history['perfect_data'] = True

    perfect_pair = RE(dark_light_subtract(sample_num))    

    this_light = catalog[perfect_pair[1]].primary.read().detector_image[0]

    perfect_int = simple_integration(this_light,num_bins=301)

    _history['perfect_data'] = False
    
    return perfect_int

def retrieve_im(num):
    return catalog[num].primary.read().detector_image[0]