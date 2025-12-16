<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
    <UCard class="w-full max-w-md">
      <template #header>
        <div class="text-center">
          <h1 class="text-2xl font-semibold">
            Fitbit Project
          </h1>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Sistema de Monitoramento de Saúde
          </p>
        </div>
      </template>

      <div class="flex flex-col gap-4">
        <UButton
          size="lg"
          block
          @click="navigateTo('/auth/login')"
        >
          Fazer Login
        </UButton>

        <UButton
          size="lg"
          block
          variant="outline"
          @click="navigateTo('/auth/register')"
        >
          Criar Conta
        </UButton>
      </div>
    </UCard>
  </div>
</template>
