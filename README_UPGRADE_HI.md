# MoodBloom 4.4 — Owner & Privacy Edition

## MoodBloom 4.4 — is build mein additional fixes

- Personal home aur group dashboard ko compact, premium navigation mein arrange kiya gaya; group analytics aur personal charts alag scopes mein hi rehte hain.
- Notification preferences mein Reminder Studio ko single entry point banaya, taaki purana custom reminder menu aur naya Reminder Studio duplicate na lage.
- `menu_reminder` callback routing ko reminder engine ke liye reserve kiya.
- `/story`, `/mystery`, `/grouphelp` aur group feature commands ko command handlers/menu se connect kiya. `/bloom` aur `/reward` apne existing engines se register hote hain.
- Mystery option buttons long text par cut na hon isliye readable short labels use karte hain; result message mein selected aur complete correct answer full text mein aata hai. Long result Telegram ki 4096-character limit ke andar multiple messages mein split hota hai, action buttons final part par rehte hain.
- Personal mood chart, personal weekly chart aur group chart ko alag pastel-style visual design, count labels aur percentages ke saath refresh kiya.
- Missing token par project import/test time par fail nahi hota; actual bot start karte waqt clear configuration error deta hai.

## Kya update hua

- HTML formatting tags aur `parse_mode="HTML"` hata diye gaye. Messages Python strings mein hain; jo purani Telegram Markdown formatting thi, woh jahan zaroori hai wahan preserve ki gayi hai. Alag HTML website files ki zaroorat nahi.
- Mystery answers ab masked/half text ki jagah poora correct answer dikhate hain. Same case retry, new mystery aur browse buttons bhi diye gaye hain.
- Naya `reminder_engine.py`: personal, group aur recipient reminders ke liye separate persistent storage.
- Unlimited reminder count: personal reminders user ID se aur group reminders group chat ID se isolate hote hain. Reminder list pages mein hai.
- Custom date/time input (IST): `YYYY-MM-DD HH:MM`, `DD-MM-YYYY HH:MM`, `tomorrow HH:MM`, `today HH:MM`, ya `HH:MM`.
- Personal reminder: `/reminders` private chat mein.
- Group reminder: group mein `/reminders` ya Group dashboard → Reminder Studio. Group reminders manage karne ke liye admin hona zaroori hai.
- Notification custom-reminder limit remove ki gayi.
- Reminder worker har 20 seconds due reminders check karta hai; pending reminders JSON file mein persist hote hain.
- `/start` par agar valid GIF file ya `MOODBLOOM_ANIMATION_FILE_ID` set ho, to animation, welcome caption aur buttons ek hi Telegram message mein aayenge. Invalid GIF file ko use nahi kiya jayega.

## Windows par setup

1. `.env.example` ko copy karke uska naam `.env` rakho.
2. `.env` mein `BOT_TOKEN` ke saamne @BotFather ka naya token paste karo. Token kisi ko share mat karna.
3. PowerShell mein project folder kholo.
4. Commands chalao:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python bot.py
```

Agar PowerShell activation block kare, sirf current terminal ke liye ye chala sakte ho:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Reminder kaise banayein

1. Private chat mein `/reminders` bhejo.
2. `Reminder for me` ya `Send reminder to a person` choose karo.
3. Title/message bhejo: `Paani peena | Abhi ek glass paani pi lo`
4. Date/time bhejo: `2026-12-31 18:30` ya `tomorrow 09:15`.
5. `Saved reminders` se reminder dekh ya delete kar sakte ho.

Group ke liye Group dashboard → `Reminder Studio` kholo. Group reminder sirf usi group ke record mein save hota hai; doosre group ya personal list mein nahi dikhega.

### Kisi ko DM bhejne ki Telegram limitation

- Numeric Telegram user ID sabse reliable hai.
- `@username` tabhi resolve ho sakta hai jab bot ne username ko pehle kisi group mein observe karke save kiya ho.
- Telegram bots aam taur par kisi user ko private message pehle nahi bhej sakte jab tak user ne bot ko `/start` na kiya ho. Agar recipient ne bot start nahi kiya, delivery fail ho sakti hai aur creator ko warning milegi.
- Bot ko reminder ke waqt online/running hona chahiye. Restart ke baad saved pending reminders restore hote hain; bot band hone par due time par message nahi bhej sakta, aur restart ke baad due reminder process hoga.

## GIF setup (optional)

`MOODBLOOM_ANIMATION_FILE_ID` mein valid Telegram animation file ID set karo, ya `assets/moodbloom.gif` mein real GIF file rakho. Project ke purane ZIP mein is naam ki file actual GIF nahi thi, isliye use clean package se hata diya gaya hai.

## Important

- Existing `data/history.json`, `data/groups.json` aur `data/moodbloom_v4.json` ko preserve kiya gaya hai. Upgrade se pehle apne `data` folder ka backup bana lena.
- `backupbot.py` legacy copy hai; normal startup ke liye `python bot.py` use karo.
- HTML files project mein nahi thi; pehle sirf Python files ke andar Telegram HTML formatting tags the. Un tags ko plain text mein convert kar diya gaya hai.

## Safe upgrade on an already-hosted bot

- This 4.3 source package intentionally does **not** include your live `data/` folder or `.env`. That prevents accidental replacement of saved personal/group data and avoids sharing secrets.
- Before deploying, stop the existing bot in the hosting dashboard and back up its `data/` folder.
- Upload/replace the Python source files and `requirements.txt` from this package, but **leave the existing `.env` and `data/` folder untouched**.
- Install/update requirements, then start the existing service again. Do not run the same Telegram token in two live processes simultaneously.
- If your host uses a start command, keep `python bot.py` unless the platform's existing setup requires a different command.
- New reminders are stored in `data/reminders.json`; the reminder engine creates this file automatically. Personal reminders are keyed by user ID; group reminders are keyed by chat ID.

## Command additions and callback fixes

- Added `/story`, `/mystery`, and `/grouphelp` command routes; group commands are registered by the group engine.
- Fixed completed-goal buttons so tapping a completed goal refreshes the goal list instead of trying to complete a malformed goal ID.
- Callback answer attempts are guarded so stale/double answers don't crash the callback handler; validation cases render a useful updated screen.
- The old daily reminder's “Disable” button now actually disables the saved daily reminder and removes its scheduled job.


## MoodBloom 4.4 — Owner controls & birthday privacy

### New in this upgrade
- Owner-only `/owner`, `/ownerstats`, `/cast`, `/pausebot` and `/resumebot` commands.
- `/myid` shows your Telegram numeric ID for setup. Maintenance mode persists in `data/owner_settings.json` and blocks non-owner bot commands/buttons until resumed.
- `/cast Your message` displays a preview and requires confirmation before sending to registered private chats and saved groups. Delivery is reported as delivered vs failed/skipped.
- Personal birthday screens now show only the current user's own birthday/countdown; they do not reveal the global birthday list.
- Group birthday lists are scoped to the current group. The daily scheduler announces birthdays only in the group where the member's group-specific birthday was saved with `/groupbirthday DD-MM`.
- Existing story, mystery, mood analytics and group features remain in the source; this release extends the current project rather than replacing it.

### Owner setup
1. Start MoodBloom and send `/myid` to the bot.
2. Open your existing `.env` file on the host (do not replace it). Add `OWNER_ID=YOUR_NUMERIC_ID` using the number returned by `/myid`.
3. Keep `BOT_TOKEN` private. Do not share `.env` or `data/` files.
4. Restart the bot and send `/owner` in the bot's private chat.
5. Try `/cast 🌸 MoodBloom update: hello everyone!`; inspect the preview and confirm only when ready.

### Safe upgrade
- Stop the running bot before replacing source files.
- Back up the current `.env` and `data/` folder.
- Upload the release source files and `requirements.txt`, but preserve your existing `.env` and `data/`.
- Update dependencies and run only one bot process.
- Test first in a private test group. Telegram can reject sends to users who have not started the bot, blocked it, or to groups where the bot is no longer present/allowed to post.
