import React, { useEffect, useRef, useState } from "react";

const MyVoice = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null); // Reference to the canvas element
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null); // Web Audio API context
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null); // Analyser node for audio
  const [micStream, setMicStream] = useState<MediaStream | null>(null); // Store microphone stream
  const [audioData, setAudioData] = useState<Uint8Array | null>(null); // Store the frequency data for visualization

  // Initialize the audio context and analyser once the microphone stream is acquired
  useEffect(() => {
    // Request microphone access
    const getMicStream = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        setMicStream(stream);

        const context = new (window.AudioContext || (window as any).webkitAudioContext)(); // Create AudioContext
        setAudioContext(context);

        // Create a source node from the microphone stream
        const source = context.createMediaStreamSource(stream);

        // Create an analyser node to analyze the audio data
        const analyserNode = context.createAnalyser();
        analyserNode.fftSize = 256; // Set FFT size (frequency bin count)
        source.connect(analyserNode);
        setAnalyser(analyserNode); // Set analyser node
      } catch (err) {
        console.error("Error accessing microphone:", err);
      }
    };

    getMicStream();

    return () => {
      if (micStream) {
        micStream.getTracks().forEach((track) => track.stop()); // Stop microphone stream when the component unmounts
      }
    };
  }, []);

  // Function to draw the bubbles
  const drawBubbles = () => {
    if (analyser && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");
      if (!ctx || !audioData) return;

      const bufferLength = 5;
      const radius = 20; // Bubble radius
      const maxRadius = 50; // Max bubble size
      const width = canvas.width;
      const height = canvas.height;

      // Clear the canvas before drawing
      ctx.clearRect(0, 0, width, height);

      let xPos = width / 2 - (bufferLength * (radius * 2 + 10)) / 2; // Calculate initial X position

      // Draw the bubbles
      for (let i = 0; i < bufferLength; i++) {
        const intensity = audioData[i] / 255; // Get audio intensity (0 to 1)
        const currentRadius = radius + intensity * (maxRadius - radius); // Scale the bubble size based on intensity

        // Determine opacity based on intensity: idle state is almost invisible, active state is more visible
        const opacity = Math.max(0.1, intensity); // Set a minimum opacity of 0.1 for idle state

        ctx.beginPath();
        ctx.arc(xPos, height / 2, currentRadius, 0, 2 * Math.PI);
        ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`; // White color with varying opacity
        ctx.fill();
        ctx.closePath();

        xPos += (radius * 2 + 10); // Move X position for the next bubble
      }

      // Update audio data for the next frame
      analyser.getByteFrequencyData(audioData);

      // Call drawBubbles recursively to animate the bubbles
      requestAnimationFrame(drawBubbles);
    }
  };

  // Start drawing the bubbles once the analyser node is set up
  useEffect(() => {
    if (analyser) {
      const data = new Uint8Array(analyser.frequencyBinCount);
      setAudioData(data);
      drawBubbles(); // Start the bubble animation
    }
  }, [analyser]);

  return (
    <div className="w-full flex items-center justify-center">
      <canvas ref={canvasRef} width={500} height={100}  />
      {!micStream && <p>Loading microphone...</p>}
    </div>
  );
};

export default MyVoice;