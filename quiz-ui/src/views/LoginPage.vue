<template>
  <div class="h-[calc(100vh-80px)] flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded shadow-md w-full max-w-sm">
      <h1 class="text-3xl font-bold mb-6 text-center text-gray-900">Connexion</h1>
      <form @submit.prevent="login">
        <div class="pb-4">
          <label for="username" class="block text-sm font-medium text-gray-700 pb-2"
            >utilisateur</label
          >
          <input
            id="username"
            v-model="username"
            type="text"
            class="w-full border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-700 rounded-md shadow-sm px-3 py-2"
            required
          />
        </div>

        <div class="pb-6">
          <label for="password" class="block text-sm font-medium text-gray-700 pb-2"
            >Mot de passe</label
          >
          <input
            id="password"
            v-model="password"
            type="password"
            class="w-full border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-700 rounded-md shadow-sm px-3 py-2"
            required
          />
        </div>

        <button
          type="submit"
          class="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
        >
          Connexion
        </button>

        <p v-if="error" class="text-red-600 mt-2 text-sm">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { inject } from 'vue';

const isLoggedIn = inject('isLoggedIn', ref(false));

const username = ref('');
const password = ref('');
const error = ref('');
const router = useRouter();

const login = async () => {
  try {
    const res = await axios.post('/login', {
      //username: username.value,
      password: password.value,
    });

    const token = res.data.token;
    localStorage.setItem('token', token);
    isLoggedIn.value = true;
    router.push('/admin');
  } catch (err) {
    error.value = 'Invalid username or password';
  }
};
</script>

<style scoped></style>
