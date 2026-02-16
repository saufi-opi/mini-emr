import { ApiError } from "@/client";

export const getErrorMessage = (error: unknown, defaultMessage: string = 'An unexpected error occurred') => {
    if (error instanceof ApiError) {
        const detail = (error.body as { detail?: string })?.detail
        return detail || defaultMessage
    } else {
        return defaultMessage
    }
}