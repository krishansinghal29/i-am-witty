import { CircularProgress } from '@mui/material';

export function StepLoading() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-4 p-8">
      <CircularProgress size={48} sx={{ color: '#ea580c' }} />
      <p className="text-gray-500 font-medium">Preparing your question...</p>
    </div>
  );
}
