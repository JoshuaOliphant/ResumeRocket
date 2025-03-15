"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { ArrowLeftIcon, CheckCircleIcon } from "lucide-react";

// Form validation schema
const resetPasswordSchema = z.object({
  email: z
    .string()
    .min(1, { message: "Email is required" })
    .email({ message: "Invalid email address" }),
});

type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>;

export default function ResetPasswordPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  // Initialize form
  const form = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      email: "",
    },
  });

  // Handle form submission
  const onSubmit = async (data: ResetPasswordFormValues) => {
    setIsLoading(true);
    try {
      // In a real app, you would make an API call to request a password reset
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API call
      
      toast({
        title: "Reset link sent",
        description: "Check your email for instructions to reset your password.",
      });
      
      setIsSubmitted(true);
    } catch (error) {
      toast({
        title: "Request failed",
        description: "Something went wrong. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="space-y-6 text-center">
        <div className="flex justify-center">
          <div className="rounded-full h-12 w-12 bg-primary/10 flex items-center justify-center">
            <CheckCircleIcon className="h-6 w-6 text-primary" />
          </div>
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-semibold">Check your email</h2>
          <p className="text-sm text-muted-foreground">
            We've sent a password reset link to your email address.
            The link will expire in 30 minutes.
          </p>
        </div>
        <div className="space-y-4 pt-4">
          <p className="text-sm text-muted-foreground">
            Didn't receive an email? Check your spam folder or try again.
          </p>
          <Button 
            variant="outline" 
            className="w-full"
            onClick={() => setIsSubmitted(false)}
          >
            Try again
          </Button>
          <div className="flex items-center justify-center">
            <Link href="/login" className="text-sm text-primary flex items-center">
              <ArrowLeftIcon className="h-3 w-3 mr-1" />
              Back to login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-6">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input
                    placeholder="name@example.com"
                    type="email"
                    autoComplete="email"
                    disabled={isLoading}
                    {...field}
                  />
                </FormControl>
                <FormDescription className="text-xs">
                  We'll send you a link to reset your password
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button 
            type="submit" 
            className="w-full" 
            disabled={isLoading}
          >
            {isLoading ? "Sending link..." : "Send reset link"}
          </Button>
        </form>
      </Form>
      <div className="mt-4 text-center text-sm">
        <Link 
          href="/login" 
          className="text-primary flex items-center justify-center gap-1 underline-offset-4 hover:underline"
        >
          <ArrowLeftIcon className="h-3 w-3" />
          Back to login
        </Link>
      </div>
    </div>
  );
}