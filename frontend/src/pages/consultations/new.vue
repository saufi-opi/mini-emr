<template>
  <div class="space-y-6 px-4 py-8">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold tracking-tight">New Consultation</h1>
    </div>

    <form @submit="onSubmit" class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Session Details</CardTitle>
              <CardDescription>Record the patient information and consultation notes.</CardDescription>
            </CardHeader>
            <CardContent class="space-y-4">
              <div v-if="isAdmin" class="pb-2">
                <FormField v-slot="{ componentField }" name="doctor_id">
                  <FormItem>
                    <FormLabel>Attending Doctor</FormLabel>
                    <Select v-bind="componentField">
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a doctor" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
                          {{ doctor.full_name || doctor.email }}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                </FormField>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField v-slot="{ componentField }" name="patient_full_name">
                  <FormItem>
                    <FormLabel>Patient Full Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter patient's full name" v-bind="componentField" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                </FormField>

                <FormField v-slot="{ componentField }" name="consultation_date">
                  <FormItem>
                    <FormLabel>Consultation Date</FormLabel>
                    <FormControl>
                      <Input type="date" v-bind="componentField" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                </FormField>
              </div>

              <FormField v-slot="{ componentField }" name="notes">
                <FormItem>
                  <FormLabel>Consultation Notes</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Record clinical findings, history, and advice..." 
                      class="min-h-[300px] resize-none"
                      v-bind="componentField" 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              </FormField>
            </CardContent>
          </Card>
        </div>

        <div class="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Clinical Diagnosis</CardTitle>
              <CardDescription>Link relevant ICD-10 codes to this session.</CardDescription>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="space-y-2">
                <Label>Select Diagnoses</Label>
                <Popover v-model:open="openSearch">
                  <PopoverTrigger as-child>
                    <Button
                      variant="outline"
                      role="combobox"
                      :aria-expanded="openSearch"
                      class="w-full justify-start h-auto min-h-10 px-3 py-2 text-left"
                    >
                      <div class="flex flex-wrap gap-1 items-center max-w-[calc(100%-24px)]">
                        <template v-if="selectedDiagnoses.length > 0">
                          <Badge 
                            v-for="d in selectedDiagnoses" 
                            :key="d.id" 
                            variant="secondary"
                            class="pl-2 pr-1 py-0.5 flex items-center gap-1"
                          >
                            <span class="font-mono text-[10px] font-bold">{{ d.code }}</span>
                            <button 
                              type="button" 
                              @click.stop="toggleDiagnosis(d)"
                              class="rounded-full p-0.5 hover:bg-destructive hover:text-destructive-foreground transition-colors"
                            >
                              <X class="h-3 w-3" />
                            </button>
                          </Badge>
                        </template>
                        <span v-else class="text-muted-foreground">Search codes...</span>
                      </div>
                      <Search class="ml-auto h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent class="w-[300px] p-0" align="start">
                    <Command>
                      <div class="flex h-10 items-center gap-2 border-b px-3" data-slot="command-input-wrapper">
                        <Search class="size-4 shrink-0 opacity-50" />
                        <input 
                          placeholder="Search ICD-10..." 
                          class="placeholder:text-muted-foreground flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-hidden disabled:cursor-not-allowed disabled:opacity-50"
                          @input="(e: Event) => onSearchQuery((e.target as HTMLInputElement).value)"
                        />
                      </div>
                      <div v-if="!loadingSearch && searchResults.length === 0" class="py-6 text-center text-sm text-muted-foreground">
                        No diagnosis found.
                      </div>
                      <CommandList>
                        <CommandGroup>
                          <CommandItem
                            v-for="d in searchResults"
                            :key="d.id"
                            :value="d.code + ' ' + d.description"
                            @select="toggleDiagnosis(d)"
                          >
                            <Check
                              :class="cn(
                                'mr-2 h-4 w-4',
                                isSelected(d.id) ? 'opacity-100' : 'opacity-0'
                              )"
                            />
                            <div class="flex flex-col">
                              <span class="font-mono font-bold text-xs">{{ d.code }}</span>
                              <span class="text-xs text-muted-foreground line-clamp-1">{{ d.description }}</span>
                            </div>
                          </CommandItem>
                        </CommandGroup>
                      </CommandList>
                    </Command>
                  </PopoverContent>
                </Popover>
              </div>

              <p v-if="selectedDiagnoses.length === 0" class="text-xs text-muted-foreground italic pt-1">Add at least one diagnosis.</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent class="space-y-2">
              <Button type="submit" class="w-full" :loading="saving">
                Save Record
              </Button>
              <Button type="button" variant="ghost" class="w-full" @click="router.back()">
                Discard Changes
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { Search, Check, X } from 'lucide-vue-next';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import { toast } from 'vue-sonner';
import { useDebounceFn } from '@vueuse/core';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Command,
  CommandGroup,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import { ConsultationService, DiagnosisService, UsersService, type DiagnosisRead, type UserRead } from '@/client';
import { getErrorMessage } from '@/lib/error';
import { useAuthStore } from '@/store/auth';

const router = useRouter();
const authStore = useAuthStore();
const saving = ref(false);
const openSearch = ref(false);
const loadingSearch = ref(false);
const searchResults = ref<DiagnosisRead[]>([]);
const selectedDiagnoses = ref<DiagnosisRead[]>([]);
const doctors = ref<UserRead[]>([]);

const formSchema = toTypedSchema(z.object({
  patient_full_name: z.string().min(2, 'Patient name is required'),
  consultation_date: z.string().min(1, 'Consultation date is required'),
  doctor_id: z.string().optional(),
  notes: z.string().min(10, 'Notes should be more descriptive (at least 10 chars)'),
}));

const form = useForm({
  validationSchema: formSchema,
  initialValues: {
    consultation_date: new Date().toISOString().split('T')[0],
    doctor_id: '',
  }
});

const isAdmin = computed(() => authStore.user?.role === 'admin');

onMounted(async () => {
  if (isAdmin.value) {
    try {
      const response = await UsersService.readUsers({ limit: 100 });
      if (response) {
        // Filter to only show doctors
        doctors.value = response.data.filter(u => u.role === 'doctor' && u.is_active);
      }
    } catch (error) {
      console.error('Failed to fetch doctors:', error);
    }
  }
});

const onSearchQuery = useDebounceFn(async (query: string) => {
  loadingSearch.value = true;
  try {
    const response = await DiagnosisService.searchDiagnoses({
      search: query,
      limit: 100
    });
    if (response) {
      searchResults.value = response.data;
    }
  } catch (error) {
    console.error('Diagnosis search failed:', error);
  } finally {
    loadingSearch.value = false;
  }
}, 300);

watch(openSearch, (isOpen) => {
  if (isOpen && searchResults.value.length === 0) {
    onSearchQuery('');
  }
});

const isSelected = (id: string) => {
  return selectedDiagnoses.value.some(d => d.id === id);
};

const toggleDiagnosis = (diagnosis: DiagnosisRead) => {
  const index = selectedDiagnoses.value.findIndex(d => d.id === diagnosis.id);
  if (index > -1) {
    selectedDiagnoses.value.splice(index, 1);
  } else {
    selectedDiagnoses.value.push(diagnosis);
  }
};

const onSubmit = form.handleSubmit(async (values) => {
  if (selectedDiagnoses.value.length === 0) {
    toast.error('Please select at least one diagnosis');
    return;
  }

  saving.value = true;
  try {
    await ConsultationService.createConsultation({
      requestBody: {
        patient_full_name: values.patient_full_name,
        consultation_date: values.consultation_date,
        doctor_id: values.doctor_id || undefined,
        notes: values.notes,
        diagnosis_ids: selectedDiagnoses.value.map(d => d.id)
      }
    });
    toast.success('Consultation record saved successfully');
    router.push('/consultations');
  } catch (error) {
    toast.error(getErrorMessage(error, 'Failed to save consultation'));
  } finally {
    saving.value = false;
  }
});
</script>

<route lang="yaml">
meta:
  layout: dashboard
</route>
