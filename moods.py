import random


# ============================================================
# MOOD DATABASE
# ============================================================

MOODS = {

    "happy": {
        "emoji": "😊",
        "name": "Happy",
        "score": 5,
        "category": "positive",

        "responses": [
            "That's wonderful! 🌸 Enjoy this good moment.",
            "A happy moment deserves to be enjoyed fully ✨",
            "Your positive energy is beautiful today 💖",
            "Keep enjoying this little spark of happiness 🌈",
            "It's nice to see a little sunshine in your day ☀️",
        ],

        "activities": [
            "Listen to your favorite song 🎵",
            "Write down one thing you're grateful for 💖",
            "Share your good mood with someone 😊",
            "Take a few minutes to enjoy the moment 🌸",
            "Do something creative while your energy is high 🎨",
        ],

        "study_tips": [
            "Use this positive energy for a short focused study session 📚",
            "Pick one small topic and finish it while your motivation is high 🎯",
        ],
    },


    "sad": {
        "emoji": "😔",
        "name": "Sad",
        "score": 2,
        "category": "low",

        "responses": [
            "It's okay to have a difficult moment. Be gentle with yourself 🌸",
            "You don't have to force yourself to feel happy right now 💙",
            "Take things one small step at a time 🌱",
            "A difficult moment doesn't define your whole day 🌈",
            "Give yourself some patience today. Small steps are enough 🌿",
        ],

        "activities": [
            "Take a few slow breaths and relax 🌿",
            "Listen to something calming 🎵",
            "Write down what is on your mind ✍️",
            "Take a short break from your screen 🌱",
            "Talk to someone you trust if you feel like sharing 💬",
        ],

        "study_tips": [
            "If studying feels difficult, try just 10 minutes of one easy topic 📚",
            "Break your study task into one very small step 🎯",
        ],
    },


    "angry": {
        "emoji": "😡",
        "name": "Angry",
        "score": 2,
        "category": "low",

        "responses": [
            "Take a moment before reacting. Give yourself some space 🌿",
            "Strong emotions can pass. Slow down and breathe 💙",
            "A short pause can help you respond more calmly 🌸",
            "Give yourself a little time before making decisions 🌱",
            "It's okay to step away for a moment and reset 🧘",
        ],

        "activities": [
            "Take 5 slow breaths 🌿",
            "Step away from the situation for a few minutes 🚶",
            "Drink some water 💧",
            "Write down what is bothering you ✍️",
            "Give yourself a quiet moment before responding 💙",
        ],

        "study_tips": [
            "Take a short reset break, then return to one small study task 📚",
            "Write down the next single thing you need to complete 🎯",
        ],
    },


    "tired": {
        "emoji": "😴",
        "name": "Tired",
        "score": 2,
        "category": "low",

        "responses": [
            "You deserve a little rest today 🌙",
            "It's okay to slow down when your energy is low 🌸",
            "Don't forget that rest is part of productivity 💙",
            "Give yourself permission to take things slowly 🌿",
            "Your energy matters too. Take things at a comfortable pace 🌙",
        ],

        "activities": [
            "Take a short screen break 👀",
            "Drink some water 💧",
            "Stretch gently for a few minutes 🧘",
            "Get some quiet time if you can 🌙",
            "Do one simple task and then take a break 🌿",
        ],

        "study_tips": [
            "Try a short 15-minute study session instead of a long session 📚",
            "Review something familiar rather than starting a difficult topic 🎯",
        ],
    },


    "loved": {
        "emoji": "❤️",
        "name": "Loved",
        "score": 5,
        "category": "positive",

        "responses": [
            "That's a beautiful feeling. Hold onto this moment ❤️",
            "Feeling connected can make an ordinary day special 🌸",
            "Let yourself enjoy this warmth and positivity 💖",
            "Moments of connection are worth appreciating ✨",
            "It's beautiful when a day feels a little warmer ❤️",
        ],

        "activities": [
            "Send someone a kind message 💌",
            "Write down something you appreciate ❤️",
            "Share a smile with someone 😊",
            "Save this moment in your memory 🌸",
            "Tell someone you appreciate them 💖",
        ],

        "study_tips": [
            "Use this positive feeling as a little boost for your next study session 📚",
            "Study with a friend or share your progress with someone 💬",
        ],
    },


    "okay": {
        "emoji": "😐",
        "name": "Okay",
        "score": 3,
        "category": "neutral",

        "responses": [
            "Sometimes being okay is perfectly enough 🌱",
            "No need to force the day to be extraordinary 🌸",
            "Take the day one moment at a time ✨",
            "Maybe today is simply a calm day, and that's okay 💙",
            "A normal day is still a day worth appreciating 🌿",
        ],

        "activities": [
            "Listen to one song you enjoy 🎵",
            "Take a short walk 🚶",
            "Drink some water and stretch 💧",
            "Do one small thing that makes you smile 😊",
            "Spend a few quiet minutes away from your screen 🌿",
        ],

        "study_tips": [
            "Pick one small topic and study it for 20 minutes 📚",
            "Make a simple checklist for today's study goals 🎯",
        ],
    }
}


# ============================================================
# MOOD ALIASES
# ============================================================

MOOD_ALIASES = {

    "good": "happy",
    "great": "happy",
    "excited": "happy",
    "joyful": "happy",

    "down": "sad",
    "unhappy": "sad",

    "mad": "angry",
    "frustrated": "angry",

    "sleepy": "tired",
    "exhausted": "tired",

    "romantic": "loved",
    "connected": "loved",

    "fine": "okay",
    "normal": "okay",
    "alright": "okay",
}


# ============================================================
# QUOTES
# ============================================================

QUOTES = [

    "Small steps still move you forward. 🌱",

    "Every day is a new page. 📖",

    "You don't have to do everything at once. 🌸",

    "Progress can be quiet and still meaningful. ✨",

    "Give yourself credit for the little things. 💖",

    "A calm mind can see new possibilities. 🌿",

    "One good moment can brighten an entire day. 🌈",

    "Keep going, one step at a time. 🚀",

    "Consistency matters more than perfection. 🌱",

    "Your pace does not have to match anyone else's. 💙",

    "Even an ordinary day can contain a good moment. ✨",

    "Start where you are and take the next small step. 🌸",
]


# ============================================================
# MOTIVATIONS
# ============================================================

MOTIVATIONS = [

    "You can take things one step at a time. 💪",

    "Keep going. Your effort matters. 🌱",

    "You don't need to be perfect to make progress. ✨",

    "Start small and keep moving forward. 🚀",

    "Believe in your ability to learn and grow. 💖",

    "Today's small effort can become tomorrow's progress. 🌸",

    "Keep showing up for yourself. 🔥",

    "You are allowed to learn at your own pace. 🌿",

    "One focused step is better than waiting for perfect motivation. 🎯",

    "Your progress is built from small moments of effort. 💪",

    "Keep learning, keep improving, keep moving. 🚀",

    "You don't have to finish everything today. Just start. 🌱",
]


# ============================================================
# ACTIVITIES
# ============================================================

ACTIVITIES = [

    "Drink a glass of water 💧",

    "Take a short walk 🚶",

    "Listen to your favorite song 🎵",

    "Stretch gently for a few minutes 🧘",

    "Write down one thing you're grateful for ✍️",

    "Take a short screen break 👀",

    "Organize one small part of your room 🧹",

    "Spend a few minutes doing something creative 🎨",

    "Talk to someone you enjoy being around 💬",

    "Take a few slow breaths 🌿",

    "Write down one thing you want to accomplish today 🎯",

    "Take a few quiet minutes for yourself 🌸",
]


# ============================================================
# GROUP-FRIENDLY ACTIVITIES
# ============================================================

GROUP_ACTIVITIES = [

    "Ask everyone in the group to share one positive word 🌈",

    "Start a quick 'how is everyone doing?' check-in 💬",

    "Share one song recommendation with the group 🎵",

    "Ask everyone to mention one small win from today 🏆",


    "Ask everyone to share one study goal for today 📚",

    "Send a simple appreciation message to someone in the group 💖",

    "Start a 10-minute focused study challenge 📖",
]


# ============================================================
# DAILY QUESTIONS
# ============================================================

DAILY_QUESTIONS = [

    "What is one good thing that happened today? 🌸",

    "What is one small goal you want to complete today? 🎯",

    "What are you looking forward to? ✨",

    "What made you smile today? 😊",

    "What is one thing you learned today? 📚",

    "What is one thing you are grateful for? 💖",

    "If you could improve one thing about today, what would it be? 🌱",

    "What song matches your mood today? 🎵",

    "What is one small win you had today? 🏆",

    "What would make the rest of your day better? 🌈",
]


# ============================================================
# SAFE GROUP GAMES
# ============================================================

GROUP_GAMES = [

    {
        "type": "would_you_rather",
        "question": "Would you rather have unlimited music or unlimited movies? 🎵🎬"
    },

    {
        "type": "would_you_rather",
        "question": "Would you rather study early morning or late evening? 🌅🌙"
    },

    {
        "type": "question",
        "question": "Describe your current mood using only 3 emojis. 😄"
    },

    {
        "type": "question",
        "question": "What's one thing everyone should try learning? 🧠"
    },
]


# ============================================================
# NORMALIZE MOOD
# ============================================================

def normalize_mood(mood_key):

    if not mood_key:
        return None

    mood_key = str(
        mood_key
    ).strip().lower()

    if mood_key in MOODS:
        return mood_key

    return MOOD_ALIASES.get(
        mood_key
    )


# ============================================================
# MOOD RESPONSE
# ============================================================

def get_mood_response(
    mood_key,
    previous_mood=None
):
    """
    Returns a response and activity based on current mood.

    previous_mood is used to personalize
    mood transition responses.
    """

    mood_key = normalize_mood(
        mood_key
    )

    mood = MOODS.get(
        mood_key
    )

    if not mood:

        return (
            "Take a moment for yourself 🌸",
            random.choice(
                ACTIVITIES
            )
        )

    responses = mood.get(
        "responses",
        []
    )

    activities = mood.get(
        "activities",
        []
    )

    response = random.choice(
        responses
    )

    activity = random.choice(
        activities
    )

    previous_mood = normalize_mood(
        previous_mood
    )

    if (
        previous_mood
        and previous_mood != mood_key
    ):

        previous = MOODS.get(
            previous_mood
        )

        if previous:

            previous_name = previous.get(
                "name",
                previous_mood.title()
            )

            response = (
                response
                + "\n\n"
                + f"🌱 Your mood changed from "
                + f"**{previous_name}** to "
                + f"**{mood['name']}**."
            )

    return response, activity


# ============================================================
# MOOD INFO
# ============================================================

def get_mood_info(mood_key):

    mood_key = normalize_mood(
        mood_key
    )

    return MOODS.get(
        mood_key,
        {
            "emoji": "🌸",
            "name": "Unknown",
            "score": 3,
            "category": "neutral",
            "responses": [],
            "activities": [],
            "study_tips": [],
        }
    )


# ============================================================
# MOOD SCORE
# ============================================================

def get_mood_score(mood_key):

    mood = get_mood_info(
        mood_key
    )

    try:

        return int(
            mood.get(
                "score",
                3
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return 3


# ============================================================
# MOOD CATEGORY
# ============================================================

def get_mood_category(mood_key):

    mood = get_mood_info(
        mood_key
    )

    return mood.get(
        "category",
        "neutral"
    )


# ============================================================
# MOOD EMOJI
# ============================================================

def get_mood_emoji(mood_key):

    mood = get_mood_info(
        mood_key
    )

    return mood.get(
        "emoji",
        "🌸"
    )


# ============================================================
# MOOD NAME
# ============================================================

def get_mood_name(mood_key):

    mood = get_mood_info(
        mood_key
    )

    return mood.get(
        "name",
        "Unknown"
    )


# ============================================================
# STUDY TIP
# ============================================================

def get_study_tip(mood_key):

    mood_key = normalize_mood(
        mood_key
    )

    mood = MOODS.get(
        mood_key
    )

    if not mood:
        return random.choice(
            [
                "Take one small study step today 📚",
                "Focus on one topic at a time 🎯",
            ]
        )

    tips = mood.get(
        "study_tips",
        []
    )

    if not tips:

        return (
            "Take one small study step today 📚"
        )

    return random.choice(
        tips
    )


# ============================================================
# RANDOM CONTENT
# ============================================================

def random_quote():

    return random.choice(
        QUOTES
    )


def random_motivation():

    return random.choice(
        MOTIVATIONS
    )


def random_activity():

    return random.choice(
        ACTIVITIES
    )


def random_group_activity():

    return random.choice(
        GROUP_ACTIVITIES
    )


def random_daily_question():

    return random.choice(
        DAILY_QUESTIONS
    )


def random_group_game():

    return random.choice(
        GROUP_GAMES
    )


# ============================================================
# MOOD LIST
# ============================================================

def get_all_moods():

    return list(
        MOODS.keys()
    )


def get_mood_choices():

    choices = []

    for key, mood in MOODS.items():

        choices.append({
            "key": key,
            "emoji": mood.get(
                "emoji",
                "🌸"
            ),
            "name": mood.get(
                "name",
                key.title()
            ),
            "score": mood.get(
                "score",
                3
            ),
        })

    return choices