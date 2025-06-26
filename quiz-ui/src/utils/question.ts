export interface Question {
  id: number;
  image: string;
  position: number;
  possibleAnswers: Answer[];
  text: string;
  title: string;
}

export interface Answer {
  isCorrect: boolean;
  text: string;
  latitude?: number;
  longitude?: number;
}
