
import os
import time
import ossaudiodev
import wave

import damped_servo
import lego
import beats

if __name__ == '__main__':

    #########################################
    # Setup.
    path_data = os.path.abspath(os.path.curdir)
    fname = 'Manic Polka'

    ##########################################
    # Do it.
    fname_mp3 = fname + '.mp3'
    fname_wav = fname + '.wav'

    #audio_file = wave.open(fname_wav, 'rb')
    #params = audio_file.getparams()
    #num_channels, sample_width, frame_rate, num_frames, comptype, compname = params
    #data_audio = audio_file.readframes(num_frames)
    #audio_file.close()

    f = os.path.join(path_data, fname_wav)
    data_audio, sample_rate = beats.read_wav(f)
    num_frames, num_channels = data_audio.shape

    # Play back through speaker.
    audio_device = ossaudiodev.open('w')

    audio_device.setparameters(ossaudiodev.AFMT_S16_LE, num_channels, sample_rate)
    print(audio_device.bufsize())
    audio_device.setparameters(ossaudiodev.AFMT_S16_LE, num_channels, sample_rate)
    print(audio_device.obuffree())
    time.sleep(0.2)

    audio_device.setparameters(ossaudiodev.AFMT_S16_LE, num_channels, sample_rate)
    chunk_size = 2000
    
    delta = float(chunk_size)/sample_rate
    k0 = 0
    k1 = 0
    try:
        while True:

            k0 = k1
            k1 = k0 + chunk_size
            data_chunk = data_audio[k0:k1]

            t0 = time.time()
            audio_device.write(data_chunk.tostring())
            t1 = time.time()
            print('%.5f, %.5f' % (t1 - t0, delta))
    except KeyboardInterrupt:
        audio_device.close()
        

    # Sound analysis.
    # points = beats.process_segments(fname_mp3)

    # Done.
    
    