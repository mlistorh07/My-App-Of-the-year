from flask import Flask, render_template, request, jsonify
import requests
import json
import os

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01"
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle AI advisor chat messages."""
    data = request.get_json()
    messages = data.get("messages", [])
    grade = data.get("grade", "9")

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": (
            f"You are a warm, encouraging career guidance advisor for South African black learners "
            f"in Grade 9 to 12. You know about SA universities, NSFAS, bursaries, NSC subjects, "
            f"career paths, APS scores, and free online learning platforms (Siyavula, Khan Academy, "
            f"freeCodeCamp, Coursera, TVET colleges, MERSETA, SETA learnerships). "
            f"The learner is in Grade {grade}. Keep answers short (3-5 sentences), practical, and "
            f"motivational. Use simple language. Always mention SA institutions or free resources. "
            f"Never discourage any career dream."
        ),
        "messages": messages
    }

    try:
        response = requests.post(ANTHROPIC_API_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        reply = "".join(block.get("text", "") for block in result.get("content", []))
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-plan", methods=["POST"])
def generate_plan():
    """Generate a personalised career plan using AI."""
    data = request.get_json()
    name = data.get("name", "Learner")
    school = data.get("school", "My School")
    grade = data.get("grade", "Grade 9")
    province = data.get("province", "KwaZulu-Natal")
    career = data.get("career", "To be decided")
    subjects = data.get("subjects", "Not specified")
    skills = data.get("skills", "Not specified")
    goal = data.get("goal", "To succeed and make my family proud")

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": (
            "You are a South African career guidance advisor. Generate a personalised career plan "
            "for a learner. Return ONLY a JSON object with these exact keys: "
            "steps (array of 4 objects each with 'title' string and 'actions' array of 3 strings), "
            "subjects_advice (string, 2 sentences), "
            "bursaries (array of 3 strings), "
            "motivation (string, 2 powerful sentences addressing the learner by name). "
            "Be specific to South Africa, practical, and motivational. "
            "No markdown, no preamble, just valid JSON."
        ),
        "messages": [{
            "role": "user",
            "content": (
                f"Name: {name}, Grade: {grade}, Province: {province}, "
                f"Dream career: {career}, Best subjects: {subjects}, "
                f"Skills to learn: {skills}, Life goal: {goal}"
            )
        }]
    }

    try:
        response = requests.post(ANTHROPIC_API_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        text = "".join(block.get("text", "") for block in result.get("content", []))
        text = text.replace("```json", "").replace("```", "").strip()
        plan = json.loads(text)
        return jsonify({"plan": plan})
    except json.JSONDecodeError:
        return jsonify({"error": "Could not parse career plan. Please try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
