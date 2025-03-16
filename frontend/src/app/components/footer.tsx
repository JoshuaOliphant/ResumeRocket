"use client"

import React from "react";
import { ZapIcon } from "lucide-react";

export function Footer() {
  return (
    <footer
      className="bg-white dark:bg-gray-950 border-t border-gray-200 dark:border-gray-800 py-8"
    >
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <ZapIcon
                className="h-5 w-5 text-blue-600 dark:text-blue-500"
              />
              <span
                className="font-bold text-lg text-gray-900 dark:text-white"
              >
                ResumeRocket
              </span>
            </div>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Customizing resumes to improve your application success rates.
            </p>
          </div>

          <div>
            <h3
              className="font-semibold text-gray-900 dark:text-white mb-4"
            >
              Product
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white text-sm"
                >
                  Features
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white text-sm"
                >
                  Pricing
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white text-sm"
                >
                  Testimonials
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white text-sm"
                >
                  FAQ
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3
              className="font-semibold text-gray-900 dark:text-white mb-4"
            >
              Company
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white text-sm"
                >
                  About
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white text-sm"
                >
                  Blog
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white text-sm"
                >
                  Careers
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white text-sm"
                >
                  Contact
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3
              className="font-semibold text-gray-900 dark:text-white mb-4"
            >
              Legal
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white text-sm"
                >
                  Privacy Policy
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white text-sm"
                >
                  Terms of Service
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white text-sm"
                >
                  Cookie Policy
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div
          className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-800 text-center"
        >
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            © {new Date().getFullYear()} ResumeRocket. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}