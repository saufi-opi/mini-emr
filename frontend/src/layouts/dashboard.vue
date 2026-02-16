<script setup lang="ts">
import AppSidebar from '@/components/global/AppSidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { Separator } from '@/components/ui/separator'
import ThemeToggle from '@/components/global/ThemeToggle.vue';
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <header class="flex h-16 shrink-0 justify-between items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12 border-b">
        <div class="flex items-center gap-2 px-4">
          <SidebarTrigger class="-ml-1" />
          <Separator orientation="vertical" class="mr-2 h-4" />
        </div>
        <div class="flex items-center gap-2 px-4">
          <ThemeToggle/>
        </div>
      </header>
      <main class="flex flex-1 flex-col gap-4 p-4 pt-0">
        <router-view />
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
