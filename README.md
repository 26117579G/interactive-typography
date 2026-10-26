# Kinetic Audio-Visual Typography

## Project Idea
This is an interactive 3D particle typography tool designed for digital artists, designers, and musicians. It visualizes text as a dynamic particle system and translates user interactions into spatial deformation and live-synthesized audio.

## The Intended User
Anyone who wants to explore the boundary between visual design and sound. It can be used as a generative art installation, a tool for designing audio-reactive posters, or simply as an experimental musical instrument.

## Main Interaction
- **Input**: The user types a word, changes the gradient colors, adjusts particle physics (Explosion/Scale), and moves their mouse across the screen.
- **Response**: The particles form the word and respond to the mouse with a 3D repulsion force.
- **Feedback**: The color palette directly controls the synthesized musical instruments (e.g., blue maps to piano, red maps to guitar, green maps to flute). The "Explosion" slider controls the length of the audio envelope (long reverb when scattered, short plucks when clustered).

## User Trial and Iteration
During the development and testing phases, I observed how users interacted with the early prototypes and made several key improvements:
1. **UI Overhaul**: The initial prototype used standard Streamlit UI components. I noticed the UI felt disconnected from the 3D visuals. I redesigned the interface using a custom HTML/CSS "glassmorphism" panel, making the controls feel premium and integrated.
2. **Audio Refinement**: The first audio version generated harsh, continuous electronic tones that users found fatiguing. Based on this feedback, I completely rewrote the audio engine to map the gradient colors to specific instruments (Piano, Guitar, Flute) and used the Explosion slider to control the audio envelope.
3. **Interaction Fixes**: I noticed users struggled to interact with the particles outside the center of the screen. I implemented a Three.js Raycaster to accurately map mouse coordinates across the entire 3D space.

## How to Run
Ensure you have Python and Streamlit installed. Run the following command in your terminal:

```bash
uv run --with streamlit streamlit run app.py
```

Then open http://localhost:8501 in your browser. You must interact with the page (click "Enable Sound") to allow the browser to play audio.

Known Limitations
Audio generation relies on the Web Audio API; Chrome is recommended for the best performance.

Complex words with more than 10 letters might become too dense on small screens.

Screenshot
https://screenshot.png/