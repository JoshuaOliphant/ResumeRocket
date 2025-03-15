"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { ArrowLeftIcon, GlobeIcon, FileTextIcon } from "lucide-react";

// Form validation schemas
const urlFormSchema = z.object({
  url: z
    .string()
    .min(1, { message: "URL is required" })
    .url({ message: "Please enter a valid URL" }),
});

const textFormSchema = z.object({
  title: z
    .string()
    .min(1, { message: "Job title is required" }),
  company: z
    .string()
    .optional(),
  description: z
    .string()
    .min(50, { message: "Job description must be at least 50 characters" }),
});

type UrlFormValues = z.infer<typeof urlFormSchema>;
type TextFormValues = z.infer<typeof textFormSchema>;

export default function JobInputPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<string>("url");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Initialize URL form
  const urlForm = useForm<UrlFormValues>({
    resolver: zodResolver(urlFormSchema),
    defaultValues: {
      url: "",
    },
  });

  // Initialize text form
  const textForm = useForm<TextFormValues>({
    resolver: zodResolver(textFormSchema),
    defaultValues: {
      title: "",
      company: "",
      description: "",
    },
  });

  // Handle URL form submission
  const onUrlSubmit = async (data: UrlFormValues) => {
    setIsSubmitting(true);
    try {
      // In a real app, you would make an API call to submit the URL
      console.log("Submitting URL:", data.url);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      toast({
        title: "Success",
        description: "Job description extracted successfully.",
      });
      
      router.push("/job-management");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to extract job description. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle text form submission
  const onTextSubmit = async (data: TextFormValues) => {
    setIsSubmitting(true);
    try {
      // In a real app, you would make an API call to submit the text
      console.log("Submitting text:", data);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      toast({
        title: "Success",
        description: "Job description saved successfully.",
      });
      
      router.push("/job-management");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save job description. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <Link href="/job-management" className="mr-4">
          <Button variant="outline" size="icon">
            <ArrowLeftIcon className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Add Job</h1>
          <p className="text-muted-foreground">
            Add a job description to use for resume optimization.
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Job Details</CardTitle>
          <CardDescription>
            Enter a job description by URL or manual input.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="url">
                <GlobeIcon className="mr-2 h-4 w-4" />
                Job URL
              </TabsTrigger>
              <TabsTrigger value="text">
                <FileTextIcon className="mr-2 h-4 w-4" />
                Manual Input
              </TabsTrigger>
            </TabsList>

            <TabsContent value="url" className="space-y-4">
              <div className="rounded-md bg-blue-50 p-4 dark:bg-blue-950">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3 flex-1 md:flex md:justify-between">
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      Paste a job posting URL from LinkedIn, Indeed, or other job boards.
                      We'll extract the job details automatically.
                    </p>
                  </div>
                </div>
              </div>

              <Form {...urlForm}>
                <form onSubmit={urlForm.handleSubmit(onUrlSubmit)} className="space-y-4">
                  <FormField
                    control={urlForm.control}
                    name="url"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Job URL</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="https://www.example.com/job/12345"
                            {...field}
                            disabled={isSubmitting}
                          />
                        </FormControl>
                        <FormDescription>
                          Enter the full URL of the job posting.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <Button type="submit" className="w-full" disabled={isSubmitting}>
                    {isSubmitting ? "Processing..." : "Extract Job Details"}
                  </Button>
                </form>
              </Form>
            </TabsContent>

            <TabsContent value="text" className="space-y-4">
              <div className="rounded-md bg-blue-50 p-4 dark:bg-blue-950">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3 flex-1 md:flex md:justify-between">
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      Manually enter job details if you don't have a URL or prefer to input specific sections.
                    </p>
                  </div>
                </div>
              </div>

              <Form {...textForm}>
                <form onSubmit={textForm.handleSubmit(onTextSubmit)} className="space-y-4">
                  <FormField
                    control={textForm.control}
                    name="title"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Job Title</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Senior Frontend Developer"
                            {...field}
                            disabled={isSubmitting}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={textForm.control}
                    name="company"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Company (Optional)</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Acme Inc."
                            {...field}
                            disabled={isSubmitting}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={textForm.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Job Description</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Paste the full job description here..."
                            className="min-h-[200px]"
                            {...field}
                            disabled={isSubmitting}
                          />
                        </FormControl>
                        <FormDescription>
                          Include responsibilities, requirements, and any other relevant information.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <Button type="submit" className="w-full" disabled={isSubmitting}>
                    {isSubmitting ? "Saving..." : "Save Job Description"}
                  </Button>
                </form>
              </Form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}