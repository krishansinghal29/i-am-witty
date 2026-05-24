import { ExerciseHeader } from '@/components/exercise/ExerciseHeader';
import { StepAnalyzing } from '@/components/sprint/StepAnalyzing';
import { StepFeedback } from '@/components/sprint/StepFeedback';
import { StepListening } from '@/components/sprint/StepListening';
import { StepLoading } from '@/components/sprint/StepLoading';
import { StepRecording } from '@/components/sprint/StepRecording';
import { useUser } from '@/contexts/UserContext';
import { useDeepgramSTT } from '@/hooks/useDeepgramSTT';
import { useExerciseById } from '@/hooks/useExerciseMeta';
import {
  prefetchSprintQuestion,
  useAnalyzeSprintResponse,
  useGenerateSprintQuestion,
  type PreviousResponse,
  type SprintAnalysisResult,
} from '@/hooks/useSprintPractice';
import type { ExerciseStep } from '@/types/exercise';
import type { QuestionMessage } from '@/types/question';
import { getExerciseMeta } from '@/utils/getRandomExercisePages';
import { RECORDING_LIMIT_SECONDS, type SprintStep } from '@/utils/sprintConstants';
import { extractDisplayText } from '@/utils/sprintHelpers';
import { useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import ExerciseExamplePage from '../exercise/ExerciseExamplePage';
import ExerciseIntroductionPage from '../exercise/ExerciseIntroductionPage';

function extractImageUrl(question: QuestionMessage[]): string | null {
  const img = question.find(p => p.role === 'Image');
  return img?.content || null;
}

export default function SprintExercise() {
  const { exerciseId, count: routeCount } = useParams<{ exerciseId: string; count?: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { uid } = useUser();
  const count = Number(routeCount) || 1;

  const [step, setStep] = useState<SprintStep>(count === 1 ? 'intro' : 'loading');
  const [displayText, setDisplayText] = useState('');
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [listeningLiveText, setListeningLiveText] = useState('');
  const [questionData, setQuestionData] = useState<QuestionMessage[]>([]);
  const [recordingTimeLeft, setRecordingTimeLeft] = useState(RECORDING_LIMIT_SECONDS);
  const [analysisResult, setAnalysisResult] = useState<SprintAnalysisResult | null>(null);
  const [hasRefined, setHasRefined] = useState(false);
  const [previousResponse, setPreviousResponse] = useState<PreviousResponse | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recordingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const processedKeyRef = useRef<string | null>(null);

  const { exercise: rawExercise } = useExerciseById(exerciseId);
  const exerciseData = useMemo(() => rawExercise ? getExerciseMeta(rawExercise) : null, [rawExercise]);

  const stt = useDeepgramSTT();
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
    setImageUrl(extractImageUrl(q));
    setAvatarUrl(questionResult.avatar_image_url || null);

    // Play audio if available
    if (questionResult.audio_base64 && questionResult.content_type) {
      const audio = new Audio(`data:${questionResult.content_type};base64,${questionResult.audio_base64}`);
      audioRef.current = audio;

      const fullText = questionResult.speech_text || extractDisplayText(q);
      const words = fullText.split(/\s+/).filter(Boolean);
      let wordIdx = 0;

      let transitioned = false;
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

      // Fallback: transition after word reveal + 2s buffer, in case `ended` never fires
      const fallbackTimer = setTimeout(goToRecording, words.length * 150 + 2000);

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
  }, [stt, stopTimer]);

  const handleStopRecording = useCallback(() => {
    stopTimer();
    stt.stopRecording();
  }, [stt, stopTimer]);

  // When recording stops & audio is ready, submit for analysis
  useEffect(() => {
    if (step !== 'recording') return;
    if (stt.isRecording || stt.isConnecting) return;
    if (!stt.audioBase64 && !stt.transcript) return;

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
        previous_response: previousResponse || undefined,
      },
      {
        onSuccess: result => { setAnalysisResult(result); setStep('feedback'); },
        onError: err => { setAnalysisError(err.message); setStep('feedback'); },
      },
    );
  }, [stt.isRecording, stt.isConnecting, stt.audioBase64, step]);

  const handleRefine = useCallback(() => {
    if (!analysisResult) return;
    setPreviousResponse({
      transcription: stt.transcript,
      text_score: analysisResult.text_score,
      voice_score: analysisResult.voice_score,
      overall_score: analysisResult.overall_score,
      feedback_summary: analysisResult.text_feedback,
      text_feedback: analysisResult.text_feedback,
      voice_feedback: analysisResult.voice_feedback,
    });
    setHasRefined(true);
    stt.resetTranscription();
    setRecordingTimeLeft(RECORDING_LIMIT_SECONDS);
    setStep('recording');
  }, [analysisResult, stt]);

  const handleNext = useCallback(() => {
    prefetchSprintQuestion(queryClient, uid, exerciseId || '', count + 1);
    navigate(`/sprint/${exerciseId}/${count + 1}`);
  }, [navigate, exerciseId, count, queryClient, uid]);

  if (!exerciseId) return null;

  const exerciseStep: ExerciseStep = (() => {
    if (step === 'intro') return 'intro';
    if (step === 'example') return 'example';
    if (step === 'feedback') return 'feedback';
    return 'practice';
  })();

  return (
    <div className="flex flex-col bg-white overflow-hidden h-full">
      <ExerciseHeader exerciseName={exerciseData?.name || ''} step={exerciseStep} />
      <div className="flex-1 min-h-0 overflow-y-auto flex flex-col">
        {step === 'intro' && exerciseData && (
          <ExerciseIntroductionPage
            exerciseIntroData={{ id: exerciseData.id, name: exerciseData.name, title: exerciseData.title, description: exerciseData.description, imageUrls: exerciseData.imageUrls, primarySkills: exerciseData.primarySkills }}
            onNext={() => setStep('example')}
          />
        )}
        {step === 'example' && exerciseData && (
          <ExerciseExamplePage
            exerciseExampleData={{ examples: exerciseData.examples }}
            onNext={() => { setStep('loading'); processedKeyRef.current = null; }}
          />
        )}
        {step === 'loading' && <StepLoading />}
        {step === 'listening' && <StepListening listeningLiveText={listeningLiveText} questionData={questionData} avatarUrl={avatarUrl} />}
        {step === 'recording' && (
          <StepRecording
            stt={stt}
            displayText={displayText}
            imageUrl={imageUrl}
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
            hasRefined={hasRefined}
            userTranscript={stt.transcript}
            userAudioBase64={stt.audioBase64}
            onRefine={handleRefine}
            onNext={handleNext}
          />
        )}
      </div>
    </div>
  );
}
