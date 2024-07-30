from pydub import AudioSegment
from pydub.silence import split_on_silence

DURATION = 48000*5

audio:AudioSegment = AudioSegment.from_mp3("407176297991634954-30072024194315.mp3")

chunks = split_on_silence(audio,min_silence_len=1,keep_silence=2500)

non_silent_audio = AudioSegment.empty()
if chunks:
    for chunk in chunks:
        non_silent_audio += chunk
else:
    non_silent_audio = audio
print("saving")
non_silent_audio.export("new.mp3")