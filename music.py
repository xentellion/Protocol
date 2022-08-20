import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import asyncio

class Song:
    def __init__(self, info):
        self.source = info['formats'][0]['url']
        self.title = info['title']
        self.time = int(info['duration'])

class ServerPlay:
    def __init__(self, channel:discord.VoiceChannel):
        self.channel = channel
        self.playlist = []

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False

        self.message = None

        # [channel, songs]
        self.music_queue = []

        self.YDL_OPTIONS = {
            'format': 'bestaudio', 
            'noplaylist':'True'
        }

        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            'options': '-vn'
        }

        self.vc = ""

    def search_youtube(self, url):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s"% url, download=False)['entries'][0]
                return Song(info)
            except:
                return 0

    def play_next(self):     
        if len(self.music_queue) > 0:
            # time = self.music_queue[0][0].time
            # await ctx.send(f"**Now playing:** {self.music_queue[0][0].title} `[{time//60}:{time%60}]`")
            self.music_queue.pop(0)
            self.is_playing = True
            
            # get first url may actually pop up
            m_url = self.music_queue[0][0].source

            #play actually
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            self.vc.source = discord.PCMVolumeTransformer(self.vc.source)
            self.vc.source.volume = 0.10
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing= True

            m_url = self.music_queue[0][0].source

            # connect to channel or move
            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])
            time = self.music_queue[0][0].time
            await ctx.send(f"**Now playing:** {self.music_queue[0][0].title} `[{time//60}:{time%60}]`")
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            self.vc.source = discord.PCMVolumeTransformer(self.vc.source)
            self.vc.source.volume = 0.10
        else:
            self.is_playing = False
    
    @commands.command(aliases=["play"], help="Plays a selected song from youtube")
    async def p(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send('Connect to a voice channel')
            return
        async with ctx.typing():
            song = self.search_youtube(query)
            if song == 0:
                await ctx.send('Cannot download the song')
            else:
                self.music_queue.append([song, voice_channel])
                time = self.music_queue[0][0].time
                await ctx.send(f'🎵 **{self.music_queue[0][0].title}** `[{time//60}:{time%60}]` is added to the queue by **{ctx.message.author.name}**')
                if not self.is_playing:
                    await self.play_music(ctx)

    @commands.command(aliases=["queue"], help="Displays the current songs in queue")
    async def q(self, ctx):
        songs = ""
        for i in range (0, len(self.music_queue)):
            songs += self.music_queue[i][0].title + '\n'

        if songs != "":
            await ctx.send(songs)
        else:
            await ctx.send('Queue is empty')

    @commands.command(help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != "" and self.vc:
            self.vc.stop()
            if len(self.music_queue) > 0:
                await self.play_music(ctx)
            else:
                await ctx.send('Playlist is over')
            
    @commands.command(aliases=["disconnect"], help="Disconnecting bot from VC")
    async def dc(self, ctx):
        await self.vc.disconnect()

    @commands.command(help='This command pauses the song')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is paused")

    @commands.command(help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use play_song command")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
        if voice_state is None:
            return 
        elif len(voice_state.channel.members) == 1:
            self.music_queue = []
            await voice_state.disconnect()

def setup(bot):
    bot.add_cog(Music(bot))
