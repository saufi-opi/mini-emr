<template>
  <Dialog v-model:open="show">
    <DialogTrigger as-child>
      <slot name="trigger">
        <Button>
          <UserPlus class="mr-2 h-4 w-4" />
          Create User
        </Button>
      </slot>
    </DialogTrigger>
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Create New User</DialogTitle>
        <DialogDescription>
          Enter the details for the new user account.
        </DialogDescription>
      </DialogHeader>
      <form @submit="onSubmit" class="space-y-4 py-4">
        <FormField v-slot="{ componentField }" name="full_name">
          <FormItem class="grid grid-cols-4 items-center gap-x-4 gap-y-1">
            <FormLabel class="text-right">Full Name</FormLabel>
            <div class="col-span-3 space-y-1">
              <FormControl>
                <Input placeholder="John Doe" v-bind="componentField" />
              </FormControl>
              <FormMessage />
            </div>
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="email">
          <FormItem class="grid grid-cols-4 items-center gap-x-4 gap-y-1">
            <FormLabel class="text-right">Email</FormLabel>
            <div class="col-span-3 space-y-1">
              <FormControl>
                <Input placeholder="john@example.com" v-bind="componentField" />
              </FormControl>
              <FormMessage />
            </div>
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="role">
          <FormItem class="grid grid-cols-4 items-center gap-x-4 gap-y-1">
            <FormLabel class="text-right">Role</FormLabel>
            <div class="col-span-3 space-y-1">
              <Select v-bind="componentField">
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="doctor">Doctor</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </div>
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="password">
          <FormItem class="grid grid-cols-4 items-center gap-x-4 gap-y-1">
            <FormLabel class="text-right">Password</FormLabel>
            <div class="col-span-3 space-y-1">
              <FormControl>
                <Input type="password" v-bind="componentField" />
              </FormControl>
              <FormMessage />
            </div>
          </FormItem>
        </FormField>

        <DialogFooter>
          <Button type="button" variant="outline" @click="show = false">Cancel</Button>
          <Button type="submit" :loading="loading">Create User</Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { UserPlus } from 'lucide-vue-next';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import { toast } from 'vue-sonner';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { UsersService, type Role } from '@/client';
import { getErrorMessage } from '@/lib/error';

const emit = defineEmits(['success']);

const show = ref(false);
const loading = ref(false);

const formSchema = toTypedSchema(z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters').optional().or(z.literal('')),
  email: z.string({ required_error: 'Email is required' }).email('Invalid email address'),
  role: z.enum(['admin', 'doctor'], { required_error: 'Role is required' }),
  password: z.string({ required_error: 'Password is required' }).min(8, 'Password must be at least 8 characters'),
}));

const form = useForm({
  validationSchema: formSchema,
  initialValues: {
    role: 'doctor' as Role,
  }
});

const onSubmit = form.handleSubmit(async (values) => {
  loading.value = true;
  try {
    await UsersService.createUser({
      requestBody: {
        email: values.email,
        full_name: values.full_name || null,
        role: values.role as Role,
        password: values.password
      }
    });
    toast.success('User created successfully');
    show.value = false;
    form.resetForm();
    emit('success');
  } catch (error) {
    toast.error(getErrorMessage(error, 'Failed to create user'));
  } finally {
    loading.value = false;
  }
});
</script>
