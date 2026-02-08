Write-Host "사진 영상 용량 줄이기 v1.0.0 빌드 시작"

.venv\Scripts\activate
python -m PyInstaller --onefile --noconsole --add-data "bin;bin" --name "사진 영상 용량 줄이기 v1.0.0" media_compressor.py

Write-Host "빌드 완료"

deactivate