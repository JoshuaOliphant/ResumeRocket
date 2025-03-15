"use client"

import "./globals.css";

import React, { useState } from "react";
import Layout from "pages/layout";
import Dashboard from "pages/dashboard";

export default function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");

  return (
  <html lang="en">
    <body>
      <Layout
      currentPage={currentPage}
      setCurrentPage={setCurrentPage}
    >
      {currentPage === "dashboard" && <Dashboard />}
      {/* Other pages would be conditionally rendered here */}
    </Layout>
    </body>
  </html>
)
}
