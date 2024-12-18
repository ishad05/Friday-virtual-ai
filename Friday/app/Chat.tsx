import { useMaybeRoomContext, useVoiceAssistant } from "@livekit/components-react";
import { RoomEvent } from "livekit-client";
import React, { useEffect, useState } from "react";


interface Message {
  sender: "user" | "ai" | undefined;
  text: string | undefined;
}


const ChatUI = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const { agentTranscriptions } = useVoiceAssistant();

  const room = useMaybeRoomContext();
  const [transcriptions, setTranscriptions] = useState<{ [id: string]: TranscriptionSegment }>({});

  useEffect(() => {
    if (!room) {
      return;
    }

    const updateTranscriptions = (segments, participant, publication) => {
      setTranscriptions((prev) => {
        const newTranscriptions = { ...prev };
        for (const segment of segments) {
          newTranscriptions[segment.id] = segment;
          newTranscriptions[segment.id]['isAgent'] = new Boolean(publication.trackInfo.name == 'assistant_voice')
        }
        return newTranscriptions;
      });
    };

    room.on(RoomEvent.TranscriptionReceived, updateTranscriptions);
    return () => {
      room.off(RoomEvent.TranscriptionReceived, updateTranscriptions);
    };
  }, [room]);


  useEffect(() => {
    const transcriptionLength = Object.keys(transcriptions).length
    const newTranscription = transcriptions[Object.keys(transcriptions)[transcriptionLength - 1]]
    
    if (!newTranscription){
      return
    }

    const newMessage: Message = {
      sender: newTranscription['isAgent'] == true ? 'ai' : 'user',
      text: newTranscription.text,
    }

    if (transcriptionLength == messages.length) {
      messages[messages.length - 1] = newMessage
      return
    }

    messages.push(newMessage)
  })

  return (
    <div className="flex flex-col h-full w-full max-h-screen p-10">
      <div className="flex-grow overflow-scroll space-y-2">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-xs rounded-lg px-4 py-2 text-sm text-white ${
                message.sender === "user" ? "bg-blue-500" : "bg-gray-600"
              }`}
            >
              {message.text}
            </div>
          </div>
        ))}
      </div>
      <div>
      </div>
    </div>
  );
};

export default ChatUI;