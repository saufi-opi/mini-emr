<script setup lang="ts">
import {
  LayoutDashboard,
  Users,
  ClipboardList,
  LogOut,
  Stethoscope,
} from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from '@/components/ui/sidebar'
import { useAuthStore } from '@/store/auth'
import { computed } from 'vue'

const route = useRoute()
const authStore = useAuthStore()

const adminRoutes = [
  {
    title: 'Dashboard',
    url: '/',
    icon: LayoutDashboard,
  },
  {
    title: 'Users',
    url: '/users',
    icon: Users,
  },
  {
    title: 'Diagnoses',
    url: '/diagnoses',
    icon: Stethoscope,
  },
  {
    title: 'Consultations',
    url: '/consultations',
    icon: ClipboardList,
  },
]

const doctorRoutes = [
  {
    title: 'Dashboard',
    url: '/',
    icon: LayoutDashboard,
  },
  {
    title: 'Diagnoses',
    url: '/diagnoses',
    icon: Stethoscope,
  },
  {
    title: 'Consultations',
    url: '/consultations',
    icon: ClipboardList,
  },
]

const menuItems = computed(() => {
  if (authStore.user?.role === 'admin') {
    return adminRoutes
  } else if (authStore.user?.role === 'doctor') {
    return doctorRoutes
  }
  return []
})

</script>

<template>
  <Sidebar collapsible="icon">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as-child>
            <a href="/">
              <div class="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <ClipboardList class="size-4" />
              </div>
              <div class="grid flex-1 text-left text-sm leading-tight">
                <span class="truncate font-semibold">ClinicCare</span>
                <span class="truncate text-xs">Mini EMR</span>
              </div>
            </a>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>

    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Application</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in menuItems" :key="item.title">
              <SidebarMenuButton as-child :tooltip="item.title" :is-active="route.path === item.url">
                <router-link :to="item.url">
                  <component :is="item.icon" />
                  <span>{{ item.title }}</span>
                </router-link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" @click="authStore.logout">
            <div class="flex aspect-square size-8 items-center justify-center rounded-lg bg-muted text-muted-foreground">
              <LogOut class="size-4" />
            </div>
            <div class="grid flex-1 text-left text-sm leading-tight">
              <span class="truncate font-semibold">Logout</span>
            </div>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
</template>
