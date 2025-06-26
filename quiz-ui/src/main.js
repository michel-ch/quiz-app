import './assets/main.css'
import '@fortawesome/fontawesome-free/css/all.css';

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

axios.defaults.baseURL = API_URL;

const app = createApp(App)

app.use(router)

app.config.globalProperties.$axios = axios;

app.mount('#app')
