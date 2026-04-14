from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import subprocess
import os
import uuid

app = FastAPI()

@app.post("/process")
async def process_video(
    url: str = Query(..., description="视频直链"),
    tag: str = Query(..., description="标签"),
    display_name: str = Query(..., description="原始文件名")
):
    task_id = str(uuid.uuid4())[:4]
    output_filename = f"{task_id}_{display_name}"
    # 强制存放在 /tmp 目录下，防止权限问题
    output_path = f"/tmp/{output_filename}"
    
    # 给 url 加上双引号，防止参数里的 & 符号导致 shell 命令断开
    ffmpeg_cmd = [
        "ffmpeg", "-i", f"{url}",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", "-y", output_path
    ]
    
    try:
        # capture_output=True 捕获 FFmpeg 的咆哮
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
        domain = "https://video-api-production-8e5a.up.railway.app" 
        processed_url = f"{domain}/download/{output_filename}"
        
        return {"status": "success", "tag": tag, "processed_url": processed_url}
    except subprocess.CalledProcessError as e:
        # 这里会把 FFmpeg 的具体报错返回给 Coze 
        return {"status": "error", "msg": f"FFmpeg failed: {e.stderr[:200]}", "tag": tag}
    except Exception as e:
        return {"status": "error", "msg": str(e), "tag": tag}

@app.get("/download/{filename}")
async def download_video(filename: str):
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}
