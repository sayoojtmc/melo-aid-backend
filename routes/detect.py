

import numpy       as np
import pretty_midi as pm
import librosa     as lbr
from   librosa.display import specshow
import tensorflow  as tf
def generate(fileName):
    
    interp = tf.lite.Interpreter(model_path="onsets_frames_wavinput.tflite")
    interp.get_input_details(), interp.get_output_details()
    interp.allocate_tensors()
    inputLen = interp.get_input_details()[0]['shape'][0]
    interp.set_tensor(interp.get_input_details()[0]['index'], np.array(np.random.random_sample(inputLen), dtype=np.float32))
    interp.invoke()
    for output in interp.get_output_details():
        first32Chords = interp.get_tensor(output['index'])
        print(output['name'], first32Chords[0].min(), first32Chords[0].max(), '\n', first32Chords, end='\n\n')
    rate, songName = 16_000, 'routes/'+fileName

    song = lbr.effects.trim(lbr.load(songName, rate)[0])[0]
    songLen = int(lbr.get_duration(song, rate))
    print('Song duration\t{} min : {} sec'.format(songLen // 60, songLen % 60))
    interp.set_tensor(interp.get_input_details()[0]['index'], song[:inputLen])
    interp.invoke()
    for output in interp.get_output_details():
        first32Chords = interp.get_tensor(output['index'])
        print(output['name'], first32Chords[0].min(), first32Chords[0].max(), '\n', first32Chords, end='\n\n')
    actProb, onProb, offProb, volProb = np.empty((1, 88)), np.empty((1, 88)), np.empty((1, 88)), np.empty((1, 88))
    outputStep = interp.get_output_details()[0]['shape'][1] * 512
    paddedSong = np.append(song, np.zeros(-(song.size - inputLen) % outputStep, dtype=np.float32))
    for i in range((paddedSong.size - inputLen) // outputStep + 1):
        interp.set_tensor(interp.get_input_details()[0]['index'], paddedSong[i * outputStep : i * outputStep + inputLen])
        interp.invoke()
        actProb = np.vstack((actProb, interp.get_tensor(interp.get_output_details()[0]['index'])[0]))
        onProb  = np.vstack(( onProb, interp.get_tensor(interp.get_output_details()[1]['index'])[0]))
        offProb = np.vstack((offProb, interp.get_tensor(interp.get_output_details()[2]['index'])[0]))
        volProb = np.vstack((volProb, interp.get_tensor(interp.get_output_details()[3]['index'])[0]))

    #############
    threshold = 0
    #############


    midi = pm.PrettyMIDI(initial_tempo=lbr.beat.tempo(song, rate).mean())
    midi.lyrics += [pm.Lyric('Automatically transcribed from audio:\r\n\t' + songName, 0),
                    pm.Lyric('Used software created by Boris Shakhovsky', 0)]
    track = pm.Instrument(program=pm.instrument_name_to_program('Acoustic Grand Piano'), name='Acoustic Grand Piano')
    midi.instruments += [track]

    ''' Based on https://github.com/tensorflow/magenta/blob/master/magenta/music/sequences_lib.py#L1844
        magenta.music.midi_ionote_sequence_to_midi_file(
        magenta.music.sequences_libpianoroll_to_note_sequence(fps=rate/512, min_duration=0, min_midi_pitch=21 ... '''

    intervals, frameLenSecs = {}, lbr.frames_to_time(1, rate) # Time is in absolute seconds, not relative MIDI ticks
    ########################################################
    onsets = (onProb > threshold).astype(np.int8)
    frames = onsets | (actProb > threshold).astype(np.int8) # Ensure that any frame with an onset prediction is considered active.
    #######################################################

    def EndPitch(pitch, endFrame):
        #######################################################################################
        if volProb[intervals[pitch], pitch] < 0 or volProb[intervals[pitch], pitch] > 1: return
        #######################################################################################
        track.notes += [pm.Note(int(max(0, min(1, volProb[intervals[pitch], pitch])) * 80 + 10), pitch + 21,
                                intervals[pitch] * frameLenSecs, endFrame * frameLenSecs)]
        del intervals[pitch]

    # Add silent frame at the end so we can do a final loop and terminate any notes that are still active:
    for i, frame in enumerate(np.vstack([frames, np.zeros(frames.shape[1])])):
        for pitch, active in enumerate(frame):
            if active:
                if pitch not in intervals:
                    if onsets is None: intervals[pitch] = i
                    elif onsets[i, pitch]: intervals[pitch] = i # Start a note only if we have predicted an onset
                    #else: Even though the frame is active, there is no onset, so ignore it
                elif onsets is not None:
                    if (onsets[i, pitch] and not onsets[i - 1, pitch]):
                        EndPitch(pitch, i)   # Pitch is already active, but because of a new onset, we should end the note
                        intervals[pitch] = i # and start a new one
            elif pitch in intervals: EndPitch(pitch, i)

    if track.notes: assert len(frames) * frameLenSecs >= track.notes[-1].end, 'Wrong MIDI sequence duration'

    notes = midi.get_pitch_class_histogram()


    gamma = [n for _, n in sorted([(count, ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'][i])
                                for i, count in enumerate(notes)], reverse=True)[:7]]
    blacks = sorted(n for n in gamma if len(n) > 1)

    chroma = lbr.feature.chroma_cqt(song, rate).sum(1)
    major = [np.corrcoef(chroma, np.roll([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88], i))[0, 1] for i in range(12)]
    minor = [np.corrcoef(chroma, np.roll([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17], i))[0, 1] for i in range(12)]
    keySignature = (['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'][
        major.index(max(major)) if max(major) > max(minor) else minor.index(max(minor)) - 3]
                    + ('m' if max(major) < max(minor) else ''))
    midi.key_signature_changes += [pm.KeySignature(pm.key_name_to_key_number(keySignature), 0)]
    songName = '.'.join(songName.split('.')[:-1]) + '.mid'
    midi.write(songName)
    f=open("routes/"+fileName,"r")
    return '.'.join(songName.split('.')[:-1]) + '.mid'
    