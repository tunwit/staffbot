import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import voice_recv
from pydub.silence import split_on_silence
from pydub import AudioSegment
import asyncio
import numpy as np
import time
import tempfile
import gc 
from setup import client ,resource
import io
from datetime import datetime
import threading
import os 
import subprocess
from ffmpeg.asyncio import FFmpeg

class record(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.sample_rate = 48000 
        self.channel = 2
        self.temp = {}
        self.task = None
        self.run = True
        self.text_channel = 1267841264577941674
        self.start_session = None
        self.result = {}
        self.join_conference = []
        self.pause = False

    def callback(self,user:discord.Member, data: voice_recv.VoiceData):
        if self.pause:
            return
        if not self.start_session:
            self.start_session =datetime.now()
        if user:
            if user.id not in self.temp:
                self.temp[user.id] = [open(f"temp/{user.id}","wb"),time.time(),time.time(),None] #tempfile,firsttimetalk,recenttalk,name
                self.temp[user.id][3] = user.display_name

            self.temp[user.id][0].write(data.pcm)
            self.temp[user.id][2] = time.time()

    def process(self,_id,user,data):
        print(f"saving {user}")
        data[0].seek(0)
        audio = AudioSegment(
            data=bytes(data[0].read()),
            sample_width=2,  # 16-bit audio
            frame_rate=self.sample_rate,  
            channels=self.channel  # Stereo
            )
        print(f"spliting {data[3]}")
        chunks = split_on_silence(audio,keep_silence=2500,min_silence_len=1)
        performanced = AudioSegment.empty()
        if chunks:
            for chunk in chunks:
                performanced += chunk
        else:
            performanced = audio
        print(f"done spliting {data[3]}")
        with io.BytesIO() as f:
            performanced.export(f, format='mp3',bitrate="64k")
            filename = f"{user}-{_id}.mp3"
            print(f"uploading {data[3]}")
            client.upload_fileobj(f, "csbot", filename)
            self.result[user] = [f"https://pub-cbd1e74ceb804677bfc1ed1e43a2600f.r2.dev/{filename}",data[3]]
            print(f"done uploading {data[3]}")

    def process_all(self,_id):
        merge = None
        print(f"saving all")
        for user,data in self.temp.items():
            print(f"merging all {data[3]}")
            data[0].seek(0)
            audio = AudioSegment(
                data=bytes(data[0].read()),
                sample_width=2,  # 16-bit audio
                frame_rate=self.sample_rate,  
                channels=self.channel  # Stereo
                )
            processed = AudioSegment.silent(duration=((data[1]-self.start_session.timestamp()-1)*1000),frame_rate=self.sample_rate)+audio # -1 for compensate delay
            if merge:
                merge = merge.overlay(processed)
            else:
                merge = processed

        with io.BytesIO() as f:
            merge.export(f, format='mp3',bitrate="64k")
            filename = f"all-{_id}.mp3"
            print(f"uploading all")
            client.upload_fileobj(f, "csbot", filename)
            self.result['000'] = [f"https://pub-cbd1e74ceb804677bfc1ed1e43a2600f.r2.dev/{filename}","all"]


    async def save(self,interaction:discord.Interaction):
        _id = self.start_session.strftime("%d%m%Y%H%M%S")
        workers = []
        for user,data in self.temp.items():
            ffmpeg = (
                FFmpeg()
                .option("y")
                .input(f"temp/{user}",
                    f="s16le",
                    ar="48000",
                    ac = "2")
                .output(f"temp/{user}-{time.time()}.mp3",
                        {
                        "filter_complex":"silenceremove=stop_threshold=-50dB:stop_duration=2:stop_periods=-1"
                        })
                    )
            
            compensate = data[1] - self.start_session 
            
            ffmpeg_all_preparation = (
                FFmpeg()
                .option("y")
                .input(f"temp/{user}",
                    f="s16le",
                    ar="48000",
                    ac = "2")
                .output(f"temp/{user}",
                        {
                        "filter_complex":f"adelay={compensate}|{compensate}"
                        })
                    )
            try:
                await ffmpeg.execute()
                await ffmpeg_all_preparation.execute()
            except:
                print(f"There is an error while processing {data[3]}")
                continue
            print(f"done {user}")

        for user,data in self.temp.items():
            pass

            # thread = threading.Thread(target=self.process, args=(_id,user,data,))
            # thread.start()
            # workers.append(thread)
        return
        thread = threading.Thread(target=self.process_all, args=(_id,))
        thread.start()
        workers.append(thread)
        for worker in workers:
            worker.join()

        for user,data in self.temp.items():
            data[0].close()
            print(f"close temp file for {data[3]}")
        self.temp.clear()
        print("done")

        channel = interaction.guild.get_channel(self.text_channel)
        if not channel:
            await interaction.followup.send("Channel not found sending in defualt channel")
            channel = interaction.channel
        
        messages = [f"Here is Conference record of **{self.start_session.strftime('%d/%m/%Y')} {self.start_session.strftime('%H:%M')}-{datetime.now().strftime('%H:%M')}**"]
        for name,result in self.result.items():
            messages.append(f"\n**{result[1]}** : {result[0]}")
        self.result.clear()
        message = ''.join(messages)
        await channel.send(message)
        notpaticipate = []
        counter = 1
        for member in interaction.guild.members:
            if member not in self.join_conference:
                notpaticipate.append(f" {counter}. {member.display_name} ")
                counter += 1
        p_m = '\n'.join(notpaticipate)
        embed = discord.Embed(title="Conference result",description=f'Thankyou for participate this conference during\n{self.start_session.strftime("%H:%M")}-{datetime.now().strftime("%H:%M")}' ,color=0x6a208a)
        embed.add_field(name="Not Paticipate",value=f"`{p_m}`")
        await channel.send(embed=embed)
        await channel.send("------------------------------------")
        gc.collect()

                
    async def start(self):
        while self.run:
            await asyncio.sleep(0.2)
            if self.pause:
                continue
            for user,data in self.temp.items():
                current = time.time()
                last = data[2]
                diff = current - last
                if (diff > 0.2 ): # if not talk more than 10 sec will not record for storage safing
                    num_silence_frames = int(self.sample_rate   * 0.2)
                    silence_data = (b'\x00\x00' * self.channel)* num_silence_frames
                    self.temp[user][0].write(silence_data)
                    print(f"insert silences for {data[3]} {time.time() - self.start_session.timestamp()}")
        
    @app_commands.command(name="record",description="record")
    async def record(self,interaction:discord.Interaction):
        self.__init__(self.bot)
        vc = await interaction.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
        vc.listen(voice_recv.BasicSink(self.callback))
        self.task = self.bot.loop.create_task(self.start())
        for member in interaction.user.voice.channel.members:
            self.join_conference.append(member)
        await interaction.response.send_message("Record started",ephemeral=True)
        embed = discord.Embed(title="🔴 Tracking Quorum",description="This tracking is recording your voice 🎙️" ,color=0x6a208a)
        await interaction.followup.send(embed=embed)
        
    @app_commands.command(name="stop",description="stop record")
    async def stop(self,interaction:discord.Interaction):
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Record Stopped",ephemeral=True)
        self.run = False
        self.task.cancel()
        self.task = None
        self.bot.loop.create_task(self.save(interaction))

    @app_commands.command(name="absent",description="for known absent result in not showing in not paticipate")
    async def absent(self,interaction:discord.Interaction,member:discord.Member):
        if not self.run:
            await interaction.response.send_message("This command only avaliable during Conference session",ephemeral=True)
            return
        self.join_conference.append(member)
        await interaction.response.send_message(f"Success fully add {member.name} to absend list",ephemeral=True)

    @app_commands.command(name="toggle_pause",description="toggle pause record")
    async def toggle_pause(self,interaction:discord.Interaction):
        if self.pause:
            self.pause = False
        else:
            self.pause = True
        await interaction.response.send_message(f"Conference are now {'recording' if not self.pause else 'pause'}")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member:discord.Member, before, after): 
        if member == self.bot.user:
           return
        if before.channel == None and after.channel != None: #None -> join
            self.join_conference.append(member)
        elif before.channel != None and after.channel != None and before.channel != after.channel: #Join -> Join (move to)
            self.join_conference.append(member)
        else:
            return

async def setup(bot):    
  await bot.add_cog(record(bot))  
