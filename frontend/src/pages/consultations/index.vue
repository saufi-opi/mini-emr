<template>
  <div class="space-y-4 px-4 py-8">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold tracking-tight">Consultations</h1>
      <Button as-child>
        <router-link to="/consultations/new">
          <Plus class="mr-2 h-4 w-4" />
          New Consultation
        </router-link>
      </Button>
    </div>

    <DataTable
      v-model:pageIndex="pageIndex"
      v-model:pageSize="pageSize"
      v-model:sorting="sorting"
      v-model:searchValue="searchQuery"
      :columns="columns"
      :data="consultations"
      :totalCount="totalRecords"
      showSearch
      searchPlaceholder="Search by patient name or notes..."
    >
      <template #filters>
        <Button variant="outline" size="icon" @click="loadConsultations" :loading="loading">
          <RefreshCcw class="h-4 w-4" :class="{ 'animate-spin': loading }" />
        </Button>
      </template>
    </DataTable>

    <!-- Details Component will go here -->
    <ConsultationDetails v-if="selectedConsultation" :consultation="selectedConsultation" @close="selectedConsultation = null" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import type { SortingState } from '@tanstack/vue-table';
import { Plus, RefreshCcw } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import DataTable from '@/components/global/DataTable.vue';
import { getColumns } from '@/components/consultation/columns';
import ConsultationDetails from '@/components/consultation/ConsultationDetails.vue';
import { ConsultationService, type ConsultationRead, type ConsultationList } from '@/client';
import { useDebounceFn } from '@vueuse/core';

const consultations = ref<ConsultationList[]>([]);
const totalRecords = ref(0);
const loading = ref(false);
const selectedConsultation = ref<ConsultationRead | null>(null);

const pageIndex = ref(0);
const pageSize = ref(10);
const searchQuery = ref('');
const sorting = ref<SortingState>([]);

const columns = computed(() => getColumns(async (consultation) => {
  try {
    const full = await ConsultationService.getConsultation({ consultationId: consultation.id });
    if (full) {
      selectedConsultation.value = full;
    }
  } catch (error) {
    console.error('Failed to view consultation details:', error);
  }
}));

const loadConsultations = async () => {
    loading.value = true;
    try {
        const firstSort = sorting.value?.[0];
        const sortIdMap: Record<string, string> = {
          'patient_full_name': 'patient_name'
        };
        const sortId = firstSort ? (sortIdMap[firstSort.id] || firstSort.id) : undefined;
        const sort = (firstSort && sortId)
          ? `${firstSort.desc ? '-' : ''}${sortId}`
          : undefined;

        const response = await ConsultationService.listConsultations({
            skip: pageIndex.value * pageSize.value,
            limit: pageSize.value,
            sort,
            search: searchQuery.value || undefined
        });
        if (response) {
            consultations.value = response.data;
            totalRecords.value = response.count;
        }
    } catch (error) {
      console.error('Failed to load consultations:', error);
    } finally {
        loading.value = false;
    }
};

const debouncedLoad = useDebounceFn(() => {
  pageIndex.value = 0;
  loadConsultations();
}, 500);

watch([pageIndex, pageSize, sorting], () => {
  loadConsultations();
});

watch(searchQuery, () => {
  debouncedLoad();
});

onMounted(() => {
    loadConsultations();
});
</script>

<route lang="yaml">
meta:
  layout: dashboard
</route>
