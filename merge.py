import PIL
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

import os
import asyncio
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip, ColorClip, vfx
import moviepy.audio.fx.all as afx

PROMPT_FILE = "prompts.txt"
IMAGE_FOLDER = "ai_generated_images"
FINAL_OUTPUT = "Final_Long_Educational_Video.mp4"

CREATOR_NAME = "AapkaNaam"
TOPIC_NAME = "Dil ke Rishtey" 

INTRO_HOOK_TEXT = f"Dosto, main {CREATOR_NAME}. Aaj ki kahani {TOPIC_NAME} ke baare mein hai. Yeh video end tak dekhna, shayad aapki aankhon mein bhi aansu aa jayein."

# 🎙️ Clear & Normal Speed Voice Generator
async def generate_voiceover(text, output_file):
    # Rate aur Pitch default kar diya taaki aawaz saaf aur normal aaye
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+0%", pitch="+0Hz", volume="+20%")
    await communicate.save(output_file)

# 🎥 Zoom Effects Function
def resize_func_zoomin(t):
    return 1 + 0.03 * t  

def resize_func_zoomout(t):
    return 1.15 - 0.03 * t 

async def main():
    print("🎬 STORY VIDEO MAKER STARTED (NO TEXT, CLEAR VOICE)...")
    
    intro_audio_path = "intro_voice.mp3"
    await generate_voiceover(INTRO_HOOK_TEXT, intro_audio_path)
    
    scenes = []
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if line:
                parts = line.split('|')
                vo_text = parts[1].strip() if len(parts) > 1 else ""
                scenes.append({"video_num": idx + 1, "voiceover": vo_text})

    final_clips = []
    
    for i, scene in enumerate(scenes):
        v_num = scene['video_num']
        vo_text = scene['voiceover']
        
        img_path = os.path.join(IMAGE_FOLDER, f"Generated_Image_{v_num}.jpg")
        audio_path = os.path.join(IMAGE_FOLDER, f"Voice_{v_num}.mp3")
        
        if not os.path.exists(img_path):
            continue
            
        print(f"🎙️ Generating voice & editing Scene {v_num}...")
        
        target_audio = intro_audio_path if i == 0 else audio_path
        
        if i > 0 and vo_text:
            await generate_voiceover(vo_text, audio_path)
            
        if not os.path.exists(target_audio):
            continue

        audio = AudioFileClip(target_audio)
        duration = audio.duration + 0.5 

        # Image processing
        img_clip = ImageClip(img_path).set_duration(duration)
        img_clip = img_clip.resize(height=1080) 
        img_clip = img_clip.set_position("center")
        
        # 🔎 Adding Zoom In / Zoom Out
        if i % 2 == 0:
            img_clip = img_clip.resize(resize_func_zoomin)
        else:
            img_clip = img_clip.resize(resize_func_zoomout)
            
        bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0)).set_duration(duration)
        
        # Merge bg and image (Captions Removed)
        video_clip = CompositeVideoClip([bg_clip, img_clip.set_position("center")])
        video_clip = video_clip.set_audio(audio)
        
        # Fade transition
        if i > 0:
            video_clip = video_clip.crossfadein(1.0)
            
        final_clips.append(video_clip)

    if not final_clips:
        print("❌ Koi clip nahi bani!")
        return

    print("✂️ Assembling Final Timeline...")
    final_video = concatenate_videoclips(final_clips, method="compose", padding=-0.5)
    
    bg_music_path = "bg.mp3" 
    if os.path.exists(bg_music_path):
        print("🎵 Adding BGM...")
        bg_clip = AudioFileClip(bg_music_path).fx(afx.volumex, 0.08).fx(afx.audio_loop, duration=final_video.duration)
        final_mixed_audio = CompositeAudioClip([final_video.audio, bg_clip])
        final_video = final_video.set_audio(final_mixed_audio)

    print(f"💾 Exporting... {FINAL_OUTPUT}")
    # FPS 24 kar diya hai taaki video aur jaldi render/export ho
    final_video.write_videofile(FINAL_OUTPUT, fps=24, codec="libx264", audio_codec="aac")
    print("✅ YOUTUBE READY MASTERPIECE DONE!!")

if __name__ == "__main__":
    asyncio.run(main())
