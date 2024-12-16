import asyncio

from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero
from api import AssistantFnc  # Importing the functions from api.py

load_dotenv()


async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are Friday, an ai assistant created by Isha Dewangan. Your interface with users will be through voice."
            "You should use short and concise responses, and avoid usage of unpronouncable punctuations."
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


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))