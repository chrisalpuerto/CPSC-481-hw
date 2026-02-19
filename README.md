## CPSC 481 HW: The Agentic Design Lab

# Authors: Chris Alpuerto, Andrew Mankin, Nathaniel Obeso

Topic 4: Edge Case Logic
Stance A: Predictable (The agent stops/logs errors when logic is unclear)

Inside main.py, we have a program that uses the Vertex API w/ Gemini to do video analysis on a video inside a GCS bucket with a specific prompt (prompt imported from prompts.py), and for this use case it is supposed to analyze basketball videos to depict timestamps for certain events.

Inside the actual function, we have multiple try and except handlers to handle specific errors, such as; video analysis errors, invalid video errors, invalid credential errors and general exception errors. Right now for every except error thrown, it halts the entire program, as before we had a few places where if the error was thrown, it would still continue with the program.