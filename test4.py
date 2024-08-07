import os 
from ffmpeg import FFmpeg,Progress
import temp
ffmpeg = (
    FFmpeg()
    .option("y")
    .input("temp/483104273761304577-compensate.mp3",
            f="s16le",
            ar="48000",
            ac = "2")
    .input("temp/847770564525162546-compensate.mp3",
            f="s16le",
            ar="48000",
            ac = "2")
    .output("o.mp3",
            {
                "filter_complex ":"amix=inputs=3:duration=longest"
            })
          )

print(ffmpeg.arguments)

ffmpeg.execute()




# os.system("ffmpeg -i temp/483104273761304577-1722918409.6261818.mp3 -af silenceremove=stop_threshold=-50dB:stop_duration=2:stop_periods=-1 output.mp3")