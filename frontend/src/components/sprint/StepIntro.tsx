import { ArrowRight, Sparkles } from 'lucide-react';
import { getExerciseDescription, getExerciseDisplayName } from '@/utils/sprintHelpers';

interface Props {
  exerciseId: string;
  onStart: () => void;
}

export function StepIntro({ exerciseId, onStart }: Props) {
  const name = getExerciseDisplayName(exerciseId);
  const description = getExerciseDescription(exerciseId);

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="flex-1 overflow-y-auto p-4">
        <div className="border border-gray-100 rounded-xl overflow-hidden shadow-sm">
          <div className="p-5 bg-white">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <span className="text-orange-600 text-sm font-semibold">Today's Focus</span>
            </div>
            <h2 className="text-xl font-bold text-gray-800 mb-3">{name}</h2>
            <p className="text-base text-gray-600 leading-relaxed">{description}</p>
          </div>
        </div>
      </div>
      <div className="p-4 bg-white border-t border-gray-100">
        <button
          onClick={onStart}
          className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold py-4 rounded-xl shadow-lg flex items-center justify-center gap-2"
        >
          <span>Start Practicing</span>
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
