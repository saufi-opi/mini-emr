import { h } from 'vue';
import type { ColumnDef } from '@tanstack/vue-table';
import { Pencil, Trash2, CheckCircle2, XCircle } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { UserRead } from '@/client';
import { toast } from 'vue-sonner';

export const columns: ColumnDef<UserRead>[] = [
  {
    accessorKey: 'full_name',
    header: 'Full Name',
    cell: ({ row }) => h('div', { class: 'font-medium' }, row.getValue('full_name')),
    enableSorting: true,
  },
  {
    accessorKey: 'email',
    header: 'Email',
    enableSorting: true,
  },
  {
    accessorKey: 'role',
    header: 'Role',
    cell: ({ row }) => {
      const role = row.getValue('role') as string;
      return h(Badge, { variant: role === 'admin' ? 'destructive' : 'secondary', class: 'capitalize' }, () => role);
    },
    enableSorting: true,
  },
  {
    accessorKey: 'is_active',
    header: 'Status',
    cell: ({ row }) => {
      const isActive = row.getValue('is_active');
      return h('div', { class: 'flex items-center gap-2' }, [
        isActive 
          ? h(CheckCircle2, { class: 'h-4 w-4 text-green-500' })
          : h(XCircle, { class: 'h-4 w-4 text-red-500' }),
        h('span', isActive ? 'Active' : 'Inactive')
      ]);
    },
    enableSorting: true,
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      const user = row.original;
      return h('div', { class: 'flex justify-end gap-2' }, [
        h(Button, {
          size: 'icon',
          variant: 'ghost',
          class: 'h-8 w-8 text-primary hover:text-primary hover:bg-primary/10',
          title: `Edit ${user.full_name}`,
          onClick: () => {
            toast.info(`Edit function not implemented yet`);
          }
        }, {
          default: () => h(Pencil, { class: 'h-4 w-4' })
        }),
        h(Button, {
          size: 'icon',
          variant: 'ghost',
          class: 'h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10',
          title: `Delete ${user.full_name}`,
          onClick: () => {
            toast.info(`Delete function not implemented yet`);
          }
        }, {
          default: () => h(Trash2, { class: 'h-4 w-4' })
        }),
      ]);
    },
  },
];
