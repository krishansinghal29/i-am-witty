/**
 * useDeepgramSTT - Hook for real-time streaming speech-to-text via Deepgram WebSocket
 * 
 * Captures microphone audio, streams to Deepgram WebSocket, receives word-by-word
 * transcription. Simultaneously collects raw audio chunks for backend voice analysis.
 * Works on both web and Capacitor WebView (uses standard Web APIs).
 */

import { useState, useRef, useCallback, useMemo, useEffect } from 'react';

export const useDeepgramSTT = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  /** Base64-encoded audio blob captured during the recording session */
  const [audioBase64, setAudioBase64] = useState<string | null>(null);
  /** Recording duration in seconds (updated in real-time and finalized on stop) */
  const [durationSeconds, setDurationSeconds] = useState(0);

  const socketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const startTimeRef = useRef<number>(0);
  const lastSpeechTimeRef = useRef<number>(0);
  const pauseCountRef = useRef<number>(0);
  const wordCountRef = useRef<number>(0);
  const finalTranscriptRef = useRef<string>('');
  const isRecordingRef = useRef(false);
  /** Stores the resolved mimeType used by MediaRecorder */
  const mimeTypeRef = useRef<string>('');
  /** Collects raw audio chunks for building the final audio blob */
  const audioChunksRef = useRef<Blob[]>([]);

  const resetTranscription = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    setError(null);
    setAudioBase64(null);
    setDurationSeconds(0);
    wordCountRef.current = 0;
    pauseCountRef.current = 0;
    finalTranscriptRef.current = '';
    startTimeRef.current = 0;
    audioChunksRef.current = [];
  }, []);

  const stopRecording = useCallback(() => {
    // Stop media recorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    mediaRecorderRef.current = null;

    // Close WebSocket
    if (socketRef.current) {
      if (socketRef.current.readyState === WebSocket.OPEN) {
        // Send close message to Deepgram
        socketRef.current.send(JSON.stringify({ type: 'CloseStream' }));
      }
      socketRef.current.close();
      socketRef.current = null;
    }

    // Stop media stream tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Calculate final duration - only if we actually started recording
    const finalDuration = startTimeRef.current > 0
      ? (Date.now() - startTimeRef.current) / 1000
      : 0;
    setDurationSeconds(finalDuration);

    // Build audio blob from collected chunks and convert to base64
    if (audioChunksRef.current.length > 0) {
      const finalMimeType = mimeTypeRef.current || 'audio/webm';
      const audioBlob = new Blob(audioChunksRef.current, { type: finalMimeType });
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result;
        if (typeof result === 'string') {
          const base64 = result.split(',')[1]; // strip data:... prefix
          setAudioBase64(base64 ?? null);
        }
      };
      reader.readAsDataURL(audioBlob);
    }

    setIsRecording(false);
    isRecordingRef.current = false;
    setIsConnecting(false);
    // Move interim to final
    setInterimTranscript('');
  }, []);

  const startRecording = useCallback(async () => {
    setError(null);
    setIsConnecting(true);
    resetTranscription();

    try {
      const token = (import.meta.env['VITE_DEEPGRAM_API_KEY'] as string | undefined)?.trim();
      if (!token) {
        throw new Error('Missing VITE_DEEPGRAM_API_KEY in frontend environment');
      }

      // 1. Get microphone access
      if (!navigator.mediaDevices?.getUserMedia) {
        throw Object.assign(new Error('MediaDevices API unavailable'), { name: 'NotSupportedError' });
      }
      // Avoid exact sampleRate/channelCount constraints — they cause NotFoundError
      // on devices that don't natively support those exact values.
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      streamRef.current = stream;

      // 2. Open WebSocket to Deepgram
      const wsUrl = `wss://api.deepgram.com/v1/listen?model=nova-3&language=en&smart_format=true&filler_words=true&punctuate=true&interim_results=true`;
      
      const socket = new WebSocket(wsUrl, ['token', token]);
      socketRef.current = socket;

      // If the WebSocket never opens (network hang, firewall, etc.) clear the stuck state.
      const connectTimeout = setTimeout(() => {
        if (!isRecordingRef.current) {
          console.warn('[DeepgramSTT] Connection timed out');
          try { socket.close(); } catch { /* ignore */ }
          socketRef.current = null;
          if (streamRef.current) {
            streamRef.current.getTracks().forEach(t => t.stop());
            streamRef.current = null;
          }
          setError('Connection timed out. Check your internet and try again.');
          setIsConnecting(false);
        }
      }, 10_000);

      socket.onopen = () => {
        clearTimeout(connectTimeout);
        console.log('[DeepgramSTT] WebSocket connected');
        setIsConnecting(false);
        setIsRecording(true);
        isRecordingRef.current = true;
        startTimeRef.current = Date.now();
        lastSpeechTimeRef.current = Date.now();

        // 3. Determine best supported mimeType and start MediaRecorder
        let selectedMimeType = '';
        if (typeof MediaRecorder.isTypeSupported === 'function') {
          const types = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/mp4',
            'audio/aac',
            'audio/ogg;codecs=opus',
          ];
          for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
              selectedMimeType = type;
              break;
            }
          }
        }
        mimeTypeRef.current = selectedMimeType;

        const options = selectedMimeType ? { mimeType: selectedMimeType } : undefined;
        const mediaRecorder = new MediaRecorder(stream, options);
        
        // If the browser selected a different mimeType internally, update our ref
        if (mediaRecorder.mimeType) {
          mimeTypeRef.current = mediaRecorder.mimeType;
        }
        
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            // Collect chunks for final audio blob
            audioChunksRef.current.push(event.data);
            // Stream to Deepgram for real-time transcription
            if (socket.readyState === WebSocket.OPEN) {
              socket.send(event.data);
            }
          }
        };

        // Send audio chunks every 250ms for real-time feel
        mediaRecorder.start(250);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'Results' && data.channel?.alternatives?.[0]) {
            const alternative = data.channel.alternatives[0];
            const transcriptText = alternative.transcript || '';
            
            if (data.is_final) {
              // Final result — append to transcript
              if (transcriptText.trim()) {
                finalTranscriptRef.current += (finalTranscriptRef.current ? ' ' : '') + transcriptText.trim();
                setTranscript(finalTranscriptRef.current);
                setInterimTranscript('');

                // Count words
                wordCountRef.current = finalTranscriptRef.current.split(/\s+/).filter(w => w.length > 0).length;

                // Track pauses (gap > 2 seconds between speech)
                const now = Date.now();
                if (now - lastSpeechTimeRef.current > 2000 && lastSpeechTimeRef.current > 0) {
                  pauseCountRef.current += 1;
                }
                lastSpeechTimeRef.current = now;
              }
            } else {
              // Interim result — show in real-time (not final)
              setInterimTranscript(transcriptText);
            }

            // Update duration in real-time
            if (startTimeRef.current > 0) {
              setDurationSeconds((Date.now() - startTimeRef.current) / 1000);
            }
          }
        } catch (err) {
          console.warn('[DeepgramSTT] Error parsing message:', err);
        }
      };

      socket.onerror = (event) => {
        clearTimeout(connectTimeout);
        console.error('[DeepgramSTT] WebSocket error:', event);
        // onclose fires after onerror with the actual code/reason — let it set the error
      };

      socket.onclose = (event) => {
        clearTimeout(connectTimeout);
        console.log('[DeepgramSTT] WebSocket closed:', event.code, event.reason);
        if (!isRecordingRef.current && event.code === 1000) return; // clean close after stopRecording

        let errorMsg: string | null = null;
        if (event.code === 1008 || event.code === 4010 || event.code === 4011) {
          errorMsg = 'Speech recognition auth failed. Check your Deepgram API key.';
        } else if (event.code === 1006) {
          // Abnormal closure — often means the connection was never established
          errorMsg = 'Speech recognition connection failed. Check your internet connection.';
        } else if (event.code !== 1000 && event.code !== 1001) {
          errorMsg = `Speech recognition error (${event.code}${event.reason ? ': ' + event.reason : ''})`;
        }

        if (errorMsg) setError(errorMsg);

        if (isRecordingRef.current) {
          stopRecording();
        }
      };
    } catch (err: any) {
      console.error('[DeepgramSTT] Error starting recording:', err);

      // Release any resources that were acquired before the error
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      if (socketRef.current) {
        try { socketRef.current.close(); } catch { /* ignore */ }
        socketRef.current = null;
      }

      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setError('Microphone access denied. Please allow microphone access in your browser.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        // Chrome on macOS throws NotFoundError when the OS-level mic permission is denied
        setError('Microphone not accessible. Check that your browser has microphone permission in System Settings → Privacy → Microphone.');
      } else if (err.name === 'NotSupportedError') {
        setError('Microphone is not supported on this connection. Please use HTTPS or localhost.');
      } else {
        setError(`Unable to access microphone: ${err.message || 'unknown error'}`);
      }

      setIsConnecting(false);
      setIsRecording(false);
      isRecordingRef.current = false;
    }
  }, [resetTranscription, stopRecording]);

  // Release mic + socket when the component using this hook unmounts
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        try { mediaRecorderRef.current.stop(); } catch { /* ignore */ }
      }
      mediaRecorderRef.current = null;
      if (socketRef.current) {
        try { socketRef.current.close(); } catch { /* ignore */ }
        socketRef.current = null;
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };
  }, []);

  // Return a stable object via useMemo to prevent infinite re-renders
  // in consumers who use this as a dependency
  return useMemo(() => ({
    isRecording,
    isConnecting,
    transcript,
    interimTranscript,
    /** Base64-encoded raw audio from the recording session */
    audioBase64,
    /** Recording duration in seconds */
    durationSeconds,
    /** Number of detected pauses (gaps > 2s between speech) */
    pauseCount: pauseCountRef.current,
    /** Total words spoken */
    wordCount: wordCountRef.current,
    error,
    startRecording,
    stopRecording,
    resetTranscription,
  }), [
    isRecording,
    isConnecting,
    transcript,
    interimTranscript,
    audioBase64,
    durationSeconds,
    error,
    startRecording,
    stopRecording,
    resetTranscription,
  ]);
};
