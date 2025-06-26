<template>
  <div class="fixed inset-0 backdrop-blur-sm flex items-center justify-center z-50">
    <div class="bg-white p-6 rounded w-full max-w-md">
      <h2 class="text-xl font-bold mb-4">
        {{ question ? 'Modifier la question' : 'Ajouter une question' }}
      </h2>

      <form @submit.prevent="save">
        <div class="mb-2">
          <label class="block text-sm font-medium">Titre</label>
          <input v-model="form.title" class="w-full border p-2 rounded" />
        </div>

        <div class="mb-2">
          <label class="block text-sm font-medium">Texte</label>
          <input v-model="form.text" class="w-full border p-2 rounded" />
        </div>

        <div class="mb-2">
          <label class="block text-sm font-medium">Position</label>
          <input
            v-model.number="form.position"
            type="number"
            class="w-full border p-2 rounded"
            :min="1"
          />
        </div>

        <div class="mb-2">
          <label class="block text-sm font-medium"
            >Response (format: text::isCorrect::latitude::longitude)</label
          >
          <textarea v-model="answersInput" class="w-full border p-2 rounded"></textarea>
        </div>

        <div class="mb-2">
          <label class="block text-sm font-medium">Télécharger une image</label>
          <ImageUpload @file-change="imageFileChangedHandler" :fileDataUrl="imageAsb64" />
          <img
            v-if="imageAsb64"
            :src="imageAsb64"
            alt="Preview"
            class="mt-2 rounded border w-full max-h-64 object-contain"
          />
        </div>

        <div class="pb-4">
          <label class="block text-sm font-medium">Copier coller l'image en base64</label>
          <input
            v-model="form.image"
            @input="imageAsb64 = form.image"
            class="w-full border p-2 rounded"
          />
        </div>

        <div class="flex justify-between mt-4">
          <button type="button" @click="$emit('close')" class="px-4 py-2 bg-gray-200 rounded">
            Cancel
          </button>

          <div class="flex gap-2">
            <button
              v-if="question"
              type="button"
              @click="deleteQuestion"
              class="px-4 py-2 bg-red-500 text-white rounded"
            >
              Supprimer
            </button>
            <button type="submit" class="px-4 py-2 bg-green-500 text-white rounded">
              {{ question ? 'Update' : 'Create' }}
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits, getCurrentInstance } from 'vue';
import axios from 'axios';
import type { Question, Answer } from '../utils/question';
import ImageUpload from './ImageUpload.vue';

const instance = getCurrentInstance();
const $axios = instance?.appContext.config.globalProperties.$axios || axios;
$axios.interceptors.request.use((config: { headers: { Authorization: string } }) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const props = defineProps<{ question: Question | null }>();
const emit = defineEmits(['close', 'saved']);

const form = ref<Question>({
  id: 0,
  title: '',
  text: '',
  position: 1,
  image: '',
  possibleAnswers: [],
});
const answersInput = ref('');
const imageAsb64 = ref('');

watch(
  () => props.question,
  (newVal) => {
    if (newVal) {
      form.value = { ...newVal };

      // Format answers with latitude & longitude
      answersInput.value = newVal.possibleAnswers
        .map((a) =>
          [
            a.text ?? '',
            a.isCorrect ? 'true' : 'false',
            (a.latitude ?? 0).toString(),
            (a.longitude ?? 0).toString(),
          ].join('::')
        )
        .join('\n');

      if (newVal.image) {
        imageAsb64.value = newVal.image.startsWith('data:')
          ? newVal.image
          : `data:image/jpeg;base64,${newVal.image}`;
      } else {
        imageAsb64.value = '';
      }
    } else {
      form.value = {
        id: 0,
        title: '',
        text: '',
        position: 1,
        image: '',
        possibleAnswers: [],
      };
      answersInput.value = '';
      imageAsb64.value = '';
    }
  },
  { immediate: true }
);

function imageFileChangedHandler(b64: string) {
  if (!b64.startsWith('data:')) {
    imageAsb64.value = `data:image/png;base64,${b64}`;
  } else {
    imageAsb64.value = b64;
  }
  form.value.image = imageAsb64.value;
}

const save = async () => {
  form.value.possibleAnswers = answersInput.value.split('\n').map((line) => {
    const parts = line.split('::');
    return {
      text: parts[0]?.trim() ?? '',
      isCorrect: parts[1]?.trim() === 'true',
      latitude: parseFloat(parts[2]) || 0,
      longitude: parseFloat(parts[3]) || 0,
    } as Answer;
  });

  if (props.question) {
    await $axios.put(`/questions/${props.question.id}`, form.value);
  } else {
    await $axios.post('/questions', form.value);
  }
  emit('saved');
  emit('close');
};

const deleteQuestion = async () => {
  if (props.question) {
    await $axios.delete(`/questions/${props.question.id}`);
    emit('saved');
    emit('close');
  }
};
</script>
