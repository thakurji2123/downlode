import PIL
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

import os
import asyncio
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip, TextClip, ColorClip, vfx
import moviepy.audio.fx.all as afx

PROMPT_FILE = "prompts.txt"
IMAGE_FOLDER = "ai_generated_images"
FINAL_OUTPUT = "Final_Long_Educational_Video.mp4"

# ==========================================
CHANNEL_NAME = "@bro thakur"   # <--- Apna English Channel Naam Dalo
INTRO_HOOK_TEXT = "Welcome, brothers and sisters. Today, we look at a powerful message from the life of Jesus Christ. Watch till the end, and let God bless your soul."
MAX_VIDEO_DURATION = 14 * 60  # STRICT LIMIT: 14 Minutes (840 Seconds)
# ==========================================

async def generate_voiceover(text, output_file):
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="+5%", pitch="-5Hz", volume="+30%")
    await communicate.save(output_file)

def resize_func_zoomin(t): return 1 + 0.02 * t  
def resize_func_zoomout(t): return 1.1 - 0.02 * t 

def create_dynamic_captions(text, duration):
    if not text: return []
    words = text.split()
    chunks = [' '.join(words[i:i+2]) for i in range(0, len(words), 2)]
    time_per_chunk = duration / len(chunks)
    
    text_clips = []
    current_time = 0
    for chunk in chunks:
        txt_clip = TextClip(chunk, fontsize=90, color='yellow', font="Arial-Bold", stroke_color='black', stroke_width=3)
        txt_clip = txt_clip.set_position(('center', 800))
        txt_clip = txt_clip.set_start(current_time).set_duration(time_per_chunk)
        txt_clip = txt_clip.crossfadein(0.1)
        text_clips.append(txt_clip)
        current_time += time_per_chunk
    return text_clips

async def main():
    print("🎬 US AUDIENCE VIDEO MAKER STARTED...")
    
    intro_audio_path = "intro_voice.mp3"
    await generate_voiceover(INTRO_HOOK_TEXT, intro_audio_path)
    
    scenes = []
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if line:
                    parts = line.split('|')
                    vo_text = parts[1].strip() if len(parts) > 1 else ""
                    scenes.append({"video_num": idx + 1, "voiceover": vo_text})
    else:
        print(f"❌ Error: {PROMPT_FILE} not found!")
        return

    final_clips = []
    current_total_duration = 0  # Isse hum track karenge ki video kitni lambi ban chuki hai
    
    for i, scene in enumerate(scenes):
        # ⏰ TIMING CHECK
        if current_total_duration >= MAX_VIDEO_DURATION:
            print("⏰ Reached 14-Minute Limit! Stopping here to avoid YouTube 15-min rejection.")
            break

        v_num = scene['video_num']
        vo_text = scene['voiceover']
        
        img_path = os.path.join(IMAGE_FOLDER, f"Generated_Image_{v_num}.jpg")
        audio_path = os.path.join(IMAGE_FOLDER, f"Voice_{v_num}.mp3")
        
        if not os.path.exists(img_path): continue
        
        if os.path.getsize(img_path) < 1024:
            print(f"⚠️ Skipping Image {v_num} - File is corrupted or empty.")
            continue
            
        target_audio = intro_audio_path if i == 0 else audio_path
        text_to_speak = INTRO_HOOK_TEXT if i == 0 else vo_text
        
        if i > 0 and vo_text: 
            await generate_voiceover(vo_text, audio_path)
        
        if not os.path.exists(target_audio): continue

        try:
            audio = AudioFileClip(target_audio)
            duration = audio.duration + 0.3 

            # Add to total duration tracker
            current_total_duration += duration

            img_clip = ImageClip(img_path).set_duration(duration)
            img_clip = img_clip.resize(height=1080) 
            img_clip = img_clip.fx(vfx.colorx, 1.15).fx(vfx.lum_contrast, lum=5, contrast=0.1).set_position("center")
            
            if i % 2 == 0: img_clip = img_clip.resize(resize_func_zoomin)
            else: img_clip = img_clip.resize(resize_func_zoomout)
                
            bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0)).set_duration(duration)
            dynamic_captions = create_dynamic_captions(text_to_speak, duration)
            
            video_clip = CompositeVideoClip([bg_clip, img_clip] + dynamic_captions)
            video_clip = video_clip.set_audio(audio)
            
            if i > 0: video_clip = video_clip.crossfadein(1.0)
            
            final_clips.append(video_clip)
            print(f"✅ Scene {v_num} | Length: {round(current_total_duration/60, 2)} Mins")
            
        except Exception as e:
            print(f"⚠️ Failed to process scene {v_num}, skipping... Error: {e}")
            continue

    if not final_clips: 
        print("❌ No valid clips generated.")
        return

    print("⏳ Merging all clips, please wait...")
    final_video = concatenate_videoclips(final_clips, method="compose", padding=-0.5)
    
    watermark = TextClip(f" {CHANNEL_NAME} ", fontsize=45, color='white', font="Arial-Bold", bg_color='black')
    watermark = watermark.set_opacity(0.4).set_position(("right", "top")).set_duration(final_video.duration)
    
    sub_text = TextClip("🔔 SUBSCRIBE FOR DAILY BLESSINGS!", fontsize=70, color='yellow', bg_color='red', font="Arial-Bold")
    sub_text = sub_text.set_position("center").set_duration(4).set_start(final_video.duration - 4).crossfadein(1)

    final_video = CompositeVideoClip([final_video, watermark, sub_text])

    bg_music_path = "bg.mp3" 
    if os.path.exists(bg_music_path):
        bg_clip = AudioFileClip(bg_music_path).fx(afx.volumex, 0.08).fx(afx.audio_loop, duration=final_video.duration)
        final_mixed_audio = CompositeAudioClip([final_video.audio, bg_clip])
        final_video = final_video.set_audio(final_mixed_audio)

    final_video.write_videofile(FINAL_OUTPUT, fps=24, codec="libx264", audio_codec="aac")
    print(f"✅ DONE! Total Video Length: {round(final_video.duration/60, 2)} Minutes")

if __name__ == "__main__":
    asyncio.run(main())
