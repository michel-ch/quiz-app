<template>
  <div class="main-layout grid grid-cols-[400px_1fr] h-[calc(100vh-80px)]">
    
    <div class="left-panel bg-white p-8 flex flex-col justify-center">
      <div>
        <h1 class="text-4xl font-bold text-black pb-4">Inserer votre nom</h1>
        <p v-if="showError" class="text-red-500 text-sm mb-2">Veuillez entrer votre nom pour continuer</p>
        <input
          v-model="playerName"
          placeholder="Votre nom"
          class="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition"
          @input="showError = false"
        />
      </div>
    </div>

    <div class="relative w-full h-full map-background">
      <button 
        class="start-button absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-[#45403C] text-white text-2xl px-8 py-4 rounded-xl shadow-md hover:bg-[#2e2b28] transition"
        @click="handleStart"
      >
        Continuer
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { setPlayerName } from '../utils/player'

const router = useRouter()
const playerName = ref('')
const showError = ref(false)

function handleStart() {
  if (!playerName.value.trim()) {
    showError.value = true
    return
  }
  
  setPlayerName(playerName.value.trim())
  router.push('/quiz')
}
</script>

<style scoped>
.map-background {
  background-image: url('../assets/map.png');
  background-size: cover;
  background-position: center;
}
</style>
