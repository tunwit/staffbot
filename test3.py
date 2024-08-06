from pydub import AudioSegment
from pydub.silence import split_on_silence

DURATION = 48000*5

audio:AudioSegment = AudioSegment.from_raw(file="temp/483104273761304577",
            sample_width=2,  # 16-bit audio
            frame_rate=48000,  
            channels=2  # Stereo
            )

o:AudioSegment = AudioSegment.from_raw(file="temp/847770564525162546",
            sample_width=2,  # 16-bit audio
            frame_rate=48000,  
            channels=2  # Stereo
            )

overlay = audio.overlay(o)
overlay.export("new.mp3")