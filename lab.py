# No Imports Allowed!


def backwards(sound):
    audio = {'rate': sound['rate'], 'samples': sound['samples'][::-1]}
    return audio

def mix(sound1, sound2, p):
    #Check that sample rates are equal
    if sound1['rate'] != sound2['rate']:
        return None
    
    #Create two new copies of the audio and multiply by the mixing parameter
    sound1_mixed_samples = [num * p for num in sound1['samples']]
    sound2_mixed_samples = [num * (1-p) for num in sound2['samples']]

    #Add the lists together and return the mixed audio
    #zip function creates tuples pairs and if lists have different lengths, it ignores the elements that do not have a pair.
    return {'rate': sound1['rate'], 'samples': [sum(x) for x in zip(sound1_mixed_samples, sound2_mixed_samples)]}


def echo(sound, num_echoes, delay, scale):
    s1 = {'rate': sound['rate'], 'samples': sound['samples'][::]} #Create new sound dict
    samples = s1['samples']
    sample_delay = round(delay * s1['rate'])
    l = [0 for x in range(len(s1['samples']) + num_echoes * sample_delay)]
    collection = []
    
    for x in range(len(samples)): #add original sound samples
        l[x] = samples[x]

    for x in range(num_echoes):
        l1=[]
        for y in samples:
            l1.append(y * scale**(x+1))
        collection.append(l1)

    c = sample_delay
    for x in collection:
        i = 0
        for y in x:
            l[c + i] += y
            i += 1
        c += sample_delay
    s1['samples'] = l
    return s1

def pan(sound):
    s = {'rate': sound['rate'], 'left': sound['left'][::], 'right':sound['right'][::]}
    left = s['left']
    right = s['right']
    for x in range(len(left)):
        left[x] *= 1 - (x/(len(left) - 1))
        right[x] *= x/(len(left) - 1)
    return s


def remove_vocals(sound):
    s = {'rate': sound['rate'], 'samples':[]}
    left = sound['left'][::]
    right = sound['right'][::]
    for x in range(len(left)):
        s['samples'].append(left[x] - right[x])
    return s


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
from os import remove
from turtle import back
import wave
import struct


def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack("<h", frame[:2])[0])
                right.append(struct.unpack("<h", frame[2:])[0])
            else:
                datum = struct.unpack("<h", frame)[0]
                left.append(datum)
                right.append(datum)

        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack("<h", frame[:2])[0]
                right = struct.unpack("<h", frame[2:])[0]
                samples.append((left + right) / 2)
            else:
                datum = struct.unpack("<h", frame)[0]
                samples.append(datum)

        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l, r in zip(sound["left"], sound["right"]):
            l = int(max(-1, min(1, l)) * (2**15 - 1))
            r = int(max(-1, min(1, r)) * (2**15 - 1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/meow.wav, rather than just as meow.wav, to account for the sound
    # files being in a different directory than this file)
    # meow = load_wav("sounds/meow.wav")
    car = load_wav("sounds/lookout_mountain.wav", stereo=True)
    write_wav(remove_vocals(car), 'vocal_lookout_mountain.wav')

    # write_wav(backwards(meow), 'meow_reversed.wav')
