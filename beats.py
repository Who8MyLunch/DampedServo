
import argparse
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
    #if not (e == '.mp3' or e == '.m4a'):
    #    fname_song = b + '.mp3'
    
    fname_analysis = b + '.full.yml'

    f = os.path.join(path_analysis, fname_analysis)
    if os.path.isfile(f):
        print('Load existing analysis')
        analysis, meta = io.read(f)
    else:
        # Read config.
        info, meta = io.read(fname_config)
        if not info['songs']:
            info['songs'] = {}
            
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
    

    
def parse_analysis(analysis):
    """
    Pick out the information I want to make my robot dance!
    """
    beats = []
    for b in analysis['beats']:
        t0 = b['start']
        beats.append(t0)

    segments = []
    for s in analysis['segments']:
        t0 = s['start']
        #v0 = s['loudness_start']        
        #p0 = (10.**(v0/20))
        
        t1 = t0 + s['loudness_max_time']
        p1 = s['loudness_max']
        v1 = (10.**(p1/20))
    
        segments.append( (t1, p1, v1) )        

    # Done.
    return beats, segments


    
def analyze_song(fname_song):
    """
    Helper function.
    """

    path_work = os.path.dirname(fname_song)
    path_analysis = os.path.join(path_work, 'Audio Analysis')
    if not os.path.isdir(path_analysis):
        os.mkdir(path_analysis)

    b, e = os.path.splitext(os.path.basename(fname_song))
    fname_beats = b + '.beats.npz'
    fname_segments = b + '.segments.npz'
    
    fa = os.path.join(path_analysis, fname_beats)
    fb = os.path.join(path_analysis, fname_segments)
    if os.path.isfile(fa) and os.path.isfile(fb):
        print('Loading analysis')
        beats, meta = io.read(fa)
        segments, meta = io.read(fb)
    else:
        print('Analyze song')
        analysis = echo_nest_analysis(fname_song)

        print('Caching analysis results')
        beats, segments = parse_analysis(analysis)

        beats = np.asarray(beats)
        segments = np.asarray(segments)
    
        io.write(fa, beats)
        io.write(fb, segments)

    # Normalize levels.
    v = segments[:, 2]

    v = v / np.median(v)
    #lo, hi = np.percentile(v, [20., 80.])
    #v = (v - lo) / (hi - lo)
    #v = np.clip(v, 0, 1)
    
    segments[:, 2] = v
    
    # Done,
    return beats, segments

#############################################################


class Player(threading.Thread):
    """
    This class handles audio play back with ability to report back about beats.
    """
    
    def __init__(self, fname, time_interval=None, lag=0.):
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

        b, e = os.path.splitext(fname)
        #if not (e == '.mp3' or e == '.m4a'):
        #    fname = b + '.mp3'
            
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
        self.audio_beats, self.audio_segments = analyze_song(fname)

        print('Configure audio device')
        self.chunk_size = int(self.time_interval * self.sample_rate)
        print('  time interval: %.1f ms' % (self.time_interval*1000))
        print('  audio chunk size: %d' % self.chunk_size)
        
        self.audio_device = ossaudiodev.open('w')
        self.audio_device.setparameters(ossaudiodev.AFMT_S16_LE, self.num_channels, self.sample_rate)

        bufsize =  self.audio_device.bufsize()
        self.bufsize = bufsize
        print('  audio buffer size: %d' % bufsize)
    
        time.sleep(0.01)
        self.audio_device.setparameters(ossaudiodev.AFMT_S16_LE, self.num_channels, self.sample_rate)

        # Estimate time lag.
        self.lag = float(bufsize)/self.chunk_size * self.time_interval + lag
        print('  time lag: %.3f' % self.lag)
        
        # Done.
                
        
    @property
    def timestamp(self):
        """
        Timestamp for use music current being played.
        """
        self.lock.acquire()
        value = self._timestamp
        self.lock.release()
        
        return value
        
        
    @timestamp.setter
    def timestamp(self, value):
        self.lock.acquire()
        self._timestamp = value
        self.lock.release()
                
        
    def run(self):
        """
        This is where the action happens.
        """
        k0 = 0
        k1 = 0

        t0 = time.time()
        t1 = t0
        
        self.is_running = True
        try:
            while self.is_running:
                
                k0 = k1
                k1 = k0 + self.chunk_size
                data_chunk_str = self.data_audio[k0:k1].tostring()

                self.timestamp = float(k1) / self.sample_rate - self.lag
                self.audio_device.write(data_chunk_str)

            # Loop is over, Still some data in the pipeline.
            dt = float(self.bufsize) / float(self.sample_rate)
            print('Empty buffer: %.2f' % dt)
            time.sleep(dt)
    
        except KeyboardInterrupt:
            print('\nUser stop!')
            self.stop()

        # Finish.
        print('Close audio devcice')
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

        # Make a list of audio events.
        data_beats = [ (t, 'beat') for t in self.audio_beats]
        data_segs = [ (t, 'segment', (p,v) ) for t,p,v in self.audio_segments]

        data = data_beats + data_segs
        data = np.asarray(data, dtype=np.object)
        times = [d[0] for d in data]

        ix = np.argsort(times)
        data = data[ix]

        v_old = 0.
        for d in data:
            t = d[0]
            while self.timestamp <= t:
                time.sleep(self.time_interval*0.1)

            yield d


            

if __name__ == '__main__':
    
    #########################################
    # Setup.


    parser = argparse.ArgumentParser(description='Process a song.')
    
    parser.add_argument('fname', type=str, help='Song file name.')

    args = parser.parse_args()

    print('Processing data for: %s' % args.fname)
    results = analyze_song(args.fname)
    

    
    # Done.
    
    