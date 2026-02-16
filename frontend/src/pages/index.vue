<script setup lang="ts">
</script>

<template>
  <div class="py-6">
    <h1 class="text-2xl font-bold tracking-tight">Dashboard Overview</h1>
    <p class="text-muted-foreground">Welcome to ClinicCare Mini EMR.</p>
    
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mt-8">
      <div v-for="i in 4" :key="i" class="rounded-xl border bg-card text-card-foreground shadow">
        <div class="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
          <h3 class="tracking-tight text-sm font-medium">Metric {{ i }}</h3>
        </div>
        <div class="p-6 pt-0">
          <div class="text-2xl font-bold">+{{ i * 123 }}</div>
          <p class="text-xs text-muted-foreground">+20.1% from last month</p>
        </div>
      </div>
    </div>

    <div class="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-7">
      <div class="col-span-4 rounded-xl border bg-card text-card-foreground shadow h-[400px]">
        <div class="p-6">
          <h3 class="font-semibold leading-none tracking-tight">Recent Activity</h3>
        </div>
        <div class="p-6 pt-0">
          <!-- Placeholder for charts or lists -->
          <div class="flex items-center justify-center h-[300px] bg-muted/20 rounded-lg border border-dashed text-muted-foreground">
            Activity Chart Content
          </div>
        </div>
      </div>
      <div class="col-span-3 rounded-xl border bg-card text-card-foreground shadow h-[400px]">
        <div class="p-6">
          <h3 class="font-semibold leading-none tracking-tight">Upcoming Appointments</h3>
        </div>
        <div class="p-6 pt-0">
          <!-- Placeholder for upcoming items -->
          <div class="space-y-4">
             <div v-for="i in 5" :key="i" class="flex items-center gap-4">
               <div class="size-9 rounded-full bg-muted/50" />
               <div class="space-y-1">
                 <p class="text-sm font-medium leading-none">Patient Name {{ i }}</p>
                 <p class="text-sm text-muted-foreground">10:30 AM</p>
               </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<route lang="yaml">
meta:
  layout: dashboard
</route>
