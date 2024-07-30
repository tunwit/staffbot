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

class record(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.sample_rate = 48000 
        self.channel = 2
        self.wav = None
        self.temp = {}
        self.task = None
        self.run = True
        self.text_channel = 979689935743377471
        self.start_session = None
        self.result = {}
        self.join_conference = []

    def callback(self,user:discord.Member, data: voice_recv.VoiceData):
        if user:
            if user.id not in self.temp:
                self.temp[user.id] = [tempfile.NamedTemporaryFile(),time.time(),None]
                self.temp[user.id][2] = user.display_name

            self.temp[user.id][0].write(data.pcm)
            self.temp[user.id][1] = time.time()


    async def save(self):
        merge = None
        _id = self.start_session.strftime("%d%m%Y%H%M%S")
        for user,data in self.temp.items():
            print(f"saving {user}")
            data[0].seek(0)
            audio = AudioSegment(
                data=bytes(data[0].read()),
                sample_width=2,  # 16-bit audio
                frame_rate=self.sample_rate,  
                channels=self.channel  # Stereo
                )
            chunks = split_on_silence(audio,min_silence_len=1000,keep_silence=2500)
            performanced = AudioSegment.empty()
            if chunks:
                for chunk in chunks:
                    performanced += chunk
            else:
                performanced = audio
                
            with io.BytesIO() as f:
                performanced.export(f, format='mp3',bitrate="64k")
                filename = f"{user}-{_id}.mp3"
                client.upload_fileobj(f, "csbot", filename)
                self.result[data[2]] = f"https://pub-cbd1e74ceb804677bfc1ed1e43a2600f.r2.dev/{filename}"
            if merge:
                merge = merge.overlay(audio)
                print(f"overlay {data[2]}")

            else:
                merge = audio
                print(f"base {data[2]}")

        with io.BytesIO() as f:
            merge.export(f, format='mp3',bitrate="64k")
            filename = f"all-{_id}.mp3"
            client.upload_fileobj(f, "csbot", filename)
            self.result['all'] = f"https://pub-cbd1e74ceb804677bfc1ed1e43a2600f.r2.dev/{filename}"

                
    async def start(self):
        while self.run:
            for user,data in self.temp.items():
                current = time.time()
                last = data[1]
                diff = current - last
                if (diff > 0.2 ): # if not talk more than 10 sec will not record for storage safing
                    num_silence_frames = int(self.sample_rate   * 0.2)
                    silence_data = (b'\x00\x00' * self.channel)* num_silence_frames
                    self.temp[user][0].write(silence_data)
                    print(f"insert silences for {data[2]}")
            await asyncio.sleep(0.2)
        
    @app_commands.command(name="record",description="record")
    async def record(self,interaction:discord.Interaction):
        vc = await interaction.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
        vc.listen(voice_recv.BasicSink(self.callback))
        self.start_session =datetime.now()
        self.task = self.bot.loop.create_task(self.start())
        for member in interaction.user.voice.channel.members:
            self.join_conference.append(member)
        await interaction.response.send_message("Record started",ephemeral=True)
        embed = discord.Embed(title="🔴 Tracking Quorum",description="This tracking is recording your voice 🎙️" ,color=0x6a208a)
        await interaction.followup.send(embed=embed)
        
    @app_commands.command(name="stop",description="stop record")
    async def stop(self,interaction:discord.Interaction):
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Record Stoped",ephemeral=True)
        self.run = False
        self.task.cancel()
        await self.save()
        for user,data in self.temp.items():
            data[0].close()
            print(f"close temp file for {data[2]}")
        self.temp.clear()
        print("done")

        channel = interaction.guild.get_channel(self.text_channel)
        if not channel:
            await interaction.followup.send("Channel not found")
            return
        
        messages = [f"Here is Conference record of **{self.start_session.strftime('%d/%m/%Y')}**"]
        for name,result in self.result.items():
            messages.append(f"\n**{name}** : {result}")
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
        embed = discord.Embed(title="Conference result",description="" ,color=0x6a208a)
        embed.add_field(name="Not Paticipate",value=f"`{p_m}`")
        await channel.send(embed=embed)
        gc.collect()

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
