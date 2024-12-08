import whisper

# Modeli yükleyin
model = whisper.load_model("base")

# Ses dosyasını transkript edin
result = model.transcribe("ses_dosyası.mp3")

# Transkripti yazdırın
print(result['text'])





