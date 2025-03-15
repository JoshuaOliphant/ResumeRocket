"use client";

import React from "react";
import AuthenticatedLayout from "@/components/layouts/authenticated-layout";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthenticatedLayout>{children}</AuthenticatedLayout>;
}