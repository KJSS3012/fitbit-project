<template>
  <div>
    <h1>PulseLink</h1>

    <button @click="login">
      Conectar com Fitbit
    </button>

    <button @click="getProfile">
      Ver perfil
    </button>

    <pre>{{ profile }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const profile = ref(null)

const login = () => {
  window.location.href = 'http://localhost:8000/auth/fitbit'
}

const getProfile = async () => {
  profile.value = await $fetch('http://localhost:8000/auth/fitbit/profile')
}
</script>
