
import os

import numpy as np
import scipy as sp
import scipy.io.wavfile

import data_io as io
import requests

import pyechonest
import pyechonest.config
import pyechonest.track

################################
# File IO.
def read_wav(fname):
    """
    http://www.scipy.org/doc/api_docs/SciPy.io.wavfile.html
    """
    sample_rate, data = sp.io.wavfile.read(fname)

    # Done.
    return data, sample_rate


def write_wav(fname, data, sample_rate):
    """
    http://www.scipy.org/doc/api_docs/SciPy.io.wavfile.html
    """
    sp.io.wavfile.write(fname, sample_rate, data)
    
    # Done.



def echo_nest_analysis(fname_song, fname_config=None):
    """
    Get track details via Echo Nest API.
    """
    if not fname_config:
        fname_config = 'config.yml'
      
    fname_config = os.path.abspath(fname_config)  
    path_work = os.path.dirname(fname_config)
    
    path_analysis = os.path.join(path_work, 'Analysis')
    if not os.path.isdir(path_analysis):
        os.mkdir(path_analysis)

    fname_song = os.path.basename(fname_song)
    
    fname_analysis = os.path.splitext(fname_song)[0] + '.full.yml'

    f = os.path.join(path_analysis, fname_analysis)
    if os.path.isfile(f):
        print('Load existing analysis')
        analysis, meta = io.read(f)
    else:
        # Read config.
        info, meta = io.read(fname_config)
        if not 'songs' in info:
            info['songs'] = {}
        
        # Configure Echo Nest API key.
        pyechonest.config.ECHO_NEST_API_KEY = info['api_key']
    
        # Load track details.
        if fname_song not in info['songs']:
            print('Upload new song to Echo Nest: %s' % fname_song)
            
            info['songs'][fname_song] = {}
            
            track = pyechonest.track.track_from_filename(fname_song)
            
            info['songs'][fname_song]['id'] = track.id
            info['songs'][fname_song]['analysis_url'] = track.analysis_url
            
            # Save updated config.
            io.write(fname_config, info)
    
        else:
            print('Download song analysis from Echo Nest: %s' % fname_song)
            track = pyechonest.track.track_from_id(info['songs'][fname_song]['id'])
            
        print('Retrieve full analysis from url')
        r = requests.get(track.analysis_url)
        analysis = r.json()

    
        print('Save analysis to cache folder')
        f = os.path.join(path_analysis, fname_analysis)
        io.write(f, analysis)
    
    # Done.
    return analysis
    
    
    
def parse_segments(analysis):
    """
    Pick out the information I want to make my robot dance!
    """
    points = []
    for segment in analysis['segments']:
        t0 = segment['start']
        v0 = segment['loudness_start']
    
        p0 = (10.**(v0/20))
        
        t1 = t0 + segment['loudness_max_time']
        v1 = segment['loudness_max']
        p1 = (10.**(v1/20))
    
        points.append( (t0, v0, p0) )            
        points.append( (t1, v1, p1) )        
        
    points = np.asarray(points)
    
    # Done.
    return points


    
def process_segments(fname_song):
    """
    Helper function.
    """

    path_work = os.path.dirname(fname_song)
    path_analysis = os.path.join(path_work, 'Analysis')
    if not os.path.isdir(path_analysis):
        os.mkdir(path_analysis)

    fname_points = os.path.basename(fname_song) + '.npz'
    f = os.path.join(path_analysis, fname_points)
    if os.path.isfile(f):
        print('Loading points')
        points, meta = io.read(f)
    else:
        print('Compute points')
        analysis = echo_nest_analysis(fname_song)

        print('Caching points')
        points = parse_segments(analysis)

        io.write(f, points)
    
    # Done,
    return points

    
            
if __name__ == '__main__':
    pass
