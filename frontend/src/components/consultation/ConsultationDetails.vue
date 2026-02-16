<script setup lang="ts">
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import type { ConsultationRead } from '@/client'
import { Calendar, User, FileText, Stethoscope } from 'lucide-vue-next'
import { formatDate } from '@/lib/utils'

const props = defineProps<{
  consultation: ConsultationRead | null
}>()

const emit = defineEmits(['close'])
</script>

<template>
  <Sheet :open="!!consultation" @update:open="$emit('close')">
    <SheetContent class="sm:max-w-md overflow-y-auto px-4">
      <SheetHeader class="space-y-4">
        <SheetTitle class="flex items-center gap-2">
          <FileText class="h-5 w-5 text-primary" />
          Consultation Details
        </SheetTitle>
        <SheetDescription>
          Full record of the consultation sessions.
        </SheetDescription>
      </SheetHeader>

      <div v-if="consultation" class="mt-6 space-y-6">
        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <div class="p-2 rounded-full bg-primary/10">
              <User class="h-4 w-4 text-primary" />
            </div>
            <div>
              <p class="text-xs text-muted-foreground uppercase font-semibold">Patient</p>
              <p class="font-medium text-lg">{{ consultation.patient_full_name }}</p>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <div class="p-2 rounded-full bg-primary/10">
              <Calendar class="h-4 w-4 text-primary" />
            </div>
            <div>
              <p class="text-xs text-muted-foreground uppercase font-semibold">Consultation Date</p>
              <p class="font-medium text-base">{{ formatDate(new Date(consultation.consultation_date)) }}</p>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <div class="p-2 rounded-full bg-primary/10">
              <User class="h-4 w-4 text-primary" />
            </div>
            <div>
              <p class="text-xs text-muted-foreground uppercase font-semibold">Doctor</p>
              <p class="font-medium text-base">{{ consultation.doctor_name || 'N/A' }}</p>
            </div>
          </div>
        </div>

        <Separator />

        <div class="space-y-3">
          <div class="flex items-center gap-2 mb-1">
             <Stethoscope class="h-4 w-4 text-primary" />
             <h3 class="font-semibold">Diagnoses</h3>
          </div>
          <div v-if="consultation.diagnoses?.length" class="flex flex-wrap gap-2">
            <Badge v-for="d in consultation.diagnoses" :key="d.id" variant="secondary" class="px-2 py-1 font-mono text-xs">
              {{ d.code }} - {{ d.description }}
            </Badge>
          </div>
          <p v-else class="text-sm text-muted-foreground italic">No diagnoses linked.</p>
        </div>

        <Separator />

        <div class="space-y-3">
          <h3 class="font-semibold flex items-center gap-2">
            Notes
          </h3>
          <div class="rounded-lg border bg-muted/50 p-4">
            <p class="text-sm leading-relaxed whitespace-pre-wrap text-foreground">
              {{ consultation.notes || 'No notes recorded.' }}
            </p>
          </div>
        </div>
      </div>
    </SheetContent>
  </Sheet>
</template>
