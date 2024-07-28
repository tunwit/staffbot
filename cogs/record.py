import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import voice_recv
import wave
from pydub import AudioSegment
import asyncio
import numpy as np
import time
import tempfile
import gc 
from setup import client ,resource
import io
from datetime import datetime

class record(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.sample_rate = 48000 
        self.channel = 2
        self.wav = None
        self.audios = {
        }
        self.temp = {}
        self.task = None
        self.run = True
        self.text_channel = 979689935743377471
        self.start_session = None
        self.result = {}

    def callback(self,user:discord.Member, data: voice_recv.VoiceData):
        if user:
            if user.id not in self.audios:
                self.temp[user.id] = [tempfile.NamedTemporaryFile(),time.time(),None]
                self.temp[user.id][2] = user.display_name

                self.audios[user.id] = [tempfile.NamedTemporaryFile(),time.time(),None]
                self.audios[user.id][2] = user.display_name
            self.temp[user.id][0].write(data.pcm)
            self.audios[user.id][0].write(data.pcm)
            self.audios[user.id][1] = time.time()

    async def save(self):
        for user,data in self.audios.items():
            print(f"saving {user}")
            data[0].seek(0)
            audio_segment = AudioSegment(
                data=bytes(data[0].read()),
                sample_width=2,  # 16-bit audio
                frame_rate=self.sample_rate,  
                channels=self.channel  # Stereo
                )
            with io.BytesIO() as f:
                audio_segment.export(f, format='mp3',bitrate="64k")
                _id = self.start_session.strftime("%d%m%Y%H%M%S")
                filename = f"{user}-{_id}.mp3"
                client.upload_fileobj(f, "csbot", filename)
                self.result[data[2]] = f"https://pub-cbd1e74ceb804677bfc1ed1e43a2600f.r2.dev/{filename}"
        
        await self.merge()
        
    async def merge(self):
        self.temp[list(self.temp)[0]][0].seek(0)
        merged = AudioSegment(
                data=bytes(self.temp[list(self.temp)[0]][0].read()),
                sample_width=2,  # 16-bit audio
                frame_rate=self.sample_rate,  
                channels=self.channel  # Stereo
                )
        for user,data in self.temp.items():
            print(f"merging {data[2]}")
            data[0].seek(0)
            audio_segment = AudioSegment(
                data=bytes(data[0].read()),
                sample_width=2,  # 16-bit audio
                frame_rate=self.sample_rate,  
                channels=self.channel  # Stereo
                )
            merged = merged.overlay(audio_segment)
        
        with io.BytesIO() as f:
                merged.export(f, format='mp3',bitrate="64k")
                _id = self.start_session.strftime("%d%m%Y%H%M%S")
                filename = f"all-{_id}.mp3"
                client.upload_fileobj(f, "csbot", filename)
                self.result['all'] = f"https://pub-cbd1e74ceb804677bfc1ed1e43a2600f.r2.dev/{filename}"
    
    async def start(self):
        while self.run:
            for user,data in self.audios.items():
                current = time.time()
                last = data[1]
                diff = current - last
                if (diff > 0.2 and diff < 10): # if not talk more than 10 sec will not record for storage safing
                    num_silence_frames = int(self.sample_rate   * 0.2)
                    silence_data = (b'\x00\x00' * self.channel)* num_silence_frames
                    self.audios[user][0].write(silence_data)
                    print(f"insert silences for {data[2]}")
                if diff > 0.2:
                    self.temp[user][0].write(silence_data)

            await asyncio.sleep(0.2)
        
    @app_commands.command(name="record",description="record")
    async def record(self,interaction:discord.Interaction):
        vc = await interaction.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
        vc.listen(voice_recv.BasicSink(self.callback))
        self.start_session =datetime.now()

        self.task = self.bot.loop.create_task(self.start())

        guild = interaction.guild
        channel = guild.get_channel(self.channel)
        # channel.fetch_message()
        
        await interaction.response.send_message("Record started",ephemeral=True)
        
    @app_commands.command(name="stop",description="stop record")
    async def stop(self,interaction:discord.Interaction):
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Record Stoped",ephemeral=True)
        self.run = False
        self.task.cancel()
        await self.save()
        self.audios.clear()
        self.temp.clear()
        for user,data in self.temp.items():
            data[0].close()
            print(f"close temp file for {data[2]}")
        print("done")
  
        gc.collect()

async def setup(bot):    
  await bot.add_cog(record(bot))  
