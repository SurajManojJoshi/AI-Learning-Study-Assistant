"""
Learning Pathways Module — Full Rebuild
Features:
  - Weekly roadmap generation via Gemini
  - YouTube channel recommendations per topic
  - Best website / resource recommendations
  - Wikipedia-based topic summary & Q&A
  - YouTube video notes (transcript summary) via Gemini
"""

import re
import json
from typing import Dict, Any, Optional, List
from config import generate_gemini_text

# ─────────────────────────────────────────────────────────────────────────────
# YouTube channel recommendations (curated, always-correct links)
# ─────────────────────────────────────────────────────────────────────────────
YT_CHANNELS: Dict[str, List[Dict[str, str]]] = {
    "Python Programming": [
        {"name": "Corey Schafer",          "url": "https://www.youtube.com/@coreyms",           "why": "Best in-depth Python tutorials, OOP, Flask, Django"},
        {"name": "Tech With Tim",           "url": "https://www.youtube.com/@TechWithTim",        "why": "Beginner to advanced Python + AI projects"},
        {"name": "Sentdex",                 "url": "https://www.youtube.com/@sentdex",            "why": "Python for data, ML, finance, Pygame"},
        {"name": "freeCodeCamp",            "url": "https://www.youtube.com/@freecodecamp",       "why": "Full Python courses from scratch (free)"},
        {"name": "ArjanCodes",              "url": "https://www.youtube.com/@ArjanCodes",         "why": "Clean code, design patterns, advanced Python"},
    ],
    "Machine Learning": [
        {"name": "Andrej Karpathy",         "url": "https://www.youtube.com/@AndrejKarpathy",     "why": "Deep learning from first principles by an OpenAI legend"},
        {"name": "StatQuest (Josh Starmer)","url": "https://www.youtube.com/@statquest",          "why": "Best visual explanations of ML/stats concepts"},
        {"name": "3Blue1Brown",             "url": "https://www.youtube.com/@3blue1brown",        "why": "Neural networks & math beautifully animated"},
        {"name": "Krish Naik",              "url": "https://www.youtube.com/@krishnaik06",        "why": "End-to-end ML projects & interview prep"},
        {"name": "Sentdex",                 "url": "https://www.youtube.com/@sentdex",            "why": "Practical ML & deep learning coding"},
    ],
    "Web Development": [
        {"name": "Traversy Media",          "url": "https://www.youtube.com/@TraversyMedia",      "why": "Full stack web dev crash courses"},
        {"name": "Fireship",                "url": "https://www.youtube.com/@Fireship",           "why": "100-second concept videos + full project builds"},
        {"name": "Kevin Powell",            "url": "https://www.youtube.com/@KevinPowell",        "why": "The best CSS teacher on YouTube"},
        {"name": "Academind",               "url": "https://www.youtube.com/@academind",          "why": "React, Angular, Node, Vue in depth"},
        {"name": "Web Dev Simplified",      "url": "https://www.youtube.com/@WebDevSimplified",   "why": "Clear, concise JavaScript & React tutorials"},
    ],
    "Data Science": [
        {"name": "Ken Jee",                 "url": "https://www.youtube.com/@KenJee_ds",          "why": "Data science career + projects"},
        {"name": "Alex The Analyst",        "url": "https://www.youtube.com/@AlexTheAnalyst",     "why": "SQL, Excel, Power BI, Python for analysts"},
        {"name": "Luke Barousse",           "url": "https://www.youtube.com/@LukeBarousse",       "why": "Data analyst roadmap & real job insights"},
        {"name": "StatQuest (Josh Starmer)","url": "https://www.youtube.com/@statquest",          "why": "Statistics & ML made simple with visuals"},
        {"name": "freeCodeCamp",            "url": "https://www.youtube.com/@freecodecamp",       "why": "Full data science bootcamp videos"},
    ],
    "Cloud Computing": [
        {"name": "TechWorld with Nana",     "url": "https://www.youtube.com/@TechWorldwithNana",  "why": "DevOps, Kubernetes, Docker explained clearly"},
        {"name": "A Cloud Guru",            "url": "https://www.youtube.com/@ACloudGuru",         "why": "AWS, Azure, GCP certification prep"},
        {"name": "NetworkChuck",            "url": "https://www.youtube.com/@NetworkChuck",       "why": "Fun & engaging cloud, networking, Linux videos"},
        {"name": "freeCodeCamp",            "url": "https://www.youtube.com/@freecodecamp",       "why": "Full AWS/Azure courses free"},
        {"name": "Abhishek Veeramalla",     "url": "https://www.youtube.com/@AbhishekVeeramalla", "why": "DevOps & cloud hands-on projects"},
    ],
    "Database Systems": [
        {"name": "CMU Database Group",      "url": "https://www.youtube.com/@CMUDatabaseGroup",   "why": "University-level database course lectures"},
        {"name": "Alex The Analyst",        "url": "https://www.youtube.com/@AlexTheAnalyst",     "why": "SQL from beginner to advanced"},
        {"name": "Kudvenkat",               "url": "https://www.youtube.com/@kudvenkat",          "why": "SQL Server & C# tutorials in depth"},
        {"name": "freeCodeCamp",            "url": "https://www.youtube.com/@freecodecamp",       "why": "Full SQL & database design courses"},
        {"name": "Caleb Curry",             "url": "https://www.youtube.com/@calebbcurry",        "why": "Database design & normalization explained well"},
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# Best websites per topic (curated)
# ─────────────────────────────────────────────────────────────────────────────
WEBSITES: Dict[str, List[Dict[str, str]]] = {
    "Python Programming": [
        {"name": "docs.python.org",       "url": "https://docs.python.org/3/",                "what": "Official Python docs"},
        {"name": "Real Python",           "url": "https://realpython.com",                    "what": "In-depth tutorials & articles"},
        {"name": "Python.org tutorials",  "url": "https://docs.python.org/3/tutorial/",       "what": "Official beginner tutorial"},
        {"name": "LeetCode",              "url": "https://leetcode.com",                      "what": "Practice coding problems"},
        {"name": "freeCodeCamp",          "url": "https://www.freecodecamp.org",              "what": "Free full courses"},
    ],
    "Machine Learning": [
        {"name": "fast.ai",               "url": "https://www.fast.ai",                       "what": "Top-down practical deep learning"},
        {"name": "Kaggle",                "url": "https://www.kaggle.com/learn",              "what": "Free ML courses + competitions"},
        {"name": "scikit-learn docs",     "url": "https://scikit-learn.org/stable/",          "what": "Official ML library docs"},
        {"name": "Papers With Code",      "url": "https://paperswithcode.com",                "what": "Latest ML papers + code"},
        {"name": "Google ML Crash Course","url": "https://developers.google.com/machine-learning/crash-course", "what": "Free ML course by Google"},
    ],
    "Web Development": [
        {"name": "MDN Web Docs",          "url": "https://developer.mozilla.org",             "what": "The bible of web development"},
        {"name": "css-tricks.com",        "url": "https://css-tricks.com",                    "what": "CSS tips, tricks, flexbox, grid"},
        {"name": "javascript.info",       "url": "https://javascript.info",                   "what": "Best free JavaScript textbook"},
        {"name": "roadmap.sh",            "url": "https://roadmap.sh",                        "what": "Visual developer roadmaps"},
        {"name": "freeCodeCamp",          "url": "https://www.freecodecamp.org",              "what": "Full web dev curriculum free"},
    ],
    "Data Science": [
        {"name": "Kaggle Learn",          "url": "https://www.kaggle.com/learn",              "what": "Free micro-courses in data science"},
        {"name": "Towards Data Science",  "url": "https://towardsdatascience.com",            "what": "Articles & tutorials by practitioners"},
        {"name": "DataCamp",              "url": "https://www.datacamp.com",                  "what": "Interactive data science courses"},
        {"name": "Mode Analytics",        "url": "https://mode.com/sql-tutorial/",            "what": "Interactive SQL tutorial"},
        {"name": "StatLearning (ESL)",    "url": "https://web.stanford.edu/~hastie/ElemStatLearn/", "what": "Free stats/ML textbook from Stanford"},
    ],
    "Cloud Computing": [
        {"name": "AWS Free Tier",         "url": "https://aws.amazon.com/free/",              "what": "Practice on real AWS free"},
        {"name": "Google Cloud Skills",   "url": "https://cloudskillsboost.google",           "what": "Free GCP labs & courses"},
        {"name": "Microsoft Learn",       "url": "https://learn.microsoft.com/azure",         "what": "Free Azure learning paths"},
        {"name": "KodeKloud",             "url": "https://kodekloud.com",                     "what": "Hands-on DevOps & cloud labs"},
        {"name": "roadmap.sh/devops",     "url": "https://roadmap.sh/devops",                 "what": "DevOps learning roadmap"},
    ],
    "Database Systems": [
        {"name": "SQLZoo",                "url": "https://sqlzoo.net",                        "what": "Interactive SQL exercises"},
        {"name": "Mode SQL Tutorial",     "url": "https://mode.com/sql-tutorial/",            "what": "Beginner to advanced SQL"},
        {"name": "DB-Fiddle",             "url": "https://www.db-fiddle.com",                 "what": "Run SQL online in browser"},
        {"name": "Use The Index, Luke",   "url": "https://use-the-index-luke.com",            "what": "SQL indexing & performance deep dive"},
        {"name": "MongoDB University",    "url": "https://learn.mongodb.com",                 "what": "Free official MongoDB courses"},
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# Weekly roadmap generator
# ─────────────────────────────────────────────────────────────────────────────
def generate_weekly_roadmap(topic: str, level: str, weeks: int, hours_per_week: float) -> str:
    """Generate a detailed week-by-week learning plan via Gemini."""
    system_prompt = (
        "You are an expert curriculum designer. "
        "Create realistic, actionable, week-by-week learning plans with clear milestones."
    )
    prompt = (
        f"Create a detailed {weeks}-week learning roadmap for: **{topic}**\n"
        f"Student level: {level}\n"
        f"Available time: {hours_per_week} hours/week\n\n"
        f"For EACH week provide:\n"
        f"### Week N: [Title]\n"
        f"**Goal:** one sentence goal for the week\n"
        f"**Topics to cover:** bullet list of 3-5 specific topics/concepts\n"
        f"**Daily tasks:** what to do each day (Mon-Fri style breakdown)\n"
        f"**Project/Practice:** one hands-on mini task or exercise\n"
        f"**Milestone:** how to know you've completed this week successfully\n\n"
        f"After all weeks add:\n"
        f"### Final Project\n"
        f"A capstone project idea that uses everything learned.\n\n"
        f"### 3 Pro Tips\n"
        f"Practical study tips specific to learning {topic}.\n\n"
        f"Be specific, actionable, and realistic. No vague advice."
    )
    try:
        return generate_gemini_text(prompt, system_instruction=system_prompt)
    except Exception as e:
        return _fallback_weekly_plan(topic, level, weeks, hours_per_week)


def _fallback_weekly_plan(topic: str, level: str, weeks: int, hours_per_week: float) -> str:
    lines = [f"## {weeks}-Week Roadmap: {topic}  ({level} · {hours_per_week} hrs/week)\n"]
    for w in range(1, weeks + 1):
        if w == 1:
            title = "Foundations & Setup"
            tasks = ["Install tools & set up environment", "Read official getting-started guide",
                     "Complete 1 beginner tutorial", "Take notes on core concepts"]
        elif w == weeks:
            title = "Final Project & Review"
            tasks = ["Build a capstone project", "Review all key concepts",
                     "Fix gaps in knowledge", "Share or deploy your project"]
        else:
            title = f"Core Topic — Module {w-1}"
            tasks = [f"Study {topic} sub-topic {w-1}", "Work through practice exercises",
                     "Build a small demo", "Write a short summary of what you learned"]
        lines.append(f"### Week {w}: {title}")
        lines.append(f"**Goal:** Make solid progress on {topic} module {w}.")
        lines.append("**Topics:**")
        for t in tasks:
            lines.append(f"- {t}")
        lines.append(f"**Milestone:** Complete the mini project and review notes.\n")
    lines.append("### Final Project")
    lines.append(f"Build a real-world application that demonstrates your {topic} skills.\n")
    lines.append("### 3 Pro Tips")
    lines.append("1. Code every day, even 20 minutes counts.")
    lines.append("2. Teach concepts to someone else to solidify understanding.")
    lines.append("3. Build projects — reading alone won't make you fluent.")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# YouTube channel recommendations (AI for unknown topics)
# ─────────────────────────────────────────────────────────────────────────────
def get_yt_channels(topic: str) -> List[Dict[str, str]]:
    """Return curated channels if known, else ask Gemini."""
    for key, channels in YT_CHANNELS.items():
        if key.lower() == topic.lower():
            return channels
    # Gemini fallback for unknown topics
    prompt = (
        f"List 5 of the best YouTube channels for learning '{topic}'.\n"
        f"For each provide: channel name, YouTube URL, and one sentence on why it's great.\n"
        f"Output as JSON array: [{{'name':..., 'url':..., 'why':...}}]"
    )
    try:
        raw = generate_gemini_text(prompt)
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        m = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if m:
            return json.loads(m.group(0))
    except Exception:
        pass
    return [
        {"name": f"Search: '{topic} tutorial'", "url": f"https://www.youtube.com/results?search_query={topic.replace(' ','+')}+tutorial", "why": "Search YouTube directly"},
        {"name": "freeCodeCamp",               "url": "https://www.youtube.com/@freecodecamp", "why": "Long-form free courses"},
    ]


def get_websites(topic: str) -> List[Dict[str, str]]:
    """Return curated sites if known, else ask Gemini."""
    for key, sites in WEBSITES.items():
        if key.lower() == topic.lower():
            return sites
    prompt = (
        f"List 5 of the best free websites/resources for learning '{topic}'.\n"
        f"For each provide: site name, URL, one sentence on what it offers.\n"
        f"Output as JSON array: [{{'name':..., 'url':..., 'what':...}}]"
    )
    try:
        raw = generate_gemini_text(prompt)
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        m = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if m:
            return json.loads(m.group(0))
    except Exception:
        pass
    return [
        {"name": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org", "what": "Tutorials & articles"},
        {"name": "freeCodeCamp",  "url": "https://www.freecodecamp.org",  "what": "Free courses"},
        {"name": "Khan Academy",  "url": "https://www.khanacademy.org",   "what": "Foundational concepts"},
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Wikipedia-based answering
# ─────────────────────────────────────────────────────────────────────────────
def get_wikipedia_summary(topic: str) -> Dict[str, Any]:
    """Fetch Wikipedia summary for a topic using the Wikipedia REST API."""
    import urllib.request, urllib.parse, urllib.error
    try:
        slug = urllib.parse.quote(topic.replace(" ", "_"))
        url  = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
        req  = urllib.request.Request(url, headers={"User-Agent": "StudyAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        return {
            "title":   data.get("title", topic),
            "summary": data.get("extract", ""),
            "url":     data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            "image":   data.get("thumbnail", {}).get("source", ""),
            "found":   True,
        }
    except Exception as e:
        return {"title": topic, "summary": "", "url": "", "image": "", "found": False, "error": str(e)}


def answer_from_wikipedia(topic: str, question: str) -> str:
    """Fetch Wikipedia content then answer a question using Gemini."""
    wiki = get_wikipedia_summary(topic)
    if not wiki["found"] or not wiki["summary"]:
        return f"Could not find a Wikipedia article for '{topic}'. Try a more specific term."

    system_prompt = (
        "You are a knowledgeable tutor. Answer the student's question accurately "
        "using the provided Wikipedia content. Be concise and clear."
    )
    prompt = (
        f"Wikipedia article: **{wiki['title']}**\n\n"
        f"{wiki['summary']}\n\n"
        f"Student question: {question}\n\n"
        f"Answer based on the Wikipedia content above:"
    )
    try:
        answer = generate_gemini_text(prompt, system_instruction=system_prompt)
        return answer
    except Exception as e:
        # If Gemini fails, just return the Wikipedia summary
        return wiki["summary"]


# ─────────────────────────────────────────────────────────────────────────────
# YouTube notes generator
# ─────────────────────────────────────────────────────────────────────────────
def extract_yt_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"embed\/([0-9A-Za-z_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def generate_yt_notes(youtube_url: str, extra_context: str = "") -> Dict[str, Any]:
    """
    Generate study notes for a YouTube video.
    Since we can't access the actual transcript without the youtube_transcript_api,
    we use Gemini to generate comprehensive notes based on the video URL + title context.
    Asks the user to optionally paste a description or key points.
    """
    video_id = extract_yt_video_id(youtube_url)
    if not video_id:
        return {"success": False, "error": "Invalid YouTube URL. Could not extract video ID."}

    video_url_clean = f"https://www.youtube.com/watch?v={video_id}"

    # Try to get video metadata via oEmbed (no API key needed)
    title = "YouTube Video"
    try:
        import urllib.request, urllib.parse
        oembed_url = f"https://www.youtube.com/oembed?url={urllib.parse.quote(video_url_clean)}&format=json"
        req = urllib.request.Request(oembed_url, headers={"User-Agent": "StudyAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            meta = json.loads(resp.read().decode())
            title = meta.get("title", "YouTube Video")
    except Exception:
        pass

    context_block = ""
    if extra_context.strip():
        context_block = (
            f"\n\nThe user has provided these notes/description about the video:\n"
            f"{extra_context.strip()}\n\n"
            "Use this to make the notes more accurate."
        )

    system_prompt = (
        "You are an expert note-taker and educator. "
        "Generate comprehensive, well-structured study notes from educational content."
    )
    prompt = (
        f"Generate detailed study notes for this YouTube video:\n"
        f"Title: {title}\n"
        f"URL: {video_url_clean}\n"
        f"{context_block}\n"
        f"Create notes as if you watched the full video. Include:\n"
        f"## 📺 Video: {title}\n"
        f"**Source:** {video_url_clean}\n\n"
        f"### 🎯 Key Concepts\n"
        f"List the main concepts explained in the video.\n\n"
        f"### 📝 Detailed Notes\n"
        f"Section-by-section breakdown of what was taught.\n\n"
        f"### 💡 Key Takeaways\n"
        f"5-7 bullet points — the most important things to remember.\n\n"
        f"### ❓ Practice Questions\n"
        f"3-5 questions to test understanding of the video content.\n\n"
        f"### 🔗 Related Topics to Explore\n"
        f"3 related topics to study next."
    )

    try:
        notes_text = generate_gemini_text(prompt, system_instruction=system_prompt)
        return {
            "success":    True,
            "title":      title,
            "video_id":   video_id,
            "url":        video_url_clean,
            "notes":      notes_text,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# DETAILED INTERACTIVE LESSONS
# ─────────────────────────────────────────────────────────────────────────────

# Predefined detailed lessons for common Python topics (work offline)
_PYTHON_LESSONS = {
    "Variables & Data Types": (
        "## 📚 Lesson: Variables & Data Types\n\n"
        "### What is a Variable?\n"
        "A variable is a **named container** that stores a value in memory. "
        "Think of it like a labeled box — you put something in, and later you can find it by its label.\n\n"
        "### Creating Variables in Python\n"
        "Python is dynamically typed — you don't declare the type. Just assign:\n"
        "```python\n"
        "name = \"Alice\"        # string (str)\n"
        "age = 25               # integer (int)\n"
        "height = 5.9           # float (float)\n"
        "is_student = True      # boolean (bool)\n"
        "```\n\n"
        "### Core Data Types\n"
        "| Type | Example | Description |\n"
        "|------|---------|-------------|\n"
        "| `int` | `42` | Whole numbers |\n"
        "| `float` | `3.14` | Decimal numbers |\n"
        "| `str` | `\"hello\"` | Text (use `'` or `\"`) |\n"
        "| `bool` | `True` / `False` | True/False values |\n"
        "| `list` | `[1, 2, 3]` | Ordered, mutable collection |\n"
        "| `dict` | `{\"a\": 1}` | Key-value pairs |\n"
        "| `tuple` | `(1, 2)` | Ordered, immutable collection |\n"
        "| `set` | `{1, 2, 3}` | Unordered, unique items |\n\n"
        "### Checking & Converting Types\n"
        "```python\n"
        "type(age)        # <class 'int'>\n"
        "str(42)          # '42'  — int to string\n"
        "int('15')        # 15    — string to int\n"
        "float('3.5')     # 3.5   — string to float\n"
        "```\n\n"
        "### ⚠️ Common Mistakes\n"
        "1. **Using a reserved keyword** as a variable name (`list = [1,2]` shadows the built-in)\n"
        "2. **Case sensitivity**: `Name` and `name` are DIFFERENT variables\n"
        "3. **Forgetting quotes**: `x = hello` → NameError. Use `x = \"hello\"`\n\n"
        "### 🎯 Practice Exercise\n"
        "Create variables for a person's name, age, and whether they like Python. "
        "Print them all in one sentence.\n"
        "**Answer:**\n"
        "```python\n"
        "name = \"Sam\"\n"
        "age = 20\n"
        "likes_python = True\n"
        "print(f\"{name} is {age} years old. Likes Python: {likes_python}\")\n"
        "```\n\n"
        "### ✅ Key Takeaways\n"
        "- Variables store values; Python figures out the type automatically\n"
        "- Use `type()` to check, and `int()/str()/float()` to convert\n"
        "- Names are case-sensitive and can't be reserved keywords"
    ),
    "Operators": (
        "## 📚 Lesson: Operators\n\n"
        "### What are Operators?\n"
        "Operators are **symbols that perform operations** on variables and values. "
        "Like `+` adds, `-` subtracts, `==` compares.\n\n"
        "### 1. Arithmetic Operators\n"
        "```python\n"
        "5 + 2    # 7   Addition\n"
        "5 - 2    # 3   Subtraction\n"
        "5 * 2    # 10  Multiplication\n"
        "5 / 2    # 2.5 Division (always returns float)\n"
        "5 // 2   # 2   Floor division (rounds down)\n"
        "5 % 2    # 1   Modulo (remainder)\n"
        "5 ** 2   # 25  Exponent (power)\n"
        "```\n\n"
        "### 2. Comparison Operators (return True/False)\n"
        "```python\n"
        "5 == 5   # True   Equal\n"
        "5 != 3   # True   Not equal\n"
        "5 > 3    # True   Greater than\n"
        "5 < 3    # False  Less than\n"
        "5 >= 5   # True   Greater or equal\n"
        "5 <= 4   # False  Less or equal\n"
        "```\n\n"
        "### 3. Logical Operators\n"
        "```python\n"
        "True and False   # False  Both must be True\n"
        "True or False    # True   At least one True\n"
        "not True         # False  Reverses\n"
        "```\n\n"
        "### 4. Assignment Operators\n"
        "```python\n"
        "x = 5      # Assign\n"
        "x += 3     # x = x + 3 → 8\n"
        "x -= 2     # x = x - 2 → 6\n"
        "x *= 2     # x = x * 2 → 12\n"
        "```\n\n"
        "### ⚠️ Common Mistakes\n"
        "1. **`=` vs `==`**: `=` assigns, `==` compares. `if x = 5:` is an error.\n"
        "2. **Division always floats**: `4 / 2` gives `2.0` not `2`. Use `//` for integers.\n"
        "3. **Operator precedence**: `2 + 3 * 4` = `14` not `20` (multiplication first)\n\n"
        "### 🎯 Practice Exercise\n"
        "Calculate the area of a rectangle (length=10, width=5) and check if it's greater than 40.\n"
        "**Answer:**\n"
        "```python\n"
        "length, width = 10, 5\n"
        "area = length * width\n"
        "print(area > 40)  # True\n"
        "```\n\n"
        "### ✅ Key Takeaways\n"
        "- Arithmetic: `+ - * / // % **`\n"
        "- Comparison: `== != > < >= <=` → always return bool\n"
        "- Logical: `and or not`\n"
        "- `=` assigns, `==` compares"
    ),
    "Control Flow": (
        "## 📚 Lesson: Control Flow (if / elif / else)\n\n"
        "### What is Control Flow?\n"
        "Control flow lets your program **make decisions** and run different code based on conditions.\n\n"
        "### if / elif / else\n"
        "```python\n"
        "score = 85\n"
        "if score >= 90:\n"
        "    print(\"A\")\n"
        "elif score >= 80:\n"
        "    print(\"B\")\n"
        "elif score >= 70:\n"
        "    print(\"C\")\n"
        "else:\n"
        "    print(\"Fail\")\n"
        "# Output: B\n"
        "```\n\n"
        "### Indentation Matters!\n"
        "Python uses indentation (4 spaces) to define code blocks. No braces like other languages.\n"
        "```python\n"
        "if True:\n"
        "    print(\"inside if\")     # ← must be indented\n"
        "print(\"always runs\")      # ← not inside if\n"
        "```\n\n"
        "### Nested Conditions\n"
        "```python\n"
        "age = 20\n"
        "has_id = True\n"
        "if age >= 18:\n"
        "    if has_id:\n"
        "        print(\"Entry allowed\")\n"
        "    else:\n"
        "        print(\"Need ID\")\n"
        "```\n\n"
        "### Ternary (one-liner if)\n"
        "```python\n"
        "status = \"Adult\" if age >= 18 else \"Minor\"\n"
        "```\n\n"
        "### ⚠️ Common Mistakes\n"
        "1. **Missing colon** `:` after `if` / `elif` / `else`\n"
        "2. **Inconsistent indentation** — mixing tabs and spaces causes errors\n"
        "3. **Using `=` instead of `==`** in conditions\n\n"
        "### 🎯 Practice Exercise\n"
        "Ask a user's temperature. If above 100°F, print \"Fever\". Between 97-100, print \"Normal\". Below 97, print \"Low\".\n"
        "**Answer:**\n"
        "```python\n"
        "temp = float(input(\"Temperature: \"))\n"
        "if temp > 100:\n"
        "    print(\"Fever\")\n"
        "elif temp >= 97:\n"
        "    print(\"Normal\")\n"
        "else:\n"
        "    print(\"Low\")\n"
        "```\n\n"
        "### ✅ Key Takeaways\n"
        "- `if/elif/else` for decisions\n"
        "- Always end the condition line with `:`\n"
        "- Indent code blocks with 4 spaces\n"
        "- Use ternary for simple if/else assignments"
    ),
    "Functions": (
        "## 📚 Lesson: Functions\n\n"
        "### What is a Function?\n"
        "A function is a **reusable block of code** that does one specific task. "
        "You define it once, call it many times.\n\n"
        "### Defining & Calling\n"
        "```python\n"
        "def greet(name):\n"
        "    return f\"Hello, {name}!\"\n"
        "\n"
        "print(greet(\"Alice\"))   # Hello, Alice!\n"
        "print(greet(\"Bob\"))     # Hello, Bob!\n"
        "```\n\n"
        "### Parameters & Arguments\n"
        "```python\n"
        "# Default values\n"
        "def greet(name, greeting=\"Hello\"):\n"
        "    return f\"{greeting}, {name}!\"\n"
        "\n"
        "greet(\"Sam\")                # Hello, Sam!\n"
        "greet(\"Sam\", \"Hi\")          # Hi, Sam!\n"
        "\n"
        "# Multiple returns (tuple)\n"
        "def min_max(nums):\n"
        "    return min(nums), max(nums)\n"
        "\n"
        "lo, hi = min_max([3, 1, 9, 4])\n"
        "```\n\n"
        "### *args and **kwargs\n"
        "```python\n"
        "def total(*nums):           # any number of positional args\n"
        "    return sum(nums)\n"
        "total(1, 2, 3)              # 6\n"
        "\n"
        "def info(**data):           # any number of keyword args\n"
        "    for k, v in data.items():\n"
        "        print(f\"{k}: {v}\")\n"
        "info(name=\"Sam\", age=20)\n"
        "```\n\n"
        "### ⚠️ Common Mistakes\n"
        "1. **Forgetting `return`** — without it, the function returns `None`\n"
        "2. **Defining after calling** — function must be defined before it's called\n"
        "3. **Mutable default arguments**: `def f(items=[]):` is dangerous — the list persists between calls. Use `None` instead.\n\n"
        "### 🎯 Practice Exercise\n"
        "Write a function `is_even(n)` that returns `True` if even, `False` if odd.\n"
        "**Answer:**\n"
        "```python\n"
        "def is_even(n):\n"
        "    return n % 2 == 0\n"
        "\n"
        "print(is_even(4))   # True\n"
        "print(is_even(7))   # False\n"
        "```\n\n"
        "### ✅ Key Takeaways\n"
        "- `def name(params):` defines a function\n"
        "- `return` sends a value back; without it you get `None`\n"
        "- Default params: `def f(x=10):`\n"
        "- `*args` = many positional, `**kwargs` = many keyword"
    ),
    "Lists & Dicts": (
        "## 📚 Lesson: Lists & Dictionaries\n\n"
        "### Lists — Ordered, Mutable Collections\n"
        "```python\n"
        "fruits = [\"apple\", \"banana\", \"cherry\"]\n"
        "fruits[0]          # 'apple'  (0-indexed)\n"
        "fruits[-1]         # 'cherry' (last item)\n"
        "fruits.append(\"date\")   # add to end\n"
        "fruits.insert(0, \"avocado\")  # insert at index\n"
        "fruits.remove(\"banana\")\n"
        "len(fruits)        # 4\n"
        "```\n\n"
        "### Slicing Lists\n"
        "```python\n"
        "nums = [10, 20, 30, 40, 50]\n"
        "nums[1:4]    # [20, 30, 40]  (start to end-1)\n"
        "nums[:3]     # [10, 20, 30]  (first 3)\n"
        "nums[2:]     # [30, 40, 50]  (from index 2)\n"
        "nums[::-1]   # [50, 40, 30, 20, 10]  (reverse)\n"
        "```\n\n"
        "### Dictionaries — Key-Value Pairs\n"
        "```python\n"
        "person = {\"name\": \"Alice\", \"age\": 25, \"city\": \"NYC\"}\n"
        "person[\"name\"]          # 'Alice'\n"
        "person[\"email\"] = \"a@b.com\"   # add new key\n"
        "del person[\"city\"]       # remove key\n"
        "\"name\" in person       # True\n"
        "person.keys()          # dict_keys(['name', 'age'])\n"
        "person.values()        # dict_values(['Alice', 25])\n"
        "```\n\n"
        "### Looping Through Collections\n"
        "```python\n"
        "for item in fruits:\n"
        "    print(item)\n"
        "\n"
        "for key, value in person.items():\n"
        "    print(f\"{key}: {value}\")\n"
        "```\n\n"
        "### ⚠️ Common Mistakes\n"
        "1. **Index out of range**: `fruits[10]` → IndexError\n"
        "2. **Modifying while iterating**: don't add/remove during a for loop\n"
        "3. **KeyError**: `person[\"phone\"]` if key doesn't exist. Use `person.get(\"phone\", \"N/A\")` instead.\n\n"
        "### 🎯 Practice Exercise\n"
        "Create a list of 5 numbers, print only the even ones. Then create a dict of 3 friends and their ages.\n"
        "**Answer:**\n"
        "```python\n"
        "nums = [1, 2, 3, 4, 5, 6]\n"
        "evens = [n for n in nums if n % 2 == 0]\n"
        "print(evens)  # [2, 4, 6]\n"
        "\n"
        "friends = {\"Alice\": 25, \"Bob\": 30, \"Sam\": 22}\n"
        "for name, age in friends.items():\n"
        "    print(f\"{name} is {age}\")\n"
        "```\n\n"
        "### ✅ Key Takeaways\n"
        "- Lists: `[...]` — ordered, mutable, index with `[i]`\n"
        "- Dicts: `{key: val}` — fast lookup by key\n"
        "- Slice with `[start:end]`, reverse with `[::-1]`\n"
        "- Use `.get(key, default)` to avoid KeyErrors"
    ),
}


def get_detailed_lesson(topic: str, sub_topic: str) -> str:
    """
    Returns a full detailed lesson for a sub-topic.
    Uses predefined lessons when available, otherwise generates via Gemini.
    Each lesson includes: what it is, syntax/examples, common mistakes,
    practice exercise with answer, and key takeaways.
    """
    # Check predefined Python lessons first
    if sub_topic in _PYTHON_LESSONS:
        return _PYTHON_LESSONS[sub_topic]

    # Try case-insensitive match
    for key, lesson in _PYTHON_LESSONS.items():
        if key.lower() == sub_topic.lower():
            return lesson

    # Generate via Gemini for any other topic
    system_prompt = (
        "You are an expert programming tutor. "
        "Create clear, beginner-friendly lessons with real code examples. "
        "Always include syntax, examples, common mistakes, a practice exercise with answer, "
        "and key takeaways."
    )
    prompt = (
        f"Create a detailed beginner-friendly lesson on **'{sub_topic}'** "
        f"in the context of learning **'{topic}'**.\n\n"
        f"Use this exact structure:\n"
        f"## 📚 Lesson: {sub_topic}\n\n"
        f"### What is it?\n"
        f"A clear plain-English explanation (2-3 sentences).\n\n"
        f"### How to Use It (with syntax)\n"
        f"Show the syntax and 2-3 code examples with comments.\n\n"
        f"### Common Mistakes\n"
        f"List 3 common mistakes beginners make, with a one-line fix for each.\n\n"
        f"### 🎯 Practice Exercise\n"
        f"Give one hands-on exercise, then show the full answer with code.\n\n"
        f"### ✅ Key Takeaways\n"
        f"3-4 bullet points summarizing the most important things to remember."
    )
    try:
        return generate_gemini_text(prompt, system_instruction=system_prompt)
    except Exception as e:
        return (
            f"## 📚 Lesson: {sub_topic}\n\n"
            f"### What is it?\n"
            f"{sub_topic} is an important concept in {topic}.\n\n"
            f"### How to Learn\n"
            f"1. Search YouTube for \"{topic} {sub_topic} tutorial\"\n"
            f"2. Read the official documentation\n"
            f"3. Practice with small examples\n\n"
            f"### Practice\n"
            f"Try writing a small program that uses {sub_topic}.\n\n"
            f"### ✅ Key Takeaways\n"
            f"- {sub_topic} is fundamental to {topic}\n"
            f"- Practice with real examples\n"
            f"- Build small projects to apply what you learn"
        )
