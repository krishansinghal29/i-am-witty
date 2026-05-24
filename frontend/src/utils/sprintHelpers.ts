export function getExerciseDisplayName(exerciseId: string): string {
  const map: Record<string, string> = {
    yesAnd: 'Yes, And...',
    misinterpretation: 'Misinterpretation',
    loveHate: 'Love/Hate',
    ifByXYouMeanY: 'If by X you mean Y...',
    questionAnswerTease: 'Question Answer Tease',
    vibing: 'Vibing',
    pushPull: 'Push/Pull',
  };
  return map[exerciseId] || 'Sprint Exercise';
}

export function extractSpeechText(question: unknown): string {
  if (Array.isArray(question)) {
    return question
      .filter((p: any) => p.role !== 'Image' && p.content)
      .map((p: any) => p.content)
      .join(' ');
  }
  if (typeof question === 'string') return question;
  return '';
}

export function extractDisplayText(question: unknown): string {
  if (Array.isArray(question)) {
    return question
      .filter((p: any) => p.role !== 'Image')
      .map((p: any) => (p.role && p.content ? `${p.role}: ${p.content}` : p.content || ''))
      .join('\n\n');
  }
  return extractSpeechText(question);
}
