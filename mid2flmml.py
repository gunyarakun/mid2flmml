FILE_NAME = 'tekito.mid'

import midi

notes = ['C', 'C+', 'D', 'D+', 'E', 'F', 'F+', 'G', 'G+', 'A', 'A+', 'B']
globals = []
channels = [[] for d in 17 * [None]]
channel_stats = [{
  'note': None,
  'note_on_time': None,
  'note_off_time': None,
  'velocity': None,
  'octave': None,
} for d in 17 * [None]]

def pitch_to_octave_and_note(pitch):
  return [pitch / 12, notes[pitch % 12]]

def add_length(e, note, from_time, tpq):
  if not note:
    raise 'note is none'
  td = e.time - from_time
  if td == 0:
    if note != 'R':
      raise 'no time diff'
    return
  while td > tpq:
    channels[e.channel].append(note)
    td -= tpq
    if td > 0:
      channels[e.channel].append('&')
  if td > 0:
    channels[e.channel].append(note)
    channels[e.channel].append(str(int(((tpq / td) * 4))))

def add_octave_and_note(event, octave, pitch, tpq):
  if channel_stats[e.channel]['note_on_time']:
    print 'WARNING!: detect waon.'
    return
  cmd = ''
  if channel_stats[e.channel]['note_off_time']:
    add_length(e, 'R', channel_stats[e.channel]['note_off_time'], tpq)
  if channel_stats[e.channel]['velocity'] != e.velocity:
    channels[e.channel].append('@V%d' % e.velocity)
    channel_stats[e.channel]['velocity'] = e.velocity
  octave, note = pitch_to_octave_and_note(e.pitch)
  if channel_stats[e.channel]['octave']:
    od = octave - channel_stats[e.channel]['octave']
  else:
    od = None
  channel_stats[e.channel]['octave'] = octave

  if od == 1:
    channels[e.channel].append('<')
  elif od == 0:
    pass
  elif od == -1:
    channels[e.channel].append('>')
  else:
    channels[e.channel].append('O%d' % octave)
  channel_stats[e.channel]['note'] = note
  channel_stats[e.channel]['note_on_time'] = e.time
  channel_stats[e.channel]['note_off_time'] = None

def note_off(e, tpq):
  add_length(e, channel_stats[e.channel]['note'], channel_stats[e.channel]['note_on_time'], tpq)
  channel_stats[e.channel]['note'] = None
  channel_stats[e.channel]['note_on_time'] = None
  channel_stats[e.channel]['note_off_time'] = e.time

mid = midi.MidiFile()
mid.open(FILE_NAME)
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
      secPerQuarterNote = midi.getNumber(e.data, 3)[0] / 1000000.0
      if mid.ticksPerQuarterNote:
        print "tpq: %d" % mid.ticksPerQuarterNote
        tpq = float(mid.ticksPerQuarterNote)
      else:
        print "tps: %d" % mid.ticksPerSecond
        tpq = mid.ticksPerSecond * secPerQuarterNote
      tempo = 60.0 / secPerQuarterNote
      print "tempo: %d" % tempo
      globals.append('T%d' % tempo)
    elif e.type == 'PROGRAM_CHANGE':
      # TODO: http://noike.info/~kenzi/cgi-bin/mml2mp3/doc/FlMML_to_mml2mid.html
      # globals.append('/* program change ' + str(e.data) + ' */')
      pass
    elif e.type == 'CONTROLLER_CHANGE':
      # TODO: like PITCH_BEND
      pass
    elif e.type == 'PITCH_BEND':
      if channel_stats[e.channel]['note_on_time']:
        if channel_stats[e.channel]['note_on_time'] != e.time:
          note_off(e, tpq)
          channels[e.channel].append('&')
      octave, note = pitch_to_octave_and_note(e.pitch)
      add_octave_and_note(e, octave, note, tpq)
    elif e.type == 'NOTE_ON':
      octave, note = pitch_to_octave_and_note(e.pitch)
      add_octave_and_note(e, octave, note, tpq)
    elif e.type == 'NOTE_OFF':
      note_off(e, tpq)
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
