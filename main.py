import asyncio
import subprocess
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero
from api import AssistantFnc  # Importing the functions from api.py
import webbrowser

load_dotenv()


async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are Friday, an ai assistant created by Isha Dewangan. Your interface with users will be through voice."
            "You should use short and concise responses, and avoid usage of unpronouncable punctuations."
            "you should crack some savage jokes and give savage replies"
            "your owner is Isha, her date of birth is 5 april,2003. She is from a small city is Bastar jagdalpur"
            "Your owner's favourite hobbies are to watch horror, suspense thriller movies and shows she also enjoy "
            "asian dramas and animes, also her favourite fast food is momo"
        )
    )

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Load the assistant functionality
    assistant_fnc = AssistantFnc()  # Adding functions from api.py

    assistant = VoiceAssistant(
        vad=silero.VAD.load(),
        stt=openai.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        fnc_ctx=assistant_fnc
    )
    assistant.start(ctx.room)

    await asyncio.sleep(1)
    await assistant.say("Hey, I am FRIDAY! how can i help you today?", allow_interruptions=True)

def start_nextjs_app():
    process = subprocess.Popen(
        ["pnpm","dev"],
        cwd="Friday",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

if __name__ == "__main__":
    nextjs_process = start_nextjs_app()
    webbrowser.open("http://localhost:3000")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))