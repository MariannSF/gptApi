# utils.py

def format_for_openai(messages):
    formatted = []

    for msg in messages:
        role = msg["role"]

        if role == "bot":
            role = "assistant"

        formatted.append({
            "role": role,
            "content": [
                {"type": "input_text", "text": msg["content"]}
            ]
        })

    return formatted