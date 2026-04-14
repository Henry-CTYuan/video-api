from fastapi import FastAPI, Query
from fastapi.responses import FileResponse # 导入这个
import subprocess
import os
import uuid

app = FastAPI()

# 获取当前程序运行的目录，用于存放和访问视频
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.post("/process")
async def process_video(
    url: str = Query(..., description="视频直链"),
    tag: str = Query(..., description="标签"),
    display_name: str = Query(..., description="原始文件名")
):
    task_id = str(uuid.uuid4())[:4]
    output_filename = f"{task_id}_{display_name}"
    output_path = os.path.join(BASE_DIR, output_filename)
    
    ffmpeg_cmd = [
        "ffmpeg", "-i", url,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "superfast", "-y", output_path
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        # 获取你在 Railway 的公网域名（这需要你在 Railway 环境变量里手动加一个 DOMAIN）
        # 或者今晚先写死你现在的域名：
        domain = "https://你的railway域名.up.railway.app" 
        processed_url = f"{domain}/download/{output_filename}"
        
        return {
            "status": "success",
            "tag": tag,
            "processed_url": processed_url, # 返回这个 URL 给 Coze
            "display_name": display_name
        }
    except Exception as e:
        return {"status": "error", "msg": str(e)}

# 新增：让别人能通过 URL 下载这个文件
@app.get("/download/{filename}")
async def download_video(filename: str):
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}
