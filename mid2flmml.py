import midi

notes = ['C', 'C+', 'D', 'D+', 'E', 'F', 'F+', 'G', 'G+', 'A', 'A+', 'B']
globals = []
channels = [[] for d in 16 * [None]]
channel_stats = [{
  'note': None,
  'note_on_time': None,
  'velocity': None,
  'octave': None,
} for d in 16 * [None]]

def pitch_to_octave_and_note(pitch):
  return [pitch / 12, notes[pitch % 12]]

def add_octave_and_note(event, octave, pitch):
  if channel_stats[e.channel]['velocity'] != e.velocity:
    channels[e.channel].append('@V%d' % e.velocity)
  octave, note = pitch_to_octave_and_note(e.pitch)
  if channel_stats[e.channel]['octave']:
    od = octave - channel_stats[e.channel]['octave']
  else:
    od = None

  if od == 1:
    channels[e.channel].append('<')
  elif od == 0:
    pass
  elif od == -1:
    channels[e.channel].append('<')
  else:
    channels[e.channel].append('O%d' % octave)
  channels[e.channel].append(note)
  channel_stats[e.channel]['note'] = note
  channel_stats[e.channel]['note_on_time'] = e.time

mid = midi.MidiFile()
mid.open('dora_h.mid')
mid.read()
for track in mid.tracks:
  for e in track.events:
    if e.type == 'SEQUENCE_TRACK_NAME':
      globals.append('/* ' + e.data + ' */\n')
    elif e.type == 'COPYRIGHT_NOTICE':
      globals.append('/* ' + e.data + ' */\n')
    elif e.type == 'DeltaTime':
      pass
    elif e.type == 'SET_TEMPO':
      secPerQuarterNote = 1000000.0 / midi.getNumber(e.data, 3)[0]
      if mid.ticksPerQuarterNote:
        tpq = mid.ticksPerQuarterNote
      else:
        tpq = mid.ticksPerSecond / secPerQuarterNote
      tempo = 60.0 / secPerQuarterNote
      globals.append('T%d' % tempo)
    elif e.type == 'PROGRAM_CHANGE':
      globals.append('/* program change ' + str(e.data) + ' */')
    elif e.type == 'CONTROLLER_CHANGE':
      # TODO: NOTE_ON tochu change taiou
      pass
    elif e.type == 'PITCH_BEND':
      octave, note = pitch_to_octave_and_note(e.pitch)
      add_octave_and_note(e, octave, note)
    elif e.type == 'NOTE_ON':
      octave, note = pitch_to_octave_and_note(e.pitch)
      add_octave_and_note(e, octave, note)
    elif e.type == 'NOTE_OFF':
      td = e.time - channel_stats[e.channel]['note_on_time']
      while td > tpq:
        channels[e.channel].append('&')
        channels[e.channel].append(channes_stats[e.channel]['note'])
        td -= tpq
      if td > 0:
        channels[e.channel].append(str((tpq / td) * 4))
    elif e.type == 'END_OF_TRACK':
      pass
    else:
      print e

# output
print ''.join(globals)
for i in channels:
  if len(i) > 0:
    print ''.join(i)
    print ';\n'
mid.close()
