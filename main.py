import discord
from discord.ext import commands
import os
from flask import Flask
import threading

TOKEN = os.getenv("TOKEN")
ALLOWED_IDS = [527857925981470730, 1079593002722406422, 972011985506033724]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

sumber_id, target_id, invite_id = None, None, None
aktif_mirror, aktif_invite = True, True
pesan_map, invites_cache = {}, {}

app = Flask(__name__)
@app.route('/')
def home():
    m = "MIRROR ON" if aktif_mirror else "MIRROR OFF"
    i = "INVITE ON" if aktif_invite else "INVITE OFF"
    return f"<h1>Jekkie V15 Render Gacor</h1><p>{m} | {i}</p>"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def embed(t,d,c=0x00FF88):
    e=discord.Embed(title=t,description=d,color=c)
    e.set_footer(text="Jekkie V15 Render")
    return e

def is_owner(i): return i.user.id in ALLOWED_IDS

@bot.event
async def on_ready():
    for guild in bot.guilds:
        try:
            bot.tree.copy_global_to_guild(guild=guild)
            await bot.tree.sync(guild=guild)
            invites_cache[guild.id] = await guild.invites()
        except: pass
    print(f"RENDER ONLINE {bot.user}")

@bot.event
async def on_member_join(member):
    if not aktif_invite: return
    try:
        guild=member.guild
        before=invites_cache.get(guild.id, [])
        after=await guild.invites()
        invites_cache[guild.id]=after
        inviter=None
        for b in before:
            for a in after:
                if b.code==a.code and b.uses < a.uses:
                    inviter=a.inviter; break
        total=sum(x.uses for x in after if inviter and x.inviter and x.inviter.id==inviter.id)
        ch_id=invite_id or sumber_id
        ch=bot.get_channel(ch_id) if ch_id else guild.system_channel
        if not ch: return
        em=discord.Embed(color=0x2F3136, description=f"-- welcome : {member.mention}\n-- invited by : {inviter.mention if inviter else 'Unknown'}\n-- total invite : {total}")
        em.set_author(name="Jekkie invite", icon_url=bot.user.display_avatar.url)
        em.set_thumbnail(url=member.display_avatar.url)
        await ch.send(embed=em)
    except Exception as e: print(e)

@bot.tree.command(name="setsumber")
async def setsumber(interaction: discord.Interaction, channel: discord.TextChannel):
    global sumber_id
    if not is_owner(interaction): return await interaction.response.send_message("Denied", ephemeral=True)
    sumber_id=channel.id; await interaction.response.send_message(embed=embed("SOURCE",f"{channel.mention}"), ephemeral=True)

@bot.tree.command(name="settarget")
async def settarget(interaction: discord.Interaction, channel: discord.TextChannel):
    global target_id
    if not is_owner(interaction): return await interaction.response.send_message("Denied", ephemeral=True)
    target_id=channel.id; await interaction.response.send_message(embed=embed("TARGET",f"{channel.mention}"), ephemeral=True)

@bot.tree.command(name="setinvite")
async def setinvite(interaction: discord.Interaction, channel: discord.TextChannel):
    global invite_id
    if not is_owner(interaction): return await interaction.response.send_message("Denied", ephemeral=True)
    invite_id=channel.id; await interaction.response.send_message(embed=embed("INVITE",f"{channel.mention}"), ephemeral=True)

@bot.tree.command(name="start_mirror")
async def start_mirror(interaction: discord.Interaction):
    global aktif_mirror
    if not is_owner(interaction): return await interaction.response.send_message("Denied", ephemeral=True)
    aktif_mirror=True; await interaction.response.send_message(embed=embed("MIRROR ON","Aktif"), ephemeral=True)

@bot.tree.command(name="stop_mirror")
async def stop_mirror(interaction: discord.Interaction):
    global aktif_mirror
    if not is_owner(interaction): return await interaction.response.send_message("Denied", ephemeral=True)
    aktif_mirror=False; await interaction.response.send_message(embed=embed("MIRROR OFF","Pause"), ephemeral=True)

@bot.tree.command(name="start_invite")
async def start_invite(interaction: discord.Interaction):
    global aktif_invite
    if not is_owner(interaction): return await interaction.response.send_message("Denied", ephemeral=True)
    aktif_invite=True; await interaction.response.send_message(embed=embed("INVITE ON","Aktif"), ephemeral=True)

@bot.tree.command(name="stop_invite")
async def stop_invite(interaction: discord.Interaction):
    global aktif_invite
    if not is_owner(interaction): return await interaction.response.send_message("Denied", ephemeral=True)
    aktif_invite=False; await interaction.response.send_message(embed=embed("INVITE OFF","Pause"), ephemeral=True)

@bot.tree.command(name="status")
async def status(interaction: discord.Interaction):
    if not is_owner(interaction): return await interaction.response.send_message("Denied", ephemeral=True)
    m="ON" if aktif_mirror else "OFF"; i="ON" if aktif_invite else "OFF"
    await interaction.response.send_message(embed=embed("STATUS",f"Mirror:{m} Invite:{i}"), ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot or not sumber_id or not target_id or not aktif_mirror: return
    if message.channel.id==sumber_id:
        tujuan=bot.get_channel(target_id)
        if not tujuan: return
        files=[await a.to_file() for a in message.attachments] if message.attachments else []
        ref=None
        if message.reference and message.reference.message_id in pesan_map:
            try: ref=(await tujuan.fetch_message(pesan_map[message.reference.message_id])).to_reference()
            except: pass
        if message.content or files:
            k=await tujuan.send(content=message.content or None, files=files or None, reference=ref)
            pesan_map[message.id]=k.id

threading.Thread(target=run_web).start()
bot.run(TOKEN)
