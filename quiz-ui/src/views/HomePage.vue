<template>
  <div class="main-layout grid grid-cols-[400px_1fr] h-[calc(100vh-80px)]">
    <div class="left-panel bg-white p-8 flex flex-col justify-start gap-6">
      <div>
        <h1 class="text-4xl font-bold text-black py-2">Geoquiz</h1>
        <p class="text-gray-700 text-xl">Tester votre connaissance géographique</p>
      </div>

      <div>
        <h2 class="text-xl font-bold text-black pb-4 font-bold text-black">Meilleurs scores</h2>
        <ul class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100 shadow-sm">
          <li v-for="(player, index) in bestScores" :key="index" class="flex justify-between px-4 py-2 text-lg font-bold text-black">
            <span>{{ index + 1 }}. {{ player.playerName }}</span>
            <span class="pl-3">
              <span class="bg-orange-100 text-orange-600 font-semibold px-2 py-0.5 rounded-md text-sm font-bold text-black">
                {{ player.score }}
              </span>
            </span>
          </li>
        </ul>
      </div>
    </div>

    <div class="map-container relative w-full h-full">
      <img src="../assets/map.png" alt="Map" class="w-full h-full object-cover" />
      <RouterLink to="/start">
        <button class="start-button absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-[#45403C] text-white text-2xl px-8 py-4 rounded-xl shadow-md hover:bg-[#2e2b28] transition">
          Commencer
        </button>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeMount, getCurrentInstance } from 'vue'
import axios from 'axios'

const instance = getCurrentInstance();
const $axios = instance?.appContext.config.globalProperties.$axios || axios;

const bestScores = ref([])

async function getBestScores(){
  try {
    const res = await $axios.get('/quiz-info');
    bestScores.value = res.data.scores || [];
  } catch (err) {
    console.error('Erreur lors du chargement des scores:', err)
  }
}
onBeforeMount (async () => {
  getBestScores();
})
</script>
