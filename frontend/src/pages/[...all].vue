<template>
  <div class="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
    <div class="mb-6 rounded-full bg-muted p-6">
      <FileQuestion class="size-16 text-muted-foreground" />
    </div>
    <h1 class="text-4xl font-bold tracking-tight mb-2">Page Not Found</h1>
    <p class="text-muted-foreground text-lg mb-8 max-w-md">
      Sorry, we couldn't find the page you're looking for. It might have been moved or deleted.
    </p>
    <div class="flex gap-4">
      <Button variant="outline" @click="$router.back()">
        Go Back
      </Button>
      <Button @click="$router.push('/')">
        Return Home
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileQuestion } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

defineOptions({
  name: 'NotFoundPage',
  layout: 'dashboard'
})
</script>
