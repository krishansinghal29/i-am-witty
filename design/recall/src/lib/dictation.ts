/**
 * Browser dictation through the Web Speech API (Chrome, Edge, Safari).
 * `supported` is false where the API is missing, so callers can hide the
 * control entirely. Text is appended after whatever was there when dictation
 * started; interim words show live and settle as the browser finalises them.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

interface RecognitionAlternative {
  transcript: string;
}

interface RecognitionResult {
  isFinal: boolean;
  0: RecognitionAlternative;
}

interface RecognitionEvent {
  resultIndex: number;
  results: { length: number; [index: number]: RecognitionResult };
}

interface Recognition {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: RecognitionEvent) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

type RecognitionCtor = new () => Recognition;

function recognitionCtor(): RecognitionCtor | null {
  if (typeof window === 'undefined') return null;
  const w = window as unknown as { SpeechRecognition?: RecognitionCtor; webkitSpeechRecognition?: RecognitionCtor };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

export function useDictation(onText: (text: string) => void) {
  const [ctor] = useState(recognitionCtor);
  const [listening, setListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recognition = useRef<Recognition | null>(null);
  const onTextRef = useRef(onText);
  onTextRef.current = onText;

  useEffect(() => () => recognition.current?.abort(), []);

  const start = useCallback(
    (current: string) => {
      if (!ctor || recognition.current) return;
      const rec = new ctor();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = navigator.language || 'en-US';

      const base = current.trim() ? `${current.replace(/\s+$/, '')} ` : '';
      let finals = '';
      rec.onresult = (event) => {
        let interim = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) finals += result[0].transcript;
          else interim += result[0].transcript;
        }
        onTextRef.current(base + `${finals}${interim}`.replace(/\s+/g, ' ').trimStart());
      };
      rec.onerror = (event) => {
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          setError('Microphone access is blocked. Allow it in your browser settings to dictate.');
        } else if (event.error !== 'aborted' && event.error !== 'no-speech') {
          setError('Dictation stopped. Tap Dictate to try again.');
        }
      };
      rec.onend = () => {
        recognition.current = null;
        setListening(false);
      };

      setError(null);
      try {
        rec.start();
        recognition.current = rec;
        setListening(true);
      } catch {
        setError('Dictation could not start. Try again.');
      }
    },
    [ctor],
  );

  const stop = useCallback(() => recognition.current?.stop(), []);

  return { supported: ctor !== null, listening, error, start, stop };
}
