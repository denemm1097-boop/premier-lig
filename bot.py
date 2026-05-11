import discord
from discord.ext import commands
import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

# ────────────────────────────────────────────────────────────
# Config
# ────────────────────────────────────────────────────────────
PREFIX = "."

ROLES = {
    "FUTBOLCU":        1502440606239035483,
    "TEKNIK_DIREKTOR": 1502440639873159210,
    "UYE":             1502440854298562612,
    "BAYAN_UYE":       1502440841925361734,
    "DEGER_YETKILISI": 1502437247247581294,
    "KAYIT_YETKILISI": 1502437233821483080,
    "BOT_COMMANDER":   1502440977615290530,
    "MODERATOR":       1502437113038110803,
    "TAKIM_KAPTANI":   1502440820031356958,
    "OWNER":           1502436551223935149,
    "KAYITSIZ":        1502453206595276942,
}

CHANNELS = {
    "DEGER_LOG":       1502434477245202483,
    "GUVENLIK_LOG":    1502434415698247804,
    "ANTRENMAN":       1502434504361644082,
    "PENALTI":         1502434507020697804,
    "DEGER_BILDIRIM":  1502434475404169327,
    "TRANSFER_LOG":    1502434510292127845,
    "KAYIT_BILDIRIM":  1502434430772445336,
    "KAYIT_LOG":       1502434480927936753,
}

ROLE_HIERARCHY = [
    1502436551223935149,  # OWNER
    1502440977615290530,  # BOT_COMMANDER
    1502437113038110803,  # MODERATOR
    1502437247247581294,  # DEGER_YETKILISI
    1502437233821483080,  # KAYIT_YETKILISI
    1502440820031356958,  # TAKIM_KAPTANI
    1502440639873159210,  # TEKNIK_DIREKTOR
    1502440606239035483,  # FUTBOLCU
    1502440854298562612,  # UYE
    1502440841925361734,  # BAYAN_UYE
    1502453206595276942,  # KAYITSIZ
]

# ────────────────────────────────────────────────────────────
# Data manager
# ────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def load_data(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(filename: str, data: dict):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ────────────────────────────────────────────────────────────
# Hierarchy helpers
# ────────────────────────────────────────────────────────────
def get_role_level(member: discord.Member) -> int:
    for i, role_id in enumerate(ROLE_HIERARCHY):
        if any(r.id == role_id for r in member.roles):
            return i
    return len(ROLE_HIERARCHY)

def is_higher_than(executor: discord.Member, target: discord.Member) -> bool:
    return get_role_level(executor) < get_role_level(target)

def has_role(member: discord.Member, role_key: str) -> bool:
    return any(r.id == ROLES[role_key] for r in member.roles)

# ────────────────────────────────────────────────────────────
# Duration helpers
# ────────────────────────────────────────────────────────────
import re
import datetime

def parse_duration(s: str) -> int | None:
    """Returns milliseconds or None."""
    m = re.match(r"^(\d+)(d|h|m|s)$", s, re.IGNORECASE)
    if not m:
        return None
    val = int(m.group(1))
    unit = m.group(2).lower()
    mult = {"s": 1000, "m": 60_000, "h": 3_600_000, "d": 86_400_000}
    return val * mult[unit]

def format_duration(ms: int) -> str:
    d = ms // 86_400_000
    ms %= 86_400_000
    h = ms // 3_600_000
    ms %= 3_600_000
    m = ms // 60_000
    ms %= 60_000
    s = ms // 1000
    parts = []
    if d: parts.append(f"{d} gün")
    if h: parts.append(f"{h} saat")
    if m: parts.append(f"{m} dakika")
    if s: parts.append(f"{s} saniye")
    return " ".join(parts) or "0 saniye"

# ────────────────────────────────────────────────────────────
# Bot setup
# ────────────────────────────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ────────────────────────────────────────────────────────────
# EVENTS
# ────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"✅ Bot aktif: {bot.user}")
    print(f"📊 {len(bot.guilds)} sunucuda hizmet veriliyor.")

@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    import time
    
    kayitsiz_role = guild.get_role(ROLES["KAYITSIZ"])
    if kayitsiz_role:
        try:
            await member.add_roles(kayitsiz_role)
        except Exception:
            pass

    dm_embed = discord.Embed(
        title="⚽ Şanlı Premier Lig'e Hoş Geldin!",
        color=0x5865F2,
        description=(
            f"Merhaba **{member.display_name}**! 👋\n\n"
            "**Şanlı Premier Lig RP** sunucusuna hoş geldin!\n\n"
            "📋 Sunucuya giriş yapabilmek için kayıt yetkililerini beklemelisin.\n"
            "💬 Kayıt kanalında seni en kısa sürede karşılayacaklar.\n\n"
            f"⚽ Sunucumuzda {guild.member_count}. üye olarak katıldın!\n\n"
            "🏆 Seni aramızda görmekten mutluluk duyuyoruz!"
        )
    )
    dm_embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    dm_embed.add_field(name="📌 Sunucu", value=guild.name, inline=True)
    dm_embed.add_field(name="👥 Toplam Üye", value=str(guild.member_count), inline=True)
    dm_embed.add_field(name="📅 Katılım", value=f"<t:{int(time.time())}:F>", inline=True)
    try:
        await member.send(embed=dm_embed)
    except Exception:
        pass

    kayit_channel = guild.get_channel(CHANNELS["KAYIT_BILDIRIM"])
    if not kayit_channel:
        return

    pending = load_data("pendingRegistrations.json")
    pending[str(member.id)] = {
        "userId": member.id,
        "userTag": str(member),
        "joinedAt": int(time.time() * 1000),
        "claimedBy": None,
        "registered": False,
    }
    save_data("pendingRegistrations.json", pending)

    button = discord.ui.Button(
        label="📋 Kaydı Üstlen",
        style=discord.ButtonStyle.primary,
        custom_id=f"kayit_ustlen_{member.id}"
    )
    view = discord.ui.View(timeout=None)
    view.add_item(button)

    join_embed = discord.Embed(
        title="🆕 Yeni Üye Katıldı!",
        color=0x00B300,
        description=(
            f"**{member.mention}** sunucuya katıldı!\n\n"
            f"Kaydı üstlen ve işlemi tamamla."
        )
    )
    join_embed.set_thumbnail(url=member.display_avatar.url)
    join_embed.add_field(name="👤 Kullanıcı", value=f"{member.mention} ({member})", inline=True)
    join_embed.add_field(name="📅 Katılım", value=f"<t:{int(time.time())}:R>", inline=True)
    join_embed.add_field(name="👥 Sunucu Üye Sayısı", value=str(guild.member_count), inline=True)

    # ✅ DÜZELTME: Artık sadece 1 mesaj atılıyor
    await kayit_channel.send(
        content=f"<@&{ROLES['KAYIT_YETKILISI']}>",
        embed=join_embed,
        view=view
    )


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    import time

    # AFK kontrolü
    afk_data = load_data("afk.json")
    user_id = str(message.author.id)

    if user_id in afk_data:
        afk_info = afk_data.pop(user_id)
        save_data("afk.json", afk_data)
        duration = format_duration(int(time.time() * 1000) - afk_info["since"])
        embed = discord.Embed(
            color=0x5865F2,
            description=f"👋 Hoş geldin! **{duration}** süre AFK'daydın.\n**Sebep:** {afk_info['reason']}"
        )
        try:
            await message.reply(embed=embed)
        except Exception:
            pass

    # Mention'da AFK kontrolü
    for mentioned in message.mentions:
        mid = str(mentioned.id)
        if mid in afk_data:
            afk_info = afk_data[mid]
            duration = format_duration(int(time.time() * 1000) - afk_info["since"])
            embed = discord.Embed(
                color=0xFFA500,
                description=(
                    f"💤 <@{mid}> şu an AFK.\n"
                    f"**Sebep:** {afk_info['reason']}\n"
                    f"**Süre:** {duration} önce başladı"
                )
            )
            try:
                await message.reply(embed=embed)
            except Exception:
                pass

    # Selam cevabı
    lower = message.content.lower().strip()
    if lower in ("sa", "selamınaleyküm", "selam", "s.a"):
        try:
            await message.reply(
                f"Ve Aleykümselam Hoşgeldin <a:PL_lop:1502653089688191036>\n"
                f"<#{CHANNELS['ANTRENMAN']}> Kanalından Antrenman Yapmayı Unutmayınız"
            )
        except Exception:
            pass

    await bot.process_commands(message)


@bot.event
async def on_message_delete(message: discord.Message):
    if not message.author or message.author.bot:
        return
    if not message.content:
        return
    import time
    snipes = load_data("snipe.json")
    snipes[str(message.channel.id)] = {
        "content": message.content,
        "authorId": message.author.id,
        "authorTag": str(message.author),
        "deletedAt": int(time.time() * 1000),
    }
    save_data("snipe.json", snipes)


@bot.event
async def on_audit_log_entry_create(entry: discord.AuditLogEntry):
    SUSPICIOUS = [
        discord.AuditLogAction.member_role_update,
        discord.AuditLogAction.member_update,
        discord.AuditLogAction.role_update,
        discord.AuditLogAction.ban,
        discord.AuditLogAction.kick,
    ]
    if entry.action not in SUSPICIOUS:
        return
    if not entry.user or entry.user.bot:
        return

    guild = entry.guild if hasattr(entry, "guild") else None
    if guild is None:
        return

    executor = guild.get_member(entry.user.id)
    if not executor:
        return
    if has_role(executor, "OWNER"):
        return

    async def punish(target_id, action_name, note):
        log_ch = guild.get_channel(CHANNELS["GUVENLIK_LOG"])
        roles_to_remove = [r for r in executor.roles if r.id != guild.id]
        try:
            await executor.remove_roles(*roles_to_remove, reason="Güvenlik sistemi: şüpheli işlem")
        except Exception:
            pass
        if log_ch:
            embed = discord.Embed(
                title="🚨 ACİL DURUM — GÜVENLİK ALARMI",
                color=0xFF0000,
                description=f"<@&{ROLES['OWNER']}> ACİL DURUM!"
            )
            embed.add_field(name="👤 İşlemi Yapan", value=f"{executor.mention} ({executor})", inline=True)
            embed.add_field(name="🎯 Hedef", value=f"<@{target_id}>" if target_id else "Bilinmiyor", inline=True)
            embed.add_field(name="⚠️ İşlem", value=action_name, inline=True)
            embed.add_field(name="📝 Not", value=note, inline=False)
            embed.add_field(name="🔴 Sonuç", value="Kullanıcının tüm rolleri çekildi.", inline=False)
            await log_ch.send(embed=embed)

    if entry.action == discord.AuditLogAction.member_role_update:
        target = guild.get_member(entry.target.id) if entry.target else None
        if target and executor.id == target.id:
            await punish(target.id, "Kendine rol verdi", "Kendine rol vermeye çalıştı.")
        elif target:
            exec_level = get_role_level(executor)
            tgt_level = get_role_level(target)
            if exec_level >= tgt_level and not has_role(executor, "OWNER"):
                await punish(target.id, "Yetkisiz rol atadı", "Kendinden üst/eşit birine rol vermeye çalıştı.")

    elif entry.action == discord.AuditLogAction.role_update:
        await punish(None, "Rol izni değiştirildi", "Bir rolün izinlerini değiştirdi.")

    elif entry.action == discord.AuditLogAction.member_update:
        if entry.target and executor.id != entry.target.id:
            target = guild.get_member(entry.target.id)
            if target:
                exec_level = get_role_level(executor)
                tgt_level = get_role_level(target)
                if exec_level >= tgt_level:
                    await punish(target.id, "Yetkisiz isim değişikliği", "Kendinden üst/eşit birinin ismini değiştirmeye çalıştı.")


# ────────────────────────────────────────────────────────────
# INTERACTION HANDLER (buttons & modals)
# ────────────────────────────────────────────────────────────

@bot.event
async def on_interaction(interaction: discord.Interaction):
    import time, urllib.parse

    if interaction.type == discord.InteractionType.component:
        cid = interaction.data["custom_id"]
        member = interaction.user
        guild = interaction.guild

        # ── Kayıt üstlen ──
        if cid.startswith("kayit_ustlen_"):
            if not has_role(member, "KAYIT_YETKILISI"):
                return await interaction.response.send_message("❌ Bu butonu sadece **Kayıt Yetkilileri** kullanabilir.", ephemeral=True)

            user_id = cid.split("_")[2]
            pending = load_data("pendingRegistrations.json")
            entry = pending.get(user_id)
            if not entry:
                return await interaction.response.send_message("❌ Bu kayıt artık geçerli değil.", ephemeral=True)
            if entry.get("claimedBy"):
                return await interaction.response.send_message(f"❌ Bu kayıt zaten <@{entry['claimedBy']}> tarafından üstlenildi.", ephemeral=True)

            entry["claimedBy"] = member.id
            entry["claimedAt"] = int(time.time() * 1000)
            save_data("pendingRegistrations.json", pending)

            # 5 dakikada otomatik serbest bırakma
            async def expire_task():
                await asyncio.sleep(300)  # 5 dakika
                fresh = load_data("pendingRegistrations.json")
                e = fresh.get(user_id)
                if e and e.get("claimedBy") == member.id and not e.get("registered"):
                    e["claimedBy"] = None
                    e.pop("claimedAt", None)
                    save_data("pendingRegistrations.json", fresh)
                    try:
                        await member.send(f"⚠️ Üstlendiğin kayıt (**{e.get('userTag')}**) 5 dakika içinde tamamlanmadığı için serbest bırakıldı.")
                    except Exception:
                        pass
            asyncio.create_task(expire_task())

            embed = discord.Embed(
                title="✅ Kayıt Üstlenildi",
                color=0x00B300,
                description=(
                    f"<@{user_id}> kullanıcısının kaydı **{member.display_name}** tarafından üstlenildi.\n\n"
                    "5 dakika içinde `.k <isim>` komutuyla kayıt yapılmalıdır."
                )
            )
            return await interaction.response.edit_message(embed=embed, view=None)

        # ── Kayıt tür butonları ──
        if (cid.startswith("kayit_") and
                not cid.startswith("kayit_ustlen_") and
                not cid.startswith("kayit_iptal")):
            parts = cid.split("_")
            reg_type = parts[1]
            target_id = parts[2]
            isim = "_".join(parts[3:]).replace("_", " ")

            pending = load_data("pendingRegistrations.json")
            claimed = next(
                (e for e in pending.values() if e["userId"] == int(target_id) and e.get("claimedBy") == member.id and not e.get("registered")),
                None
            )
            if not claimed:
                return await interaction.response.send_message("❌ Bu kaydı yapmak için yetkili değilsin veya süre dolmuş.", ephemeral=True)

            target = guild.get_member(int(target_id))
            if not target:
                return await interaction.response.send_message("❌ Kullanıcı sunucuda bulunamadı.", ephemeral=True)

            role_map = {
                "aye":      (ROLES["UYE"], "Üye"),
                "bayan":    (ROLES["BAYAN_UYE"], "Bayan Üye"),
                "futbolcu": (ROLES["FUTBOLCU"], "Futbolcu"),
                "td":       (ROLES["TEKNIK_DIREKTOR"], "Teknik Direktör"),
            }
            role_info = role_map.get(reg_type)
            if not role_info:
                return await interaction.response.send_message("❌ Geçersiz rol tipi.", ephemeral=True)

            role_obj = guild.get_role(role_info[0])
            kayitsiz_role = guild.get_role(ROLES["KAYITSIZ"])
            try:
                if kayitsiz_role:
                    await target.remove_roles(kayitsiz_role)
                if role_obj:
                    await target.add_roles(role_obj)
                await target.edit(nick=isim)
            except Exception:
                return await interaction.response.send_message("❌ Roller verilirken hata oluştu.", ephemeral=True)

            regs = load_data("registrations.json")
            regs[str(target.id)] = {
                "registrarId": member.id,
                "roleName": role_info[1],
                "registeredAt": int(time.time() * 1000),
            }
            save_data("registrations.json", regs)

            pending[str(target_id)]["registered"] = True
            save_data("pendingRegistrations.json", pending)

            embed = discord.Embed(title="✅ Kayıt Tamamlandı", color=0x00B300)
            embed.add_field(name="👤 Kullanıcı", value=target.mention, inline=True)
            embed.add_field(name="📝 İsim", value=isim, inline=True)
            embed.add_field(name="🎭 Rol", value=role_info[1], inline=True)
            embed.add_field(name="👮 Kaydeden", value=member.mention, inline=True)
            await interaction.response.edit_message(embed=embed, view=None)

            log_ch = guild.get_channel(CHANNELS["KAYIT_LOG"])
            if log_ch:
                log_embed = discord.Embed(
                    title="📋 Yeni Kayıt",
                    color=0x00B300,
                    description=f"**{target.display_name}** aramıza katıldı! Hoş geldin! 🎉"
                )
                log_embed.set_thumbnail(url=target.display_avatar.url)
                log_embed.add_field(name="👤 Kullanıcı", value=target.mention, inline=True)
                log_embed.add_field(name="📝 İsim", value=isim, inline=True)
                log_embed.add_field(name="🎭 Rol", value=role_info[1], inline=True)
                log_embed.add_field(name="👮 Kaydeden", value=member.mention, inline=True)
                log_embed.add_field(name="👥 Üye Sayısı", value=str(guild.member_count), inline=True)
                await log_ch.send(embed=log_embed)
            return

        # Ban onay/iptal
        if cid.startswith("ban_onayla_"):
            if not has_role(member, "BOT_COMMANDER") and not has_role(member, "OWNER"):
                return await interaction.response.send_message("❌ Yetersiz yetki.", ephemeral=True)
            parts = cid.split("_")
            target_id = int(parts[2])
            reason = urllib.parse.unquote("_".join(parts[3:]))
            target = guild.get_member(target_id)
            if not target:
                return await interaction.response.send_message("❌ Kullanıcı bulunamadı.", ephemeral=True)
            try:
                await target.ban(reason=reason)
            except Exception:
                return await interaction.response.send_message("❌ Ban atamadım.", ephemeral=True)
            embed = discord.Embed(title="🔨 Kullanıcı Banlandı", color=0xFF0000)
            embed.add_field(name="👤 Kullanıcı", value=str(target), inline=True)
            embed.add_field(name="📝 Sebep", value=reason, inline=True)
            embed.add_field(name="👮 Yetkili", value=member.mention, inline=True)
            return await interaction.response.edit_message(embed=embed, view=None)

        if cid == "ban_iptal":
            embed = discord.Embed(color=0x808080, description="❌ Ban işlemi iptal edildi.")
            return await interaction.response.edit_message(embed=embed, view=None)

        # Kick onay/iptal
        if cid.startswith("kick_onayla_"):
            if not has_role(member, "BOT_COMMANDER") and not has_role(member, "OWNER"):
                return await interaction.response.send_message("❌ Yetersiz yetki.", ephemeral=True)
            parts = cid.split("_")
            target_id = int(parts[2])
            reason = urllib.parse.unquote("_".join(parts[3:]))
            target = guild.get_member(target_id)
            if not target:
                return await interaction.response.send_message("❌ Kullanıcı bulunamadı.", ephemeral=True)
            try:
                await target.kick(reason=reason)
            except Exception:
                return await interaction.response.send_message("❌ Kick atamadım.", ephemeral=True)
            embed = discord.Embed(title="👟 Kullanıcı Atıldı", color=0xFF6600)
            embed.add_field(name="👤 Kullanıcı", value=str(target), inline=True)
            embed.add_field(name="📝 Sebep", value=reason, inline=True)
            embed.add_field(name="👮 Yetkili", value=member.mention, inline=True)
            return await interaction.response.edit_message(embed=embed, view=None)

        if cid == "kick_iptal":
            embed = discord.Embed(color=0x808080, description="❌ Kick işlemi iptal edildi.")
            return await interaction.response.edit_message(embed=embed, view=None)

        # KAP butonları
        if cid in ("kap_transfer", "kap_uzatma", "kap_fesh"):
            allowed = has_role(member, "TEKNIK_DIREKTOR") or has_role(member, "TAKIM_KAPTANI") or has_role(member, "OWNER")
            if not allowed:
                return await interaction.response.send_message("❌ Yetersiz yetki.", ephemeral=True)

            if cid == "kap_transfer":
                modal = discord.ui.Modal(title="📤 Transfer Formu", custom_id="kap_modal_transfer")
                modal.add_item(discord.ui.TextInput(label="Oyuncu İsmi", custom_id="oyuncu_ismi", required=True))
                modal.add_item(discord.ui.TextInput(label="Eski Takımı", custom_id="eski_takim", required=True))
                modal.add_item(discord.ui.TextInput(label="Yeni Takımı", custom_id="yeni_takim", required=True))
                modal.add_item(discord.ui.TextInput(label="Aldığı Maaş", custom_id="maas", required=True))
                modal.add_item(discord.ui.TextInput(label="Kaç Sezon / Ek Madde / Fesh Bedeli", custom_id="sezon_ek", style=discord.TextStyle.paragraph, required=True))
                return await interaction.response.send_modal(modal)

            elif cid == "kap_uzatma":
                modal = discord.ui.Modal(title="📝 Sözleşme Uzatma Formu", custom_id="kap_modal_uzatma")
                modal.add_item(discord.ui.TextInput(label="Oyuncu İsmi", custom_id="oyuncu_ismi", required=True))
                modal.add_item(discord.ui.TextInput(label="Takımı", custom_id="takim", required=True))
                modal.add_item(discord.ui.TextInput(label="Aldığı Maaş", custom_id="maas", required=True))
                modal.add_item(discord.ui.TextInput(label="Kaç Sezon / Ek Madde", custom_id="sezon_ek", style=discord.TextStyle.paragraph, required=True))
                return await interaction.response.send_modal(modal)

            elif cid == "kap_fesh":
                modal = discord.ui.Modal(title="🚫 Fesh Formu", custom_id="kap_modal_fesh")
                modal.add_item(discord.ui.TextInput(label="Oyuncu İsmi", custom_id="oyuncu_ismi", required=True))
                modal.add_item(discord.ui.TextInput(label="Eski Takımı", custom_id="eski_takim", required=True))
                modal.add_item(discord.ui.TextInput(label="Fesh Sebebi", custom_id="fesh_sebebi", style=discord.TextStyle.paragraph, required=True))
                return await interaction.response.send_modal(modal)

    # ── Modal submit ──
    elif interaction.type == discord.InteractionType.modal_submit:
        cid = interaction.data["custom_id"]
        member = interaction.user
        guild = interaction.guild

        def get_val(field_id):
            for comp in interaction.data.get("components", []):
                for item in comp.get("components", []):
                    if item.get("custom_id") == field_id:
                        return item.get("value", "")
            return ""

        if cid == "kap_modal_transfer":
            oyuncu = get_val("oyuncu_ismi")
            eski = get_val("eski_takim")
            yeni = get_val("yeni_takim")
            maas = get_val("maas")
            sezon = get_val("sezon_ek")

            team_roles = load_data("teamRoles.json")
            allowed_role_ids = team_roles.get("roles", [])
            assigned_role_name = None

            if allowed_role_ids:
                yeni_role = next(
                    (r for r in guild.roles if r.id in allowed_role_ids and yeni.lower() in r.name.lower()),
                    None
                )
                if yeni_role:
                    await guild.chunk()
                    oyuncu_member = next(
                        (m for m in guild.members if oyuncu.lower() in m.display_name.lower()),
                        None
                    )
                    if oyuncu_member:
                        eski_role = next(
                            (r for r in oyuncu_member.roles if r.id in allowed_role_ids),
                            None
                        )
                        if eski_role:
                            try:
                                await oyuncu_member.remove_roles(eski_role)
                            except Exception:
                                pass
                        try:
                            await oyuncu_member.add_roles(yeni_role)
                            assigned_role_name = yeni_role.name
                        except Exception:
                            pass

            embed = discord.Embed(title="📤 Transfer Haberi", color=0x00B300)
            embed.add_field(name="👤 Oyuncu İsmi", value=oyuncu, inline=True)
            embed.add_field(name="🏟️ Eski Takım", value=eski, inline=True)
            embed.add_field(name="🏟️ Yeni Takım", value=yeni, inline=True)
            embed.add_field(name="💰 Maaş", value=maas, inline=True)
            embed.add_field(name="📋 Sezon/Ek Madde/Fesh", value=sezon, inline=False)
            embed.add_field(name="👮 İşlemi Yapan", value=member.mention, inline=True)
            if assigned_role_name:
                embed.add_field(name="✅ Verilen Takım Rolü", value=assigned_role_name, inline=True)
            embed.set_footer(text="Premier Lig RP | KAP Sistemi")
            await interaction.response.send_message(embed=embed)
            log_ch = guild.get_channel(CHANNELS["TRANSFER_LOG"])
            if log_ch:
                await log_ch.send(embed=embed)

        elif cid == "kap_modal_uzatma":
            oyuncu = get_val("oyuncu_ismi")
            takim = get_val("takim")
            maas = get_val("maas")
            sezon = get_val("sezon_ek")

            embed = discord.Embed(title="📝 Sözleşme Uzatma Haberi", color=0x5865F2)
            embed.add_field(name="👤 Oyuncu İsmi", value=oyuncu, inline=True)
            embed.add_field(name="🏟️ Takım", value=takim, inline=True)
            embed.add_field(name="💰 Maaş", value=maas, inline=True)
            embed.add_field(name="📋 Sezon/Ek Madde", value=sezon, inline=False)
            embed.add_field(name="👮 İşlemi Yapan", value=member.mention, inline=True)
            embed.set_footer(text="Premier Lig RP | KAP Sistemi")
            await interaction.response.send_message(embed=embed)
            log_ch = guild.get_channel(CHANNELS["TRANSFER_LOG"])
            if log_ch:
                await log_ch.send(embed=embed)

        elif cid == "kap_modal_fesh":
            oyuncu = get_val("oyuncu_ismi")
            eski = get_val("eski_takim")
            sebep = get_val("fesh_sebebi")

            embed = discord.Embed(title="🚫 Fesh Haberi", color=0xFF0000)
            embed.add_field(name="👤 Oyuncu İsmi", value=oyuncu, inline=True)
            embed.add_field(name="🏟️ Eski Takım", value=eski, inline=True)
            embed.add_field(name="📝 Fesh Sebebi", value=sebep, inline=False)
            embed.add_field(name="👮 İşlemi Yapan", value=member.mention, inline=True)
            embed.set_footer(text="Premier Lig RP | KAP Sistemi")
            await interaction.response.send_message(embed=embed)
            log_ch = guild.get_channel(CHANNELS["TRANSFER_LOG"])
            if log_ch:
                await log_ch.send(embed=embed)


# ────────────────────────────────────────────────────────────
# COMMANDS
# ────────────────────────────────────────────────────────────

@bot.command(name="yardim", aliases=["yardım"])
async def yardim(ctx):
    embed = discord.Embed(
        title="📖 Premier Lig RP Bot — Komut Listesi",
        color=0x5865F2
    )
    embed.add_field(
        name="⚽ Oyuncu Komutları (Herkes)",
        value=(
            "`.afk [sebep]` — AFK modunu aç\n"
            "`.kayıtbilgi @kullanıcı` — Kimin kayıt ettiğini gör\n"
            "`.sunucu` — Sunucu bilgilerini gör\n"
            "`.snipe` — Son silinen mesajı gör"
        ),
        inline=False
    )
    embed.add_field(
        name="⚽ Futbolcu Komutları (@Futbolcu)",
        value=(
            "`.ant` — Antrenman yap (1 saatte 1 kez, #antrenman kanalı)\n"
            "`.penalti` — Penaltı at (#penaltı kanalı)"
        ),
        inline=False
    )
    embed.add_field(
        name="📋 Kayıt Komutları (@Kayıt Yetkilisi)",
        value=(
            "`.k <isim>` — Üstlendiğin kullanıcıyı kayıt et\n"
            "`.kayitsiz @kullanıcı` — Kullanıcıyı kayıtsız yap\n"
            "`.ara <isim>` — Sunucuda üye ara"
        ),
        inline=False
    )
    embed.add_field(
        name="💰 Değer Komutları (@Değer Yetkilisi)",
        value="`.ydver @kullanıcı <miktar> <sebep>` — Oyuncuya değer ver",
        inline=False
    )
    embed.add_field(
        name="🔨 Moderasyon Komutları (@Moderatör)",
        value=(
            "`.mute @kullanıcı <süre> [sebep]` — Kullanıcıyı sustur\n"
            "`.unmute @kullanıcı` — Susturmayı kaldır"
        ),
        inline=False
    )
    embed.add_field(
        name="🛡️ Bot Commander Komutları",
        value=(
            "`.ban @kullanıcı [sebep]` — Banla\n"
            "`.kick @kullanıcı [sebep]` — At\n"
            "`.rolver @kullanıcı <rol adı>` — Rol ver\n"
            "`.rolal @kullanıcı <rol adı>` — Rol al"
        ),
        inline=False
    )
    embed.add_field(
        name="📤 KAP Komutları (@Teknik Direktör / @Takım Kaptanı)",
        value=(
            "`.kap` — Transfer, sözleşme uzatma veya fesh\n"
            "`.takim <takım adı>` — Takım kadrosunu gör"
        ),
        inline=False
    )
    embed.add_field(
        name="👑 Owner Komutları",
        value="`.takimrolekle <rol adı>` — Takım rolü ekle",
        inline=False
    )
    embed.add_field(
        name="⏱️ Süre Formatı",
        value="`d`=Gün, `h`=Saat, `m`=Dakika | Örnek: `3d`, `12h`, `30m`",
        inline=False
    )
    embed.set_footer(text="Premier Lig RP | Yardım Menüsü")
    await ctx.reply(embed=embed)


@bot.command(name="afk")
async def afk_cmd(ctx, *, reason="AFK"):
    import time
    afk_data = load_data("afk.json")
    afk_data[str(ctx.author.id)] = {
        "reason": reason,
        "since": int(time.time() * 1000),
        "username": str(ctx.author),
    }
    save_data("afk.json", afk_data)
    embed = discord.Embed(
        title="💤 AFK Modu Aktif",
        color=0x5865F2,
        description=f"**{ctx.author.display_name}** AFK moduna geçti.\n**Sebep:** {reason}"
    )
    await ctx.reply(embed=embed)

@bot.command(name="emojitest")
async def emoji_test(ctx):
    names = [e.name for e in ctx.guild.emojis if "bar" in e.name.lower() or "ll" in e.name.lower()]
    await ctx.reply(f"Bulunan emojiler: {names}")


@bot.command(name="snipe")
async def snipe_cmd(ctx):
    import time
    snipes = load_data("snipe.json")
    entry = snipes.get(str(ctx.channel.id))
    if not entry:
        return await ctx.reply("❌ Bu kanalda yakın zamanda silinmiş mesaj yok.")
    embed = discord.Embed(title="🗑️ Silinen Mesaj", color=0xFF6600)
    embed.description = entry.get("content") or "*[İçerik yok]*"
    embed.add_field(name="👤 Gönderen", value=f"<@{entry['authorId']}> ({entry['authorTag']})", inline=True)
    embed.add_field(name="🕐 Silinme", value=f"<t:{entry['deletedAt']//1000}:R>", inline=True)
    await ctx.reply(embed=embed)


@bot.command(name="sunucu")
async def sunucu_cmd(ctx):
    guild = ctx.guild
    await guild.fetch()
    owner = await guild.fetch_member(guild.owner_id) if guild.owner_id else None
    embed = discord.Embed(title=f"🏟️ {guild.name}", color=0x5865F2)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="🆔 Sunucu ID", value=str(guild.id), inline=True)
    embed.add_field(name="👑 Sunucu Sahibi", value=str(owner) if owner else "Bilinmiyor", inline=True)
    embed.add_field(name="👥 Üye Sayısı", value=str(guild.member_count), inline=True)
    embed.add_field(name="🎭 Rol Sayısı", value=str(len(guild.roles) - 1), inline=True)
    embed.add_field(name="💬 Kanal Sayısı", value=str(len(guild.channels)), inline=True)
    embed.add_field(name="📅 Açılış", value=f"<t:{int(guild.created_at.timestamp())}:F>", inline=True)
    embed.add_field(name="⚡ Boost", value=f"Seviye {guild.premium_tier} ({guild.premium_subscription_count} boost)", inline=True)
    embed.add_field(name="🌍 Bölge", value=guild.preferred_locale, inline=True)
    embed.set_footer(text="Premier Lig RP")
    await ctx.reply(embed=embed)

@bot.command(name="ant")
async def ant_cmd(ctx):
    import time
    COOLDOWN_MS = 60 * 60 * 1000
    MAX_SESSIONS = 10
    if ctx.channel.id != CHANNELS["ANTRENMAN"]:
        return await ctx.reply(f"❌ Bu komutu yalnızca <#{CHANNELS['ANTRENMAN']}> kanalında kullanabilirsin.")
    if not has_role(ctx.author, "FUTBOLCU"):
        return await ctx.reply("❌ Bu komutu kullanmak için **Futbolcu** rolüne sahip olmalısın.")
    training = load_data("training.json")
    now = int(time.time() * 1000)
    uid = str(ctx.author.id)
    if uid not in training:
        training[uid] = {"count": 0, "lastUsed": 0}
    ud = training[uid]
    elapsed = now - ud["lastUsed"]
    if ud["lastUsed"] > 0 and elapsed < COOLDOWN_MS:
        remaining = COOLDOWN_MS - elapsed
        mins = (remaining + 59_999) // 60_000
        return await ctx.reply(f"⏱️ Antrenman için **{mins} dakika** daha beklemelisin.")
    ud["count"] += 1
    ud["lastUsed"] = now
    if ud["count"] > MAX_SESSIONS:
        ud["count"] = 1
    save_data("training.json", training)
    def build_bar(guild, current):
        bar = ""
        for i in range(10):
            is_filled = i < current
            if i == 0:
                emoji_name = "LL_dolubarsol" if is_filled else "LL_bosbarsol"
            elif i == 9:
                emoji_name = "LL_dolubarsag" if is_filled else "LL_bosbarsag"
            else:
                emoji_name = "LL_dolubarorta" if is_filled else "LL_bosbarorta"
            emoji = discord.utils.get(guild.emojis, name=emoji_name)
            if emoji:
                bar += f"<:{emoji.name}:{emoji.id}>"
            else:
                bar += "🟩" if is_filled else "⬜"
        return bar
    bar = build_bar(ctx.guild, ud["count"])
    embed = discord.Embed(
        title="⚽ Antrenman",
        color=0x00B300,
        description=(
            f"**{ctx.author.display_name}** antrenman yaptı!\n\n"
            f"**İlerleme:** {ud['count']}/10\n\n"
            f"{bar}"
        )
    )
    embed.set_footer(text="Premier Lig RP | Antrenman Sistemi")
    await ctx.reply(embed=embed)
    if ud["count"] == 10:
        notif_ch = ctx.guild.get_channel(CHANNELS["DEGER_BILDIRIM"])
        if notif_ch:
            await notif_ch.send(embed=discord.Embed(
                title="🏆 10/10 Antrenman Tamamlandı!",
                color=0xFFD700,
                description=f"<@&{ROLES['DEGER_YETKILISI']}> dikkat!\n\n**{ctx.author.mention}** 10/10 antrenman tamamladı!\nDeğer güncellemesi yapabilirsiniz."
            ))
        ud["count"] = 0
        save_data("training.json", training)


@bot.command(name="penalti", aliases=["penaltı"])
async def penalti_cmd(ctx):
    import random, asyncio

    if ctx.channel.id != CHANNELS["PENALTI"]:
        return await ctx.reply(f"❌ Bu komutu yalnızca <#{CHANNELS['PENALTI']}> kanalında kullanabilirsin.")
    if not has_role(ctx.author, "FUTBOLCU"):
        return await ctx.reply("❌ Bu komutu kullanmak için **Futbolcu** rolüne sahip olmalısın.")

    OUTCOMES = [
        {"label": "⚽ GOL! Müthiş bir şut!", "isGoal": True, "weight": 20},
        {"label": "❌ Aut! Top dışarı çıktı!", "isGoal": False, "weight": 20},
        {"label": "🏁 Direkten döndü!", "isGoal": False, "weight": 20},
        {"label": "🧤 Kaleci kurtardı!", "isGoal": False, "weight": 20},
        {"label": "🙈 Şut tepeye gitti!", "isGoal": False, "weight": 10},
        {"label": "💥 Yan direk!", "isGoal": False, "weight": 10},
    ]

    total = sum(o["weight"] for o in OUTCOMES)
    rand = random.random() * total
    outcome = OUTCOMES[-1]
    for o in OUTCOMES:
        rand -= o["weight"]
        if rand <= 0:
            outcome = o
            break

    steps = [
        "⚽ **Penaltı noktasına yaklaşıyor...**",
        "🏃 **Koşuya başladı...**",
        "👟 **Şut çekiyor...**",
        "💨 **Top uçuyor...**",
    ]
    msg = await ctx.channel.send(steps[0])
    for step in steps[1:]:
        await asyncio.sleep(1.2)
        await msg.edit(content=step)
    await asyncio.sleep(1.4)

    embed = discord.Embed(
        title="🥅 Penaltı Sonucu",
        color=0xFFD700 if outcome["isGoal"] else 0xFF0000,
        description=(
            f"**{ctx.author.display_name}** penaltı attı!\n\n"
            f"**Sonuç:** {outcome['label']}"
        )
    )
    embed.set_footer(text="Premier Lig RP | Penaltı Sistemi")
    await msg.edit(content=None, embed=embed)

    if outcome["isGoal"]:
        notif_ch = ctx.guild.get_channel(CHANNELS["DEGER_BILDIRIM"])
        if notif_ch:
            notif_embed = discord.Embed(
                title="⚽ Penaltı Golü!",
                color=0xFFD700,
                description=(
                    f"<@&{ROLES['DEGER_YETKILISI']}> dikkat!\n\n"
                    f"**{ctx.author.mention}** penaltıdan gol attı!\n"
                    "Değer güncellemesi yapabilirsiniz."
                )
            )
            await notif_ch.send(embed=notif_embed)


@bot.command(name="k")
async def kayit_cmd(ctx, *, isim=None):
    if not has_role(ctx.author, "KAYIT_YETKILISI"):
        return await ctx.reply("❌ Bu komutu kullanmak için **Kayıt Yetkilisi** rolüne sahip olmalısın.")

    pending = load_data("pendingRegistrations.json")
    claimed = next(
        (e for e in pending.values() if e.get("claimedBy") == ctx.author.id and not e.get("registered")),
        None
    )
    if not claimed:
        return await ctx.reply("❌ Üstlendiğin ve kaydını bekleyen bir kullanıcı yok.")
    if not isim:
        return await ctx.reply("❌ Kullanım: `.k <isim>`")

    target = ctx.guild.get_member(claimed["userId"])
    if not target:
        del pending[str(claimed["userId"])]
        save_data("pendingRegistrations.json", pending)
        return await ctx.reply("❌ Kaydedilecek kullanıcı sunucuda bulunamadı.")

    view = discord.ui.View(timeout=None)
    uid = target.id
    name_enc = isim.replace(" ", "_")
    view.add_item(discord.ui.Button(label="@Üye", style=discord.ButtonStyle.primary, custom_id=f"kayit_aye_{uid}_{name_enc}"))
    view.add_item(discord.ui.Button(label="@Bayan Üye", style=discord.ButtonStyle.success, custom_id=f"kayit_bayan_{uid}_{name_enc}"))
    view.add_item(discord.ui.Button(label="@Futbolcu", style=discord.ButtonStyle.danger, custom_id=f"kayit_futbolcu_{uid}_{name_enc}"))
    view.add_item(discord.ui.Button(label="@Teknik Direktör", style=discord.ButtonStyle.secondary, custom_id=f"kayit_td_{uid}_{name_enc}"))

    embed = discord.Embed(
        title="📋 Kayıt Sistemi",
        color=0x5865F2,
        description=f"**{target.mention}** kullanıcısı için kayıt türünü seçin.\n\n**İsim:** {isim}"
    )
    embed.set_footer(text="Sadece kayıt eden yetkili butona basabilir.")
    await ctx.reply(embed=embed, view=view)


@bot.command(name="kayitsiz")
async def kayitsiz_cmd(ctx, target: discord.Member = None):
    allowed = has_role(ctx.author, "KAYIT_YETKILISI") or has_role(ctx.author, "OWNER") or has_role(ctx.author, "BOT_COMMANDER")
    if not allowed:
        return await ctx.reply("❌ Bu komutu kullanmak için **Kayıt Yetkilisi** rolüne sahip olmalısın.")
    if not target:
        return await ctx.reply("❌ Kullanım: `.kayitsiz @kullanıcı`")

    roles_to_remove = [r for r in target.roles if r.id != ctx.guild.id]
    kayitsiz_role = ctx.guild.get_role(ROLES["KAYITSIZ"])
    try:
        await target.remove_roles(*roles_to_remove)
        if kayitsiz_role:
            await target.add_roles(kayitsiz_role)
        await target.edit(nick=None)
    except Exception:
        return await ctx.reply("❌ Rolleri kaldıramadım. Gerekli yetkim olmayabilir.")

    embed = discord.Embed(
        title="🔄 Kayıtsız Yapıldı",
        color=0xFF0000,
        description="Tüm rolleri alındı ve **Kayıtsız** rolü verildi."
    )
    embed.add_field(name="👤 Kullanıcı", value=target.mention, inline=True)
    embed.add_field(name="👮 İşlemi Yapan", value=ctx.author.mention, inline=True)
    await ctx.reply(embed=embed)


@bot.command(name="ara")
async def ara_cmd(ctx, *, query=None):
    allowed = has_role(ctx.author, "KAYIT_YETKILISI") or has_role(ctx.author, "OWNER")
    if not allowed:
        return await ctx.reply("❌ Bu komutu kullanmak için **Kayıt Yetkilisi** rolüne sahip olmalısın.")
    if not query:
        return await ctx.reply("❌ Kullanım: `.ara <isim>`")

    await ctx.guild.chunk()
    results = [m for m in ctx.guild.members if query.lower() in m.display_name.lower() or query.lower() in m.name.lower()]
    if not results:
        return await ctx.reply(f"❌ `{query}` için hiç üye bulunamadı.")

    list_text = "\n".join(f"• {m.display_name} ({m}) — {m.mention}" for m in results[:15])
    embed = discord.Embed(title=f'🔍 Arama Sonuçları: "{query}"', color=0x5865F2, description=list_text)
    embed.set_footer(text=f"{len(results)} sonuç{' (ilk 15)' if len(results) > 15 else ''}")
    await ctx.reply(embed=embed)


@bot.command(name="kayitbilgi", aliases=["kayıtbilgi"])
async def kayitbilgi_cmd(ctx, target: discord.Member = None):
    if not target:
        return await ctx.reply("❌ Kullanım: `.kayıtbilgi @kullanıcı`")

    regs = load_data("registrations.json")
    entry = regs.get(str(target.id))
    if not entry:
        return await ctx.reply(f"❌ **{target.display_name}** için kayıt bilgisi bulunamadı.")

    registrar = ctx.guild.get_member(entry["registrarId"])
    ts = entry["registeredAt"] // 1000

    embed = discord.Embed(title="📋 Kayıt Bilgisi", color=0x5865F2)
    embed.add_field(name="👤 Kullanıcı", value=target.mention, inline=True)
    embed.add_field(name="👮 Kaydeden", value=registrar.mention if registrar else f"ID: {entry['registrarId']}", inline=True)
    embed.add_field(name="🎭 Verilen Rol", value=entry.get("roleName", "Bilinmiyor"), inline=True)
    embed.add_field(name="📅 Kayıt Tarihi", value=f"<t:{ts}:F>", inline=True)
    await ctx.reply(embed=embed)


@bot.command(name="ydver")
async def ydver_cmd(ctx, target: discord.Member = None, amount: str = None, *, reason=None):
    if not has_role(ctx.author, "DEGER_YETKILISI"):
        return await ctx.reply("❌ Bu komutu kullanmak için **Değer Yetkilisi** rolüne sahip olmalısın.")
    if not target or not amount or not reason:
        return await ctx.reply("❌ Kullanım: `.ydver @kullanıcı <miktar> <sebep>`")

    try:
        amount_num = int(amount)
        if amount_num <= 0:
            raise ValueError
    except ValueError:
        return await ctx.reply("❌ Geçerli bir miktar girin (pozitif tam sayı).")

    nick = target.display_name
    match = re.search(r"(\d+(?:\.\d+)?)M€", nick)
    if not match:
        return await ctx.reply(f"❌ **{nick}** kullanıcısının isminde değer formatı bulunamadı (örn: `16M€` veya `16.5M€`).")

    current = int(float(match.group(1)))  
    new_val = current + amount_num
    new_value_str = f"{new_val}M€"

    try:
        await target.edit(nick=nick.replace(match.group(0), new_value_str))
    except Exception:
        return await ctx.reply("❌ Kullanıcının nickini değiştiremedim.")

    embed = discord.Embed(title="⚽ Değer Güncellendi", color=0x00B300)
    embed.add_field(name="👤 Oyuncu", value=target.mention, inline=True)
    embed.add_field(name="📊 Eski Değer", value=f"{current}M€", inline=True)
    embed.add_field(name="📈 Yeni Değer", value=new_value_str, inline=True)
    embed.add_field(name="➕ Artış", value=f"+{amount_num}M€", inline=True)
    embed.add_field(name="📝 Sebep", value=reason, inline=True)
    embed.add_field(name="👮 Yetkili", value=ctx.author.mention, inline=True)
    embed.set_footer(text="Premier Lig RP | Değer Sistemi")
    await ctx.reply(embed=embed)

    log_ch = ctx.guild.get_channel(CHANNELS["DEGER_LOG"])
    if log_ch:
        await log_ch.send(embed=embed)

@bot.command(name="şart", aliases=["sart", "şartlar", "kurallar"])
async def sart_cmd(ctx):
    embed = discord.Embed(
        title="Premier Lig Sunucuya Girme Şartları",
        color=0x00B300,
        description="Sunucuya kayıt olabilmek için aşağıdaki şartları yerine getirmeniz gerekmektedir:"
    )
    
    embed.add_field(
        name="📌 Gerekli İşlemler",
        value=(
            f"🎉 <#{1502434459352301568}> Kanalındaki **Tüm Çekilişlere** Katılmak\n"
            f"🎭 <#{1502434445662359733}> Kanalından **En Az 2 Rol** Almak\n"
            f"🗳️ <#{1502434443963400302}> Kanalından **Sunucuya Oy** Vermek"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Önemli Uyarı",
        value="**Lütfen Kayıt Yetkililerini Kandırmaya Çalışmayın!**",
        inline=False
    )
    
    embed.set_footer(text="Premier Lig RP • Giriş Şartları")
    await ctx.reply(embed=embed)
    
@bot.command(name="mute")
async def mute_cmd(ctx, target: discord.Member = None, duration_str: str = None, *, reason="Sebep belirtilmedi"):
    allowed = has_role(ctx.author, "MODERATOR") or has_role(ctx.author, "OWNER")
    if not allowed:
        return await ctx.reply("❌ Bu komutu kullanmak için **Moderatör** rolüne sahip olmalısın.")
    if not target or not duration_str:
        return await ctx.reply("❌ Kullanım: `.mute @kullanıcı <süre> [sebep]` — Süre: `1d`, `12h`, `30m`")
    if target.id == ctx.author.id:
        return await ctx.reply("❌ Kendini mute edemezsin.")
    if not is_higher_than(ctx.author, target):
        return await ctx.reply("❌ Kendinden üst veya eşit birini mute edemezsin.")

    ms = parse_duration(duration_str)
    if not ms:
        return await ctx.reply("❌ Geçersiz süre. Örnek: `1d`, `12h`, `30m`")
    if ms > 28 * 24 * 60 * 60 * 1000:
        return await ctx.reply("❌ Maksimum mute süresi 28 gündür.")

    import datetime
    try:
        await target.timeout(datetime.timedelta(milliseconds=ms), reason=reason)
    except Exception:
        return await ctx.reply("❌ Kullanıcıyı mute edemedim.")

    embed = discord.Embed(title="🔇 Kullanıcı Mute Edildi", color=0xFF9900)
    embed.add_field(name="👤 Kullanıcı", value=target.mention, inline=True)
    embed.add_field(name="⏱️ Süre", value=format_duration(ms), inline=True)
    embed.add_field(name="📝 Sebep", value=reason, inline=True)
    embed.add_field(name="👮 Yetkili", value=ctx.author.mention, inline=True)
    await ctx.reply(embed=embed)


@bot.command(name="unmute")
async def unmute_cmd(ctx, target: discord.Member = None):
    allowed = has_role(ctx.author, "MODERATOR") or has_role(ctx.author, "OWNER")
    if not allowed:
        return await ctx.reply("❌ Bu komutu kullanmak için **Moderatör** rolüne sahip olmalısın.")
    if not target:
        return await ctx.reply("❌ Kullanım: `.unmute @kullanıcı`")
    if target.id == ctx.author.id:
        return await ctx.reply("❌ Kendini unmute edemezsin.")
    if not is_higher_than(ctx.author, target):
        return await ctx.reply("❌ Kendinden üst veya eşit birini unmute edemezsin.")

    try:
        await target.timeout(None)
    except Exception:
        return await ctx.reply("❌ Kullanıcıyı unmute edemedim.")

    embed = discord.Embed(title="🔊 Kullanıcı Unmute Edildi", color=0x00B300)
    embed.add_field(name="👤 Kullanıcı", value=target.mention, inline=True)
    embed.add_field(name="👮 Yetkili", value=ctx.author.mention, inline=True)
    await ctx.reply(embed=embed)


@bot.command(name="ban")
async def ban_cmd(ctx, target: discord.Member = None, *, reason="Sebep belirtilmedi"):
    import urllib.parse
    allowed = has_role(ctx.author, "BOT_COMMANDER") or has_role(ctx.author, "OWNER")
    if not allowed:
        return await ctx.reply("❌ Bu komutu kullanmak için **Bot Commander** rolüne sahip olmalısın.")
    if not target:
        return await ctx.reply("❌ Kullanım: `.ban @kullanıcı [sebep]`")
    if target.id == ctx.author.id:
        return await ctx.reply("❌ Kendine ban atamazsın.")
    if not is_higher_than(ctx.author, target):
        return await ctx.reply("❌ Kendinden üst veya eşit birini ban atamazsın.")

    reason_enc = urllib.parse.quote(reason)
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="✅ Onayla", style=discord.ButtonStyle.danger, custom_id=f"ban_onayla_{target.id}_{reason_enc}"))
    view.add_item(discord.ui.Button(label="❌ İptal", style=discord.ButtonStyle.secondary, custom_id="ban_iptal"))

    embed = discord.Embed(title="🔨 Ban Onayı", color=0xFF0000, description="Bu işlemi onaylamak istiyor musun?")
    embed.add_field(name="👤 Hedef", value=f"{target.mention} ({target})", inline=True)
    embed.add_field(name="📝 Sebep", value=reason, inline=True)
    await ctx.reply(embed=embed, view=view)


@bot.command(name="kick")
async def kick_cmd(ctx, target: discord.Member = None, *, reason="Sebep belirtilmedi"):
    import urllib.parse
    allowed = has_role(ctx.author, "BOT_COMMANDER") or has_role(ctx.author, "OWNER")
    if not allowed:
        return await ctx.reply("❌ Bu komutu kullanmak için **Bot Commander** rolüne sahip olmalısın.")
    if not target:
        return await ctx.reply("❌ Kullanım: `.kick @kullanıcı [sebep]`")
    if target.id == ctx.author.id:
        return await ctx.reply("❌ Kendini kick edemezsin.")
    if not is_higher_than(ctx.author, target):
        return await ctx.reply("❌ Kendinden üst veya eşit birini kick edemezsin.")

    reason_enc = urllib.parse.quote(reason)
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="✅ Onayla", style=discord.ButtonStyle.danger, custom_id=f"kick_onayla_{target.id}_{reason_enc}"))
    view.add_item(discord.ui.Button(label="❌ İptal", style=discord.ButtonStyle.secondary, custom_id="kick_iptal"))

    embed = discord.Embed(title="👟 Kick Onayı", color=0xFF6600, description="Bu işlemi onaylamak istiyor musun?")
    embed.add_field(name="👤 Hedef", value=f"{target.mention} ({target})", inline=True)
    embed.add_field(name="📝 Sebep", value=reason, inline=True)
    await ctx.reply(embed=embed, view=view)


@bot.command(name="rolver")
async def rolver_cmd(ctx, target: discord.Member = None, *, role_name=None):
    allowed = has_role(ctx.author, "BOT_COMMANDER") or has_role(ctx.author, "OWNER") or has_role(ctx.author, "MODERATOR")
    if not allowed:
        return await ctx.reply("❌ Bu komutu kullanmak için **Bot Commander** veya **Moderatör** rolüne sahip olmalısın.")
    if not target or not role_name:
        return await ctx.reply("❌ Kullanım: `.rolver @kullanıcı <rol adı>`")
    if target.id == ctx.author.id:
        return await ctx.reply("❌ Kendine rol veremezsin.")
    if not is_higher_than(ctx.author, target):
        return await ctx.reply("❌ Kendinden üst veya eşit birine rol veremezsin.")

    role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), ctx.guild.roles)
    if not role:
        return await ctx.reply(f"❌ `{role_name}` adında bir rol bulunamadı.")

    try:
        await target.add_roles(role)
    except Exception:
        return await ctx.reply("❌ Rolü veremedim.")

    embed = discord.Embed(title="✅ Rol Verildi", color=0x00B300)
    embed.add_field(name="👤 Kullanıcı", value=target.mention, inline=True)
    embed.add_field(name="🎭 Rol", value=role.mention, inline=True)
    embed.add_field(name="👮 Yetkili", value=ctx.author.mention, inline=True)
    await ctx.reply(embed=embed)


@bot.command(name="rolal")
async def rolal_cmd(ctx, target: discord.Member = None, *, role_name=None):
    allowed = has_role(ctx.author, "BOT_COMMANDER") or has_role(ctx.author, "OWNER") or has_role(ctx.author, "MODERATOR")
    if not allowed:
        return await ctx.reply("❌ Bu komutu kullanmak için **Bot Commander** veya **Moderatör** rolüne sahip olmalısın.")
    if not target or not role_name:
        return await ctx.reply("❌ Kullanım: `.rolal @kullanıcı <rol adı>`")
    if target.id == ctx.author.id:
        return await ctx.reply("❌ Kendinden rol alamazsın.")
    if not is_higher_than(ctx.author, target):
        return await ctx.reply("❌ Kendinden üst veya eşit birinden rol alamazsın.")

    role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), ctx.guild.roles)
    if not role:
        return await ctx.reply(f"❌ `{role_name}` adında bir rol bulunamadı.")

    try:
        await target.remove_roles(role)
    except Exception:
        return await ctx.reply("❌ Rolü alamadım.")

    embed = discord.Embed(title="🗑️ Rol Alındı", color=0xFF0000)
    embed.add_field(name="👤 Kullanıcı", value=target.mention, inline=True)
    embed.add_field(name="🎭 Alınan Rol", value=role.mention, inline=True)
    embed.add_field(name="👮 Yetkili", value=ctx.author.mention, inline=True)
    await ctx.reply(embed=embed)


@bot.command(name="kap")
async def kap_cmd(ctx):
    allowed = has_role(ctx.author, "TEKNIK_DIREKTOR") or has_role(ctx.author, "TAKIM_KAPTANI") or has_role(ctx.author, "OWNER")
    if not allowed:
        return await ctx.reply("❌ Bu komutu kullanmak için **Teknik Direktör** veya **Takım Kaptanı** rolüne sahip olmalısın.")

    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="📤 Transfer", style=discord.ButtonStyle.primary, custom_id="kap_transfer"))
    view.add_item(discord.ui.Button(label="📝 Sözleşme Uzatma", style=discord.ButtonStyle.success, custom_id="kap_uzatma"))
    view.add_item(discord.ui.Button(label="🚫 Fesh", style=discord.ButtonStyle.danger, custom_id="kap_fesh"))

    embed = discord.Embed(title="📋 KAP Sistemi", color=0x5865F2, description="Yapmak istediğiniz işlemi seçin:")
    embed.add_field(name="📤 Transfer", value="Oyuncu transferi gerçekleştir", inline=True)
    embed.add_field(name="📝 Sözleşme Uzatma", value="Mevcut sözleşmeyi uzat", inline=True)
    embed.add_field(name="🚫 Fesh", value="Sözleşmeyi feshettir", inline=True)
    await ctx.reply(embed=embed, view=view)


@bot.command(name="takim", aliases=["takım"])
async def takim_cmd(ctx, *, team_name=None):
    if not team_name:
        return await ctx.reply("❌ Kullanım: `.takim <takım adı>`")

    role = discord.utils.find(lambda r: team_name.lower() in r.name.lower(), ctx.guild.roles)
    if not role:
        return await ctx.reply(f"❌ `{team_name}` adıyla eşleşen bir takım rolü bulunamadı.")

    members = role.members
    if not members:
        return await ctx.reply(f"❌ **{role.name}** takımında hiç oyuncu yok.")

    futbolcular = [m for m in members if has_role(m, "FUTBOLCU")]
    tdler = [m for m in members if has_role(m, "TEKNIK_DIREKTOR")]
    diger = [m for m in members if not has_role(m, "FUTBOLCU") and not has_role(m, "TEKNIK_DIREKTOR")]

    embed = discord.Embed(title=f"🏟️ {role.name} Takımı", color=role.color)
    if tdler:
        embed.add_field(name=f"👔 Teknik Direktörler ({len(tdler)})", value="\n".join(m.display_name for m in tdler), inline=False)
    if futbolcular:
        embed.add_field(name=f"⚽ Futbolcular ({len(futbolcular)})", value="\n".join(m.display_name for m in futbolcular), inline=False)
    if diger:
        embed.add_field(name=f"👥 Diğer ({len(diger)})", value="\n".join(m.display_name for m in diger), inline=False)
    embed.set_footer(text=f"Toplam: {len(members)} üye")
    await ctx.reply(embed=embed)


@bot.command(name="takimrolekle", aliases=["takımrolekle"])
async def takimrolekle_cmd(ctx, *, role_name=None):
    if not has_role(ctx.author, "OWNER"):
        return await ctx.reply("❌ Bu komutu kullanmak için **Owner** rolüne sahip olmalısın.")
    if not role_name:
        return await ctx.reply("❌ Kullanım: `.takımrolekle <rol adı>`")

    role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), ctx.guild.roles)
    if not role:
        return await ctx.reply(f"❌ `{role_name}` adında bir rol bulunamadı.")

    team_roles = load_data("teamRoles.json")
    if "roles" not in team_roles:
        team_roles["roles"] = []
    if role.id in team_roles["roles"]:
        return await ctx.reply(f"❌ `{role.name}` zaten takım rolleri listesinde.")

    team_roles["roles"].append(role.id)
    save_data("teamRoles.json", team_roles)

    embed = discord.Embed(
        title="✅ Takım Rolü Eklendi",
        color=0x00B300,
        description=f"**{role.name}** takım rolleri listesine eklendi."
    )
    await ctx.reply(embed=embed)


# ────────────────────────────────────────────────────────────
# Run
# ────────────────────────────────────────────────────────────
token = os.getenv("DISCORD_TOKEN")
if not token:
    print("❌ DISCORD_TOKEN tapılmadı! .env faylını yoxlayın.")
    exit(1)

bot.run(token)
