# MoodBloom 4.2 — Premium Reminder Edition

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
