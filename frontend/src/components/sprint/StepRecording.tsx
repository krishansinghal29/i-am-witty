import { CircularProgress } from '@mui/material';
import { motion } from 'framer-motion';
import { useEffect, useRef } from 'react';
import { useDeepgramSTT } from '@/hooks/useDeepgramSTT';
import { RECORDING_LIMIT_SECONDS } from '@/utils/sprintConstants';

type STTReturn = ReturnType<typeof useDeepgramSTT>;

interface Props {
  stt: STTReturn;
  displayText: string;
  recordingTimeLeft: number;
  onStartRecording: () => Promise<void>;
  onStopRecording: () => void;
}

function getTimerColor(t: number) {
  if (t > 15) return '#10B981';
  if (t > 5) return '#F59E0B';
  return '#EF4444';
}

export function StepRecording({ stt, displayText, recordingTimeLeft, onStartRecording, onStopRecording }: Props) {
  const hasAutoStarted = useRef(false);
  const progress = (recordingTimeLeft / RECORDING_LIMIT_SECONDS) * 100;
  const color = getTimerColor(recordingTimeLeft);

  useEffect(() => {
    if (!hasAutoStarted.current && !stt.isRecording && !stt.isConnecting) {
      hasAutoStarted.current = true;
      void onStartRecording();
    }
  }, [onStartRecording, stt.isConnecting, stt.isRecording]);

  if (stt.error && !stt.isRecording && !stt.isConnecting) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center">
        <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center">
          <span className="text-red-500 text-2xl">⚠️</span>
        </div>
        <p className="text-gray-800 font-semibold">Failed to Connect</p>
        <p className="text-sm text-gray-500">{stt.error}</p>
        <button
          onClick={() => { hasAutoStarted.current = false; void onStartRecording(); }}
          className="px-6 py-3 bg-orange-500 text-white rounded-xl font-semibold hover:bg-orange-600"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (stt.isConnecting) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4">
        <CircularProgress size={48} sx={{ color: '#ea580c' }} />
        <p className="text-gray-500">Connecting microphone...</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-4 p-6">
      {/* Countdown ring */}
      <button
        onClick={onStopRecording}
        title="Click to stop recording"
        className="relative flex flex-col items-center gap-2 cursor-pointer group focus:outline-none"
      >
        <div className="relative flex items-center justify-center" style={{ width: 120, height: 120 }}>
          <CircularProgress variant="determinate" value={100} size={120} thickness={3} sx={{ color: '#f3f4f6', position: 'absolute' }} />
          <CircularProgress variant="determinate" value={progress} size={120} thickness={3} sx={{ color, position: 'absolute', '& .MuiCircularProgress-circle': { transition: 'stroke-dashoffset 1s linear', strokeLinecap: 'round' } }} />
          <div className="w-16 h-16 rounded-full bg-red-500 group-hover:bg-red-600 flex items-center justify-center shadow-lg transition-colors">
            <div className="w-5 h-5 bg-white rounded-sm" />
          </div>
        </div>
        <p className="font-bold text-2xl tabular-nums group-hover:opacity-70 transition-opacity" style={{ color }}>{recordingTimeLeft}s</p>
      </button>
      <p className="text-sm text-gray-500 mb-2">What would you say in this situation?</p>

      {/* Question text */}
      {displayText && (
        <div className="w-full max-w-md bg-gray-50 rounded-xl p-4 border border-gray-100 text-sm text-gray-600 whitespace-pre-line">
          {displayText}
        </div>
      )}

      {/* Wave animation */}
      {stt.isRecording && (
        <div className="flex items-center gap-1.5 my-2">
          {[1, 2, 3, 4, 5].map(i => (
            <motion.div key={i} className="w-1.5 rounded-full bg-red-400"
              animate={{ height: [8, 24, 8] }}
              transition={{ duration: 0.5, delay: i * 0.1, repeat: Infinity, ease: 'easeInOut' }} />
          ))}
        </div>
      )}

      {/* Live transcript */}
      <div className="w-full max-w-md bg-white rounded-xl p-4 border border-gray-100 min-h-[80px] text-sm text-left">
        <span className="text-gray-700">{stt.transcript}</span>
        {stt.interimTranscript && <span className="text-amber-500"> {stt.interimTranscript}</span>}
        {!stt.transcript && !stt.interimTranscript && <span className="text-gray-300">Your words will appear here...</span>}
      </div>

      <div className="flex gap-6 text-center">
        <div><p className="font-bold text-orange-500">{stt.wordCount}</p><p className="text-xs text-gray-400">Words</p></div>
        <div><p className="font-bold text-amber-500">{Math.round(stt.durationSeconds)}s</p><p className="text-xs text-gray-400">Duration</p></div>
      </div>
    </div>
  );
}
