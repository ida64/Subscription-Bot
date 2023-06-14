import discord
import pymongo
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

mongo_client = pymongo.MongoClient(os.getenv("MONGO_CONN_URI"))
db = mongo_client[os.getenv("MONGO_DB_NAME")]

async def get_license(license):
    collection = db["users"]
    key = collection.find_one({"key": license})
    return key

async def reset_hardware_id(license):
    collection = db["users"]
    key = collection.find_one({"key": license})
    if key:
        key["hardware_reset"] = True
        collection.update_one({"key": license}, {"$set": key})
        return True
    else:
        return False

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

class HardwareIDModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="License Key", placeholder="Enter your license key", style=discord.InputTextStyle.short))

    async def callback(self, interaction: discord.Interaction):
        hardware_id = self.children[0].value
        key = await get_license(hardware_id)
        if key:
            if len(hardware_id) <= 25:
                if key["hardware_reset"]:
                    await interaction.response.send_message("Your Hardware ID has already been reset!", ephemeral=True)
                else:
                    await reset_hardware_id(hardware_id)
                    await interaction.response.send_message("Your Hardware ID has been reset!", ephemeral=True)
            else:
                await interaction.response.send_message("Invalid license key", ephemeral=True)
        else:
            await interaction.response.send_message("Invalid license key", ephemeral=True)

class LicenseInfoModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="License Key", placeholder="Enter your license key", style=discord.InputTextStyle.short))

    async def callback(self, interaction: discord.Interaction):
        license_key = self.children[0].value
        key = await get_license(license_key)
        if key:
            if len(license_key) <= 25:
                embed = discord.Embed(title=license_key, color=0x2F3136)
                embed.add_field(name="Product", value=key["associated_product"], inline=False)
                if key["redeemed"]:
                    activated_at = datetime.datetime.fromtimestamp(key["activated_at"]).strftime("%m/%d/%Y, %H:%M:%S")
                    embed.add_field(name="Activated At", value=activated_at, inline=False)

                    expiration = datetime.datetime.fromtimestamp(key["expiration"]).strftime("%m/%d/%Y, %H:%M:%S")
                    embed.add_field(name="Expiration", value=expiration, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("Invalid license key", ephemeral=True)

class InfoView(discord.ui.View):
    @discord.ui.button(label="🔑License Info", row=0)
    async def license_info_callback(self, button, interaction):
        await interaction.response.send_modal(LicenseInfoModal(title="View License Info"))

    @discord.ui.button(label="🖥️Hardware ID", row=0)
    async def hardware_id_callback(self, button, interaction):
        await interaction.response.send_modal(HardwareIDModal(title="Reset Hardware ID"))

bot.slash_command_auto_sync = True

@bot.slash_command(description="General utils for your subscription", guild_ids=[int(os.getenv("DISCORD_GUILD_ID"))])
async def info(ctx):
    await ctx.respond(view=InfoView(), ephemeral=True)

bot.add_application_command(info)

@bot.event
async def on_ready():
    print("Bot is ready!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/info for info"))
    
    # sync global
    await bot.sync_commands()

bot.run(os.getenv("DISCORD_BOT_TOKEN"))