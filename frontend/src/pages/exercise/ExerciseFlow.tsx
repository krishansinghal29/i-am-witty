import { motion } from 'framer-motion';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ExerciseHeader } from '@/components/exercise/ExerciseHeader';
import { useExerciseById } from '@/hooks';
import type { Exercise, ExerciseStep } from '@/types/exercise';
import type { QuestionMessage } from '@/types/question';
import { getExerciseMeta } from '@/utils/getRandomExercisePages';
import ExerciseExamplePage from './ExerciseExamplePage';
import ExerciseFeedbackPage from './ExerciseFeedbackPage';
import ExerciseIntroductionPage from './ExerciseIntroductionPage';
import ExercisePracticePage from './ExercisePracticePage';

const ExerciseFlow = () => {
  const { exerciseId, count: routeCount } = useParams<{ exerciseId: string; count: string }>();
  const navigate = useNavigate();
  const count = Number(routeCount) || 1;
  const [step, setStep] = useState<ExerciseStep>(count === 1 ? 'intro' : 'practice');
  const [userResponse, setUserResponse] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState<string | QuestionMessage[]>('');
  const [exerciseData, setExerciseData] = useState<Exercise | null>(null);

  const { exercise: rawExercise, isLoading } = useExerciseById(exerciseId);
  const randomizedExercise = useMemo(() => (rawExercise ? getExerciseMeta(rawExercise) : null), [rawExercise]);

  useEffect(() => {
    if (randomizedExercise) setExerciseData(randomizedExercise);
  }, [randomizedExercise]);

  useEffect(() => {
    setStep(count === 1 ? 'intro' : 'practice');
  }, [count]);

  if (isLoading || !exerciseId) {
    return <div className="h-screen flex items-center justify-center text-gray-400">Loading...</div>;
  }

  if (!exerciseData) {
    return <div className="h-screen flex items-center justify-center text-gray-400">Exercise not found</div>;
  }

  const handleContinue = (_id?: string, question?: string | QuestionMessage[], response?: string) => {
    if (question) setCurrentQuestion(question);
    if (response) setUserResponse(response);

    switch (step) {
      case 'intro': setStep('example'); break;
      case 'example': setStep('practice'); break;
      case 'practice': setStep('feedback'); break;
      case 'feedback':
        navigate(`/exercise/${exerciseData.id}/${count + 1}`);
        break;
    }
  };

  return (
    <div className="flex flex-col bg-white overflow-hidden h-full">
      <ExerciseHeader exerciseName={exerciseData.name || ''} step={step} />
      <div className="flex-1 min-h-0 relative overflow-y-auto">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.2 }}
          className="h-full flex flex-col"
        >
          {step === 'intro' && (
            <ExerciseIntroductionPage
              exerciseIntroData={{ id: exerciseData.id, name: exerciseData.name, title: exerciseData.title, description: exerciseData.description, imageUrls: exerciseData.imageUrls, primarySkills: exerciseData.primarySkills }}
              onNext={handleContinue}
            />
          )}
          {step === 'example' && (
            <ExerciseExamplePage
              exerciseExampleData={{ examples: exerciseData.examples }}
              onNext={handleContinue}
            />
          )}
          {step === 'practice' && (
            <ExercisePracticePage
              exerciseId={exerciseData.id ?? ''}
              count={count}
              onNext={handleContinue}
            />
          )}
          {step === 'feedback' && (
            <ExerciseFeedbackPage
              exerciseId={exerciseData.id ?? ''}
              question={currentQuestion}
              userResponse={userResponse}
              count={count}
              onNext={handleContinue}
            />
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default ExerciseFlow;
