import { ArrowRight, Sparkles } from 'lucide-react';
import type { ExerciseIntroData } from '@/types/exercise';

const ExerciseIntroductionPage = ({
  exerciseIntroData,
  onNext,
}: {
  exerciseIntroData: ExerciseIntroData;
  onNext: () => void;
}) => (
  <div className="flex flex-col h-full bg-white">
    <div className="flex-1 overflow-y-auto w-full">
      <div className="px-4 py-4">
        <div className="border border-gray-100 rounded-xl overflow-hidden shadow-sm">
          {exerciseIntroData.imageUrls?.[0] && (
            <div className="aspect-video bg-gray-50">
              <img
                src={exerciseIntroData.imageUrls[0]}
                alt={exerciseIntroData.name}
                className="w-full h-full object-cover"
              />
            </div>
          )}
          <div className="p-5 bg-white">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <span className="text-orange-600 text-sm font-semibold">Today's Focus</span>
            </div>
            {exerciseIntroData.title?.[0] && (
              <h2 className="text-xl font-bold text-gray-800 mb-3">{exerciseIntroData.title[0]}</h2>
            )}
            {exerciseIntroData.description?.[0] && (
              <p className="text-base text-gray-600 mb-4 leading-relaxed">{exerciseIntroData.description[0]}</p>
            )}
            {(exerciseIntroData.primarySkills?.length ?? 0) > 0 && (
              <div className="flex flex-wrap gap-2">
                {exerciseIntroData.primarySkills!.map(skill => (
                  <span key={skill} className="px-2 py-1 bg-orange-50 text-orange-700 text-xs rounded-full border border-orange-200 font-medium">
                    {skill.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
    <div className="p-4 bg-white border-t border-gray-100">
      <button
        onClick={onNext}
        className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold py-4 rounded-xl shadow-lg flex items-center justify-center gap-2"
      >
        <span>Learn By Example</span>
        <ArrowRight className="w-5 h-5" />
      </button>
    </div>
  </div>
);

export default ExerciseIntroductionPage;
