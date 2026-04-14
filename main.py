from fastapi import FastAPI, Query
import subprocess
import os

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Video Processor is Running"}

@app.post("/process")
async def process_video(url: str = Query(..., description="视频的原始下载地址")):
    output_file = "output_1080p.mp4"
    
    # 强制转为 1920x1080，比例不对补黑边
    ffmpeg_cmd = [
        "ffmpeg", "-i", url,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "superfast", "-crf", "28", "-y", 
        output_file
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        # 注意：为了今晚能跑通，这里直接简单返回。
        # 实际生产需要上传到云存储，今晚先确保逻辑通。
        return {"status": "success", "msg": "处理完成", "filename": output_file}
    except Exception as e:
        return {"status": "error", "msg": str(e)}