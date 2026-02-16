import { h } from 'vue';
import type { ColumnDef } from '@tanstack/vue-table';
import type { DiagnosisRead } from '@/client';

export const columns: ColumnDef<DiagnosisRead>[] = [
  {
    accessorKey: 'code',
    header: 'Code',
    cell: ({ row }) => h('div', { class: 'font-mono font-medium' }, row.getValue('code')),
    enableSorting: true,
  },
  {
    accessorKey: 'description',
    header: 'Description',
    cell: ({ row }) => h('div', { class: 'max-w-[500px] truncate' }, row.getValue('description')),
    enableSorting: true,
  },
  {
    accessorKey: 'created_at',
    header: 'Created At',
    cell: ({ row }) => {
      const date = new Date(row.getValue('created_at'));
      return h('div', {}, date.toLocaleDateString());
    },
    enableSorting: true,
  },
];
