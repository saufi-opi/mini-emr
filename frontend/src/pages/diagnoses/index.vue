<template>
  <div class="space-y-4 px-4 py-8">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold tracking-tight">Diagnoses Management</h1>
    </div>

    <DataTable
      v-model:pageIndex="pageIndex"
      v-model:pageSize="pageSize"
      v-model:sorting="sorting"
      v-model:searchValue="searchQuery"
      :columns="columns"
      :data="diagnoses"
      :totalCount="totalRecords"
      showSearch
      searchPlaceholder="Search by code or description..."
    >
      <template #filters>
        <Button variant="outline" size="icon" @click="loadDiagnoses" :loading="loading">
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
import { columns } from '@/components/diagnoses/columns';
import { DiagnosisService, type DiagnosisRead } from '@/client';
import { useDebounceFn } from '@vueuse/core';

const diagnoses = ref<DiagnosisRead[]>([]);
const totalRecords = ref(0);
const loading = ref(false);

const pageIndex = ref(0);
const pageSize = ref(10);
const searchQuery = ref('');
const sorting = ref<SortingState>([]);

const loadDiagnoses = async () => {
  loading.value = true;
  try {
    const firstSort = sorting.value?.[0];
    const sort = firstSort 
      ? `${firstSort.desc ? '-' : ''}${firstSort.id}`
      : undefined;

    const response = await DiagnosisService.searchDiagnoses({
      skip: pageIndex.value * pageSize.value,
      limit: pageSize.value,
      sort,
      search: searchQuery.value || undefined
    });
    
    if (response) {
      diagnoses.value = response.data;
      totalRecords.value = response.count;
    }
  } catch (error) {
    console.error('Failed to load diagnoses:', error);
  } finally {
    loading.value = false;
  }
};

const debouncedLoad = useDebounceFn(() => {
  pageIndex.value = 0;
  loadDiagnoses();
}, 500);

watch([pageIndex, pageSize, sorting], () => {
  loadDiagnoses();
});

watch(searchQuery, () => {
  debouncedLoad();
});

onMounted(() => {
  loadDiagnoses();
});
</script>

<route lang="yaml">
meta:
  layout: dashboard
</route>
