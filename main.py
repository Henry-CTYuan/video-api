from fastapi import FastAPI, Query
import subprocess
import os
import uuid

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Video Processor is Running"}

@app.post("/process")
async def process_video(
    url: str = Query(..., description="视频直链"),
    tag: str = Query(..., description="来自前置节点的标签（如：开场）"),
    display_name: str = Query(..., description="原始文件名（如：开场.mp4）")
):
    # 1. 为了防止重名冲突，给输出文件加个简短随机前缀
    task_id = str(uuid.uuid4())[:4]
    output_file = f"{task_id}_{display_name}"
    
    # 2. FFmpeg 核心转换命令：强制 1920*1080 16:9，比例不对补黑边
    ffmpeg_cmd = [
        "ffmpeg", "-i", url,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "superfast", "-crf", "26", "-y", 
        output_file
    ]
    
    try:
        # 执行处理
        subprocess.run(ffmpeg_cmd, check=True)
        
        # 3. 关键：原样返回 tag 和 display_name 供 Coze 定位
        return {
            "status": "success",
            "tag": tag,
            "display_name": display_name,
            "msg": f"文件 {display_name} 处理成功",
            "output_path": output_file
        }
    except Exception as e:
        return {
            "status": "error",
            "tag": tag,
            "display_name": display_name,
            "msg": str(e)
        }
