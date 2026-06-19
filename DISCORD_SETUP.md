# Discord Integration Setup Guide

## Trin 1: Opret Discord Bot

1. Gå til [Discord Developer Portal](https://discord.com/developers/applications)
2. Klik "New Application" og giv den et navn (f.eks. "Stock Analysis Bot")
3. Gå til "Bot" sektionen og klik "Add Bot"
4. Under "TOKEN", klik "Copy" for at kopiere bot-tokenet

## Trin 2: Giv Bot Permissions

1. Gå til "OAuth2" → "URL Generator"
2. Under "SCOPES", vælg: `bot`
3. Under "PERMISSIONS", vælg:
   - Send Messages
   - Read Messages/View Channels
   - Attach Files
4. Kopier den genererede URL og åbn den i din browser for at invitere botten til din Discord server

## Trin 3: Opsætning

1. Opret en kanal på din Discord server kaldet `#reports`
2. Kopier `.env.example` til `.env`
3. Indsæt dit bot-token i `.env`:
   ```
   DISCORD_BOT_TOKEN=your_copied_token_here
   ```

## Trin 4: Installér dependencies

```bash
pip install -r requirements.txt
```

## Trin 5: Kør analysen

```bash
python main.py NOVO-B.CO
```

Din rapport bliver nu automatisk uploadet til Discord `#reports` kanalen!

## Troubleshooting

- **"Kanal ikke fundet"**: Sørg for at kanalen hedder præcis `reports` (uden `#`)
- **"Token fejl"**: Dobbelttjek at tokenet er korrekt i `.env`
- **"Bot mangler permissions"**: Gå til Server Settings → Roles og giv botten flere permissions
- **Timeout fejl**: Discord serverens latency kan påvirke dette - det er normalt

## Skjul Token fra Git

Hvis du bruger Git, skal du sørge for at `.env` er i `.gitignore`:

```
# .gitignore
.env
```
