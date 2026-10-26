## Starting Idea
I wanted to build an interactive poster. The initial idea was a simple 2D text that would jitter and wave. However, I wanted to elevate the visual impact and make it feel like a high-end digital art installation.

## Design and Code Changes
I iterated from a 2D physics simulation to a 3D WebGL particle system (using Three.js). I added a Gaussian distribution for the particles and implemented spring physics so they smoothly scatter and reform. Later, I integrated the Web Audio API to generate real-time audio.

## User Trial and Response
During the iterative process, I tested the experience on peers. 
- **Observation 1**: Users felt the initial interface was too basic and didn't match the immersive 3D art. 
  - **Response**: I rebuilt the UI using custom HTML/CSS with a glassmorphism effect to create a cohesive, modern aesthetic.
- **Observation 2**: Users found the initial synthesized audio to be too harsh and continuous.
  - **Response**: I redesigned the audio engine. I mapped the color gradient to different instrument timbres (Piano, Guitar, Flute) and tied the Explosion slider to the audio envelope length. This made the sound much more musical and responsive to the visuals.
- **Observation 3**: Users had trouble pushing particles at the edges of the screen.
  - **Response**: I replaced the basic mouse tracking with a Raycaster, allowing the repulsion force to work accurately across the entire screen.

## AI Use
I used DeepSeek for brainstorming the physics algorithms, the Web Audio API synthesis, and optimizing the Three.js particle generation.
- **What I kept**: DeepSeek suggested using the Raycaster to project 2D mouse coordinates onto the 3D plane. It also provided the foundational logic for the pentatonic scale audio synthesis, which guarantees the notes never sound dissonant.
- **What I changed/rejected**: The AI initially suggested pure sine waves for the audio and a basic `if/else` color mapping. I rejected this because it sounded too harsh and the color transitions were abrupt. I modified the code to implement complex envelopes, blended three oscillators to simulate physical instruments, and used color distance weighting to smoothly morph between instrument types based on the gradient colors.