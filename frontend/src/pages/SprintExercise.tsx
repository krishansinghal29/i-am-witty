import { ExerciseHeader } from '@/components/exercise/ExerciseHeader';
import { StepAnalyzing } from '@/components/sprint/StepAnalyzing';
import { StepFeedback } from '@/components/sprint/StepFeedback';
import { StepIntro } from '@/components/sprint/StepIntro';
import { StepListening } from '@/components/sprint/StepListening';
import { StepLoading } from '@/components/sprint/StepLoading';
import { StepRecording } from '@/components/sprint/StepRecording';
import { useUser } from '@/contexts/UserContext';
import { useDeepgramSTT } from '@/hooks/useDeepgramSTT';
import {
  prefetchSprintQuestion,
  useAnalyzeSprintResponse,
  useGenerateSprintQuestion,
  type SprintAnalysisResult,
} from '@/hooks/useSprintPractice';
import type { ExerciseStep } from '@/types/exercise';
import type { QuestionMessage } from '@/types/question';
import { RECORDING_LIMIT_SECONDS, type SprintStep } from '@/utils/sprintConstants';
import { extractDisplayText, getExerciseDisplayName } from '@/utils/sprintHelpers';
import { useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { sprintQuestionQueryKeys } from '@/hooks/queryKeys';

export default function SprintExercise() {
  const { exerciseId, count: routeCount } = useParams<{ exerciseId: string; count?: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { uid } = useUser();
  const count = Number(routeCount) || 1;
  const [step, setStep] = useState<SprintStep>('intro');
  const [scaffoldStage, setScaffoldStage] = useState(1);
  const [displayText, setDisplayText] = useState('');
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [listeningLiveText, setListeningLiveText] = useState('');
  const [questionData, setQuestionData] = useState<QuestionMessage[]>([]);
  const [recordingTimeLeft, setRecordingTimeLeft] = useState(RECORDING_LIMIT_SECONDS);
  const [analysisResult, setAnalysisResult] = useState<SprintAnalysisResult | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recordingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const processedKeyRef = useRef<string | null>(null);
  const scaffoldStageRef = useRef(scaffoldStage);
  scaffoldStageRef.current = scaffoldStage;

  const stt = useDeepgramSTT();

  // Clear cached question whenever the exercise changes so a fresh one is always fetched on tab switch
  useEffect(() => {
    if (exerciseId) {
      queryClient.removeQueries({
        queryKey: sprintQuestionQueryKeys.forUserAndExercise(uid, exerciseId),
      });
    }
  }, [exerciseId]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    setStep('intro');
    setScaffoldStage(1);
    setAnalysisResult(null);
    setAnalysisError(null);
    setRecordingTimeLeft(RECORDING_LIMIT_SECONDS);
    processedKeyRef.current = null;
    stt.resetTranscription();
  }, [count, exerciseId]); // eslint-disable-line react-hooks/exhaustive-deps
  const analyzeMutation = useAnalyzeSprintResponse();

  const { data: questionResult } = useGenerateSprintQuestion(uid, exerciseId || '', count, step === 'loading');

  // When question data arrives, move to listening
  useEffect(() => {
    if (!questionResult || step !== 'loading') return;
    const key = `${exerciseId}-${count}`;
    if (processedKeyRef.current === key) return;
    processedKeyRef.current = key;

    const q = questionResult.question || [];
    setQuestionData(q);
    setDisplayText(extractDisplayText(q));
    setAvatarUrl(questionResult.avatar_image_url || null);

    // Play audio if available
    if (questionResult.audio_base64 && questionResult.content_type) {
      const audio = new Audio(`data:${questionResult.content_type};base64,${questionResult.audio_base64}`);
      audioRef.current = audio;

      const fullText = questionResult.speech_text || extractDisplayText(q);
      const words = fullText.split(/\s+/).filter(Boolean);
      let wordIdx = 0;

      let transitioned = false;
      let fallbackTimer: ReturnType<typeof setTimeout>;

      const goToRecording = () => {
        if (transitioned) return;
        transitioned = true;
        clearInterval(revealInterval);
        clearTimeout(fallbackTimer);
        setListeningLiveText(fullText);
        setStep('recording');
      };

      const revealInterval = setInterval(() => {
        if (wordIdx < words.length) {
          wordIdx++;
          setListeningLiveText(words.slice(0, wordIdx).join(' '));
        }
      }, 150);

      // Use actual audio duration for the fallback so it never fires early.
      // 60s safety net kicks in only if metadata never loads.
      fallbackTimer = setTimeout(goToRecording, 60_000);
      audio.addEventListener('loadedmetadata', () => {
        clearTimeout(fallbackTimer);
        fallbackTimer = setTimeout(goToRecording, (audio.duration + 1) * 1000);
      });

      audio.addEventListener('ended', goToRecording);

      audio.play().catch(goToRecording);

      setStep('listening');
    } else {
      setListeningLiveText(extractDisplayText(q));
      setStep('recording');
    }
  }, [questionResult, step, exerciseId, count]);

  // Recording timer
  const stopTimer = useCallback(() => {
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
  }, []);

  const handleStartRecording = useCallback(async () => {
    setRecordingTimeLeft(RECORDING_LIMIT_SECONDS);
    await stt.startRecording();
    // Timer starts in the useEffect below once stt.isRecording becomes true
  }, [stt]);

  // Start the countdown only after the WebSocket is open and recording has begun
  useEffect(() => {
    if (step !== 'recording' || !stt.isRecording) return;
    recordingTimerRef.current = setInterval(() => {
      setRecordingTimeLeft(prev => {
        if (prev <= 1) {
          stopTimer();
          stt.stopRecording();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return stopTimer;
  }, [stt.isRecording, step]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleStopRecording = useCallback(() => {
    stopTimer();
    stt.stopRecording();
  }, [stt, stopTimer]);

  const handleLearnClick = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    stopTimer();
    stt.stopRecording();
    stt.resetTranscription();
    setScaffoldStage(1);
    setAnalysisResult(null);
    setAnalysisError(null);
    setListeningLiveText('');
    processedKeyRef.current = null;
    setStep('intro');
  }, [stt, stopTimer]);

  // When recording stops & audio is ready, advance scaffold stage or submit for analysis
  useEffect(() => {
    if (step !== 'recording') return;
    if (stt.isRecording || stt.isConnecting) return;
    if (!stt.audioBase64 && !stt.transcript) return;

    if (exerciseId === 'pushPull' && scaffoldStageRef.current < 3) {
      setScaffoldStage(s => s + 1);
      setRecordingTimeLeft(RECORDING_LIMIT_SECONDS);
      stt.resetTranscription();
      return;
    }

    setStep('analyzing');
    setAnalysisError(null);

    analyzeMutation.mutate(
      {
        transcription: stt.transcript,
        audio_base64: stt.audioBase64 || '',
        duration_seconds: stt.durationSeconds,
        word_count: stt.wordCount,
        question_data: questionData,
        exercise_type: exerciseId || '',
      },
      {
        onSuccess: result => { setAnalysisResult(result); setStep('feedback'); },
        onError: err => { setAnalysisError(err.message); setStep('feedback'); },
      },
    );
  }, [stt.isRecording, stt.isConnecting, stt.audioBase64, step]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleRetry = useCallback(() => {
    stt.resetTranscription();
    setRecordingTimeLeft(RECORDING_LIMIT_SECONDS);
    if (exerciseId === 'pushPull') setScaffoldStage(1);
    setStep('recording');
  }, [stt, exerciseId]);

  const handleNext = useCallback(() => {
    prefetchSprintQuestion(queryClient, uid, exerciseId || '', count + 1);
    navigate(`/sprint/${exerciseId}/${count + 1}`);
  }, [navigate, exerciseId, count, queryClient, uid]);

  if (!exerciseId) return null;

  const exerciseStep: ExerciseStep = step === 'intro' ? 'intro' : step === 'feedback' ? 'feedback' : 'practice';

  return (
    <div className="flex flex-col bg-white overflow-hidden h-full">
      <ExerciseHeader exerciseName={getExerciseDisplayName(exerciseId)} step={exerciseStep} onLearn={handleLearnClick} />
      <div className="flex-1 min-h-0 overflow-y-auto flex flex-col">
        {step === 'intro' && <StepIntro exerciseId={exerciseId} onStart={() => setStep('loading')} />}
        {step === 'loading' && <StepLoading />}
        {step === 'listening' && <StepListening listeningLiveText={listeningLiveText} questionData={questionData} avatarUrl={avatarUrl} />}
        {step === 'recording' && (
          <StepRecording
            key={exerciseId === 'pushPull' ? scaffoldStage : 0}
            stt={stt}
            displayText={displayText}
            scaffoldStage={exerciseId === 'pushPull' ? scaffoldStage : undefined}
            recordingTimeLeft={recordingTimeLeft}
            onStartRecording={handleStartRecording}
            onStopRecording={handleStopRecording}
          />
        )}
        {step === 'analyzing' && <StepAnalyzing />}
        {step === 'feedback' && (
          <StepFeedback
            analysisResult={analysisResult}
            error={analysisError}
            userTranscript={stt.transcript}
            userAudioBase64={stt.audioBase64}
            originalQuestion={displayText}
            onRetry={handleRetry}
            onNext={handleNext}
          />
        )}
      </div>
    </div>
  );
}
