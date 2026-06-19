import os
import asyncio
import discord
from discord.ext import commands
from pathlib import Path


class DiscordReportClient:
    """Sender stock analysis reports til Discord"""

    def __init__(self):
        self.token = os.getenv("DISCORD_BOT_TOKEN")
        self.channel_name = "reports"
        self.intents = discord.Intents.default()
        self.client = discord.Client(intents=self.intents)

    async def send_report_to_discord(self, ticker: str, filename: str) -> bool:
        """
        Sender rapport fil til Discord kanal
        
        Args:
            ticker: Stock ticker symbol
            filename: Sti til rapport filen
            
        Returns:
            True hvis succesfuld, False hvis fejl
        """
        if not self.token:
            print("Fejl: DISCORD_BOT_TOKEN er ikke sat i environment variables")
            return False

        if not os.path.exists(filename):
            print(f"Fejl: Rapport fil ikke fundet: {filename}")
            return False

        try:
            @self.client.event
            async def on_ready():
                """Kører når botten er forbundet"""
                try:
                    # Find kanal
                    channel = discord.utils.get(
                        self.client.get_all_channels(),
                        name=self.channel_name
                    )

                    if not channel:
                        print(f"Fejl: Kanal '{self.channel_name}' ikke fundet")
                        await self.client.close()
                        return

                    # Læs rapport fil
                    with open(filename, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Split hvis for lang (Discord limit: 2000 chars per message)
                    if len(content) > 1900:
                        # Send som fil upload
                        file = discord.File(filename, filename=Path(filename).name)
                        await channel.send(
                            f"📊 **Stock Analyse Report** - {ticker}",
                            file=file
                        )
                    else:
                        # Send som markdown
                        await channel.send(f"```markdown\n{content}\n```")

                    print(f"✅ Rapport sendt til Discord: #{channel.name}")
                    await self.client.close()

                except Exception as e:
                    print(f"Fejl ved sending af rapport: {e}")
                    await self.client.close()

            await self.client.start(self.token)
            return True

        except Exception as e:
            print(f"Fejl ved forbindelse til Discord: {e}")
            return False


def send_report_async(ticker: str, filename: str) -> bool:
    """
    Wrapper function til at sende rapport asynchront
    
    Args:
        ticker: Stock ticker symbol
        filename: Sti til rapport filen
        
    Returns:
        True hvis succesfuld, False hvis fejl
    """
    discord_client = DiscordReportClient()

    # Kør async function
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(
        discord_client.send_report_to_discord(ticker, filename)
    )
