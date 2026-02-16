<template>
  <Toaster position="top-right" :rich-colors="true" />
  <RouterView />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { Toaster } from '@/components/ui/sonner'
import "vue-sonner/style.css"
</script>

<style>
/* Base styles if needed */
</style>
