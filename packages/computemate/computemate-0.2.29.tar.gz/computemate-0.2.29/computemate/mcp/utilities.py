from fastmcp import FastMCP
from fastmcp.prompts.prompt import PromptMessage, TextContent
from agentmake import agentmake
from computemate import config, AGENTMAKE_CONFIG
import logging, os

# configure backend
AGENTMAKE_CONFIG["backend"] = config.backend

# Configure logging before creating the FastMCP server
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.ERROR)

mcp = FastMCP(name="ComputeMate Utilities")

def getResponse(messages:list) -> str:
    return messages[-1].get("content") if messages and "content" in messages[-1] else "Error!"

# media files

@mcp.tool
def process_media_files(request:str) -> str:
    """Process, edit, or convert media files—such as videos or audio—that can be handled using the `ffmpeg` command; specify how you want to process the file(s); requires file path(s) for the file(s) to be processed.

Args [required]:
    code: Generate Python code that executes an `ffmpeg` command to process media files, such as videos or audio, based on the specifications in my request.
    title: Title for the task
"""
    global agentmake, getResponse
    messages = agentmake(request, **{'tool': 'cli/ffmpeg'}, **AGENTMAKE_CONFIG)
    return getResponse(messages)

# youtube

@mcp.tool
def youtube_download_mp4_video(request:str) -> str:
    """Download Youtube audio into mp4 video file; a valid Youtube URL is required

Args [required]:
    url: Youtube url given by user

Args [optional]:
    location: Output folder where downloaded file is to be saved
"""
    global agentmake, getResponse
    messages = agentmake(request, **{'tool': 'youtube/download_video'}, **AGENTMAKE_CONFIG)
    return getResponse(messages)

@mcp.tool
def youtube_download_mp3_audio(request:str) -> str:
    """Download Youtube audio into mp3 audio file; a valid Youtube URL is required

Args [required]:
    url: Youtube url given by user

Args [optional]:
    location: Output folder where downloaded file is to be saved
"""
    global agentmake, getResponse
    messages = agentmake(request, **{'tool': 'youtube/download_audio'}, **AGENTMAKE_CONFIG)
    return getResponse(messages)

@mcp.prompt
def youtube_download_video_and_audio(request:str) -> PromptMessage:
    """Transcribe a Youtube video and download it into both video and audio files"""
    global PromptMessage, TextContent
    prompt_text = f"""You are a Youtube agent. Your goal is to transcribe a Youtube video and download it into both video and audio files, when you are given a YouTube URL.
    
Please perform the following steps in order:
1. Call the tool `youtube_download_mp4_video` to download it into a video file.
2. Call the tool `youtube_download_mp3_audio` to download it into an audio file.
3. Give me the paths to both downloaded files.


# Here is the request:
---
{request}
---
"""
    return PromptMessage(role="user", content=TextContent(type="text", text=prompt_text))

@mcp.tool
def create_maps(request:str) -> str:
    """Create a map; a location / description of the map is required

Args [required]:
    code: Generate python code that integrates packages 'folium' and 'geopy', when needed, to resolve my request for map creation. Created maps are saved in *.html file. Tell me the file path at the end of your response.
"""
    global agentmake, getResponse
    messages = agentmake(request, **{'tool': 'create/maps'}, **AGENTMAKE_CONFIG)
    return getResponse(messages)

@mcp.tool
def create_qr_code(request:str) -> str:
    """Create QR code; an url / text content is required

Args [required]:
    url: The url that is to be converted into qr code. Return '' if not given.
    text: The text content that is to be converted into qr code. Return '' if not given.
"""
    global agentmake, getResponse
    messages = agentmake(request, **{'tool': 'create/qr_code'}, **AGENTMAKE_CONFIG)
    return getResponse(messages)

@mcp.tool
def create_statistical_graph(request:str) -> str:
    """Create statistical plots, such as pie charts / bar charts / line charts / scatter plots / heatmaps / histograms / boxplots / violin plots / radar charts / polar charts / contour plots / density plots / 3D plots, to visualize statistical data; instruction and data are required

Args [required]:
    code: Generate python code that integrates library `matplotlib` to resolve my input. Save the result in png format. Tell me the saved image path at the end of your response.
"""
    return ""

mcp.run(show_banner=False)
