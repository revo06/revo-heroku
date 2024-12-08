import ffmpeg

def convert_video_to_audio(video_path):
    # Ses dosyasının çıkacağı yol
    audio_path = video_path.rsplit('.', 1)[0] + ".mp3"
    
    try:
        # Video dosyasını ses dosyasına dönüştürme
        ffmpeg.input(video_path).output(audio_path, qscale_a=0).run(capture_stdout=True, capture_stderr=True)
        print(f"Video başarıyla ses dosyasına dönüştürüldü: {audio_path}")
    except ffmpeg.Error as e:
        # Hata durumunda stderr çıktısını ekrana yazdırma
        print("FFmpeg hata detayları:")
        print(e.stderr.decode())  # Hata mesajını daha anlaşılır şekilde yazdır
    return audio_path
