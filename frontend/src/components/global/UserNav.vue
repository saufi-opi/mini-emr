<script setup lang="ts">
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LogOut, User as UserIcon } from 'lucide-vue-next'
import { useAuthStore } from '@/store/auth'
import { computed } from 'vue'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const initials = computed(() => {
  if (!user.value?.full_name) return user.value?.email?.charAt(0).toUpperCase() || 'U'
  return user.value.full_name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})
</script>

<template>
  <DropdownMenu v-if="user">
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" class="relative h-10 w-10 rounded-full bg-primary/10 hover:bg-primary/20 p-0 overflow-hidden border">
         <span class="text-xs font-bold text-primary">{{ initials }}</span>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent class="w-56" align="end">
      <DropdownMenuLabel class="font-normal flex flex-col gap-1">
        <div class="flex flex-col space-y-1">
          <p class="text-sm font-medium leading-none">{{ user.full_name || 'User' }}</p>
          <p class="text-xs leading-none text-muted-foreground">
            {{ user.email }}
          </p>
        </div>
        <div class="pt-2">
            <Badge variant="secondary" class="capitalize text-[10px] px-1.5 py-0">{{ user.role }}</Badge>
        </div>
      </DropdownMenuLabel>
      <DropdownMenuSeparator />
      <DropdownMenuGroup>
        <DropdownMenuItem class="cursor-pointer">
          <UserIcon class="mr-2 h-4 w-4" />
          <span>Profile</span>
        </DropdownMenuItem>
      </DropdownMenuGroup>
      <DropdownMenuSeparator />
      <DropdownMenuItem @click="authStore.logout" class="cursor-pointer text-destructive focus:text-destructive">
        <LogOut class="mr-2 h-4 w-4" />
        <span>Log out</span>
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
