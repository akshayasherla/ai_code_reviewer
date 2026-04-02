import reflex as rx

from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------- STATE ----------
class State(rx.State):
    current_page: str = "home"

    # Analyzer state
    code_input: str = ""
    language: str = ""
    quality_score: str = "N/A"
    issues: int = 0
    explanation: str = "Your results will appear here with simple explanation of errors and improvements."
    original_code: str = ""
    improved_code: str = ""
    last_code: str = ""
    last_result: str = ""

    # AI Assistant
    ai_input: str = ""
    ai_output: str = ""

    def set_ai_input(self, value):
        self.ai_input = value

    def run_ai(self):
        if not self.ai_input.strip():
            self.ai_output = "Please enter a prompt."
            return

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": self.ai_input}],
            )
            self.ai_output = response.choices[0].message.content

        except Exception as e:
            self.ai_output = f"AI Error: {str(e)}"

    # Navigation
    def set_home(self): self.current_page = "home"
    def set_analyzer(self): self.current_page = "analyzer"
    def set_ai(self): self.current_page = "ai"
    def set_history(self): self.current_page = "history"
    def set_about(self): self.current_page = "about"

    def set_code_input(self, value):
        self.code_input = value

    def set_language(self, value):
        self.language = value

    # ---------- ANALYZER ----------
    def analyze_code(self):
        self.original_code = self.code_input

        if not self.code_input.strip():
            self.quality_score = "0/10"
            self.issues = 1
            self.explanation = "No code provided."
            self.improved_code = ""
            self.last_code = self.code_input
            self.last_result = self.improved_code
            return

        issues = 0
        explanation_list = []

        code = self.code_input

        # ---------- BASIC CHECKS ----------
        if len(code.strip()) < 10:
            issues += 1
            explanation_list.append("Code is too short.")

        if self.language == "Python":
            if "print(" not in code:
                issues += 1
                explanation_list.append("Missing print statement.")

            if code.count("(") != code.count(")"):
               issues += 1
               explanation_list.append("Unbalanced parentheses.")

        elif self.language == "JavaScript":
            if "console.log" not in code:
                issues += 1
                explanation_list.append("Missing console.log.")
            if ";" not in code:
                issues += 1
                explanation_list.append("Missing semicolon.")

        elif self.language == "Java":
            if "System.out.println" not in code:
                issues += 1
                explanation_list.append("Missing System.out.println.")
            if "class" not in code:
                issues += 1
                explanation_list.append("Missing class structure.")

        # ---------- SCORE ----------
        if issues == 0:
            score = 10
            explanation_list.append("No issues found. Code looks good ✅")
        else:
            score = max(10 - issues * 2, 1)

        self.quality_score = f"{score}/10"
        self.issues = issues
        self.explanation = explanation_list[0]

        # ---------- AI IMPROVEMENT ----------
        prompt = f"""
You are an expert code reviewer.

Analyze the following {self.language} code:
---
{self.code_input}
---

Give:
1. Fixed version of code
2. Improved clean version
Only return code.
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
            )

            raw_output = response.choices[0].message.content

            cleaned = raw_output.replace("```python", "").replace("```", "")

            remove_words = [
                "### Fixed Version of Code",
                "### Improved Clean Version",
                "**Fixed Version of Code**",
                "**Improved Clean Version**",
                "1. Fixed version of code:",
                "2. Improved clean version:",
                "Fixed version of code:",
                "Improved clean version:"
            ]

            for word in remove_words:
                cleaned = cleaned.replace(word, "")

            self.improved_code = cleaned.strip()

        except Exception as e:
            self.improved_code = f"AI Error: {str(e)}"

        # ---------- SAVE HISTORY (ALWAYS LAST) ----------
        self.last_code = self.code_input
        self.last_result = self.improved_code.split("\n")[0]
# ---------- NAVBAR ----------
def navbar():
    return rx.hstack(
        rx.heading("AI Code Reviewer", size="6", color="white"),
        rx.spacer(),
        rx.hstack(
            rx.text("Home", on_click=State.set_home, cursor="pointer"),
            rx.text("Analyzer", on_click=State.set_analyzer, cursor="pointer"),
            rx.text("AI Assistant", on_click=State.set_ai, cursor="pointer"),
            rx.text("History", on_click=State.set_history, cursor="pointer"),
            rx.text("About", on_click=State.set_about, cursor="pointer"),
            spacing="6",
            color="#CBD5F5",
        ),
        padding="15px",
        border_bottom="1px solid #1E293B",
    )


# ---------- HOME PAGE ----------
def home_page():
    return rx.vstack(

        rx.vstack(
            rx.heading(
                "AI-Powered Code Intelligence",
                size="9",
                text_align="center",
            ),
            rx.text(
                "Analyze, fix, and improve your code with advanced AI-driven insights.",
                color="#94A3B8",
                text_align="center",
                max_width="600px",
            ),
            rx.hstack(
                rx.button(
                    "Start Analyzing",
                    on_click=State.set_analyzer,
                    bg="#6366F1",
                    color="white",
                    _hover={"bg": "#4F46E5"},
                ),
                rx.button(
                    "Try AI Assistant",
                    on_click=State.set_ai,
                    variant="outline",
                ),
                spacing="4",
            ),
            spacing="5",
            align="center",
            padding_top="80px",
        ),

        rx.grid(
            rx.box(
                rx.heading("Smart Analysis", size="5"),
                rx.text("Detect syntax errors and code issues instantly."),
                bg="#0F172A",
                padding="20px",
                border_radius="12px",
                width="100%",
            ),
            rx.box(
                rx.heading("Code Quality Score", size="5"),
                rx.text("Understand how good your code really is."),
                bg="#0F172A",
                padding="20px",
                border_radius="12px",
                width="100%",
            ),
            rx.box(
                rx.heading("AI Suggestions", size="5"),
                rx.text("Get improvements and optimized solutions."),
                bg="#0F172A",
                padding="20px",
                border_radius="12px",
                width="100%",
            ),
            columns="3",
            spacing="6",
            padding_top="60px",
            max_width="900px",
        ),

        rx.vstack(
            rx.heading("Why Use This Tool?", size="6"),
            rx.text(
                "Built for developers who want faster debugging, cleaner code, and smarter development workflows.",
                color="#94A3B8",
                text_align="center",
                max_width="700px",
            ),
            spacing="3",
            align="center",
            padding_top="60px",
        ),

        spacing="9",
        align="center",
        padding_bottom="60px",
    )


# ---------- ANALYZER PAGE ----------
def analyzer_page():
    return rx.vstack(

        rx.heading("Code Analyzer", size="8"),
        rx.text(
            "Paste your code below and get detailed analysis with clear explanations.",
            color="#94A3B8",
        ),

        rx.box(
            rx.vstack(
                rx.text("Paste your code:", color="#CBD5F5"),
                rx.text_area(
                    placeholder="Paste your code here...",
                    width="100%",
                    height="300px",
                    bg="#020617",
                    color="white",
                    on_change=State.set_code_input,
                ),
                rx.hstack(
                    rx.select(
                        ["Python", "JavaScript", "Java"],
                        placeholder="Select Language",
                        on_change=State.set_language,
                    ),
                    rx.button(
                        "Analyze Code",
                        on_click=State.analyze_code,
                        bg="#6366F1",
                        color="white",
                        _hover={"bg": "#4F46E5"},
                    ),
                    spacing="4",
                ),
                spacing="4",
            ),
            bg="#0F172A",
            padding="20px",
            border_radius="12px",
            width="100%",
            max_width="900px",
        ),

        rx.box(
            rx.vstack(
                rx.heading("Analysis Result", size="6"),
                rx.text(State.quality_score),
                rx.text(f"Issues Found: {State.issues}"),
                rx.divider(),
                rx.heading("Explanation", size="5"),
                rx.text(State.explanation, color="#94A3B8"),
                rx.divider(),
                rx.heading("Code Comparison", size="5"),
                rx.hstack(
                    rx.box(
                        rx.text(State.original_code),
                        bg="#020617",
                        padding="10px",
                        width="50%",
                    ),
                    rx.box(
                        rx.text(State.improved_code),
                        bg="#020617",
                        padding="10px",
                        width="50%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                spacing="4",
            ),
            bg="#0F172A",
            padding="20px",
            border_radius="12px",
            width="100%",
            max_width="900px",
        ),

        spacing="6",
        align="center",
        padding_top="40px",
        padding_bottom="60px",
    )


# ---------- OTHER PAGES ----------
def ai_page():
    return rx.vstack(
        rx.heading("AI Assistant", size="6"),
        rx.text(
            "Ask coding questions, get explanations, or generate code using AI.",
            color="#94A3B8",
        ),

        rx.box(
            rx.vstack(
                rx.text_area(
                    placeholder="Ask anything about code...",
                    width="100%",
                    height="150px",
                    bg="#020617",
                    color="white",
                    on_change=State.set_ai_input,
                ),
                rx.button(
                    "Run AI",
                    on_click=State.run_ai,
                    bg="#6366F1",
                    color="white",
                    _hover={"bg": "#4F46E5"},
                ),
                spacing="4",
            ),
            bg="#0F172A",
            padding="20px",
            border_radius="12px",
            width="100%",
            max_width="900px",
        ),

        rx.box(
            rx.vstack(
                rx.heading("AI Response", size="5"),
                rx.text(State.ai_output, color="#94A3B8"),
                spacing="3",
            ),
            bg="#0F172A",
            padding="20px",
            border_radius="12px",
            width="100%",
            max_width="900px",
        ),

        spacing="6",
        align="center",
        padding_top="40px",
        padding_bottom="60px",
    )

def history_page():
    return rx.vstack(

        rx.heading("History", size="8"),

        rx.text(
            "View your most recent analyzed code and AI improvements.",
            color="#94A3B8",
        ),

        rx.box(
            rx.vstack(
                rx.heading("Last Submitted Code", size="5"),
                rx.box(
                    rx.text(State.last_code),
                    rx.text(State.last_result),
                    bg="#020617",
                    padding="10px",
                ),
                rx.divider(),
                rx.heading("AI Improved Code", size="5"),
                rx.box(
                    rx.text(f"CODE: {State.last_code}"),
                    rx.text(f"RESULT: {State.last_result}"),
                    bg="#020617",
                    padding="10px",
                ),
                spacing="4",
            ),
            bg="#0F172A",
            padding="20px",
            border_radius="12px",
            width="100%",
            max_width="900px",
        ),

        spacing="6",
        align="center",
        padding_top="40px",
        padding_bottom="60px",
    )


def about_page():
    return rx.vstack(

        rx.heading("About This Project", size="8"),

        rx.text(
            "AI Code Reviewer is an intelligent platform designed to help developers write better, cleaner, and more efficient code using the power of artificial intelligence.",
            color="#94A3B8",
            max_width="800px",
            text_align="center",
        ),

        rx.box(
            rx.vstack(
                rx.heading("🚀 What This Project Does", size="5"),
                rx.text("• Analyzes code for syntax and logical issues"),
                rx.text("• Provides a quality score for your code"),
                rx.text("• Suggests improved and optimized versions"),
                rx.text("• Offers an AI Assistant for real-time help"),
                spacing="2",
            ),
            bg="#0F172A",
            padding="20px",
            border_radius="12px",
            width="100%",
            max_width="800px",
        ),

        rx.box(
            rx.vstack(
                rx.heading("🧠 Technology Used", size="5"),
                rx.text("• Reflex (Frontend + Backend Framework)"),
                rx.text("• Groq API for high-speed AI inference"),
                rx.text("• LLaMA 3.1 8B Instant model"),
                rx.text("• Python for logic and processing"),
                spacing="2",
            ),
            bg="#0F172A",
            padding="20px",
            border_radius="12px",
            width="100%",
            max_width="800px",
        ),

        rx.box(
            rx.vstack(
                rx.heading("🌟 Vision", size="5"),
                rx.text(
                    "Our goal is to simplify coding by providing intelligent insights, reducing debugging time, and helping developers focus on building impactful solutions.",
                ),
                spacing="2",
            ),
            bg="#0F172A",
            padding="20px",
            border_radius="12px",
            width="100%",
            max_width="800px",
        ),

        rx.box(
            rx.vstack(
                rx.heading("🔮 Future Scope", size="5"),
                rx.text("• Support for more programming languages"),
                rx.text("• Real-time collaborative coding"),
                rx.text("• Integration with IDEs like VS Code"),
                rx.text("• Advanced AI debugging and auto-fixing"),
                spacing="2",
            ),
            bg="#0F172A",
            padding="20px",
            border_radius="12px",
            width="100%",
            max_width="800px",
        ),

        spacing="6",
        align="center",
        padding_top="40px",
        padding_bottom="60px",
    )


# ---------- MAIN ----------
def index():
    return rx.box(
        navbar(),
        rx.cond(
            State.current_page == "home",
            home_page(),
            rx.cond(
                State.current_page == "analyzer",
                analyzer_page(),
                rx.cond(
                    State.current_page == "ai",
                    ai_page(),
                    rx.cond(
                        State.current_page == "history",
                        history_page(),
                        about_page(),
                    ),
                ),
            ),
        ),
        bg="#020617",
        color="white",
        min_height="100vh",
    )


app = rx.App()
app.add_page(index)