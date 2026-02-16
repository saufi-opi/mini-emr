import { h } from 'vue';
import type { ColumnDef } from '@tanstack/vue-table';
import { Eye } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { ConsultationList } from '@/client';
import { formatDate } from '@/lib/utils';

export const getColumns = (onView: (consultation: ConsultationList) => void): ColumnDef<ConsultationList>[] => [
  {
    accessorKey: 'patient_full_name',
    header: 'Patient Name',
    cell: ({ row }) => h('div', { class: 'font-medium' }, row.getValue('patient_full_name')),
    enableSorting: true,
  },
  {
    accessorKey: 'doctor_name',
    header: 'Doctor',
    cell: ({ row }) => h('div', { class: 'text-muted-foreground' }, row.getValue('doctor_name')),
    enableSorting: false,
  },
  {
    accessorKey: 'consultation_date',
    header: 'Consultation Date',
    cell: ({ row }) => {
      const date = new Date(row.getValue('consultation_date'));
      return h('div', { class: 'text-muted-foreground' }, formatDate(date));
    },
    enableSorting: true,
  },
  {
    id: 'diagnoses',
    header: 'Diagnoses',
    cell: ({ row }) => {
      const diagnoses = row.original.diagnoses || [];
      if (diagnoses.length === 0) return h('span', { class: 'text-muted-foreground' }, 'No diagnoses');
      
      const first = diagnoses[0];
      const othersCount = diagnoses.length - 1;
      
      return h('div', { class: 'flex items-center gap-1' }, [
        h(Badge, { variant: 'secondary', class: 'font-mono' }, () => first?.code),
        othersCount > 0 ? h(Badge, { variant: 'outline' }, () => `+${othersCount} more`) : null
      ]);
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      const consultation = row.original;
      return h('div', { class: 'flex justify-end' }, [
        h(Button, {
          size: 'icon',
          variant: 'ghost',
          class: 'h-8 w-8 text-primary hover:text-primary hover:bg-primary/10',
          title: 'View Details',
          onClick: () => onView(consultation)
        }, {
          default: () => h(Eye, { class: 'h-4 w-4' })
        }),
      ]);
    },
  },
];
