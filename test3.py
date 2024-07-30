from pydub import AudioSegment

DURATION = 48000*5

audio:AudioSegment = AudioSegment.from_mp3("test/407176297991634954-LittLeBirDD.mp3")
counter = 0
for pcm in audio.raw_data:
    if pcm == 0:
        counter += 1
    elif counter >= DURATION:
        counter = 0
        continue
    else:
        counter = 0
    print(pcm)