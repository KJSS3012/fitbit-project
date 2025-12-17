export default defineNuxtRouteMiddleware(async (to, from) => {
  const { isAuthenticated, fetchUser, token } = useAuth()

  const publicPages = ['/auth/login', '/auth/register', '/']
  
  if (publicPages.includes(to.path)) {
    return
  }

  if (token.value && !isAuthenticated.value) {
    await fetchUser()
  }

  if (!isAuthenticated.value) {
    return navigateTo('/auth/login')
  }
})