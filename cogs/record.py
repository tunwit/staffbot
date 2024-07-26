import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import voice_recv
import wave
from pydub import AudioSegment
import asyncio
import numpy as np
import time

class record(commands.Cog):
    def __init__(self, bot ):
        self.bot = bot
        self.sample_rate = 48000 
        self.channel = 2
        self.wav = None
        self.audios = {

        }
        self.last_recive = {}
        self.task = None
        self.run = True

    def calculate_rms(self,pcm_data):
        pcm_array = np.frombuffer(pcm_data, dtype=np.int16)
    
        # Convert to float32 for calculations
        pcm_float = pcm_array.astype(np.float32)
        
        # Normalize based on sample width
        pcm_float = pcm_float / (2**(8 * 2 - 1))
        
        # Calculate RMS
        rms = np.sqrt(np.mean(pcm_float**2))
        
        return rms * 100

    def callback(self,user:discord.Member, data: voice_recv.VoiceData):
        if user:
            if user.id not in self.audios:
                self.audios[user.id] = [bytearray(),time.time(),None]
                self.audios[user.id][2] = user.display_name
            if self.calculate_rms(data.pcm) > 1.2: #threshold for minimum volume
                self.audios[user.id][0].extend(data.pcm)
                self.audios[user.id][1] = time.time()

    async def save(self):
        print("saving")
        combind = AudioSegment.empty()
        for user,data in self.audios.items():
            print(f"saving {user}")
            audio_segment = AudioSegment(
                data=bytes(data[0]),
                sample_width=2,  # 16-bit audio
                frame_rate=self.sample_rate,  
                channels=self.channel  # Stereo
                )
            audio_segment.export(f'test\\{user}-{data[2]}.mp3', format='mp3',bitrate="64k")
            combind = combind.overlay(audio_segment,position=0)
        combind.export(f'test\\all.mp3', format='mp3',bitrate="64k")

    async def start(self):
        while self.run:
            for user,data in self.audios.items():
                current = time.time()
                last = data[1]
                diff = current - last
                if diff > 0.2 and diff < 10: # if not talk more than 10 sec will not record for storage safing
                    num_silence_frames = int(self.sample_rate   * 0.2)
                    silence_data = (b'\x00\x00' * self.channel )* num_silence_frames
                    self.audios[user][0].extend(silence_data)
                    print(f"insert silences for {data[2]}")
            await asyncio.sleep(0.2)
        
    @app_commands.command(name="record",description="record")
    async def record(self,interaction:discord.Interaction):
        vc = await interaction.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
        vc.listen(voice_recv.BasicSink(self.callback))
        self.task = self.bot.loop.create_task(self.start())
        await interaction.response.send_message("Record started",ephemeral=True)
        
    @app_commands.command(name="stop",description="stop record")
    async def stop(self,interaction:discord.Interaction):
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Record Stoped",ephemeral=True)
        self.run = False
        self.task.cancel()
        await self.save()
        self.audios.clear()

async def setup(bot):    
  await bot.add_cog(record(bot))  
