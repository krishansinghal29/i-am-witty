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

export function getExerciseDescription(exerciseId: string): string {
  const map: Record<string, string> = {
    yesAnd: '"Yes, and..." improv exercise that trains premise acceptance and creative expansion.',
    misinterpretation: 'Find an unexpected reading in any everyday sentence — turn the mundane into something surprising.',
    loveHate: 'Express nuanced, opinionated takes with charm by balancing genuine love and playful hate.',
    ifByXYouMeanY: 'Redirect criticism into status by reframing what was said into something you can own.',
    questionAnswerTease: 'Balance direct answers with playful tension — answer, then leave them wanting more.',
    vibing: 'Focus on emotional attunement, connection, and keeping conversational momentum alive.',
    pushPull: 'Balance genuine interest with playful challenge — pull them in, then gently push back.',
  };
  return map[exerciseId] || 'Practice your conversational skills with this exercise.';
}

export function extractSpeechText(question: unknown): string {
  if (Array.isArray(question)) {
    return question
      .filter((p: any) => p.content)
      .map((p: any) => p.content)
      .join(' ');
  }
  if (typeof question === 'string') return question;
  return '';
}

export function extractDisplayText(question: unknown): string {
  if (Array.isArray(question)) {
    return question
      .filter((p: any) => p.content)
      .map((p: any) => (p.role && p.content ? `${p.role}: ${p.content}` : p.content || ''))
      .join('\n\n');
  }
  return extractSpeechText(question);
}
