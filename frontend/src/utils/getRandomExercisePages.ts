import type { ExampleOptions, Exercise } from '@/types/exercise';

const pickRandom = <T>(items?: T[]): T | undefined => {
  if (!items || items.length === 0) return undefined;
  return items[Math.floor(Math.random() * items.length)];
};

export const getExerciseMeta = (exercise: Exercise): Exercise => {
  const title = pickRandom(exercise.title);
  const description = pickRandom(exercise.description);
  const imageUrl = pickRandom(exercise.imageUrls);

  let examples: ExampleOptions[] | undefined;
  if (exercise.examples) {
    const keys = Object.keys(exercise.examples);
    const randomKey = pickRandom(keys);
    if (randomKey) examples = exercise.examples[randomKey];
  }

  return {
    id: exercise.id || '',
    ...(exercise.name && { name: exercise.name }),
    ...(title !== undefined && { title: [title] }),
    ...(description !== undefined && { description: [description] }),
    ...(exercise.primarySkills && { primarySkills: [...exercise.primarySkills] }),
    ...(imageUrl && { imageUrls: [imageUrl] }),
    ...(examples !== undefined && { examples: { default: examples } }),
  };
};
