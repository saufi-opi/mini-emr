<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div v-if="showSearch" class="relative w-full sm:max-w-xs">
        <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          :placeholder="searchPlaceholder"
          class="pl-9"
          :model-value="searchValue"
          @input="$emit('update:searchValue', ($event.target as HTMLInputElement).value)"
        />
      </div>
      <div class="flex items-center gap-2 w-full sm:w-auto ml-auto">
        <slot name="filters" />
      </div>
    </div>

    <div class="rounded-md border overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id" class="hover:bg-transparent border-b">
            <TableHead
              v-for="header in headerGroup.headers"
              :key="header.id"
              :class="cn(
                'py-3 font-bold uppercase tracking-wider text-xs text-muted-foreground',
                header.column.getCanSort() && 'cursor-pointer select-none'
              )"
            >
              <div
                v-if="!header.isPlaceholder"
                class="flex items-center gap-2"
                :class="cn(header.column.getCanSort() && 'hover:text-primary transition-colors')"
                @click="header.column.getToggleSortingHandler()?.($event)"
              >
                <FlexRender :render="header.column.columnDef.header" :props="header.getContext()" />
                <div v-if="header.column.getCanSort()" class="w-4 h-4 flex items-center justify-center">
                  <ArrowUp v-if="header.column.getIsSorted() === 'asc'" class="h-4 w-4 text-primary" />
                  <ArrowDown v-else-if="header.column.getIsSorted() === 'desc'" class="h-4 w-4 text-primary" />
                  <ArrowUpDown v-else class="h-4 w-4 text-muted-foreground/50" />
                </div>
              </div>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <template v-if="table.getRowModel().rows?.length">
            <TableRow v-for="row in table.getRowModel().rows" :key="row.id">
              <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id">
                <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
              </TableCell>
            </TableRow>
          </template>
          <TableRow v-else>
            <TableCell :colspan="columns.length" class="h-32 text-center text-muted-foreground">
              No results found.
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <div v-if="!hidePagination" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-2">
      <div class="flex flex-col sm:flex-row sm:items-center gap-4">
        <div class="text-sm text-muted-foreground">
          <template v-if="totalCount > 0 || data.length > 0">
            Showing 
            <span class="font-medium text-foreground">{{ (pageIndex * pageSize) + 1 }}</span>
            to 
            <span class="font-medium text-foreground">{{ Math.min((pageIndex + 1) * pageSize, totalCount || data.length) }}</span>
            of 
            <span class="font-medium text-foreground">{{ totalCount || data.length }}</span>
            entries
          </template>
          <template v-else>
            Showing 0 to 0 of 0 entries
          </template>
        </div>
        <div class="flex items-center gap-x-2">
          <p class="text-sm text-muted-foreground">Rows per page</p>
          <Select
            :model-value="pageSize.toString()"
            @update:model-value="$emit('update:pageSize', Number($event))"
          >
            <SelectTrigger class="h-8 w-[70px]">
              <SelectValue :placeholder="pageSize.toString()" />
            </SelectTrigger>
            <SelectContent side="top">
              <SelectItem v-for="size in [5, 10, 25, 50]" :key="size" :value="size.toString()">
                {{ size }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div class="flex items-center gap-x-6">
        <div class="flex items-center gap-x-1 text-sm text-muted-foreground">
          <span>Page</span>
          <span class="font-medium text-foreground">{{ pageIndex + 1 }}</span>
          <span>of</span>
          <span class="font-medium text-foreground">{{ totalPages }}</span>
        </div>

        <div class="flex items-center gap-x-1">
          <Button
            variant="outline"
            size="sm"
            class="h-8 w-8 p-0"
            :disabled="!table.getCanPreviousPage()"
            @click="table.setPageIndex(0)"
          >
            <span class="sr-only">Go to first page</span>
            <ChevronsLeft class="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            class="h-8 w-8 p-0"
            :disabled="!table.getCanPreviousPage()"
            @click="table.previousPage()"
          >
            <span class="sr-only">Go to previous page</span>
            <ChevronLeft class="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            class="h-8 w-8 p-0"
            :disabled="!table.getCanNextPage()"
            @click="table.nextPage()"
          >
            <span class="sr-only">Go to next page</span>
            <ChevronRight class="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            class="h-8 w-8 p-0"
            :disabled="!table.getCanNextPage()"
            @click="table.setPageIndex(table.getPageCount() - 1)"
          >
            <span class="sr-only">Go to last page</span>
            <ChevronsRight class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" generic="TData, TValue">
import { computed } from 'vue'
import {
  useVueTable,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  FlexRender,
  type ColumnDef,
  type SortingState,
  type PaginationState,
  type OnChangeFn,
  type Updater,
} from '@tanstack/vue-table'
import {
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Search,
} from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { cn } from '@/lib/utils'

interface Props {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  pageIndex?: number
  pageSize?: number
  totalCount?: number
  sorting?: SortingState
  searchValue?: string
  searchPlaceholder?: string
  showSearch?: boolean
  hidePagination?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  pageIndex: 0,
  pageSize: 10,
  totalCount: 0,
  sorting: () => [],
  searchValue: '',
  searchPlaceholder: 'Search...',
  showSearch: false,
  hidePagination: false,
})

const emit = defineEmits<{
  'update:pageIndex': [value: number]
  'update:pageSize': [value: number]
  'update:sorting': [value: SortingState]
  'update:searchValue': [value: string]
}>()

const isServerSide = computed(() => props.totalCount !== undefined)

const totalPages = computed(() => {
  const count = isServerSide.value ? props.totalCount : props.data.length
  return Math.max(1, Math.ceil((count || 0) / props.pageSize))
})

const handlePaginationChange: OnChangeFn<PaginationState> = (updaterOrValue: Updater<PaginationState>) => {
  const nextState = typeof updaterOrValue === 'function' 
    ? updaterOrValue({ pageIndex: props.pageIndex, pageSize: props.pageSize }) 
    : updaterOrValue
    
  if (nextState.pageIndex !== props.pageIndex) {
    emit('update:pageIndex', nextState.pageIndex)
  }
  if (nextState.pageSize !== props.pageSize) {
    emit('update:pageSize', nextState.pageSize)
  }
}

const handleSortingChange: OnChangeFn<SortingState> = (updaterOrValue: Updater<SortingState>) => {
  const nextState = typeof updaterOrValue === 'function' ? updaterOrValue(props.sorting) : updaterOrValue
  emit('update:sorting', nextState)
}

const table = useVueTable({
  get data() { return props.data },
  get columns() { return props.columns },
  state: {
    get pagination() {
      return {
        pageIndex: props.pageIndex,
        pageSize: props.pageSize,
      }
    },
    get sorting() {
      return props.sorting
    },
    get globalFilter() {
      return props.searchValue
    },
  },
  get pageCount() { return totalPages.value },
  get manualPagination() { return isServerSide.value },
  get manualSorting() { return isServerSide.value },
  get manualFiltering() { return isServerSide.value },
  onPaginationChange: handlePaginationChange,
  onSortingChange: handleSortingChange,
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})
</script>
