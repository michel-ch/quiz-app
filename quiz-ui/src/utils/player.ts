export function setPlayerName(name: string) {
  localStorage.setItem('playerName', name);
}

export function getPlayerName(): string | null {
  return localStorage.getItem('playerName');
} 