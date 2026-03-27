# Video Recording Instructions

Follow these steps to record and finalize your HMS presentation video.

---

## Step 1: Prepare Your Environment

### Hardware Setup

- **Camera/Webcam:** Built-in or external USB webcam (for intro on-camera segment)
- **Microphone:** USB headset or external microphone (critical for good audio)
- **Monitor(s):** 1–2 monitors (one for recording, one for reference/script)
- **Screen recording software:** OBS Studio (free), Camtasia, ScreenFlow (Mac), or built-in tools

### Software Setup

#### Option A: OBS Studio (Recommended, Free)

1. Download: https://obsproject.com/
2. Install and open OBS
3. Create a new scene called "HMS Presentation"
4. Add sources:
   - **Video Capture Device** (for webcam intro): Click "+" under Sources → Video Capture Device → Select your webcam
   - **Display Capture** (for screen recordings): Click "+" → Display Capture → Select your monitor
   - **Audio Input Capture** (for microphone): Click "+" → Audio Input Capture → Select your USB mic
5. Set output settings:
   - Go to Settings → Output
   - Recording Format: MP4
   - Encoder: Hardware (NVIDIA/AMD if available) or x264
   - Quality: High (bitrate 4000–6000 kbps for 1080p)
   - Frame rate: 30 fps

#### Option B: Camtasia (Paid, Easier)

1. Download: https://www.techsmith.com/camtasia.html
2. Install and open Camtasia
3. Create new recording
4. Select "Record Screen" and/or "Record Webcam"
5. Adjust output quality in settings (1080p recommended)

#### Option C: Built-in Tools

- **Windows:** Use Xbox Game Bar (Win + G) for basic recording, or Snip & Sketch
- **Mac:** Use QuickTime Player or ScreenFlow

---

## Step 2: Prepare Your Content

### Before Recording

- [ ] Open HMS application in browser (running locally or deployed)
- [ ] Have user accounts ready (patient, doctor, admin) with test data
- [ ] Open VS Code with HMS backend code visible
- [ ] Prepare architecture diagram (PowerPoint, Figma PDF, or image)
- [ ] Have VIDEO_SCRIPT.md and STORYBOARD.md open in a reference window

### Test Run

1. Do a 1–2 minute test recording to check audio levels and video quality
2. Play back and listen for:
   - Clear voice (not too loud or soft)
   - No background noise
   - Screen text is readable at playback size
3. Adjust microphone input/output levels if needed

---

## Step 3: Record Each Section

### Segment 1: Introduction (30 sec)

**Setup:**
- Use webcam only (no screen sharing)
- Good lighting on your face
- Professional background (bookshelf, plain wall, or virtual background)

**Recording:**
1. Open OBS and select the "Video Capture Device" source (webcam)
2. Start recording
3. Read the intro script from VIDEO_SCRIPT.md (Section 1)
4. Speak clearly, maintain eye contact, use natural gestures
5. Stop recording

**File:** Save as `intro.mp4` or similar

---

### Segment 2: Approach (30 sec)

**Setup:**
- Use screen capture + overlay architecture diagram
- Have VIDEO_SCRIPT.md Section 2 visible for reference

**Recording:**
1. In OBS, add a Display Capture source (your second monitor or main monitor)
2. Open the architecture diagram on screen
3. Start recording
4. Point to sections of the diagram while reading the script
5. Narrate the approach clearly
6. Stop recording

**File:** Save as `approach.mp4`

---

### Segment 3: Key Features (90 sec)

**Setup:**
- Use screen capture of your browser showing the HMS app
- Have VIDEO_SCRIPT.md Section 3 visible (each subsection: 3.1, 3.2, 3.3, 3.4)

**Recording Subsections:**

**3.1 – Authentication & Registration (20 sec)**
1. Start recording
2. Show login page
3. Click "Register"
4. Fill out form (Name, Email, Password, Role)
5. Submit
6. Log in
7. Show dashboard
8. Stop recording

**3.2 – Role-Based Dashboards (25 sec)**
1. Resume recording
2. Show patient dashboard and its elements
3. Log out, log in as doctor
4. Show doctor dashboard
5. Log out, log in as admin
6. Show admin dashboard
7. Stop recording

**3.3 – Appointment Booking (25 sec)**
1. Resume recording
2. Log in as patient
3. Click "Request New Appointment"
4. Fill form (select doctor, date, notes)
5. Submit
6. Log out, log in as doctor
7. Show the appointment marked "Requested"
8. Click "Confirm"
9. Optionally show status updated to "Confirmed"
10. Stop recording

**3.4 – Background Jobs (20 sec)**
1. Resume recording
2. Open VS Code and show `backend/jobs/tasks.py`
3. Highlight job functions (send reminders, cleanup)
4. Optionally show a logs/metrics page
5. Stop recording

**File:** Save combined as `features.mp4` or individual segment files

---

### Segment 4: Additional Features (30 sec)

**Setup:**
- Use screen capture showing code and/or UI elements
- Have VIDEO_SCRIPT.md Section 4 visible

**Recording:**
1. Start recording
2. Show caching code (backend/utils/cache.py) – ~10 sec
3. Show appointment notes UI – ~5 sec
4. Show status history/audit trail – ~7 sec
5. Show modular jobs framework – ~8 sec
6. Stop recording

**File:** Save as `additional_features.mp4`

---

### Segment 5: Closing (10 sec, Optional)

**Setup:**
- Title slide or professional closing screen
- Your contact info or project link

**Recording:**
1. Start recording
2. Display closing slide
3. Read the closing remark from VIDEO_SCRIPT.md Section 5
4. Stop recording

**File:** Save as `closing.mp4`

---

## Step 4: Edit and Compile (Optional)

If you recorded segments separately, use a video editor to combine them:

### Using OBS (with built-in editing)

- OBS doesn't have a built-in editor, so export all segments and use an external tool.

### Using Camtasia (with editor)

1. Open Camtasia Editor
2. Import all segment videos
3. Drag each clip onto the timeline in order
4. Add transitions between clips (fade, cut)
5. Optionally add background music at intro/outro
6. Export as MP4

### Using Windows Photos app or iMovie

1. Open Photos (Windows) or iMovie (Mac)
2. Create new video project
3. Import all segment clips
4. Arrange in order on timeline
5. Add transitions
6. Export

### Using DaVinci Resolve (Free, Professional)

1. Download: https://www.blackmagicdesign.com/products/davinciresolve/
2. Open DaVinci Resolve
3. Create new project
4. Import clips to media library
5. Drag clips to timeline
6. Add transitions, titles, color grading if desired
7. Export → Master → MP4 (1080p)

---

## Step 5: Export Final Video

### Export Settings (Recommended)

- **Resolution:** 1920×1080 (1080p) or 1280×720 (720p) minimum
- **Frame Rate:** 30 fps
- **Codec:** H.264
- **Bitrate:** 4000–6000 kbps (1080p) or 2500–3500 kbps (720p)
- **Format:** MP4

### Export Example (OBS)

1. Go to Settings → Output
2. Set Recording Format: MP4
3. Set Quality: High
4. Click "Start Recording" on your final segment, then "Stop Recording"
5. OBS will save the file to your specified directory

---

## Step 6: Upload to Google Drive

1. Go to https://drive.google.com/
2. Log in with your university/personal Google account
3. Click "+ New" → "File upload"
4. Select your final video MP4 file
5. Once uploaded, right-click the file → "Share"
6. Set sharing to "Anyone with the link" (or "Viewer" role)
7. Copy the shareable link
8. **Update `docs/project_report.md`:** Replace `[INSERT DRIVE LINK HERE]` with your Google Drive link

---

## Step 7: Update Project Report

Once your video is uploaded:

1. Open `docs/project_report.md`
2. Find the line: `- Drive link: [INSERT DRIVE LINK HERE]`
3. Replace it with: `- Drive link: https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=drive_link` (your actual link)
4. Save the file
5. Regenerate PDF (see SUBMISSION_INSTRUCTIONS.md)

---

## Quality Checklist

Before finalizing:

- [ ] Total video duration is ~3 minutes
- [ ] Audio is clear and at consistent volume (no sudden loud/soft sections)
- [ ] No background noise (fan, traffic, typing)
- [ ] Screen recordings are sharp and text is readable
- [ ] Transitions are smooth
- [ ] All sections are present (intro, approach, features, additional features, closing)
- [ ] Video opens in a standard player without errors
- [ ] No missing or corrupted frames
- [ ] Color and brightness are consistent throughout

---

## Troubleshooting

### Audio Issues

- **Problem:** Audio is too quiet
- **Solution:** Increase microphone input level in OBS Settings → Audio → Microphone

- **Problem:** Audio is distorted/crackling
- **Solution:** Lower microphone input gain; ensure USB mic is not damaged

- **Problem:** Echo in audio
- **Solution:** Disable microphone monitoring in OBS; use a headset instead of speakers

### Video Quality Issues

- **Problem:** Screen is blurry
- **Solution:** Increase OBS canvas resolution to match your monitor (e.g., 1920×1080)

- **Problem:** Video lags or drops frames
- **Solution:** Close unnecessary applications; lower screen capture resolution or bitrate

- **Problem:** Video is too dark
- **Solution:** Adjust lighting; increase brightness in recording software or video editor

### File Issues

- **Problem:** Video won't play
- **Solution:** Use VLC Media Player (free, plays most formats); or re-export in standard MP4 format

- **Problem:** File is very large
- **Solution:** Reduce bitrate (3000 kbps) and resolution (720p); use H.264 codec for compression

---

## Final Submission

Once video is on Google Drive:

1. Copy the shareable link
2. Add it to `docs/project_report.md` (replace placeholder)
3. Regenerate PDF from Markdown (see SUBMISSION_INSTRUCTIONS.md)
4. Create submission ZIP with all files (backend/, frontend/, docs/)
5. Upload to course portal as instructed

---

## Tips for Success

- **Practice first:** Do a dry run before your final recording
- **Use a script:** Don't ad-lib; stick to the VIDEO_SCRIPT.md timings
- **Speak clearly:** Slow down if you feel rushed
- **Show, don't tell:** Screen recordings demonstrating features are more engaging than just talking
- **Be professional:** Neat appearance, clear audio, organized slides
- **Have fun:** Confidence and enthusiasm come through in the video!

