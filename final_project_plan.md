# Final Project Plan
- updated on December 7th to reflect changes to the device features

### Resources

[final project instructions link](https://github.com/IRL-CT/Developing-and-Designing-Interactive-Devices/blob/2025Fall/FinalProject.md)
[past projects link](https://github.com/IRL-CT/Developing-and-Designing-Interactive-Devices/wiki/Previous-Final-Projects)

#### Collaborators: Charlotte Lin (hl2575), Zoe Tseng (yzt2), Le-En Huang (lh764) 
#### Use of AI for this lab: Claude Sonnet4 for code development, debugging, and project planning.

---

## Proposed Work Split

| Team Member | Primary Module | Hardware Components | Key Responsibilities | Deliverables |
|-------------|---------------|---------------------|---------------------|--------------|
| **Charlotte Lin (hl2575)** | APDS Gesture Control + Speech Recognition | APDS-9960 sensor + Speakers | • Gesture recognition <br>• Sensor calibration <br>• Speech recognition | • Gesture event handler<br> • Web UI Interface<br> • Audio processing |
| **Eva Huang (lh764)** | MediaPipe Hand Pose + Audio Engine | Pi Camera + Speakers | • Real-time hand tracking<br>• Pose classification (open/fist/counting)<br>• Performance optimization | • Hand state data output<br>• Pose recognition API<br>• Real-time mixing effects<br>|
| **Zoe Tseng (yzt2)** |  Visual Feedback + Device Physical Design | PiTFT display + Pi Camera + Speakers| • Laser cut for physical device  <br> • System integration coordinator <br> • UI interface | • Web UI interface<br>• Integration framework<br> • Device Physical Design |

---

## Big Idea

Create **"Gesture DJ"** – a hand-controlled sound toy that combines APDS gesture sensing and MediaPipe hand-pose recognition to create an embodied music interaction experience. Users control sound loops, effects, and mixing through intuitive hand movements and gestures, with **multi-modal feedback** including visual display, web user interface and audio cues that respond immediately to gestures.

**Core Concept:** Transform physical gestures into musical expression : swipe to switch tracks, raise your hand to increase volume, make a fist to add distortion, open your palm to trigger effects. The system responds with immediate audio changes and **clear feedback** through multiple channels, creating an intuitive and playful DJ experience.

### Interaction Flow
1. **Start System** → Display shows ready state with available loops/sounds, LEDs indicate system status
2. **APDS Gestures** → Quick swipes and gesture control for discrete actions (track selection, volume)
3. **Hand Poses** → Expressive control for continuous effects (add sound effects, control visual effects)
4. **Sppech Recognition** → User say "Pause" or "Play" to control music
5. **Multi-Modal Feedback:**
   - **PiTFT Display:** Current song track/mode
   - **Audio Feedback:** Confirmation sounds for successful gestures
   - **Browser Interface:** Larger visualization if PiTFT proves too small
      -  **Waveform diagrams :** : Real-time beat visualizations, active effects
      -  **Camera :** : Real-time visual camera interface for gesture recognition
      -  **Track information** : Real-time indicator of current song track/mode
6. **Audio Output** → Layered loops and effects respond immediately to gestures

---

## Timeline

### Week 1: Component Development & Early Experimentation (INSTRUCTOR FEEDBACK: Test input methods early!)

1. **Days 1-2:** Parts check and **input method comparison**
   - Verify all hardware works independently
   - **CRITICAL: Test both APDS and MediaPipe early to determine which works better for DJ control**
   - Set up shared code repository structure
   - Define integration interfaces (data formats, shared state)

2. **Days 3-5:** Module development + **feedback system prototyping**
   - **APDS Module:** Get gesture recognition working, calibrate sensitivity
   - **MediaPipe Module:** Implement hand tracking, test pose classification
   - **Audio Module:** Set up pygame.mixer, load sample sounds, test playback
   - **Feedback Module:** Prototype LED patterns and PiTFT display layouts

3. **Days 6-7:** Individual testing with simulation modes + **input method decision**
   - Each person creates keyboard fallbacks for testing
   - Document module APIs and data outputs
   - **DECIDE: Which input method (APDS vs MediaPipe) feels more natural for DJ control?**
   - May choose to focus on one primary input with the other as secondary/fallback

### Week 2: Integration & Refinement

4. **Days 8-9:** Pairwise integration
   - Primary gesture input → Audio connection
   - Secondary gesture input → Audio connection
   - Test gesture-to-sound mappings

5. **Days 10-11:** Full system integration + **feedback enhancement**
   - Combine all three modules
   - Resolve timing conflicts and performance issues
   - Add visual feedback for all gestures on PiTFT
   - **Test if PiTFT is sufficient or if browser interface is needed**

6. **Days 12-13:** User experience polish + **feedback optimization**
   - Refine gesture sensitivity and response
   - **Improve feedback clarity across all channels (LED, display, audio)**
   - Test visibility of feedback in demo lighting conditions
   - Add "DJ modes" or preset configurations
   - Implement browser interface if PiTFT proves too small

### Week 3: Final Testing & Documentation

7. **Days 14-15:** Build physical enclosure/setup
   - Clean cable management
   - Position sensors and camera optimally
   - **Optimize LED placement for visibility**
   - Make system demo-ready

8. **Days 16-17:** User testing and refinement
   - Test with at least 3-5 users
   - **Specifically test feedback clarity: Can users tell what's happening?**
   - Gather feedback on intuitiveness
   - Make final adjustments

9. **Day 18:** Final documentation and demo prep
   - Record demo video
   - Finalize project documentation
   - Prepare presentation

---

## Parts Needed

**Already Have:**
* Raspberry Pi 4
* PiTFT display (ST7789)
* APDS-9960 gesture sensor
* Pi Camera (for MediaPipe)
* Speakers/audio output

**Optional Enhancements:**
* **MPR121 Touch Sensor** - for optional touch pad controls (Pads 0-11)
* USB microphone (for voice commands and audio sampling)
* External monitor/screen if browser interface is needed
* Physical device design

---
## Physical Device Design
Design sketch | <img src="https://hackmd.io/_uploads/HktUWkCfbl.png" width="600">

## Technical Architecture
![Decision Path Selection Flow-2025-12-15-030217](https://hackmd.io/_uploads/H1MfoeazWx.png)

### Module 1: APDS Gesture Control
**Inputs:** APDS-9960 sensor data

**Outputs:** 
```python
{
  'gesture': 'swipe_left' | 'swipe_right' | 'swipe_up' | 'swipe_down',
  'proximity': 0-255,
  'timestamp': float
}
```

**Gesture Mappings:**
- Swipe RIGHT: Next track (auto-play)
- Swipe LEFT: Previous track (auto-play)
- Swipe UP: Volume up (+10%)
- Swipe DOWN: Volume down (-10%)
**Note:** Based on early testing, this may become primary or secondary input method.

### Module 2: MediaPipe Hand Pose
**Inputs:** Pi Camera video stream

**Outputs:**
```python
{
  'pose': 'open' | 'fist' | 'counting',
  'finger_count': 0-5,
  'hand_rotation': -180 to 180,
  'confidence': 0.0-1.0,
  'timestamp': float
}
```

**Pose Mappings:**
-  OPEN PALM (5 fingers): Light theme (baby blue UI) - Hold for 2.5 seconds
-  CLOSED FIST (0 fingers): Dark theme (midnight UI) - Hold for 2.5 seconds
-  PEACE SIGN (2 fingers): DJ scratch effect - Instant trigger (no hold required)
**Note:** Based on early testing, this may become primary or secondary input method.

### Module 3: MPR121 Touch Controls 
**Inputs:** MPR121 capacitive touch sensor data

**Outputs:**
```python
{
  'pad': 0-11,
  'state': 'pressed' | 'released',
  'timestamp': float
}
```
**Touch Pad Mappings:**
- Pad 0-9: Select track 1-10
- Pad 10: Play/Pause toggle
- Pad 11: Stop playback
**Note:** Optional enhancement module for direct track selection.

### Module 4: Voice Commands
**Inputs:** USB microphone audio stream

**Outputs:**
```python
{
  'command': 'play' | 'pause',
  'confidence': 0.0-1.0,
  'timestamp': float
}
```

**Voice Command Mappings:**
- "play" / "start" / "go" / "resume": Start/resume playback
- "pause" / "stop" / "wait" / "hold": Pause playback
**Note:** Alternative words also work for more natural interaction.


### Module 5: Audio Engine + Audio Feedback
**Inputs:** Gesture data from both modules

**Outputs:** 
- Audio output (mixed loops + effects)
- PiTFT display (current state, gesture recognition)
- Browser interface 
- Audio confirmation sounds

**Responsibilities:**
- Maintain audio state (active loops, effect levels)
- Mix multiple audio streams in real-time
- Render feedback across multiple channels:
  - **Audio Cues:** Short confirmation sounds when gestures are recognized
- Coordinate timing between modules

### Module 6: Browser interface + PiTFT display
**Web Visualization Features:**
- Access at `http://<pi-ip>:5000` when running with `--web` flag
- **Browser Interface :** Flask server serving larger visualization with multiple modes (can be changed through user gesture)
- **Theme** : Game and neon themes to match with the DJ aesthetic
- **Main Component :**
   1. **Visualization Choice**
    - **WAVEFORM:** Real-time waveform with beat-reactive glow
    - **SPECTRUM:** Frequency spectrum analyzer with color gradient
    - **AUDIENCE:** RGB bars bouncing with bass, party mode
    - **PARTICLES:** Pulsing rings with particle burst effects
   2.  **Basic Track Controls**
   - `play`, `pause`, `swtich tracks`
   3. **Camera Preview interface** : window showing Pi's camera feed


- **PiTFT Display:** Text/graphics showing current track, mode, detected gestures

---
## Controls Reference

### APDS-9960 Gesture Controls

| Gesture | Action |
|---------|--------|
| Swipe RIGHT | Next track (auto-play) |
| Swipe LEFT | Previous track (auto-play) |
| Swipe UP | Volume up (+10%) |
| Swipe DOWN | Volume down (-10%) |

### MPR121 Touch Controls (Optional)

| Pad | Action |
|-----|--------|
| Pad 0-9 | Select track 1-10 |
| Pad 10 | Play/Pause toggle |
| Pad 11 | Stop playback |

### MediaPipe Hand Gestures (Camera Required)

| Gesture | Fingers | Action | Hold Time |
|---------|---------|--------|-----------|
|  OPEN PALM | 5 | Light theme (baby blue UI) | 2.5 seconds |
|  CLOSED FIST | 0 | Dark theme (midnight UI) | 2.5 seconds |
|  PEACE SIGN | 2 | DJ scratch effect | Instant |

**Tips:**
- Hold palm/fist gestures for 2.5 seconds to change theme
- Peace sign triggers immediately (no hold required)
- Keep hand 1-2 feet from camera for best detection
- Use good lighting for accurate gesture recognition
- Camera feed visible in web UI (top-right corner)
- Scratch effect plays random scratch sound over music

### Voice Commands

| Command | Action |
|---------|--------|
| "play" | Start/resume playback |
| "pause" | Pause playback |

**Alternative words also work:**
- Play: "start", "go", "resume"
- Pause: "stop", "wait", "hold"

### Web Visualization Modes

When running with `--web`, access the visualizer at `http://<pi-ip>:5000`:

| Mode | Description |
|------|-------------|
| WAVEFORM | Real-time waveform with beat-reactive glow |
| SPECTRUM | Frequency spectrum analyzer with color gradient |
| AUDIENCE | RGB bars bouncing with bass, party mode |
| PARTICLES | Pulsing rings with particle burst effects |

**Features:**
-  Track waveform visualization - see beats and peaks
-  Frequency spectrum with bass/mid/high analysis
-  RGB bars bounce with bass levels
-  Reactive particle effects on beat detection

---

## Risks/Contingencies

### Technical Risks

1. **Input Method Uncertainty:** Not sure whether APDS or MediaPipe works better for DJ control
   - **Mitigation:** **TEST BOTH EARLY (Days 1-2)** to determine which feels more natural
   - **Fallback:** Use one as primary input, other as secondary/enhancement

2. **PiTFT Too Small for Feedback:** Display may not be visible enough for demo/DJ use
   - **Mitigation:** Add LED indicators and audio cues as primary feedback
   - **Fallback:** Implement browser-based interface with Flask server for larger display

3. **Performance Issues:** Running MediaPipe + audio processing + multiple feedback channels may strain the Pi
   - **Mitigation:** Optimize frame rate, use lower resolution for hand tracking, simplify LED patterns
   - **Fallback:** Reduce to one primary input method, simplify visual feedback

4. **Gesture Conflicts:** APDS and hand movements might interfere with each other
   - **Mitigation:** Early testing will help determine if both can coexist
   - **Fallback:** Choose one primary input method based on Day 1-2 testing

5. **Audio Latency:** Delay between gesture and sound response
   - **Mitigation:** Use lightweight audio library, pre-load all samples
   - **Fallback:** Accept some latency, make it feel "intentional"

6. **Integration Complexity:** Three separate modules + multiple feedback channels may be difficult to synchronize
   - **Mitigation:** Regular integration checkpoints, shared state manager
   - **Fallback:** Simplify to 2-module system with single feedback channel

### Hardware Risks

7. **Camera Lighting Dependency:** MediaPipe requires good lighting
   - **Mitigation:** Test in demo environment early, add LED if needed
   - **Fallback:** If MediaPipe unreliable, use APDS as primary input

8. **Sensor Placement:** Finding optimal position for both sensors + camera + LEDs
   - **Mitigation:** Prototype enclosure early, test different configurations
   - **Fallback:** Separate stations (user moves between sensors)

9. **LED Visibility:** LEDs may not be bright enough or positioned poorly
   - **Mitigation:** Test LED brightness and placement early
   - **Fallback:** Use browser interface as primary feedback

---

## Fall-back Plan

**Level 1 - Input Method Simplification:**
Based on early testing (Days 1-2), choose the more reliable input method (APDS or MediaPipe) as primary, use the other as secondary enhancement only.

**Level 2 - Feedback Channel Reduction:**
If multi-modal feedback proves too complex, focus on 2 channels: LEDs (primary visual) + Audio (confirmation), with PiTFT showing minimal state info.

**Level 3 - Browser Interface Only:**
If PiTFT proves too small and LED implementation is problematic, focus all visual feedback on a browser-based interface served from the Pi.

**Level 4 - Single Input, Single Output:**
Simplify to one gesture input method (likely APDS for reliability) + Audio output + simple browser visualization.


**Success Criteria:** We consider the project successful if:
- Users can control at least 3 distinct audio parameters through gestures
- System responds within 200ms of gesture recognition
- **DJ receives clear, immediate feedback through at least 2 channels (visual + audio)**
- **Input method decision made by Day 2 based on real testing**
- Demo runs reliably for 3+ minutes without crashes
