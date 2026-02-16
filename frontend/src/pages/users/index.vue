<template>
  <div class="space-y-4 px-4 py-8">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold tracking-tight">User Management</h1>
      <AddUser @success="handleUserCreated" />
    </div>

    <DataTable
      v-model:pageIndex="pageIndex"
      v-model:pageSize="pageSize"
      v-model:sorting="sorting"
      v-model:searchValue="searchQuery"
      :columns="columns"
      :data="users"
      :totalCount="totalRecords"
      showSearch
      searchPlaceholder="Search by name or email..."
    >
      <template #filters>
        <Button variant="outline" size="icon" @click="loadUsers" :loading="loading">
          <RefreshCcw class="h-4 w-4" :class="{ 'animate-spin': loading }" />
        </Button>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import type { SortingState } from '@tanstack/vue-table';
import { RefreshCcw } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import DataTable from '@/components/global/DataTable.vue';
import AddUser from '@/components/user/AddUser.vue';
import { columns } from '@/components/user/columns';
import { UsersService, type UserRead } from '@/client';
import { useDebounceFn } from '@vueuse/core';

const users = ref<UserRead[]>([]);
const totalRecords = ref(0);
const loading = ref(false);

const pageIndex = ref(0);
const pageSize = ref(10);
const searchQuery = ref('');
const sorting = ref<SortingState>([{ id: 'created_at', desc: true }]);

const loadUsers = async () => {
    loading.value = true;
    try {
        const firstSort = sorting.value?.[0];
        const sort = firstSort 
          ? `${firstSort.desc ? '-' : ''}${firstSort.id}`
          : undefined;

        const response = await UsersService.readUsers({
            skip: pageIndex.value * pageSize.value, 
            limit: pageSize.value,
            sort,
            search: searchQuery.value || undefined
        });
        if (response.data) {
            users.value = response.data;
            totalRecords.value = response.count;
        }
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
        loading.value = false;
    }
};

const debouncedLoad = useDebounceFn(() => {
  pageIndex.value = 0;
  loadUsers();
}, 500);

watch([pageIndex, pageSize, sorting], () => {
  loadUsers();
});

watch(searchQuery, () => {
  debouncedLoad();
});

const handleUserCreated = () => {
  pageIndex.value = 0;
  loadUsers();
};

onMounted(() => {
    loadUsers();
});
</script>

<route lang="yaml">
meta:
  layout: dashboard
  role: admin
</route>

<style scoped>
</style>
