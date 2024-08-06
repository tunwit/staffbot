import os 
from ffmpeg import FFmpeg,Progress

ffmpeg = (
    FFmpeg()
    .option("y")
    .option("f","s16le")
    .option("ar","48000")
    .option("ac","2")
    .input("temp/483104273761304577")
    .input("temp/483104273761304577")
    .output("o.mp3",
            {
                "af":"silenceremove=stop_threshold=-50dB:stop_duration=2:stop_periods=-1"
           
            })
          )

print(ffmpeg.arguments)
try:
    ffmpeg.execute()
ex



# os.system("ffmpeg -i temp/483104273761304577-1722918409.6261818.mp3 -af silenceremove=stop_threshold=-50dB:stop_duration=2:stop_periods=-1 output.mp3")