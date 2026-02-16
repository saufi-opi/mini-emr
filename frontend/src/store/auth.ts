import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AuthService, UsersService, type LoginRequest, type UserRead } from '@/client'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()

  const accessToken = ref<string>('')
  const user = ref<UserRead | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  function setAccessToken(token: string) {
    accessToken.value = token
    if (token) {
      localStorage.setItem('was_logged_in', 'true')
    }
  }

  function setUser(u: UserRead | null) {
    user.value = u
  }

  async function fetchUser() {
    try {
      const u = await UsersService.readUserMe();
      setUser(u);
    } catch (error) {
      console.error('Fetch user error:', error);
      logout();
    }
  }

  async function login(credentials: LoginRequest): Promise<boolean> {
    try {
      const response = await AuthService.login({
        requestBody: credentials
      });
      
      if (response) {
        setAccessToken(response.access_token);
        await fetchUser();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  }

  async function refresh(): Promise<boolean> {
    try {
      const response = await AuthService.refresh();
      if (response) {
        setAccessToken(response.access_token);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Refresh error:', error);
      logout();
      return false;
    }
  }

  async function init() {
    if (localStorage.getItem('was_logged_in') === 'true') {
      const success = await refresh();
      if (success) {
        await fetchUser();
      }
    }
  }

  async function logout() {
    try {
      await AuthService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      accessToken.value = ''
      user.value = null
      localStorage.removeItem('was_logged_in')
      router.push('/login')
    }
  }

  return {
    accessToken,
    user,
    isAuthenticated,
    setAccessToken,
    setUser,
    login,
    refresh,
    init,
    logout,
  }
})
