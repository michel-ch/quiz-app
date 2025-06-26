<script setup lang="ts">
import { ref, onBeforeMount, onMounted, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { getPlayerName } from '../utils/player';
import type { Question, Answer } from '../utils/question';
import SuccessIcon from '../components/icons/SuccessIcon.vue';
import FailIcon from '../components/icons/FailIcon.vue';
import L from 'leaflet';
import 'leaflet/dist/images/marker-shadow.png';
import 'leaflet/dist/images/marker-icon.png';
import 'leaflet/dist/images/marker-icon-2x.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
});

const instance = getCurrentInstance();
const $axios = instance?.appContext.config.globalProperties.$axios || axios;
const router = useRouter();

const currentQuestion = ref<Question>({
  id: 0,
  image: '',
  position: 0,
  possibleAnswers: [],
  text: '',
  title: '',
});

const playerName = getPlayerName();
const selectedAnswers = ref<number[]>([]);
const questionsSize = ref(0);
const currentQuestionId = ref(1);

const showFeedbackModal = ref(false);
const isCorrectAnswer = ref(false);
const feedbackMessage = ref('');
const selectedAnswerText = ref('');

const mapContainer = ref<HTMLElement | null>(null);
let map: L.Map | null = null;
let currentMarkers: L.Marker[] = [];

function addZeros(number: number | string): string {
  let n, s;
  if (Number.isInteger(number)) {
    n = Math.abs(number as number);
    s = n.toString();
  } else {
    s = number.toString();
  }
  let result = s.length == 1 ? '0' + s : s;
  return result;
}

onBeforeMount(() => {
  getQuestionsSize();
  getQuestion(currentQuestionId.value);
});

onMounted(() => {
  setTimeout(() => {
    initializeMap();
  }, 100);
});

function initializeMap() {
  if (!mapContainer.value) return;

  if (!map) {
    map = L.map(mapContainer.value, {
      center: [0, 0],
      zoom: 2,
      zoomControl: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 18
    }).addTo(map);

    setTimeout(() => {
      if (map) {
        map.invalidateSize();
      }
    }, 300);
  }
  updateMarkersForCurrentQuestion();
}

function updateMarkersForCurrentQuestion() {
  if (!map) return;

  currentMarkers.forEach(marker => {
    map!.removeLayer(marker);
  });
  currentMarkers = [];

  let centerLat = 0;
  let centerLng = 0;
  let validAnswers = 0;

  if (currentQuestion.value.possibleAnswers && currentQuestion.value.possibleAnswers.length > 0) {
    let tempLat = 0;
    let tempLng = 0;
    
    for (const ans of currentQuestion.value.possibleAnswers) {
      if (ans?.latitude && ans?.longitude) {
        tempLat += ans.latitude;
        tempLng += ans.longitude;
        validAnswers++;
      }
    }
    
    if (validAnswers > 0) {
      centerLat = tempLat / validAnswers;
      centerLng = tempLng / validAnswers;
    }

    for (const ans of currentQuestion.value.possibleAnswers) {
      if (ans?.latitude && ans?.longitude) {
        const marker = L.marker([ans.latitude, ans.longitude]).addTo(map);
        currentMarkers.push(marker);
      }
    }
  }

  if (currentMarkers.length > 1) {
    const group = new L.FeatureGroup(currentMarkers);
    map.fitBounds(group.getBounds().pad(0.1));
  } else if (currentMarkers.length === 1) {
    map.setView([centerLat, centerLng], 10);
  } else if (validAnswers === 0) {
    map.setView([0, 0], 2);
  }
}

async function getQuestionsSize() {
  try {
    const response = await $axios.get('/quiz-info');
    questionsSize.value = response.data.size;
  } catch (error) {
    console.error('Error getting questions:', error);
  }
}

async function getQuestion(questionId: number) {
  try {
    const response = await $axios.get(`/questions?position=${questionId}`);
    const data = response.data;
    if (!data || !Array.isArray(data.possibleAnswers)) {
      console.error('API response for question is malformed or missing possibleAnswers:', data);
      return;
    }

    currentQuestion.value = {
      id: data.id,
      image: data.image,
      position: data.position,
      possibleAnswers: data.possibleAnswers.map((ans: Answer) => ({
        isCorrect: ans.isCorrect,
        text: ans.text,
        latitude: ans.latitude,
        longitude: ans.longitude,
      })),
      text: data.text,
      title: data.title,
    };
    
    // Update markers for the new question
    if (map) {
      updateMarkersForCurrentQuestion();
    }
  } catch (error) {
    console.error('Error getting questions:', error);
  }
}

async function submitAnswer(answerIndex: number) {
  const selectedAnswer = currentQuestion.value.possibleAnswers[answerIndex];
  selectedAnswerText.value = selectedAnswer.text;
  isCorrectAnswer.value = selectedAnswer.isCorrect;
  
  if (isCorrectAnswer.value) {
    feedbackMessage.value = 'Correct!';
  } else {
    const correctAnswer = currentQuestion.value.possibleAnswers.find(ans => ans.isCorrect);
    feedbackMessage.value = correctAnswer ? `Incorrect! La bonne réponse était: ${correctAnswer.text}` : 'Incorrect!';
  }
  selectedAnswers.value.push(answerIndex + 1);
  showFeedbackModal.value = true;
}

function continueToNextQuestion() {
  showFeedbackModal.value = false;
  if (selectedAnswers.value.length >= questionsSize.value) {
    finishQuiz();
  } else {
    currentQuestionId.value++;
    getQuestion(currentQuestionId.value);
  }
}

async function finishQuiz() {
  try {
    const response = await $axios.post('/participations', {
      playerName: playerName,
      answers: selectedAnswers.value,
    });
        
    const quizInfoResponse = await $axios.get('/quiz-info');
    const { scores } = quizInfoResponse.data;
    
    const playerScore = response.data.score;
    const playersWithHigherScore = scores.filter((s: any) => s.score > playerScore).length;
    const currentPlayerRank = playersWithHigherScore + 1;
    
    router.push({
      name: 'leaderboard',
      query: {
        score: playerScore,
        totalQuestions: questionsSize.value,
        classement: `${currentPlayerRank}/${scores.length}`,
        playerName: playerName
      }
    });
  } catch (error) {
    router.push({
      name: 'leaderboard',
      query: {
        score: 0,
        totalQuestions: questionsSize.value,
        classement: '0/0',
        playerName: playerName
      }
    });
  }
}

function formatImage(image: string) {
  if (image.startsWith('data:') || image.startsWith('http')) return image;
  return `data:image/png;base64,${image}`;
}
</script>

<template>
  <div class="h-[calc(100vh-80px)] flex flex-col overflow-hidden relative">
    <main class="flex-1 relative min-h-0">
      <div ref="mapContainer" class="w-full h-full map-container"></div>
    </main>

    <!-- Questionnaire bar - will stick to bottom -->
    <div class="flex-shrink-0 bg-white animate-slideUp">
      <div class="flex flex-col md:flex-row items-center justify-between py-4">
        <div class="px-10 py-3 w-full md:w-2/6">
          <div class="flex flex-grow flex-row">
            <div class="w-1/6 xl:w-1/6 text-2xl xl:text-3xl 2xl:text-5xl font-bold text-black">
              {{ addZeros(currentQuestion.position) }}
            </div>
            <div class="w-5/6 xl:w-5/6 text-2xl xl:text-3xl 2xl:text-5xl font-bold text-black">
              {{ currentQuestion.text }}
            </div>
          </div>
        </div>

        <!-- Middle section: Answer buttons -->
        <div class="px-10 py-3 w-full md:w-3/6 2xl:w-2/6">
          <div class="grid grid-cols-2 gap-4 lg:gap-8">
            <button
              v-for="(option, index) in currentQuestion.possibleAnswers"
              :key="index"
              class="bg-[#FD7E14] hover:bg-blue-500 text-white text-xl lg:text-2xl font-semibold py-2 px-4 rounded-xl shadow transition-colors duration-200 button-space"
              @click.stop="submitAnswer(index)"
            >
              <p class="">
                {{ option.text }}
              </p>
            </button>
          </div>
        </div>

        <!-- Right section: Image -->
        <div class="w-full md:w-1/6 lg:w-1/6 flex justify-center">
          <img
            v-if="currentQuestion.image"
            :src="formatImage(currentQuestion.image)"
            alt="Question illustration"
            class="h-full w-full object-contain"
          />
        </div>
      </div>
    </div>

    <!-- Feedback Modal -->
    <div
      v-if="showFeedbackModal"
      class="feedback-modal backdrop-blur-sm flex items-center justify-center"
    >
      <div class="bg-white p-8 rounded-lg shadow-xl max-w-md w-full mx-4 relative">
        <div class="text-center">
          <!-- Icon and result -->
          <div class="mb-4">
            <div
              v-if="isCorrectAnswer"
              class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2"
            >
              <SuccessIcon />
            </div>
            <div
              v-else
              class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-2"
            >
              <FailIcon />
            </div>
          </div>

          <!-- Feedback message -->
          <h2
            :class="[
              'text-2xl font-bold mb-4',
              isCorrectAnswer ? 'text-green-600' : 'text-red-600'
            ]"
          >
            {{ isCorrectAnswer ? 'Génial!' : 'Oups!' }}
          </h2>
          
          <p class="text-lg mb-2">
            Votre réponse: <strong>{{ selectedAnswerText }}</strong>
          </p>
          
          <p
            :class="[
              'text-base mb-6',
              isCorrectAnswer ? 'text-green-700' : 'text-red-700'
            ]"
          >
            {{ feedbackMessage }}
          </p>

          <!-- Progress indicator -->
          <p class="text-sm text-gray-600 mb-6">
            Question {{ currentQuestionId }} sur {{ questionsSize }}
          </p>

          <!-- Continue button -->
          <button
            @click="continueToNextQuestion"
            class="bg-[#FD7E14] hover:bg-blue-500 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200"
          >
            {{ currentQuestionId < questionsSize ? 'Continue' : 'Finish Quiz' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
@import 'leaflet/dist/leaflet.css';
</style>

<style scoped>
/* Ensure map container has proper dimensions */
.map-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

/* Ensure modal displays above everything */
.feedback-modal {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 9999 !important;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.animate-slideUp {
  animation: slideUp 0.3s ease-out;
}

.button-space {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
}
.button-container {
  display: flex;
  gap: 10px;
}
</style>
