import discord
from discord.ext import commands
from youtube_dl import YoutubeDL

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False

        # [song, channel]
        self.music_queue = []

        self.YDL_OPTIONS = {
            'format': 'bestaudio/best', 
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
            except:
                return 0
        
        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue > 0):
            self.is_playing = True

            # get first url may actually pop up
            m_url = self.music_queue[0][0]['source']

            self.music_queue.pop(0)

            #play actually
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing= True

            m_url = self.music_queue[0][0]['source']

            # connect to channel or move
            if self.vc == '' or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
            else:
                self.vc = await self.bot.move_to(self.music_queue[0][1])

            print(self.music_queue)

            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda: self.play_next())
        else:
            self.is_playing = False
    
    @commands.command(name="play", help="Plays a selected song from youtube")
    async def p(self, ctx, *args):
        query = " ".join(args)
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send('Connect to a voice channel')
        else:
            song = self.search_youtube(query)
            if song == 0:
                await ctx.send('Cannot download the song')
            else:
                await ctx.send('Song added to the queue')
                self.music_queue.append([song, voice_channel])

                if not self.is_playing:
                    await self.play_music()

    @commands.command(name="queue", help="Displays the current songs in queue")
    async def q(self, ctx):
        songs = ""
        for i in range (0, len(self.music_queue)):
            songs += self.music_queue[i][0]['title'] + '\n'
        print(songs)

        if songs != "":
            await ctx.send(songs)
        else:
            await ctx.send('Queue is empty')

    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != "" and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music()
            
    @commands.command(name="disconnect", help="Disconnecting bot from VC")
    async def dc(self, ctx):
        await self.vc.disconnect()

    @commands.command(name='pause', help='This command pauses the song')
    async def pause(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is paused")

    @commands.command(name='resume', help='Resumes the song')
    async def resume(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use play_song command")


def setup(bot):
    bot.add_cog(Music(bot))
