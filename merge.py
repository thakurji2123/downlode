import PIL
from PIL import Image

# 1. Pillow 10+ Compatibility Patch (MoviePy se pehle load hona zaroori hai)
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS
if not hasattr(Image, 'CUBIC'):
    Image.CUBIC = Image.Resampling.BICUBIC

import os
import asyncio
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip, TextClip, ColorClip, vfx
import moviepy.audio.fx.all as afx

PROMPT_FILE = "prompts.txt"
IMAGE_FOLDER = "ai_generated_images"
FINAL_OUTPUT = "Final_Long_Educational_Video.mp4"

# ==========================================
CREATOR_NAME = "AapkaNaam"
CHANNEL_NAME = "@AapkaChannel"   # <--- Apna Watermark Dalo
TOPIC_NAME = "Dil ke Rishtey" 

INTRO_HOOK_TEXT = f"Dosto, main {CREATOR_NAME}. Aaj ki kahani {TOPIC_NAME} ke baare mein hai. Yeh video end tak dekhna, shayad aapki aankhon mein bhi aansu aa jayein."
# ==========================================

# 🎙️ Fast & Clear Voice Generator
async def generate_voiceover(text, output_file):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+20%", pitch="+2Hz", volume="+30%")
    await communicate.save(output_file)

# 🎥 Zoom Effects
def resize_func_zoomin(t): return 1 + 0.02 * t  
def resize_func_zoomout(t): return 1.1 - 0.02 * t 

# ✍️ DYNAMIC CAPTIONS GENERATOR (2-WORDS POPUP)
def create_dynamic_captions(text, duration):
    if not text: return []
    words = text.split()
    # 2-2 words ke tukde banayenge (Jaise: "Ek din", "Rahul akele")
    chunks = [' '.join(words[i:i+2]) for i in range(0, len(words), 2)]
    
    # Har tukde ko kitna time milega (Total time / total tukde)
    time_per_chunk = duration / len(chunks)
    
    text_clips = []
    current_time = 0
    for chunk in chunks:
        # Yellow color, Black Border stroke (Image jaisa same effect)
        txt_clip = TextClip(chunk, fontsize=90, color='yellow', font="Arial-Bold", stroke_color='black', stroke_width=3)
        # Position: Center, aur thoda niche (800 px)
        txt_clip = txt_clip.set_position(('center', 800))
        txt_clip = txt_clip.set_start(current_time).set_duration(time_per_chunk)
        # Halka sa fade-in animation
        txt_clip = txt_clip.crossfadein(0.1)
        text_clips.append(txt_clip)
        current_time += time_per_chunk
        
    return text_clips

async def main():
    print("🎬 ULTIMATE YOUTUBE MAKER STARTED (DYNAMIC CAPTIONS + PRO EDITING)...")
    
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
        
        if not os.path.exists(img_path): continue
            
        print(f"🎙️ Generating voice & editing Scene {v_num}...")
        
        target_audio = intro_audio_path if i == 0 else audio_path
        text_to_speak = INTRO_HOOK_TEXT if i == 0 else vo_text
        
        if i > 0 and vo_text: await generate_voiceover(vo_text, audio_path)
        if not os.path.exists(target_audio): continue

        audio = AudioFileClip(target_audio)
        duration = audio.duration + 0.3 

        # Image processing & Color Grading
        img_clip = ImageClip(img_path).set_duration(duration)
        
        # 🟢 FIX: Yahan se 'resampling' word hata diya hai
        img_clip = img_clip.resize(height=1080) 
        img_clip = img_clip.fx(vfx.colorx, 1.15).fx(vfx.lum_contrast, lum=5, contrast=0.1).set_position("center")
        
        # 🟢 FIX: Yahan se bhi 'resampling' hata diya hai
        if i % 2 == 0: img_clip = img_clip.resize(resize_func_zoomin)
        else: img_clip = img_clip.resize(resize_func_zoomout)
            
        bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0)).set_duration(duration)
        
        # 🟢 YAHAN CAPTIONS ADD HO RAHE HAIN 🟢
        dynamic_captions = create_dynamic_captions(text_to_speak, duration)
        
        # Combine BG + Image + All Caption Chunks
        video_clip = CompositeVideoClip([bg_clip, img_clip] + dynamic_captions)
        video_clip = video_clip.set_audio(audio)
        
        if i > 0: video_clip = video_clip.crossfadein(1.0)
        final_clips.append(video_clip)

    if not final_clips: return

    print("✂️ Assembling Final Timeline...")
    final_video = concatenate_videoclips(final_clips, method="compose", padding=-0.5)
    
    # WATERMARK
    watermark = TextClip(f" {CHANNEL_NAME} ", fontsize=45, color='white', font="Arial-Bold", bg_color='black')
    watermark = watermark.set_opacity(0.4).set_position(("right", "top")).set_duration(final_video.duration)
    
    # SUBSCRIBE POPUP
    sub_text = TextClip("🔔 SUBSCRIBE FOR MORE!", fontsize=70, color='yellow', bg_color='red', font="Arial-Bold")
    sub_text = sub_text.set_position("center").set_duration(4).set_start(final_video.duration - 4).crossfadein(1)

    final_video = CompositeVideoClip([final_video, watermark, sub_text])

    # BGM
    bg_music_path = "bg.mp3" 
    if os.path.exists(bg_music_path):
        bg_clip = AudioFileClip(bg_music_path).fx(afx.volumex, 0.08).fx(afx.audio_loop, duration=final_video.duration)
        final_mixed_audio = CompositeAudioClip([final_video.audio, bg_clip])
        final_video = final_video.set_audio(final_mixed_audio)

    print(f"💾 Exporting... {FINAL_OUTPUT}")
    final_video.write_videofile(FINAL_OUTPUT, fps=24, codec="libx264", audio_codec="aac")
    print("✅ YOUTUBE READY MASTERPIECE DONE!!")

if __name__ == "__main__":
    asyncio.run(main())
