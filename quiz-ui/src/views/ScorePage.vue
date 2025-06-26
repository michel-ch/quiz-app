<template>
  <div class="h-[calc(100vh-80px)] flex items-center justify-center bg-white px-6">
    <div class="max-w-5xl w-full grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
      
      <div>
        <h1 v-if="isFromQuizCompletion" class="text-4xl font-bold text-black mb-6">Vous avez terminé!</h1>
        <p class="text-lg text-black font-medium text-xl pb-2">Votre score : <span class="font-bold">{{ displayScore }}/{{ totalQuestions }}</span></p>
        <p class="text-lg text-black font-medium text-xl pb-6">Votre classement : <span class="font-bold">{{ displayClassement }}</span></p>
        <RouterLink to="/">
          <button class="bg-orange-500 hover:bg-orange-600 text-white font-semibold px-6 py-2 rounded-md transition">
            Accueil
          </button>
        </RouterLink>
      </div>

      <div>
        <h2 class="text-2xl font-bold text-black pb-4 font-bold text-black">Meilleurs scores</h2>
        <ul class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100 shadow-sm">
          <li v-for="(player, index) in bestScores" :key="index" class="flex justify-between px-4 py-2 text-xl font-bold text-black">
            <span>{{ index + 1 }}. {{ player.playerName }}</span>
            <span class="bg-orange-100 text-orange-600 font-semibold px-2 py-0.5 rounded-md text-sm font-bold text-black">
              {{ player.score }}
            </span>
          </li>
        </ul>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { getPlayerName } from '../utils/player'

const route = useRoute()
const instance = getCurrentInstance();
const $axios = instance?.appContext.config.globalProperties.$axios || axios;

const bestScores = ref([])
const score = ref(route.query.score || '0')
const totalQuestions = ref(route.query.totalQuestions || '20')
const classement = ref(route.query.classement || '0/0')

const isFromQuizCompletion = computed(() => {
  return !!(route.query.score && route.query.playerName)
})

const displayScore = computed(() => {
  if (isFromQuizCompletion.value) {
    return score.value
  }
  
  const playerName = getPlayerName()
  if (!playerName) return '0'
  
  const playerScores = bestScores.value.filter(s => s.playerName === playerName)
  if (playerScores.length === 0) return '0'
  
  const highestScore = Math.max(...playerScores.map(s => s.score))
  return highestScore.toString()
})

const displayClassement = computed(() => {
  if (isFromQuizCompletion.value) {
    return classement.value
  }
  
  const playerName = getPlayerName()
  if (!playerName || bestScores.value.length === 0) return '0/0'
  
  const playerScores = bestScores.value.filter(s => s.playerName === playerName)
  if (playerScores.length === 0) return '0/' + bestScores.value.length
  
  const playerBestScore = Math.max(...playerScores.map(s => s.score))
  const playersWithHigherScore = bestScores.value.filter(s => s.score > playerBestScore).length
  const playerRank = playersWithHigherScore + 1
  
  return `${playerRank}/${bestScores.value.length}`
})

onMounted(async () => {
  try {
    const res = await $axios.get('/quiz-info')
    bestScores.value = res.data.scores || []
    
    if (!isFromQuizCompletion.value) {
      totalQuestions.value = res.data.size || '20'
    }
  } catch (err) {
    console.error('Erreur lors du chargement des scores:', err)
  }
})
</script>


<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>
