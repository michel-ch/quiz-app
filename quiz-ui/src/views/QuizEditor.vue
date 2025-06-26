<template>
  <div class="p-6 bg-white text-gray-900 h-[calc(100vh-80px)] overflow-y-auto">
    <h1 class="text-3xl font-bold pb-4">Quiz editor</h1>
    <div class="flex gap-4 mb-4">
      <button @click="openModal(null)" class="bg-orange-500 text-white px-4 py-2 rounded">
        + Ajouter
      </button>

      <button
        @click="deleteAllQuestions"
        class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
      >
        🗑️ Supprimer toutes les questions
      </button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-4">
      <div
        v-for="question in questions"
        :key="question.id"
        class="bg-white border border-gray-300 p-4 rounded-lg shadow-md hover:shadow-lg transition"
      >
        <h2 class="font-semibold text-lg text-black mb-2">
          {{ question.position + ' - ' + question.title }}
        </h2>
        <p class="text-sm text-gray-800 pb-4">{{ question.text }}</p>
        <button
          @click="openModal(question)"
          class="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded"
        >
          Modifier
        </button>
      </div>
    </div>

    <QuestionModal
      v-if="showModal"
      :question="selectedQuestion"
      @close="closeModal"
      @saved="fetchQuestions"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, getCurrentInstance } from 'vue';
import axios from 'axios';
import QuestionModal from './QuestionModal.vue';
import type { Question } from '../utils/question';

const instance = getCurrentInstance();
const $axios = instance?.appContext.config.globalProperties.$axios || axios;
$axios.interceptors.request.use((config: { headers: { Authorization: string } }) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const questions = ref<Question[]>([]);
const showModal = ref(false);
const selectedQuestion = ref<Question | null>(null);

const fetchQuestions = async () => {
  const res = await $axios.get('/questions');
  questions.value = res.data;
};

const deleteAllQuestions = async () => {
  await $axios.delete('/questions/all');
  fetchQuestions();
};

const openModal = async (question: Question | null) => {
  if (questions.value.length === 0) {
    try {
      await $axios.post('/rebuild-db');
      await fetchQuestions();
    } catch (err) {
      console.error('Failed to rebuild DB:', err);
      return;
    }
  }

  selectedQuestion.value = question;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  selectedQuestion.value = null;
};

onMounted(fetchQuestions);
</script>

<style scoped></style>
