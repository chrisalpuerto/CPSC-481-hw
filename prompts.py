def prompt():
    prompt = """
            Act as an elite basketball coach and analyst. Analyze every shot attempt in this video with the following structure:

            - Player Identification (if possible)
            - Shot Type (Jump shot, Layup, Dunk, etc.)
            - Shot Location (e.g., right corner, top of the key)
            - Time of Shot (timestamp or visual marker)
            - Result (Make or Miss)
            - Form Analysis (brief breakdown of mechanics)
            - Defensive Pressure (if present)

            Be thorough, structured, and use bullet points for each shot.
            """
    return prompt
