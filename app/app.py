import os
from flask import Flask, render_template, request, send_file
import whisper
import ffmpeg

app = Flask(__name__)

# 'uploads' klasörü yoksa oluştur
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Whisper modelini yükle
model = whisper.load_model("base")

# Ses dosyasını mp3 formatına dönüştür
def convert_video_to_audio(video_path):
    audio_path = video_path.rsplit('.', 1)[0] + ".mp3"
    ffmpeg.input(video_path).output(audio_path, ab='192k').run()
    return audio_path

# Yüklenen dosyanın türünü kontrol et (ses mi video mu?)
def is_video(file_path):
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv']
    return any(file_path.endswith(ext) for ext in video_extensions)

# Video yükleme ve transkript işlemi
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Video veya ses dosyasını al
        uploaded_file = request.files["file"]

        if uploaded_file:
            # Dosya ismini ve yolu ayarla
            file_path = os.path.join("uploads", uploaded_file.filename)
            uploaded_file.save(file_path)

            # Dosya türüne göre işlem yap
            if is_video(file_path):
                # Video dosyasını sese dönüştür
                audio_path = convert_video_to_audio(file_path)
            else:
                # Ses dosyasını olduğu gibi kullan
                audio_path = file_path

            # Whisper ile transkript al
            result = model.transcribe(audio_path, word_timestamps=True)

            # Transkripti SRT formatında kaydet
            srt_path = file_path.rsplit('.', 1)[0] + ".srt"
            convert_to_srt(result, srt_path)

            return send_file(srt_path, as_attachment=True)

    return render_template("index.html")

# Zaman kodlu transkripti SRT formatına dönüştür
def convert_to_srt(result, output_file):
    segments = result['segments']
    with open(output_file, 'w', encoding='utf-8') as file:
        for idx, segment in enumerate(segments):
            start_time = segment['start']
            end_time = segment['end']
            start_time_str = convert_seconds_to_srt_time(start_time)
            end_time_str = convert_seconds_to_srt_time(end_time)
            text = segment['text']
            file.write(f"{idx + 1}\n")
            file.write(f"{start_time_str} --> {end_time_str}\n")
            file.write(f"{text}\n\n")

def convert_seconds_to_srt_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Portu çevresel değişkenden al
    app.run(host="0.0.0.0", port=port, debug=True)
