<template>
  <div class="flex items-center justify-center p-4">
    <Card class="w-full max-w-[400px] shadow-lg border-border relative">
      <ThemeToggle class="absolute top-4 right-4 z-10" />
      <CardHeader class="space-y-1 text-center rounded-t-lg">
        <CardTitle class="text-2xl font-bold">Sign In</CardTitle>
        <CardDescription>
          ClinicCare Mini EMR
        </CardDescription>
      </CardHeader>
      <form @submit="onSubmit">
        <CardContent class="grid gap-4 p-6 pt-8">
          <FormField v-slot="{ componentField }" name="email">
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input 
                  type="email" 
                  placeholder="name@example.com" 
                  v-bind="componentField" 
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <FormField v-slot="{ componentField }" name="password">
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input 
                  type="password" 
                  v-bind="componentField" 
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </CardContent>
        <CardFooter class="p-6 pt-0">
          <Button 
            type="submit"
            class="w-full h-11 text-base" 
            :disabled="loading"
          >
            <template v-if="loading">
              Signing in...
            </template>
            <template v-else>
              Sign In
            </template>
          </Button>
        </CardFooter>
      </form>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import ThemeToggle from '@/components/global/ThemeToggle.vue'
import { toast } from 'vue-sonner'
import { getErrorMessage } from '@/lib/error'
import { useAuthStore } from '@/store/auth'

defineOptions({
  name: 'LoginPage',
  layout: 'default'
})

const router = useRouter()
const loading = ref(false)

const formSchema = toTypedSchema(z.object({
  email: z.string({ required_error: 'Email is required' }).email({ message: 'Invalid email address' }),
  password: z.string({ required_error: 'Password is required' }),
}))

const form = useForm({
  validationSchema: formSchema,
})

const authStore = useAuthStore()

const onSubmit = form.handleSubmit(async (values) => {
  loading.value = true
  try {
    const { success, error } = await authStore.login({
      email: values.email,
      password: values.password
    })
    if (success) {
      toast.success('Login successful!')
      router.push('/')
    } else {
      toast.error(error || 'Login failed. Please check your credentials.')
    }
  } catch (error) {
    toast.error(getErrorMessage(error, 'Login failed. Please check your credentials.'))
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
</style>
