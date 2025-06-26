<script setup>
import { RouterLink, RouterView } from 'vue-router';
import { ref, provide, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoggedIn = ref(!!localStorage.getItem('token'));
provide('isLoggedIn', isLoggedIn);

function logout() {
  localStorage.removeItem('token');
  isLoggedIn.value = false;
  router.push('/');
}

onMounted(() => {
  window.addEventListener('storage', () => {
    isLoggedIn.value = !!localStorage.getItem('token');
  });
});
</script>

<template>
  <header>
    <div class="navbar">
      <div class="left">
        <span class="logo">GeoQuiz</span>
        <RouterLink to="/" class="nav-link ">Accueil</RouterLink>
        <RouterLink to="/leaderboard" class="nav-link">Meilleurs scores</RouterLink>
        <RouterLink v-if="isLoggedIn" to="/admin" class="nav-link">Administrateur</RouterLink>
      </div>
      <div class="right">
        <div>
          <button v-if="isLoggedIn" @click="logout" class="login-link">
            <i class="fa fa-user"></i> Deconnexion
          </button>
          <RouterLink v-else to="/login" class="login-link">
            <i class="fa fa-user"></i> Connexion
          </RouterLink>
        </div>
      </div>
    </div>
  </header>

  <RouterView />
</template>
<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  border-bottom: 1px solid #eee;
  background-color: white;
}

.left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.logo {
  font-weight: bold;
  font-size: 1.4rem;
  color: #555555;
  margin-right: 2rem;
}

nav a,
.nav-link {
  text-decoration: none;
  color: #333;
  font-size: 1rem;
}

nav a:hover,
.nav-link:hover {
  color: #fd7e14;
}

nav a,
.login-link {
  text-decoration: none;
  color: #333;
  font-size: 1rem;
}

nav a:hover,
.login-link:hover {
  color: #fd7e14;
}

.right .login-link {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 500;
}

.fa-user {
  color: #fd7e14;
}
</style>
