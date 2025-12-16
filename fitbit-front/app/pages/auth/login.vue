<template>
  <div class="auth-layout">
    <AuthLoginForm />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false
})
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
  padding: 1rem;
}

@media (prefers-color-scheme: dark) {
  .auth-layout {
    background: #111827;
  }
}
</style>
