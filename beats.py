
import os
import threading
import time
import ossaudiodev

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
        fname_config = 'audio_config.yml'
      
    fname_config = os.path.abspath(fname_config)  
    path_work = os.path.dirname(fname_config)
    
    path_analysis = os.path.join(path_work, 'Audio Analysis')
    if not os.path.isdir(path_analysis):
        os.mkdir(path_analysis)

    fname_song = os.path.basename(fname_song)
    b, e = os.path.splitext(fname_song)
    if e != '.mp3':
        fname_song = b + '.mp3'
    
    fname_analysis = b + '.full.yml'

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
    path_analysis = os.path.join(path_work, 'Audio Analysis')
    if not os.path.isdir(path_analysis):
        os.mkdir(path_analysis)

    b, e = os.path.splitext(os.path.basename(fname_song))
    fname_points = b + '.npz'
    
    f = os.path.join(path_analysis, fname_points)
    if os.path.isfile(f):
        print('Loading audio points')
        points, meta = io.read(f)
    else:
        print('Analyze song...')
        analysis = echo_nest_analysis(fname_song)

        print('Caching audio points')
        points = parse_segments(analysis)

        io.write(f, points)
    
    # Done,
    return points

#############################################################


class Player(threading.Thread):
    """
    This class handles audio play back with ability to report back about beats.
    """
    
    def __init__(self, fname, time_interval=None):
        """
        Initialize class.
        """
        threading.Thread.__init__(self)

        if not time_interval:
            time_interval = 0.05

        self.time_interval = time_interval

        self.lock = threading.Lock()
        self.is_running = False

        self._timestamp = None
        
        fname = os.path.normpath(fname)

        if not os.path.isfile(fname):
            raise IOError('Input file does not exist: %s' % fname)
        
        print('Load audio data: %s' % os.path.basename(fname))
        b, e = os.path.splitext(fname)
        fname_wav = b + '.wav'
        data_audio, sample_rate = read_wav(fname_wav)

        num_frames, num_channels = data_audio.shape
        
        self.fname = fname
        self.data_audio = data_audio

        self.num_frames = num_frames
        self.num_channels = num_channels
        self.sample_rate = sample_rate

        print('Load audio analysis')
        self.audio_points = process_segments(fname_song)

        print('Configure audio device')
        self.chunk_size = int(self.time_interval * self.sample_rate)
        print('  time interval: %.1f ms' % self.time_interval*1000)
        print('  audio chunk size: %d' % self.chunk_size)
        
        self.audio_device = ossaudiodev.open('w')
        self.audio_device.setparameters(ossaudiodev.AFMT_S16_LE, self.num_channels, self.sample_rate)
        print('  audio buffer size: %d' % self.audio_device.bufsize())
    
        time.sleep(0.01)
        self.audio_device.setparameters(ossaudiodev.AFMT_S16_LE, self.num_channels, self.sample_rate)

        # Done.
        
        
        
    @property
    def timestamp(self):
        """
        Timestamp for use during music playback.
        """
        self.lock.acquire()
        value = self._timestamp
        self.lock.release()
        
        return value
        
        
        
    @timestamp.setter
    def timestamp(self, value=None):
        if value is None:
            value = time.time()
            
        self.lock.acquire()
        self._timestamp = value
        self.lock.release()
        
        
        
    def run(self):
        """
        This is where the action happens.
        """
        k0 = 0
        k1 = 0

        self.is_running = True
        try:
            while self.is_running:
                
                k0 = k1
                k1 = k0 + self.chunk_size
                data_chunk_str = self.data_audio[k0:k1].tostring()
    
                t0 = time.time()
                self.audio_device.write(data_chunk_str)
                t1 = time.time()
                print('%.5f, %.5f' % (t1 - t0, delta))
    
        except KeyboardInterrupt:
            print('\nUser stop!')

        # Finish.
        self.audio_device.close()
        
        # Done.


    def stop(self):
        if self.isAlive():
            print('Player stopping: %s' % os.path.basename(self.fname))

        self.is_running = False


    def beats(self):
        """
        Setup a generator to yield beat information in a timely manner.
        """
        while self.is_running:
            yield 'hello!'


if __name__ == '__main__':

    
    #########################################
    # Setup.
    path_data = os.path.abspath(os.path.curdir)
    fname = 'Manic Polka'

    ##########################################
    # Do it.
    fname_mp3 = fname + '.mp3'
    fname_wav = fname + '.wav'


    try:
        while True:

    except KeyboardInterrupt:
        audio_device.close()
        

    # Sound analysis.
    # points = beats.process_segments(fname_mp3)

    # Done.
    
    