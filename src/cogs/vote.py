import discord
from discord.ext import commands
from discord import app_commands

EMOJIS = {
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
    9: "9️⃣",
    10: "🔟"}

CONVERT_EMOJIS = {
    "1️⃣": 1,
    "2️⃣": 2,
    "3️⃣": 3,
    "4️⃣": 4,
    "5️⃣": 5,
    "6️⃣": 6,
    "7️⃣": 7,
    "8️⃣": 8,
    "9️⃣": 9,
    "🔟": 10
}


class VoteView(discord.ui.View):
    def __init__(self,callback):
        super().__init__(timeout=None)
        self.add_item(EndButton(callback))

class EndButton(discord.ui.Button):
    def __init__(self, on_click ):
        super().__init__(label="Endvote", style=discord.ButtonStyle.red)
        self.on_click  = on_click 

    async def callback(self , interaction: discord.Interaction):
        await self.on_click(interaction)

    
class recordAPI(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(name="vote",description="setup vote")
    @app_commands.describe(
        title="Title of the vote",
        choices="Choices for the vote, separated by commas"
    )
    async def vote(self,interaction:discord.Interaction,title:str,choices: str):
        await interaction.response.defer()
        # Split the choices by comma and strip whitespace
        choices = [ f"{EMOJIS[i+1]} : {choice.strip()}" for i,choice in enumerate(choices.split(",")) if choice.strip()]
        word = ""
        # Create a string with the choices
        for i, choice in enumerate(choices):
            word += f"{choice}\n\n"

        embed = discord.Embed(
            title=title,
            description=f"Please vote for your choice.\n\n{word.strip()}",
            color=discord.Color.blue()
        )

        async def callback(interaction: discord.Interaction):
            msg = await interaction.channel.fetch_message(interaction.message.id)
            embed = discord.Embed(
                title="Vote result",
                color=discord.Color.blue()
            )

            highest = max(msg.reactions, key=lambda r: r.count)

            ties = [r for r in msg.reactions if r.count == highest.count]
            if len(ties) > 1:
                #tie
                embed.description = "All Vote is tie"
            else:
                # Get the choice with the highest count
                winner = ties[0]
                embed.description = f"Winner is **{choices[CONVERT_EMOJIS[winner.emoji]-1].split(':')[1].strip()}** with {winner.count} votes"
            await interaction.message.clear_reactions()
            await interaction.response.edit_message(embed=embed,view=None)
        votepanel:discord.WebhookMessage = await interaction.followup.send(embed=embed,view=VoteView(callback))

        # Add reactions to the message
        for i in range(1, len(choices) + 1):
            await votepanel.add_reaction(EMOJIS[i])

        
       

async def setup(bot):    
  await bot.add_cog(recordAPI(bot))  
