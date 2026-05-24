import { Loader2, Mic, MicOff, Send } from 'lucide-react';
import { useEffect, useState } from 'react';
import QuestionDisplay from '@/components/QuestionDisplay';
import { useUser } from '@/contexts/UserContext';
import { useGenerateQuestion } from '@/hooks';
import { useDeepgramSTT } from '@/hooks/useDeepgramSTT';
import type { QuestionMessage } from '@/types/question';

const ExercisePracticePage = ({
  exerciseId,
  count,
  onNext,
}: {
  exerciseId: string;
  count: number;
  onNext: (exerciseId: string, question: string | QuestionMessage[], userResponse: string) => void;
}) => {
  const { uid } = useUser();
  const { data: questionData, isLoading: isQuestionLoading } = useGenerateQuestion(uid, exerciseId, count);
  const { isRecording, isConnecting, transcript, interimTranscript, startRecording, stopRecording, resetTranscription, error: sttError } = useDeepgramSTT();
  const [responseText, setResponseText] = useState('');

  useEffect(() => {
    const combined = interimTranscript ? `${transcript}${transcript ? ' ' : ''}${interimTranscript}` : transcript;
    if (combined) setResponseText(combined);
  }, [transcript, interimTranscript]);

  const handleToggleRecording = async () => {
    if (isRecording) stopRecording();
    else await startRecording();
  };

  const handleSubmit = () => {
    stopRecording();
    if (!responseText.trim()) return;
    const question = questionData?.question || [];
    resetTranscription();
    setResponseText('');
    onNext(exerciseId, question, responseText);
  };

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="flex-1 overflow-y-auto w-full">
        <div className="px-4 py-4">
          <div className="border border-gray-100 rounded-xl shadow-sm bg-white p-5">
            <div className="text-center mb-5">
              <span className="text-3xl">🎯</span>
              <h2 className="text-xl font-bold text-gray-800 mt-2">Your Turn to Practice</h2>
            </div>
            <QuestionDisplay question={questionData?.question} isLoading={isQuestionLoading} avatarUrl={questionData?.avatar_image_url} className="mb-5" />
            <div className="space-y-4">
              <div>
                <label className="text-sm font-semibold text-gray-600 mb-2 block">Your Response:</label>
                <textarea
                  placeholder={isConnecting ? 'Connecting...' : isRecording ? 'Speak now...' : 'What would you say?'}
                  value={responseText}
                  onChange={e => setResponseText(e.target.value)}
                  className="w-full min-h-[120px] text-base resize-none border border-gray-200 focus:border-orange-300 focus:outline-none rounded-xl p-3"
                  disabled={isQuestionLoading || isConnecting || isRecording}
                />
              </div>
              {sttError && <p className="text-sm text-red-500 text-center">{sttError}</p>}
              <div className="flex justify-center">
                <button
                  onClick={handleToggleRecording}
                  disabled={isConnecting || isQuestionLoading}
                  className={`min-w-[180px] rounded-xl border-2 px-5 py-3 font-semibold flex items-center justify-center gap-2 transition-colors
                    ${isRecording ? 'bg-red-500 border-red-500 text-white' : 'bg-white border-orange-400 text-orange-600 hover:bg-orange-50'}
                    ${(isConnecting || isQuestionLoading) ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                >
                  {isConnecting ? (
                    <><Loader2 className="h-5 w-5 animate-spin" /> Connecting...</>
                  ) : isRecording ? (
                    <><MicOff className="h-5 w-5" /> Stop Recording</>
                  ) : (
                    <><Mic className="h-5 w-5" /> Voice Response</>
                  )}
                </button>
              </div>
              {isRecording && (
                <div className="text-center">
                  <div className="inline-flex items-center gap-2 bg-red-50 text-red-600 px-4 py-2 rounded-full text-sm">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                    Recording in progress...
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      <div className="p-4 bg-white border-t border-gray-100">
        <button
          onClick={handleSubmit}
          disabled={!responseText.trim()}
          className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold py-4 rounded-xl shadow-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-5 h-5" />
          <span>Get Feedback</span>
        </button>
      </div>
    </div>
  );
};

export default ExercisePracticePage;
